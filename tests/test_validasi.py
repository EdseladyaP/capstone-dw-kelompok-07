"""Aturan validasi diuji dengan salinan Silver yang sengaja dirusak.

Silver asli harus lolos. Setiap kerusakan harus ditangkap; kalau lolos, aturannya terlalu longgar
atau memeriksa kolom yang salah. Salinan rusak hanya ada di memori, tidak pernah ditulis ke data/.
"""
import pandas as pd
import pandera.pandas as pa
import pytest

from src import konfigurasi as K
from src.validasi import aturan

skema = aturan.skema()


def harus_gagal(df, nama_aturan):
    with pytest.raises(pa.errors.SchemaErrors) as e:
        skema.validate(df, lazy=True)
    assert aturan.kena(nama_aturan, e.value.failure_cases), f"kerusakan tidak tertangkap oleh {nama_aturan}"


def test_silver_asli_lolos(silver_contoh):
    skema.validate(silver_contoh, lazy=True)


def test_nilai_di_luar_rentang_satuan(silver_contoh):
    rusak = silver_contoh.copy()
    satuan = rusak.loc[rusak.index[0], "satuan"]
    rusak.loc[rusak.index[0], "nilai"] = K.RENTANG[satuan][1] * 1.5 + 1
    harus_gagal(rusak, "nilai_dalam_rentang_satuan")


def test_kunci_kembar(silver_contoh):
    rusak = pd.concat([silver_contoh, silver_contoh.iloc[[0]]], ignore_index=True)
    harus_gagal(rusak, "kunci unik")


def test_satuan_kedua_dalam_satu_seri(silver_contoh, monkeypatch):
    rusak = silver_contoh.copy()
    # satuan kedua yang sah di kamus (kasus dengan satu satuan saja diberi satuan sah tambahan sementara)
    monkeypatch.setitem(K.RENTANG, "satuan_lain", (-1e12, 1e12))
    lain = next(s for s in K.RENTANG if s != rusak.loc[rusak.index[0], "satuan"])
    rusak.loc[rusak.index[0], "satuan"] = lain
    harus_gagal(rusak, "satu_satuan_per_seri")


def test_kode_rincian_di_luar_kamus(silver_contoh):
    rusak = silver_contoh.copy()
    rusak.loc[rusak.index[0], "rincian"] = "umur=10_14_salah;tidak_dikenal=X"
    harus_gagal(rusak, "rincian_dari_kamus")


def test_batas_bawah_melebihi_nilai(silver_contoh):
    rusak = silver_contoh.copy()
    i = rusak.index[0]
    rusak.loc[i, "batas_bawah"] = rusak.loc[i, "nilai"] + 1
    harus_gagal(rusak, "batas_bawah_le_nilai_le_batas_atas")


def test_wilayah_tidak_dikenal(silver_contoh):
    rusak = silver_contoh.copy()
    rusak.loc[rusak.index[0], "wilayah_kode"] = 9800
    harus_gagal(rusak, "wilayah dan periode")
