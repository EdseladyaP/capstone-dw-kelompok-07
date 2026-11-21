"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver.

Urutan: susun Silver dari tabel mentah -> metadata seri -> simpan -> profil -> pembanding -> grid
-> kategori anomali. Profil dan grid membaca Silver yang sudah tersimpan, jadi keduanya selalu
sesuai dengan berkas yang di-commit.
"""
from src import konfigurasi as K
from src.laporan import ROOT, catat
from src.silver import anomali, bangun, grid, metadata, pembanding, profil

SILVER = ROOT / "data" / "silver" / "silver.parquet"


def jalankan(mentah):
    silver, info = bangun.susun(mentah)
    metadata.jalankan(mentah, info["cakupan_who"])
    katalog_salah = [k for k, s in K.SERI.items() if s["katalog_satuan"] not in ("—", s["satuan"])]
    sdg_beda = [k for k, s in K.SERI.items() if s["katalog_sdg"] not in ("—", s["sdg"])]
    catat(baris_bps=int((silver["sumber"] == "bps").sum()),
          baris_koreksi_satuan=int(silver["seri_kode"].isin(katalog_salah).sum()),
          baris_koreksi_sdg=int(silver["seri_kode"].isin(sdg_beda).sum()),
          baris_rujukan=int(silver["rujukan_tahun"].notna().sum()),
          baris_batas_who=int(silver["batas_bawah"].notna().sum()))
    SILVER.parent.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(SILVER, index=False)
    calon = profil.jalankan(silver)
    pembanding.jalankan(silver, mentah)
    grid.jalankan(silver, mentah)
    anomali.jalankan(silver, mentah, calon)
    print(f"           Silver: {len(silver):,} baris -> {SILVER.relative_to(ROOT)}")
    return silver
