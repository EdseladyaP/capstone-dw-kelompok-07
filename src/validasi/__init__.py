
from pathlib import Path

import numpy as np
import pandas as pd
import pandera.pandas as pa


ROOT = Path(__file__).resolve().parents[2]

KOLOM_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
]

KOLOM_PANEL = [
    "wilayah_id",
    "nama_wilayah",
    "tahun",
    "rata_rata_lama_sekolah_tahun",
    "apk_perguruan_tinggi_persen",
    "harapan_lama_sekolah_tahun",
    "status_rata_rata_lama_sekolah_tahun",
    "status_apk_perguruan_tinggi_persen",
    "status_harapan_lama_sekolah_tahun",
    "outlier_rata_rata_lama_sekolah_tahun",
    "outlier_apk_perguruan_tinggi_persen",
    "outlier_harapan_lama_sekolah_tahun",
]

KOLOM_DETAIL = [
    "seri_kode",
    "tahun",
    "wilayah_id",
    "wilayah",
    "kategori",
    "tahun_mulai_target",
    "status",
    "nama_wilayah",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
    "outlier_asli",
]


def _cek_kolom(df, kolom):
    kurang = sorted(set(kolom) - set(df.columns))
    if kurang:
        raise ValueError(f"Kolom wajib tidak tersedia: {kurang}")


def _cek_rentang_silver(df):
    nilai = pd.to_numeric(df["nilai"], errors="coerce")
    satuan = df["satuan"].astype(str).str.strip().str.casefold()

    persen = nilai[satuan == "persen"].dropna()
    tahun = nilai[satuan == "tahun"].dropna()

    # Persentase APK dapat melebihi 100.
    hasil_persen = (persen >= 0).all()
    hasil_tahun = tahun.between(0, 30).all()

    return bool(hasil_persen and hasil_tahun)

def _cek_panel(df):
    kunci = ["wilayah_id", "tahun"]

    if df.duplicated(kunci).any():
        return False

    if df["wilayah_id"].nunique() != 38:
        return False

    if (df["wilayah_id"] == 9999).any():
        return False

    jumlah_per_tahun = df.groupby("tahun")["wilayah_id"].nunique()

    return bool((jumlah_per_tahun == 38).all())


def _cek_detail(df):
    kunci = ["seri_kode", "wilayah_id", "tahun"]

    if df.duplicated(kunci).any():
        return False

    return bool(
        set(df["seri_kode"].dropna().unique())
        .issubset({"var1429", "var1443", "var417"})
    )


def _cek_rentang_detail(df):
    nilai = pd.to_numeric(df["nilai"], errors="coerce")
    satuan = df["satuan"].astype(str).str.strip().str.casefold()

    persen = nilai[satuan == "persen"].dropna()
    tahun = nilai[satuan == "tahun"].dropna()

    return bool(
        persen.between(0, 100).all()
        and tahun.between(0, 30).all()
    )


def _validasi_pandera(df, kolom, pemeriksaan):
    skema = pa.DataFrameSchema(
        columns={
            nama: pa.Column(nullable=True)
            for nama in kolom
        },
        checks=[
            pa.Check(pemeriksaan, error="Pemeriksaan struktur/nilai gagal")
        ],
        strict=False,
    )

    skema.validate(df, lazy=True)


def _buat_data_dictionary():
    folder = ROOT / "docs"
    folder.mkdir(parents=True, exist_ok=True)

    isi = """# Data Dictionary

## Silver

| Kolom | Keterangan |
|---|---|
| sumber | Sumber data |
| seri_kode | Kode indikator |
| wilayah_kode | Kode wilayah |
| nama_wilayah | Nama wilayah |
| periode | Periode observasi |
| jenis_periode | Jenis periode: tahun, semester, atau bulan |
| rincian | Kategori/rincian indikator |
| nilai | Nilai observasi |
| satuan | Satuan nilai |
| _berkas_raw | Lokasi berkas sumber |
| _sha256_raw | Hash berkas sumber |

Silver mempertahankan observasi asli, termasuk rincian,
periode, dan informasi sumber.

## Gold

### panel_provinsi_tahun

| Kolom | Keterangan |
|---|---|
| wilayah_id | Kode provinsi |
| nama_wilayah | Nama baku provinsi |
| tahun | Tahun observasi |
| rata_rata_lama_sekolah_tahun | Rata-rata lama sekolah, satuan tahun |
| apk_perguruan_tinggi_persen | APK perguruan tinggi, satuan persen |
| harapan_lama_sekolah_tahun | Harapan lama sekolah, satuan tahun |
| status_* | Status ketersediaan nilai indikator |
| outlier_* | Penanda outlier asli |

### panel_indikator_gold

Berisi observasi detail tiga indikator utama:
var1429 (RLS), var1443 (APK perguruan tinggi),
dan var417 (HLS).

Kolom nilai menyimpan nilai observasi sesuai satuannya.
Kolom outlier_asli menunjukkan apakah observasi
termasuk anomali yang dipertahankan.

### anomali_gold

Menyimpan hasil klasifikasi anomali, nilai Silver,
batas IQR, verifikasi sumber, dan tindakan.

### audit_snapshot_gold

Menyimpan catatan snapshot yang tidak dipilih
ketika terdapat lebih dari satu snapshot.

## Aturan satuan dan wilayah

- Persen memiliki rentang 0 sampai 100.
- Lama sekolah dalam tahun memiliki rentang 0 sampai 30.
- Panel utama berisi 38 provinsi.
- Kode nasional 9999 tidak dimasukkan ke panel provinsi.
- Nilai kosong tidak otomatis diganti dengan nol.
- Penanda outlier asli tetap dipertahankan.
"""

    (folder / "data-dictionary.md").write_text(
        isi, encoding="utf-8"
    )


def jalankan(silver, gold):
    laporan = [
        "# Laporan Validasi Silver dan Gold",
        "",
        "Validasi dilakukan menggunakan Pandera.",
        "",
    ]

    hasil_pemeriksaan = []

    def periksa(nama, fungsi):
        try:
            fungsi()
            hasil_pemeriksaan.append((nama, True, "Lolos"))
        except Exception as e:
            hasil_pemeriksaan.append(
                (nama, False, str(e).splitlines()[0])
            )

    # 1. Validasi Silver
    def validasi_silver():
        _cek_kolom(silver, KOLOM_SILVER)
        _validasi_pandera(
            silver,
            KOLOM_SILVER,
            _cek_rentang_silver,
        )

        if silver["nilai"].notna().sum() == 0:
            raise ValueError("Seluruh nilai Silver kosong.")

        if silver["wilayah_kode"].isna().any():
            raise ValueError("Terdapat kode wilayah kosong.")

    periksa("Struktur dan rentang nilai Silver", validasi_silver)

    # 2. Validasi panel provinsi-tahun
    panel = gold["panel_provinsi_tahun"]

    def validasi_panel():
        _cek_kolom(panel, KOLOM_PANEL)
        _validasi_pandera(
            panel,
            KOLOM_PANEL,
            _cek_panel,
        )

        if panel["tahun"].isna().any():
            raise ValueError("Terdapat tahun kosong.")

        aturan_rentang = {
            "rata_rata_lama_sekolah_tahun": (0, 30),
            "apk_perguruan_tinggi_persen": (0, 100),
            "harapan_lama_sekolah_tahun": (0, 30),
        }

        for kolom, (bawah, atas) in aturan_rentang.items():
            nilai = pd.to_numeric(panel[kolom], errors="coerce").dropna()

            if not nilai.between(bawah, atas).all():
                raise ValueError(f"Rentang nilai {kolom} tidak sesuai.")

        kolom_status = [c for c in panel.columns if c.startswith("status_")]

        for kolom in kolom_status:
            if panel[kolom].isna().any():
                raise ValueError(f"Status kosong pada {kolom}.")

        kolom_outlier = [c for c in panel.columns if c.startswith("outlier_")]

        for kolom in kolom_outlier:
            if panel[kolom].isna().any():
                raise ValueError(f"Penanda outlier kosong pada {kolom}.")

    periksa("Keunikan kunci dan kelengkapan panel Gold", validasi_panel)

    # 3. Validasi detail indikator
    detail = gold["panel_indikator_gold"]

    def validasi_detail():
        _cek_kolom(detail, KOLOM_DETAIL)
        _validasi_pandera(
            detail,
            KOLOM_DETAIL,
            _cek_detail,
        )

        _validasi_pandera(
            detail,
            KOLOM_DETAIL,
            _cek_rentang_detail,
        )

        if detail["outlier_asli"].isna().any():
            raise ValueError("Penanda outlier detail kosong.")

    periksa("Keunikan dan rentang detail Gold", validasi_detail)

    # 4. Validasi tabel anomali
    anomali = gold["anomali_gold"]

    def validasi_anomali():
        wajib = [
            "seri_kode",
            "wilayah_id",
            "tahun",
            "klasifikasi",
            "nilai_silver",
            "nilai_klasifikasi",
            "outlier_asli",
        ]

        _cek_kolom(anomali, wajib)

        if not anomali["outlier_asli"].fillna(False).all():
            raise ValueError("Ada anomali yang kehilangan penanda.")

        sama = np.isclose(
            pd.to_numeric(anomali["nilai_silver"], errors="coerce"),
            pd.to_numeric(anomali["nilai_klasifikasi"], errors="coerce"),
            equal_nan=False,
        )

        if not sama.all():
            raise ValueError("Nilai anomali berbeda dari Silver.")

    periksa("Konsistensi catatan anomali", validasi_anomali)

    # 5. Dokumentasi hasil
    for nama, lolos, pesan in hasil_pemeriksaan:
        status = "LULUS" if lolos else "GAGAL"
        laporan.append(f"- **{nama}: {status}** — {pesan}")

    laporan.extend([
        "",
        "## Ringkasan jumlah data",
        "",
        f"- Baris Silver: {len(silver)}",
        f"- Baris panel provinsi-tahun: {len(panel)}",
        f"- Baris detail indikator: {len(detail)}",
        f"- Baris anomali: {len(anomali)}",
        f"- Jumlah provinsi panel: {panel['wilayah_id'].nunique()}",
        f"- Rentang tahun panel: {panel['tahun'].min()}–{panel['tahun'].max()}",
        "",
        "## Catatan",
        "",
        "- Silver dapat menyimpan beberapa observasi untuk satu sel.",
        "- Gold harus memiliki kunci unik sesuai bentuk tabelnya.",
        "- Nilai kosong tidak diimputasi menjadi nol.",
        "- Penanda outlier dipertahankan.",
        "- Audit snapshot kosong berarti tidak ada baris snapshot yang dieliminasi.",
    ])

    folder = ROOT / "reports"
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "validasi.md").write_text(
        "\n".join(laporan) + "\n",
        encoding="utf-8",
    )

    _buat_data_dictionary()

    gagal = [nama for nama, lolos, _ in hasil_pemeriksaan if not lolos]

    print("\n=== HASIL VALIDASI ===")
    for nama, lolos, pesan in hasil_pemeriksaan:
        print(("LULUS" if lolos else "GAGAL"), "-", nama, ":", pesan)

    print("\nLaporan: reports/validasi.md")
    print("Data dictionary: docs/data-dictionary.md")

    if gagal:
        raise ValueError(
            "Validasi gagal pada: " + ", ".join(gagal)
        )

    print("\nSemua pemeriksaan validasi berhasil.")
    return hasil_pemeriksaan
