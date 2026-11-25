"""Aturan validasi Silver (pandera) yang berlaku untuk semua kasus.

Sumber kebenaran aturan ada di src/konfigurasi.py (rentang per satuan, nama dimensi rincian,
kode rincian sah) supaya aturan, data dictionary, dan skema SQL membaca kamus yang sama.
Aturan khas kasus ada di src/validasi/khusus.py.
"""
import re

import pandera.pandas as pa

from src import konfigurasi as K
from src import wilayah as W

KUNCI = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
POLA_RINCIAN = re.compile(r"^total$|^[a-z_]+=[^;=]+(;[a-z_]+=[^;=]+)*$")


def _dimensi_sah():
    from src import kamus_ilo
    statis = {d for c in getattr(K, "TABEL_STATIS", {}).values() for d, _ in c["dimensi"].values()}
    statis |= set(kamus_ilo.DIMENSI.values()) if any(s["sumber"] == "ilostat" for s in K.SERI.values()) else set()
    return set(K.RINCIAN_DIMENSI.values()) | {"rincian_bps"} | {d for d, _ in getattr(K, "RINCIAN_BPS", {}).values()} | statis


def rincian_sah(teks):
    """'total' atau 'dim=kode;dim=kode' dengan nama dimensi dari kamus dan kode yang terdaftar (bila ada daftarnya)."""
    if not POLA_RINCIAN.match(str(teks)):
        return False
    if teks == "total":
        return True
    for bagian in teks.split(";"):
        dim, kode = bagian.split("=", 1)
        if dim not in _dimensi_sah():
            return False
        daftar = K.KODE_RINCIAN.get(dim)
        if daftar is not None and kode not in daftar:
            return False
    return True


def satu_satuan_per_seri(df):
    return df.groupby("seri_kode")["satuan"].transform("nunique") == 1


def dalam_rentang_satuan(df):
    lo = df["satuan"].map(lambda s: K.RENTANG[s][0])
    hi = df["satuan"].map(lambda s: K.RENTANG[s][1])
    return (df["nilai"] >= lo) & (df["nilai"] <= hi)


def batas_mengapit_nilai(df):
    bawah_ok = df["batas_bawah"].isna() | (df["batas_bawah"] <= df["nilai"])
    atas_ok = df["batas_atas"].isna() | (df["nilai"] <= df["batas_atas"])
    return bawah_ok & atas_ok


def skema():
    wilayah_sah = list(W.PROVINSI) + [W.INDONESIA]
    return pa.DataFrameSchema(
        {
            "sumber": pa.Column(str, pa.Check.isin(sorted({s["sumber"] for s in K.SERI.values()}))),
            "seri_kode": pa.Column(str, pa.Check.isin(list(K.SERI))),
            "wilayah_kode": pa.Column(int, pa.Check.isin(wilayah_sah)),
            "nama_wilayah": pa.Column(str),
            "periode": pa.Column(str, pa.Check.str_matches(r"^\d{4}(-S[12]|-Q[1-4]|-(0[1-9]|1[0-2]))?$")),
            "jenis_periode": pa.Column(str, pa.Check.isin(["tahun", "semester", "triwulan", "bulan"])),
            "rincian": pa.Column(str, pa.Check(lambda s: s.map(rincian_sah), name="rincian_dari_kamus")),
            "nilai": pa.Column(float, nullable=False),
            "satuan": pa.Column(str, pa.Check.isin(list(K.RENTANG))),
            "batas_bawah": pa.Column(float, nullable=True),
            "batas_atas": pa.Column(float, nullable=True),
            "rujukan_tahun": pa.Column("Int64", nullable=True),
            "_sha256_raw": pa.Column(str, pa.Check.str_length(64, 64)),
        },
        checks=[
            pa.Check(satu_satuan_per_seri, name="satu_satuan_per_seri"),
            pa.Check(dalam_rentang_satuan, name="nilai_dalam_rentang_satuan"),
            pa.Check(batas_mengapit_nilai, name="batas_bawah_le_nilai_le_batas_atas"),
        ],
        unique=KUNCI,
        strict=False,
    )


def kena(nama, gagal):
    """Apakah aturan `nama` (dari DAFTAR) muncul di tabel failure_cases pandera."""
    if gagal is None or len(gagal) == 0:
        return False
    cek = gagal["check"].astype(str)
    kolom = gagal["column"].astype(str)
    bernama = {"rincian_dari_kamus", "satu_satuan_per_seri", "nilai_dalam_rentang_satuan",
               "batas_bawah_le_nilai_le_batas_atas"}
    if nama in bernama:
        return cek.str.contains(nama, regex=False).any()
    unik = cek.str.contains("unique", case=False)
    if nama == "kunci unik":
        return unik.any()
    wil = kolom.isin(["wilayah_kode", "periode", "jenis_periode"])
    if nama == "wilayah dan periode":
        return wil.any()
    lain = ~(cek.isin(bernama) | cek.str.contains("|".join(bernama)) | unik | wil)
    return lain.any()


DAFTAR = [
    ("kolom dan tipe", "setiap kolom ada dengan tipe yang benar; nilai tidak kosong"),
    ("rincian_dari_kamus", "rincian 'total' atau 'dimensi=kode' dengan dimensi/kode dari kamus konfigurasi"),
    ("satu_satuan_per_seri", "satu seri hanya punya satu satuan"),
    ("nilai_dalam_rentang_satuan", "nilai berada di rentang sah satuannya (persen 0–100, per 1.000 0–1.000, ...)"),
    ("batas_bawah_le_nilai_le_batas_atas", "untuk baris yang punya batas: batas bawah ≤ nilai ≤ batas atas"),
    ("kunci unik", "kombinasi " + " + ".join(KUNCI) + " tidak kembar"),
    ("wilayah dan periode", "wilayah_kode dari kamus 38 provinsi + 9999; periode berbentuk baku"),
]
