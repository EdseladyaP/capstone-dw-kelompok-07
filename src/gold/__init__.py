
"""Aturan Tahap 19: pemilihan satu nilai per sel dan pembentukan panel Gold."""

from pathlib import Path
import csv
import io
import re

import pandas as pd

from src import konfigurasi as K
from src.gold import muat_sql, nasional, nasional_gold, rekonsiliasi


ROOT = Path(__file__).resolve().parents[2]

SERI_PANEL = {
    "var1443": "apk_perguruan_tinggi_persen",
    "var417": "harapan_lama_sekolah_tahun",
    "var1429": "rata_rata_lama_sekolah_tahun",
}

KOLOM_KUNCI = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "periode",
    "jenis_periode",
    "rincian",
]


def _kategori_ke_rincian(kategori):
    """Terjemahkan label turvar mentah di berkas anomali ke rincian baku Silver."""
    kat = str(kategori).strip()
    if kat.casefold() in {x.casefold() for x in K.RINCIAN_TOTAL_BPS | {"Tidak ada"}}:
        return "total"
    for _, (dimensi, kamus) in K.RINCIAN_BPS.items():
        for label, kode in kamus.items():
            if kat == label:
                return f"{dimensi}={kode}"
    return kat


def _pilih_snapshot(silver):
    """Pilih snapshot terbaru; jangan menyembunyikan konflik dalam snapshot sama."""
    df = silver.copy()

    df["_tanggal_snapshot"] = pd.to_datetime(
        df["_berkas_raw"].astype(str).str.extract(
            r"(\d{4}-\d{2}-\d{2})", expand=False
        ),
        errors="coerce",
    )

    hasil = []
    audit = []

    for _, grup in df.groupby(KOLOM_KUNCI, dropna=False, sort=False):
        if len(grup) == 1:
            hasil.append(grup.iloc[0])
            continue

        tanggal_terbaru = grup["_tanggal_snapshot"].max()

        if pd.isna(tanggal_terbaru):
            terbaru = grup
        else:
            terbaru = grup[
                grup["_tanggal_snapshot"] == tanggal_terbaru
            ]

        if terbaru["nilai"].nunique(dropna=False) > 1:
            raise ValueError(
                "Konflik nilai pada snapshot dengan tanggal sama. "
                "Periksa _berkas_raw dan nilai: "
                + terbaru[
                    ["seri_kode", "wilayah_kode", "periode",
                     "rincian", "nilai", "_berkas_raw"]
                ].to_string(index=False)
            )

        pilihan = terbaru.iloc[0]
        hasil.append(pilihan)

        audit.append({
            "seri_kode": pilihan["seri_kode"],
            "wilayah_kode": pilihan["wilayah_kode"],
            "periode": pilihan["periode"],
            "rincian": pilihan["rincian"],
            "jumlah_baris_snapshot": len(grup),
            "jumlah_baris_tidak_dipilih": len(grup) - 1,
            "snapshot_dipilih": pilihan["_berkas_raw"],
            "nilai_dipilih": pilihan["nilai"],
        })

    terpilih = pd.DataFrame(hasil).drop(
        columns=["_tanggal_snapshot"]
    ).reset_index(drop=True)

    audit_snapshot = pd.DataFrame(audit, columns=[
        "seri_kode",
        "wilayah_kode",
        "periode",
        "rincian",
        "jumlah_baris_snapshot",
        "jumlah_baris_tidak_dipilih",
        "snapshot_dipilih",
        "nilai_dipilih",
    ]).astype({
        "seri_kode": "string",
        "wilayah_kode": "int64",
        "periode": "string",
        "rincian": "string",
        "jumlah_baris_snapshot": "int64",
        "jumlah_baris_tidak_dipilih": "int64",
        "snapshot_dipilih": "string",
        "nilai_dipilih": "float64",
    })

    kunci_gold = [
        "seri_kode", "wilayah_kode", "periode", "rincian"
    ]

    if terpilih.duplicated(kunci_gold).any():
        raise ValueError(
            "Gold masih memiliki lebih dari satu nilai pada kunci indikator."
        )

    return terpilih, audit_snapshot


def _buat_panel(silver):
    """Bentuk grid Gold berdasarkan grid panel yang sudah diverifikasi."""
    file_grid = ROOT / "reports" / "grid_panel.csv"

    if not file_grid.exists():
        raise FileNotFoundError(
            "Grid acuan tidak ditemukan: reports/grid_panel.csv"
        )

    grid = pd.read_csv(file_grid)

    wajib_grid = {
        "seri_kode", "tahun", "wilayah_id",
        "wilayah", "status"
    }
    if not wajib_grid.issubset(grid.columns):
        raise ValueError("Kolom wajib grid_panel.csv tidak lengkap.")

    grid = grid[grid["seri_kode"].isin(SERI_PANEL)].copy()

    # Nilai observasi Gold harus berasal dari Silver.
    # Grid hanya digunakan sebagai acuan wilayah, tahun, dan status.
    grid = grid.drop(columns=["nilai"], errors="ignore")
    grid["tahun"] = pd.to_numeric(grid["tahun"], errors="raise").astype(int)
    grid["wilayah_id"] = pd.to_numeric(
        grid["wilayah_id"], errors="raise"
    ).astype(int)

    data = silver[
        silver["seri_kode"].isin(SERI_PANEL)
    ].copy()

    # Panel analisis hanya memakai observasi tahunan.
    non_tahunan = data[data["jenis_periode"] != "tahun"]
    if not non_tahunan.empty:
        raise ValueError(
            "Ditemukan periode semester/bulan pada indikator panel. "
            "Jangan dirata-ratakan otomatis; tetapkan aturan agregasi "
            "berdasarkan definisi indikator terlebih dahulu."
        )

    data["tahun"] = pd.to_numeric(
        data["periode"], errors="raise"
    ).astype(int)

    # Indikator utama hanya memakai rincian agregat. Silver menulisnya 'total',
    # bukan 'Tidak ada' (label turvar mentah diterjemahkan di src/silver/).
    rincian_lain = data[data["rincian"] != "total"]
    if not rincian_lain.empty:
        raise ValueError(
            "Ditemukan rincian selain 'total' pada indikator utama. "
            "Tinjau kesetaraan rincian sebelum masuk panel Gold."
        )

    data = data[data["wilayah_kode"] != 9999].copy()

    data = data.rename(columns={
        "wilayah_kode": "wilayah_id"
    })

    kunci = ["seri_kode", "tahun", "wilayah_id"]

    if data.duplicated(kunci).any():
        raise ValueError(
            "Masih ada lebih dari satu nilai untuk indikator, tahun, "
            "dan provinsi yang sama."
        )

    detail = grid.merge(
        data[
            kunci + ["nama_wilayah", "nilai", "satuan",
                     "_berkas_raw", "_sha256_raw"]
        ],
        on=kunci,
        how="left",
        validate="one_to_one",
    )

    detail["nama_wilayah"] = detail["nama_wilayah"].fillna(
        detail["wilayah"]
    )

    # Status grid menjadi acuan; nilai kosong tidak diisi nol.
    detail["outlier_asli"] = False

    return detail


def _bawa_anomali(detail, silver):
    """Bawa semua 140 klasifikasi anomali, tanpa mengubah nilai."""
    file_anomali = ROOT / "reports" / "klasifikasi_anomali.csv"

    if not file_anomali.exists():
        raise FileNotFoundError(
            "File klasifikasi tidak ditemukan: "
            "reports/klasifikasi_anomali.csv"
        )

    # Berkas cara lama memakai BOM dan label turvar mentah ('Tidak ada', 'SD/sederajat', ...).
    anomali = pd.read_csv(file_anomali, encoding="utf-8-sig")
    anomali["kategori"] = anomali["kategori"].map(_kategori_ke_rincian)

    anomali["tahun"] = pd.to_numeric(
        anomali["tahun"], errors="raise"
    ).astype(int)
    anomali["wilayah_id"] = pd.to_numeric(
        anomali["wilayah_id"], errors="raise"
    ).astype(int)

    silver_cek = silver.copy()
    silver_cek["tahun"] = pd.to_numeric(
        silver_cek["periode"], errors="coerce"
    )

    silver_cek = silver_cek.rename(columns={
        "wilayah_kode": "wilayah_id",
        "rincian": "kategori",
    })

    kunci = ["seri_kode", "wilayah_id", "tahun", "kategori"]

    hasil = anomali.merge(
        silver_cek[
            kunci + ["nilai", "_berkas_raw", "_sha256_raw"]
        ],
        on=kunci,
        how="left",
        suffixes=("_klasifikasi", "_silver"),
        indicator=True,
        validate="one_to_one",
    )

    if not (hasil["_merge"] == "both").all():
        raise ValueError(
            "Ada klasifikasi anomali yang tidak cocok dengan Silver."
        )

    if not (
        hasil["nilai_klasifikasi"].round(10)
        == hasil["nilai_silver"].round(10)
    ).all():
        raise ValueError(
            "Nilai anomali berbeda dari nilai pada Silver."
        )

    hasil["outlier_asli"] = (
        hasil["klasifikasi"] == "outlier_asli"
    )

    # Tandai observasi outlier pada detail panel utama.
    kunci_detail = ["seri_kode", "wilayah_id", "tahun"]
    tanda = hasil[kunci_detail + ["outlier_asli"]].drop_duplicates()

    detail = detail.drop(columns=["outlier_asli"]).merge(
        tanda,
        on=kunci_detail,
        how="left",
        validate="one_to_one",
    )
    detail["outlier_asli"] = detail["outlier_asli"].fillna(False)

    return detail, hasil.drop(columns=["_merge"])


def _buat_panel_lebar(detail):
        # Seragamkan nama wilayah berdasarkan kode wilayah.
    nama_baku = {
        2100: "KEPULAUAN RIAU",
        3400: "DI YOGYAKARTA",
    }

    detail = detail.copy()
    detail["nama_wilayah"] = detail["wilayah_id"].map(
        nama_baku
    ).fillna(detail["nama_wilayah"])
    """Pisahkan indikator dan status masing-masing indikator."""
    nilai = detail.pivot(
        index=["wilayah_id", "nama_wilayah", "tahun"],
        columns="seri_kode",
        values="nilai",
    )

    status = detail.pivot(
        index=["wilayah_id", "nama_wilayah", "tahun"],
        columns="seri_kode",
        values="status",
    )

    outlier = detail.pivot(
        index=["wilayah_id", "nama_wilayah", "tahun"],
        columns="seri_kode",
        values="outlier_asli",
    )

    panel = nilai.rename(columns=SERI_PANEL).reset_index()
    status = status.rename(columns={
        kode: f"status_{nama}" for kode, nama in SERI_PANEL.items()
    }).reset_index()
    outlier = outlier.rename(columns={
        kode: f"outlier_{nama}" for kode, nama in SERI_PANEL.items()
    }).reset_index()

    panel = panel.merge(
        status, on=["wilayah_id", "nama_wilayah", "tahun"],
        validate="one_to_one"
    )
    panel = panel.merge(
        outlier, on=["wilayah_id", "nama_wilayah", "tahun"],
        validate="one_to_one"
    )

    # Tandai periode sebelum awal ketersediaan indikator.
    tahun_mulai = {
        "var1429": 2015,
        "var1443": 2015,
        "var417": 2010,
    }

    for kode, nama in SERI_PANEL.items():
        kolom_status = f"status_{nama}"
        panel.loc[
            panel["tahun"] < tahun_mulai[kode],
            kolom_status
        ] = "belum_terbentuk"

    for kolom in [
        f"outlier_{nama}" for nama in SERI_PANEL.values()
    ]:
        panel[kolom] = panel[kolom].fillna(False).astype(bool)
    return panel.sort_values(
        ["wilayah_id", "tahun"]
    ).reset_index(drop=True)


def _catat_keputusan(baris):
    """Tambahkan keputusan Gold satu kali; BOM dan isi log lama tidak ditulis ulang."""
    jalur = ROOT / "log-keputusan.csv"
    lama = jalur.read_bytes() if jalur.exists() else b""
    ada = {r.get("id") for r in csv.DictReader(io.StringIO(lama.decode("utf-8-sig")))}
    kolom = [
        "id", "tanggal", "nim", "tahap", "seri_kode",
        "keputusan", "alternatif_ditolak", "alasan", "dampak_baris"
    ]
    baru = [e for e in baris if e["id"] not in ada]
    if not baru:
        return
    keluaran = io.StringIO()
    penulis = csv.writer(keluaran, lineterminator="\n")
    for entri in baru:
        penulis.writerow([entri[k] for k in kolom])
    with jalur.open("ab") as f:
        if not lama:
            f.write(b"\xef\xbb\xbf")
        elif not lama.endswith(b"\n"):
            f.write(b"\n")
        f.write(keluaran.getvalue().encode("utf-8"))


def jalankan(silver):
    """Terima Silver, bentuk panel Gold, simpan Parquet, dan kembalikan tabel."""
    silver = silver.copy()

    silver["wilayah_kode"] = pd.to_numeric(
        silver["wilayah_kode"], errors="raise"
    ).astype(int)

    silver["nilai"] = pd.to_numeric(
        silver["nilai"], errors="raise"
    )

    terpilih, audit_snapshot = _pilih_snapshot(silver)

    detail = _buat_panel(terpilih)
    detail, audit_anomali = _bawa_anomali(detail, terpilih)

    panel = _buat_panel_lebar(detail)

    folder = ROOT / "data" / "gold"
    folder.mkdir(parents=True, exist_ok=True)

    panel.to_parquet(
        folder / "panel_provinsi_tahun.parquet", index=False
    )
    detail.to_parquet(
        folder / "panel_indikator_gold.parquet", index=False
    )
    audit_anomali.to_parquet(
        folder / "anomali_gold.parquet", index=False
    )
    audit_snapshot.to_parquet(
        folder / "audit_snapshot_gold.parquet", index=False
    )

    # Tahap 5–6: pertahankan artefak Sprint 1 dan buat tabel nasional Gold.
    # Modul lama sebelumnya dijalankan manual, sehingga angka di reports/angka.json
    # tidak bisa diulang dari pipeline. Memanggilnya di sini menyatukan reproduksi.
    hasil_nasional = nasional.jalankan(silver)
    tabel_nasional = nasional_gold.jalankan(silver)
    hasil_rekonsiliasi = rekonsiliasi.jalankan(tabel_nasional)

    data_gold_sql = {
        "panel_provinsi_tahun": panel,
        "panel_indikator_gold": detail,
        "anomali_gold": audit_anomali,
        "audit_snapshot_gold": audit_snapshot,
        "nasional_gold": tabel_nasional,
        "rekonsiliasi_nasional": hasil_rekonsiliasi,
    }

    muat_sql.jalankan(silver, data_gold_sql, hasil_nasional)

    jumlah_baris_dipilih = len(
        terpilih[terpilih["seri_kode"].isin(SERI_PANEL)
                 & (terpilih["wilayah_kode"] != 9999)]
    )
    jumlah_di_luar_panel = len(terpilih) - jumlah_baris_dipilih
    jumlah_snapshot_tidak_dipilih = int(
        audit_snapshot["jumlah_baris_tidak_dipilih"].sum()
    ) if not audit_snapshot.empty else 0

    tanggal = "2026-11-24"
    keputusan = [
        {
            "id": "K-037",
            "tanggal": tanggal,
            "nim": "124450078",
            "tahap": "gold",
            "seri_kode": "duplikasi_snapshot",
            "keputusan": "Memilih snapshot bertanggal terbaru setelah membandingkan nilai; konflik nilai dalam tanggal snapshot yang sama dihentikan untuk pemeriksaan",
            "alternatif_ditolak": "Mengambil baris pertama tanpa membandingkan snapshot",
            "alasan": "Menjaga satu nilai per sel dan mempertahankan jejak snapshot yang dipilih",
            "dampak_baris": str(jumlah_snapshot_tidak_dipilih),
        },
        {
            "id": "K-038",
            "tanggal": tanggal,
            "nim": "124450078",
            "tahap": "gold",
            "seri_kode": "var1443;var417;var1429",
            "keputusan": "Panel provinsi hanya memuat APK PT, HLS, dan RLS dengan rincian total; indikator lain serta wilayah nasional tidak dicampurkan ke panel",
            "alternatif_ditolak": "Menggabungkan semua seri dan rincian ke satu kolom nilai",
            "alasan": "Menjaga konstruk indikator, wilayah, dan satuan tetap terpisah",
            "dampak_baris": str(jumlah_di_luar_panel),
        },
        {
            "id": "K-039",
            "tanggal": tanggal,
            "nim": "124450078",
            "tahap": "gold",
            "seri_kode": "var1443;var417;var1429",
            "keputusan": "Panel utama memakai periode tahunan; periode semester atau bulan tidak dirata-ratakan otomatis tanpa aturan agregasi yang sesuai definisi indikator",
            "alternatif_ditolak": "Menggabungkan periode sub-tahunan dengan rata-rata tanpa pemeriksaan",
            "alasan": "Ketiga indikator panel pada Silver saat ini memiliki jenis_periode tahun",
            "dampak_baris": "0",
        },
        {
            "id": "K-040",
            "tanggal": tanggal,
            "nim": "124450078",
            "tahap": "gold",
            "seri_kode": "anomali",
            "keputusan": "Mempertahankan nilai asli dan membawa seluruh penanda klasifikasi anomali ke tabel audit Gold serta penanda indikator panel",
            "alternatif_ditolak": "Menghapus atau mengoreksi outlier asli tanpa bukti galat input",
            "alasan": "Seluruh 140 klasifikasi cocok dengan Silver dan nilai sumber tetap dipertahankan",
            "dampak_baris": "0",
        },
    ]

    _catat_keputusan(keputusan)

    print("Gold berhasil dibuat.")
    print("Baris panel provinsi-tahun:", len(panel))
    print("Baris detail indikator:", len(detail))
    print("Klasifikasi anomali:", len(audit_anomali))
    print("Snapshot tidak dipilih:", jumlah_snapshot_tidak_dipilih)
    print("Baris Silver di luar panel utama:", jumlah_di_luar_panel)
    print("Baris tabel nasional Gold:", len(tabel_nasional))

    return {
        "panel_provinsi_tahun": panel,
        "panel_indikator_gold": detail,
        "anomali_gold": audit_anomali,
        "audit_snapshot_gold": audit_snapshot,
        "nasional_gold": tabel_nasional,
    }
