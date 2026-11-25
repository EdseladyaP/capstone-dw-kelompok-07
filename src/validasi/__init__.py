
"""Tahap 8 — Validasi Silver dan Gold."""

import numpy as np
import pandas as pd
import pandera.pandas as pa

from src.common.hasil import tulis_hasil
from src.dokumen import tulis_data_dictionary
from src.laporan import angka, catat, simpan_angka, tabel_md, tulis
from src.validasi import aturan, khusus


KOLOM_SILVER = [
    "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
    "periode", "jenis_periode", "rincian", "nilai", "satuan",
    "_berkas_raw", "_sha256_raw",
]

KOLOM_PANEL = [
    "wilayah_id", "nama_wilayah", "tahun",
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
    "seri_kode", "tahun", "wilayah_id", "wilayah",
    "kategori", "tahun_mulai_target", "status",
    "nama_wilayah", "nilai", "satuan",
    "_berkas_raw", "_sha256_raw", "outlier_asli",
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

    # APK dapat bernilai lebih dari 100 persen.
    return bool((persen >= 0).all() and tahun.between(0, 30).all())


def _cek_panel(df):
    kunci = ["wilayah_id", "tahun"]

    if df.duplicated(kunci).any():
        return False
    if df["wilayah_id"].nunique() != 38:
        return False
    if (df["wilayah_id"] == 9999).any():
        return False

    jumlah = df.groupby("tahun")["wilayah_id"].nunique()
    return bool((jumlah == 38).all())


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

    return bool((persen >= 0).all() and tahun.between(0, 30).all())


def _validasi_gold(gold):
    hasil = []

    def periksa(nama, fungsi):
        try:
            fungsi()
            hasil.append({
                "aturan": nama,
                "jenis": "keras (Gold)",
                "keterangan": "Pemeriksaan struktur dan nilai Gold",
                "hasil": "LOLOS",
            })
        except Exception as e:
            hasil.append({
                "aturan": nama,
                "jenis": "keras (Gold)",
                "keterangan": str(e).splitlines()[0],
                "hasil": "GAGAL",
            })

    panel = gold["panel_provinsi_tahun"]
    detail = gold["panel_indikator_gold"]
    anomali = gold["anomali_gold"]

    def validasi_panel():
        _cek_kolom(panel, KOLOM_PANEL)

        if not _cek_panel(panel):
            raise ValueError("Kunci atau kelengkapan panel tidak sesuai.")

        if panel["tahun"].isna().any():
            raise ValueError("Terdapat tahun kosong.")

        rentang = {
            "rata_rata_lama_sekolah_tahun": (0, 30),
            "apk_perguruan_tinggi_persen": (0, None),
            "harapan_lama_sekolah_tahun": (0, 30),
        }

        for kolom, (bawah, atas) in rentang.items():
            nilai = pd.to_numeric(panel[kolom], errors="coerce").dropna()
            if (nilai < bawah).any():
                raise ValueError(f"Nilai negatif pada {kolom}.")
            if atas is not None and not nilai.between(bawah, atas).all():
                raise ValueError(f"Rentang {kolom} tidak sesuai.")

        for kolom in panel.columns:
            if kolom.startswith(("status_", "outlier_")):
                if panel[kolom].isna().any():
                    raise ValueError(f"Ada nilai kosong pada {kolom}.")

    def validasi_detail():
        _cek_kolom(detail, KOLOM_DETAIL)
        if not _cek_detail(detail):
            raise ValueError("Kunci atau seri detail Gold tidak sesuai.")
        if not _cek_rentang_detail(detail):
            raise ValueError("Rentang nilai detail Gold tidak sesuai.")
        if detail["outlier_asli"].isna().any():
            raise ValueError("Penanda outlier detail kosong.")

    def validasi_anomali():
        wajib = [
            "seri_kode", "wilayah_id", "tahun", "klasifikasi",
            "nilai_silver", "nilai_klasifikasi", "outlier_asli",
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

    periksa("Struktur dan kelengkapan panel Gold", validasi_panel)
    periksa("Struktur dan rentang detail Gold", validasi_detail)
    periksa("Konsistensi catatan anomali Gold", validasi_anomali)

    return hasil


def jalankan(silver, gold):
    # Validasi umum Silver dari main.
    gagal_umum = pd.DataFrame()

    try:
        aturan.skema().validate(silver, lazy=True)
    except pa.errors.SchemaErrors as e:
        gagal_umum = e.failure_cases[
            ["column", "check", "failure_case", "index"]
        ]

    hasil = [
        {
            "aturan": nama,
            "jenis": "keras (umum)",
            "keterangan": ket,
            "hasil": "GAGAL" if aturan.kena(nama, gagal_umum) else "LOLOS",
        }
        for nama, ket in aturan.DAFTAR
    ]

    # Validasi khusus kasus dari main.
    rinci_khusus = []

    for nama, ket, keras, fungsi in khusus.ATURAN:
        buruk = fungsi(silver)

        if buruk.empty:
            status = "LOLOS"
        elif keras:
            status = "GAGAL"
        else:
            status = f"PERINGATAN ({len(buruk)} baris)"

        hasil.append({
            "aturan": nama,
            "jenis": "keras (kasus)" if keras else "peringatan (kasus)",
            "keterangan": ket,
            "hasil": status,
        })

        if not buruk.empty:
            rinci_khusus.append(
                f"### {nama}\n\n" + tabel_md(buruk.head(30))
            )

    # Validasi tambahan untuk tabel Gold.
    hasil.extend(_validasi_gold(gold))

    tabel = pd.DataFrame(hasil)
    keras_gagal = tabel[tabel["hasil"] == "GAGAL"]

    catat(
        aturan_validasi=len(tabel),
        aturan_lolos=int((tabel["hasil"] == "LOLOS").sum()),
        aturan_peringatan=int(
            tabel["hasil"].str.startswith("PERINGATAN").sum()
        ),
        aturan_umum=len(aturan.DAFTAR),
        aturan_khas=sum(1 for a in khusus.ATURAN if a[2]),
        aturan_khas_peringatan=sum(1 for a in khusus.ATURAN if not a[2]),
    )

    # Laporan validasi tim.
    tulis("validasi.md", "\n\n".join([
        "# Hasil validasi Silver dan Gold",
        "Validasi mencakup aturan umum, aturan khusus kasus, "
        "dan pemeriksaan tambahan pada tabel Gold.",
        tabel_md(tabel),
        "## Kegagalan aturan umum",
        tabel_md(gagal_umum.head(50)) if len(gagal_umum) else "Tidak ada.",
        "## Baris yang memicu aturan kasus",
        "\n\n".join(rinci_khusus) or "Tidak ada.",
        "## Ringkasan Gold",
        f"- Baris panel: {len(gold['panel_provinsi_tahun'])}",
        f"- Baris detail: {len(gold['panel_indikator_gold'])}",
        f"- Baris anomali: {len(gold['anomali_gold'])}",
    ]))

    # Dokumentasi dan metrics dari main.
    tulis_data_dictionary(silver)
    simpan_angka()

    a = angka()
    metrik = {
        k: v for k, v in a.items()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    }
    tulis_hasil("kunci", metrik)

    if len(keras_gagal):
        raise SystemExit(
            "Validasi gagal: "
            + ", ".join(keras_gagal["aturan"])
            + ". Lihat reports/validasi.md"
        )

    print("Semua pemeriksaan validasi berhasil.")
    return tabel
