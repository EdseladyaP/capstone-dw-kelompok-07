"""Tahap Silver — standardisasi observasi BPS dan WDI."""

from pathlib import Path
import re

import pandas as pd


PROVINSI = {
    1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2100,
    3100, 3200, 3300, 3400, 3500, 3600, 5100, 5200, 5300, 6100,
    6200, 6300, 6400, 6500, 7100, 7200, 7300, 7400, 7500, 7600,
    8100, 8200, 9100, 9200, 9400, 9500, 9600, 9700,
}
WILAYAH_VALID = PROVINSI | {9999}

BERKAS_BPS = [
    "bps_sdg4_apk_csv",
    "bps_sdg4_apk_pt_csv",
    "bps_sdg4_hls_csv",
    "bps_sdg4_rls_csv",
    "bps_sdg4_4_3_1_v2685_csv",
]

SATUAN_SERI = {
    "var303": "Persen",
    "var1443": "Persen",
    "var417": "Tahun",
    "var1429": "Tahun",
    "var2685": "Persen",
}


def _bersihkan_nama(value):
    if pd.isna(value):
        return None
    nama = re.sub(r"<[^>]*>", "", str(value))
    return " ".join(nama.split()).strip()


def _rapikan_bps(data):
    hasil = []

    for nama_berkas in BERKAS_BPS:
        if nama_berkas not in data:
            raise KeyError(f"Data ekstraksi tidak ditemukan: {nama_berkas}")

        df = data[nama_berkas].copy()

        df["wilayah_kode"] = pd.to_numeric(
            df["wilayah_id"], errors="coerce"
        )
        df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
        df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

        df = df[
            df["wilayah_kode"].isin(WILAYAH_VALID)
            & df["tahun"].notna()
            & df["nilai"].notna()
        ].copy()

        df["wilayah_kode"] = df["wilayah_kode"].astype(int)
        df["nama_wilayah"] = df["wilayah"].apply(_bersihkan_nama)
        df.loc[df["wilayah_kode"] == 9999, "nama_wilayah"] = "Indonesia"

        df["periode"] = df["tahun"].astype(int).astype(str)
        df["jenis_periode"] = "tahun"

        df["rincian"] = df["turvar"].fillna("Tidak ada").astype(str)
        df["satuan"] = df["satuan"].fillna(
            df["seri_kode"].map(SATUAN_SERI)
        )

        kolom = [
            "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
            "periode", "jenis_periode", "rincian", "nilai", "satuan",
            "_berkas_raw", "_sha256_raw",
        ]
        hasil.append(df[kolom])

    return pd.concat(hasil, ignore_index=True)


def _rapikan_wdi(data):
    nama_data = "wdi_kelompok-05-hal-01"
    if nama_data not in data:
        raise KeyError(f"Data ekstraksi tidak ditemukan: {nama_data}")

    df = data[nama_data].copy()

    # Ambil hanya indikator pendidikan tinggi untuk Indonesia.
    df = df[
        (df["indicator.id"] == "SE.TER.ENRR")
        & (df["countryiso3code"] == "IDN")
    ].copy()

    df["nilai"] = pd.to_numeric(df["value"], errors="coerce")
    df["tahun"] = pd.to_numeric(df["date"], errors="coerce")
    df = df[df["nilai"].notna() & df["tahun"].notna()].copy()

    df["sumber"] = "wdi"
    df["seri_kode"] = "SE.TER.ENRR"
    df["wilayah_kode"] = 9999
    df["nama_wilayah"] = "Indonesia"
    df["periode"] = df["tahun"].astype(int).astype(str)
    df["jenis_periode"] = "tahun"
    df["rincian"] = "Tidak ada"
    df["satuan"] = "Persen"

    kolom = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "jenis_periode", "rincian", "nilai", "satuan",
        "_berkas_raw", "_sha256_raw",
    ]
    return df[kolom]


def jalankan(mentah):
    """Terima hasil ekstraksi, simpan Silver, dan kembalikan DataFrame."""
    bps = _rapikan_bps(mentah)
    wdi = _rapikan_wdi(mentah)

    silver = pd.concat([bps, wdi], ignore_index=True)

    silver["wilayah_kode"] = silver["wilayah_kode"].astype(int)
    silver["nilai"] = pd.to_numeric(silver["nilai"], errors="raise")
    silver["periode"] = silver["periode"].astype(str)

    kolom_wajib = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "jenis_periode", "rincian", "nilai", "satuan",
        "_berkas_raw", "_sha256_raw",
    ]

    if silver[kolom_wajib].isna().any().any():
        jumlah = silver[kolom_wajib].isna().sum()
        raise ValueError(
            "Masih ada nilai kosong pada kolom Silver:\n"
            + jumlah[jumlah > 0].to_string()
        )

    if silver.duplicated(
        subset=[
            "sumber", "seri_kode", "wilayah_kode",
            "periode", "rincian", "_berkas_raw",
        ]
    ).any():
        raise ValueError("Ditemukan duplikasi kunci pada data Silver.")

    tujuan = Path("data/silver/silver.parquet")
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(tujuan, index=False)

    print("Silver berhasil dibuat:", tujuan)
    print("Jumlah baris:", len(silver))
    print("Jumlah seri:", silver["seri_kode"].nunique())
    print("Jumlah wilayah:", silver["wilayah_kode"].nunique())

    return silver
