"""Aturan khas Kasus 07 diuji dengan baris yang sengaja dirusak."""
import pandas as pd

from src.validasi import khusus


def test_aturan_khusus_lolos_pada_silver_asli(silver_contoh):
    for nama, _, keras, fungsi in khusus.ATURAN:
        if keras:
            assert fungsi(silver_contoh).empty, nama


def test_hls_mustahil_tertangkap(silver_contoh):
    rusak = silver_contoh.copy()
    rusak.loc[rusak.index[rusak["seri_kode"] == "var417"][0], "nilai"] = 125.0
    assert not khusus.lama_sekolah_masuk_akal(rusak).empty


def test_jenjang_pt_di_var303_tertangkap(silver_contoh):
    rusak = silver_contoh.copy()
    rusak.loc[rusak.index[rusak["seri_kode"] == "var303"][0], "rincian"] = "jenjang=pt"
    assert not khusus.var303_tanpa_perguruan_tinggi(rusak).empty


def test_kabkota_tertangkap(silver_contoh):
    baris = silver_contoh[silver_contoh["seri_kode"] == "var417"].iloc[[0]].copy()
    baris["wilayah_kode"] = 1101
    assert not khusus.provinsi_saja(pd.concat([silver_contoh, baris], ignore_index=True)).empty
