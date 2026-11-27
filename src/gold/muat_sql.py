"""Memuat Silver dan Gold ke DuckDB dengan primary key dan validasi jumlah baris."""

from pathlib import Path

import duckdb
import pandas as pd

from src.laporan import ROOT, catat

DB = ROOT / "data" / "gold" / "gudang.duckdb"
DDL = Path(__file__).with_name("silver.sql")


KOLOM = {
    "panel_provinsi_tahun": [
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
    ],
    "panel_indikator_gold": [
        "seri_kode", "tahun", "wilayah_id", "wilayah", "kategori",
        "tahun_mulai_target", "status", "nama_wilayah", "nilai",
        "satuan", "_berkas_raw", "_sha256_raw", "outlier_asli",
    ],
    "anomali_gold": [
        "seri_kode", "kategori", "wilayah_id", "provinsi", "tahun",
        "periode", "nilai_klasifikasi", "Q1", "Q3", "IQR",
        "batas_bawah", "batas_atas", "alasan_ditandai",
        "klasifikasi", "verifikasi_sumber", "tindakan",
        "nilai_silver", "_berkas_raw", "_sha256_raw", "outlier_asli",
    ],
    "audit_snapshot_gold": [
        "seri_kode", "wilayah_kode", "periode", "rincian",
        "jumlah_baris_snapshot", "jumlah_baris_tidak_dipilih",
        "snapshot_dipilih", "nilai_dipilih",
    ],
    "nasional_gold": [
        "seri_kode", "rincian", "sumber", "periode", "jenis_periode",
        "nilai", "satuan", "batas_bawah", "batas_atas",
        "rujukan_tahun", "asal", "catatan", "_berkas_raw",
        "_sha256_raw",
    ],
}

KOLOM_NASIONAL = [
    "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
    "periode", "jenis_periode", "rincian", "nilai", "satuan",
    "sdg_kode", "batas_bawah", "batas_atas", "rujukan_tahun",
    "_berkas_raw", "_sha256_raw",
]

KOLOM_PASANGAN = [
    "id", "seri_utama", "pembanding", "jenis",
    "periode_beririsan", "tahun", "dugaan_kategori",
]


def _masukkan(con, nama, df, kolom):
    """Masukkan DataFrame menggunakan cursor terpisah dan validasi jumlah baris."""
    data = df[kolom].copy()
    cursor = con.cursor()

    try:
        cursor.register("data_masuk", data)
        cursor.execute(
            f"INSERT INTO {nama} SELECT * FROM data_masuk"
        ).fetchall()
        cursor.unregister("data_masuk")

        jumlah = cursor.execute(
            f"SELECT COUNT(*) FROM {nama}"
        ).fetchone()[0]

        if jumlah != len(data):
            raise AssertionError(
                f"{nama}: SQL {jumlah} baris, DataFrame {len(data)} baris"
            )

        return jumlah
    finally:
        cursor.close()


def jalankan(silver, data_gold, hasil_nasional):
    """Bangun ulang database dan validasi seluruh tabel."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)

    seri = pd.read_csv(
        ROOT / "docs" / "seri.csv"
    )[[
        "seri_kode", "sumber", "tingkat",
        "nama_baku", "satuan", "sdg_kode",
    ]].copy()

    seri["sdg_kode"] = seri["sdg_kode"].astype("string")

    nas = hasil_nasional["nasional"]
    pasangan = hasil_nasional["pasangan"]

    jumlah = {}

    with duckdb.connect(str(DB)) as con:
        for perintah in DDL.read_text(encoding="utf-8").split(";"):
            if perintah.strip():
                con.execute(perintah).fetchall()

        jumlah["seri"] = _masukkan(
            con, "seri", seri,
            ["seri_kode", "sumber", "tingkat",
             "nama_baku", "satuan", "sdg_kode"]
        )

        jumlah["silver"] = _masukkan(
            con, "silver", silver,
            [
                "sumber", "seri_kode", "wilayah_kode",
                "nama_wilayah", "periode", "jenis_periode",
                "rincian", "nilai", "satuan", "sdg_kode",
                "batas_bawah", "batas_atas", "rujukan_tahun",
                "_berkas_raw", "_sha256_raw",
            ]
        )

        for nama, kolom in KOLOM.items():
            jumlah[nama] = _masukkan(
                con, nama, data_gold[nama], kolom
            )

        jumlah["nasional"] = _masukkan(
            con, "nasional", nas, KOLOM_NASIONAL
        )

        jumlah["pasangan_rekonsiliasi"] = _masukkan(
            con, "pasangan_rekonsiliasi",
            pasangan, KOLOM_PASANGAN
        )

        # Validasi jumlah SQL terhadap DataFrame sumber.
        pembanding = {
            "silver": len(silver),
            "panel_provinsi_tahun": len(data_gold["panel_provinsi_tahun"]),
            "panel_indikator_gold": len(data_gold["panel_indikator_gold"]),
            "anomali_gold": len(data_gold["anomali_gold"]),
            "audit_snapshot_gold": len(data_gold["audit_snapshot_gold"]),
            "nasional": len(nas),
            "nasional_gold": len(data_gold["nasional_gold"]),
            "pasangan_rekonsiliasi": len(pasangan),
        }

        for nama, ekspektasi in pembanding.items():
            if jumlah[nama] != ekspektasi:
                raise AssertionError(
                    f"{nama}: SQL {jumlah[nama]}, "
                    f"DataFrame {ekspektasi}"
                )

    catat(
        baris_sql=jumlah["silver"],
        baris_sql_gold=sum(
            jumlah[k] for k in jumlah
            if k not in ("seri", "silver")
        ),
    )

    print("\nDatabase DuckDB berhasil dibuat:")
    print(DB.relative_to(ROOT))

    for nama, n in jumlah.items():
        print(f"  {nama}: {n:,} baris")

    return jumlah
