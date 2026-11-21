"""Tahap 1 — bukti otomatis ekstraksi: cakupan MANIFEST, lineage, kunci BPS, dan kasus k07.

Diadaptasi dari acuan `k07-partisipasi-lama-sekolah/sprint-1/tests/test_ekstraksi.py`
ditambah pemeriksaan khusus kasus 07 (turvar APK, kelompok umur, dan HLS).
"""
import json

import pytest

from src.common.manifest import RAW, baca
from src.laporan import ROOT

pytestmark = pytest.mark.skipif(not (RAW / "MANIFEST.csv").exists(), reason="jalankan python unduh_data.py dulu")


def _ekstraksi():
    from src import ekstraksi
    return ekstraksi.jalankan()


def test_semua_berkas_manifest_tertangani():
    hasil = _ekstraksi()
    assert set(hasil["_hitung"]["berkas"]) == set(baca())


def test_baris_per_berkas_tercatat_di_laporan():
    hasil = _ekstraksi()
    hitung = hasil["_hitung"]
    assert (hitung["baris"] > 0).all()
    laporan = (ROOT / "reports" / "ekstraksi.md").read_text(encoding="utf-8")
    for berkas in hasil["_hitung"]["berkas"]:
        assert berkas in laporan
    assert "24,726" in laporan


@pytest.mark.parametrize("nama", ["bps_json", "bps_csv", "wdi_data"])
def test_setiap_baris_data_membawa_lineage(nama):
    hasil = _ekstraksi()
    if nama not in hasil:
        pytest.skip("kasus tanpa pembaca ini")
    df = hasil[nama]
    assert df["_berkas_raw"].notna().all()
    assert df["_sha256_raw"].str.fullmatch(r"[0-9a-f]{64}").all()
    manifest = baca()
    for berkas, sha in df[["_berkas_raw", "_sha256_raw"]].drop_duplicates().values:
        assert manifest[berkas] == sha


def test_kunci_json_bps_cocok_dengan_csv():
    """Pemotongan datacontent harus menghasilkan pasangan kunci dan nilai yang sama dengan CSV."""
    hasil = _ekstraksi()
    if "bps_json" not in hasil or "bps_csv" not in hasil:
        pytest.skip("kasus tanpa BPS dua format")
    j = {(r.var_id, r.wilayah_id, r.turvar.strip(), r.tahun, r.turtahun.strip()): float(r.nilai)
         for r in hasil["bps_json"].itertuples()}
    c = {(r.var_id, r.wilayah_id, str(r.turvar).strip(), r.tahun, str(r.periode).strip()): float(r.nilai)
         for r in hasil["bps_csv"].itertuples()}
    assert j == c


def test_turvar_menentukan_seri_apk_pt():
    """var303 hanya SD/SMP/SM; var1443 satu-satunya APK perguruan tinggi (lihat 4.2)."""
    j = _ekstraksi()["bps_json"]
    apk = set(j.loc[j["var_id"] == "303", "turvar"].str.strip())
    pt = set(j.loc[j["var_id"] == "1443", "turvar"].str.strip())
    assert apk == {"SD/sederajat", "SMP/sederajat", "SM/sederajat"}
    assert pt == {"Tidak ada"}


def test_kelompok_umur_var2685_tidak_digabung():
    """Keempat kelompok umur var2685 tetap menjadi empat rincian tersendiri."""
    j = _ekstraksi()["bps_json"]
    umur = set(j.loc[j["var_id"] == "2685", "turvar"].str.strip())
    assert umur == {"Usia 15-24 tahun", "Usia 25-54 tahun", "Usia 55-64 tahun", "Usia 15-64 tahun"}
    assert j.loc[j["var_id"] == "2685", "turvar_id"].nunique() == 4


def test_wdi_hanya_seri_kasus():
    hasil = _ekstraksi()
    assert set(hasil["wdi_data"]["indicator_id"]) == {"SE.TER.ENRR"}
    assert set(hasil["wdi_meta"]["id"]) == {"SE.TER.ENRR"}


def test_hls_mentah_dan_jumlah_kabkota_dibuang():
    """Pembaca mempertahankan semua baris; penyaringan kabupaten/kota dilaporkan di Silver."""
    hasil = _ekstraksi()
    hls = hasil["bps_json"]
    assert int((hls["var_id"] == "417").sum()) == 8732
    angka = json.loads((ROOT / "reports" / "angka.json").read_text(encoding="utf-8"))
    assert angka["baris_kabkota_dibuang"] == 8167
