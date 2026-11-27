"""Aturan validasi khas Kasus 07 (panduan kelompok bagian 4.4), plus satu aturan peringatan.

Setiap fungsi menerima Silver dan mengembalikan baris yang melanggar (kosong = lolos).
"""
import pandas as pd

from src import wilayah as W


def lama_sekolah_masuk_akal(silver):
    """HLS di 5–20 tahun dan RLS di 3–15 tahun."""
    batas = {"var417": (5, 20), "var1429": (3, 15)}
    buruk = []
    for seri, (lo, hi) in batas.items():
        s = silver[silver["seri_kode"] == seri]
        buruk.append(s[(s["nilai"] < lo) | (s["nilai"] > hi)][["seri_kode", "wilayah_kode", "periode", "nilai"]])
    return pd.concat(buruk, ignore_index=True)


def var303_tanpa_perguruan_tinggi(silver):
    """var303 hanya jenjang SD, SMP, SM; APK perguruan tinggi hanya dari var1443."""
    s = silver[silver["seri_kode"] == "var303"]
    return s[~s["rincian"].isin(["jenjang=sd", "jenjang=smp", "jenjang=sm"])][["periode", "wilayah_kode", "rincian"]]


def umur_var2685_tidak_dijumlah(silver):
    """var2685 tidak punya baris total buatan (kelompok umurnya tumpang tindih)."""
    s = silver[silver["seri_kode"] == "var2685"]
    return s[s["rincian"] == "total"][["periode", "wilayah_kode", "nilai"]]


def provinsi_saja(silver):
    """Tidak ada baris kabupaten/kota (kode tidak berakhiran 00) di Silver."""
    return silver[~silver["wilayah_kode"].isin(list(W.NAMA))][["seri_kode", "wilayah_kode", "periode"]]


def rls_di_bawah_hls(silver):
    """Peringatan: RLS penduduk 15+ melebihi HLS anak 7 tahun pada provinsi dan tahun yang sama."""
    h = silver[silver["seri_kode"] == "var417"].set_index(["wilayah_kode", "periode"])["nilai"]
    r = silver[silver["seri_kode"] == "var1429"].set_index(["wilayah_kode", "periode"])["nilai"]
    g = pd.DataFrame({"hls": h, "rls": r}).dropna()
    return g[g["rls"] > g["hls"]].reset_index()


ATURAN = [
    ("lama_sekolah_masuk_akal", "HLS 5–20 tahun, RLS 3–15 tahun", True, lama_sekolah_masuk_akal),
    ("var303_tanpa_perguruan_tinggi", "var303 hanya jenjang SD, SMP, SM", True, var303_tanpa_perguruan_tinggi),
    ("umur_var2685_tidak_dijumlah", "var2685 tanpa baris total (kelompok umur tumpang tindih)", True, umur_var2685_tidak_dijumlah),
    ("provinsi_saja", "tidak ada baris kabupaten/kota", True, provinsi_saja),
    ("rls_di_bawah_hls", "RLS > HLS pada sel yang sama (peringatan)", False, rls_di_bawah_hls),
]
