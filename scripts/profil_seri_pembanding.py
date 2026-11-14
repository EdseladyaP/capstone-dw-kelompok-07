"""Profil seri pembanding nasional SE.TER.ENRR (World Bank WDI) — Kasus 07.

NIM  : 124450043 — Difanya Husakina
Tugas: Tahap 2. Profil seri pembanding SE.TER.ENRR (Sprint 1)

Skrip ini HANYA MEMBACA berkas mentah di data/raw/ (tidak mengubahnya) lalu menulis:
  1. docs/tabel_ketersediaan_seri_pembanding.csv    -> ringkasan seri x rincian + penanda sebanding
  2. docs/ketersediaan_seri_periode_rincian.csv     -> seri x periode x rincian (tingkat nasional)

Sumber angka murni dari berkas mentah:
  - WDI : data/raw/wdi/2026-10-20/data/kelompok-05-hal-01.json  (observasi Indonesia)
          data/raw/wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json
  - BPS : data/raw/bps/2026-10-17/*.csv dan data/raw/bps/2026-10-17/json/*.json

Jalankan dari akar repositori:
    python scripts/profil_seri_pembanding.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DOCS = ROOT / "docs"

WDI_DATA = RAW / "wdi" / "2026-10-20" / "data" / "kelompok-05-hal-01.json"
WDI_META_WDI = RAW / "wdi" / "2026-10-20" / "metadata" / "sumber2_indikator.json"
WDI_META_SDG = RAW / "wdi" / "2026-10-20" / "metadata" / "sumber46_indikator.json"
BPS_JSON = RAW / "bps" / "2026-10-17" / "json"

# Seri pembanding (WDI). Dimensi rincian yang benar-benar ada di berkas mentah.
WDI_INDIKATOR = {
    "SE.TER.ENRR": {"dimensi": "jenis_kelamin", "rincian": "Total (semua jenis kelamin)"},
    "SE.TER.ENRR.FE": {"dimensi": "jenis_kelamin", "rincian": "Perempuan"},
    "SE.TER.ENRR.MA": {"dimensi": "jenis_kelamin", "rincian": "Laki-laki"},
}

# Seri utama BPS: berkas mentah -> kode seri.
BPS_CSV = {
    "var1443": "bps/2026-10-17/sdg4_apk_pt.csv",
    "var303": "bps/2026-10-17/sdg4_apk.csv",
    "var417": "bps/2026-10-17/sdg4_hls.csv",
    "var1429": "bps/2026-10-17/sdg4_rls.csv",
    "var2685": "bps/2026-10-17/sdg4_4_3_1_v2685.csv",
}

# Dimensi rincian tiap seri utama, diturunkan dari kolom `turvar` berkas mentah.
BPS_DIMENSI = {
    "var1443": "tidak ada",
    "var303": "jenjang_pendidikan",
    "var417": "tidak ada",
    "var1429": "tidak ada",
    "var2685": "kelompok_umur",
}

# Penanda kandidat sebanding + alasan (dibahas pada docs/Tahap 2. Profil seri pembanding SE.TER.md).
KANDIDAT = {
    "SE.TER.ENRR": {
        "kandidat": "YA",
        "pasangan": "var1443",
        "alasan": (
            "Sama-sama Gross Enrollment Ratio jenjang tersier (usia resmi 19-23 tahun, "
            "catatan var1443) dalam satuan persen, tersedia pada tingkat nasional."
        ),
    },
    "SE.TER.ENRR.FE": {
        "kandidat": "TIDAK (bersyarat)",
        "pasangan": "-",
        "alasan": (
            "Seri utama var1443 (APK PT) tidak memuat rincian jenis kelamin; "
            "baris ini hanya bisa dipakai sebagai konteks deskriptif."
        ),
    },
    "SE.TER.ENRR.MA": {
        "kandidat": "TIDAK (bersyarat)",
        "pasangan": "-",
        "alasan": (
            "Seri utama var1443 (APK PT) tidak memuat rincian jenis kelamin; "
            "baris ini hanya bisa dipakai sebagai konteks deskriptif."
        ),
    },
    "var1443": {
        "kandidat": "YA",
        "pasangan": "SE.TER.ENRR",
        "alasan": (
            "APK Perguruan Tinggi, konstruk dan satuan sebanding dengan SE.TER.ENRR; "
            "dibandingkan pada tingkat nasional (wilayah_kode 9999)."
        ),
    },
    "var303": {
        "kandidat": "TIDAK",
        "pasangan": "-",
        "alasan": "Hanya memuat jenjang SD/SMP/SM; tidak ada jenjang perguruan tinggi.",
    },
    "var417": {
        "kandidat": "TIDAK",
        "pasangan": "-",
        "alasan": "Harapan Lama Sekolah (satuan tahun) bukan rasio partisipasi tersier.",
    },
    "var1429": {
        "kandidat": "TIDAK",
        "pasangan": "-",
        "alasan": "Rata-rata Lama Sekolah (satuan tahun) bukan rasio partisipasi tersier.",
    },
    "var2685": {
        "kandidat": "TIDAK",
        "pasangan": "-",
        "alasan": (
            "Tingkat partisipasi (bukan rasio enrollment), kelompok umur berbeda, "
            "dan hanya 2022-2024."
        ),
    },
}


def _berkas_rel(path: Path) -> str:
    return path.relative_to(RAW).as_posix()


def muat_wdi() -> pd.DataFrame:
    """Observasi WDI Indonesia sebagai DataFrame (kolom: indikator, tahun, nilai, satuan)."""
    body = json.loads(WDI_DATA.read_text(encoding="utf-8"))[1]
    df = pd.json_normalize(body)
    df = df.rename(
        columns={
            "indicator.id": "indikator",
            "indicator.value": "nama_indikator",
            "countryiso3code": "iso3",
            "date": "tahun",
            "value": "nilai",
            "unit": "satuan_mentah",
        }
    )
    df = df[df["iso3"] == "IDN"].copy()
    df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
    return df


def muat_metadata_wdi() -> dict:
    """Definisi/unit/penerbit indikator SE.TER.ENRR dari dua sumber WDI & SDG."""
    hasil: dict = {}
    for path, tag in ((WDI_META_WDI, "wdi"), (WDI_META_SDG, "sdg")):
        body = json.loads(path.read_text(encoding="utf-8"))[1]
        for item in body:
            if item.get("id") in WDI_INDIKATOR:
                hasil.setdefault(item["id"], {})[tag] = item
    return hasil


def muat_metadata_bps() -> dict:
    """Metadata var BPS (label, satuan, catatan, last_update) per kode seri `var<id>`."""
    hasil: dict = {}
    for path in sorted(BPS_JSON.glob("sdg4_*.json")):
        dok = json.loads(path.read_text(encoding="utf-8"))[0]
        var = dok["var"][0]
        hasil[f"var{var['val']}"] = {
            "label": var["label"],
            "satuan_mentah": var.get("unit", ""),
            "catatan": var.get("note", ""),
            "last_update": dok.get("last_update", ""),
            "berkas": _berkas_rel(path),
        }
    return hasil


# Satuan apa adanya dari metadata mentah; bila kolom unit kosong, sebutkan dasarnya.
SATUAN_TEKS = {
    "SE.TER.ENRR": "persen (% gross) [kolom unit kosong di berkas mentah]",
    "SE.TER.ENRR.FE": "persen (% gross) [kolom unit kosong di berkas mentah]",
    "SE.TER.ENRR.MA": "persen (% gross) [kolom unit kosong di berkas mentah]",
    "var1443": "persen [kolom satuan kosong; APK dinyatakan dalam persen]",
    "var303": "persen [kolom satuan kosong; APK dinyatakan dalam persen]",
    "var417": "Tahun",
    "var1429": "tahun [kolom satuan kosong; rata-rata lama sekolah dalam tahun]",
    "var2685": "Persen",
}


def _satuan_teks(kode: str) -> str:
    """Satuan yang dilaporkan apa adanya dari metadata mentah."""
    return SATUAN_TEKS.get(kode, "")


def _periode_teks(tahun: list[int]) -> str:
    return ";".join(str(t) for t in tahun)


def profil_wdi(wdi: pd.DataFrame, meta_wdi: dict) -> tuple[list[dict], list[dict]]:
    ringkas: list[dict] = []
    panjang: list[dict] = []

    for kode, info in WDI_INDIKATOR.items():
        sub = wdi[wdi["indikator"] == kode].copy()
        sub = sub.sort_values("tahun")
        ada = sub.dropna(subset=["nilai"])
        tahun_ada = [int(t) for t in ada["tahun"].tolist()]
        rentang = range(min(tahun_ada), max(tahun_ada) + 1)
        tahun_hilang = [t for t in rentang if t not in tahun_ada]

        md = meta_wdi.get(kode, {})
        sumber_org = md.get("wdi", {}).get("sourceOrganization", "")

        kandidat = KANDIDAT[kode]
        ringkas.append(
            {
                "sumber": "wdi",
                "seri_kode": kode,
                "nama_seri": sub["nama_indikator"].iloc[0],
                "peran": "pembanding",
                "cakupan_wilayah": "Nasional (Indonesia, IDN)",
                "dimensi_rincian": info["dimensi"],
                "rincian": info["rincian"],
                "satuan": _satuan_teks(kode),
                "periode_awal": min(tahun_ada),
                "periode_akhir": max(tahun_ada),
                "jumlah_periode": len(tahun_ada),
                "periode_tersedia": _periode_teks(tahun_ada),
                "periode_hilang": _periode_teks(tahun_hilang),
                "tahun_terbit": "UIS/UNESCO dipublikasi 2026-02; snapshot WDI 2026-10-20",
                "berkas_raw": _berkas_rel(WDI_DATA),
                "kandidat_sebanding": kandidat["kandidat"],
                "pasangan_seri_utama": kandidat["pasangan"],
                "alasan": kandidat["alasan"],
                "sumber_organisasi": sumber_org,
            }
        )

        sub_rentang = sub[sub["tahun"].between(min(tahun_ada), max(tahun_ada))]
        for _, baris in sub_rentang.iterrows():
            tersedia = int(pd.notna(baris["nilai"]))
            panjang.append(
                {
                    "sumber": "wdi",
                    "seri_kode": kode,
                    "peran": "pembanding",
                    "cakupan_wilayah": "Indonesia",
                    "dimensi_rincian": info["dimensi"],
                    "rincian": info["rincian"],
                    "periode": int(baris["tahun"]),
                    "jenis_periode": "tahun",
                    "nilai": "" if not tersedia else float(baris["nilai"]),
                    "tersedia": tersedia,
                    "satuan": _satuan_teks(kode),
                    "berkas_raw": _berkas_rel(WDI_DATA),
                }
            )

    # Dimensi yang diperiksa tetapi tidak ada di sumber pembanding (bukan karangan).
    for dim, ket in (
        ("daerah", "Seluruh baris SE.TER.ENRR hanya untuk Indonesia nasional (countryiso3code=IDN)."),
        ("kelompok_umur", "Berkas mentah tidak memuat pemecahan kelompok umur untuk SE.TER.ENRR."),
    ):
        ringkas.append(
            {
                "sumber": "wdi",
                "seri_kode": "SE.TER.ENRR",
                "nama_seri": "School enrollment, tertiary (% gross)",
                "peran": "pembanding",
                "cakupan_wilayah": "Nasional (Indonesia, IDN)",
                "dimensi_rincian": dim,
                "rincian": "(tidak tersedia di sumber)",
                "satuan": "",
                "periode_awal": "",
                "periode_akhir": "",
                "jumlah_periode": 0,
                "periode_tersedia": "",
                "periode_hilang": "",
                "tahun_terbit": "UIS/UNESCO dipublikasi 2026-02; snapshot WDI 2026-10-20",
                "berkas_raw": _berkas_rel(WDI_DATA),
                "kandidat_sebanding": "TIDAK",
                "pasangan_seri_utama": "-",
                "alasan": ket,
                "sumber_organisasi": "",
            }
        )

    return ringkas, panjang


def profil_bps(meta_bps: dict) -> tuple[list[dict], list[dict]]:
    ringkas: list[dict] = []
    panjang: list[dict] = []

    for seri, rel in BPS_CSV.items():
        df = pd.read_csv(RAW / rel)
        df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
        df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
        nasional = df[df["wilayah_id"] == 9999].copy()

        md = meta_bps.get(seri, {})
        dimensi = BPS_DIMENSI[seri]
        nama = md.get("label", seri)
        satuan = _satuan_teks(seri)
        kandidat = KANDIDAT[seri]

        for rincian, grup in nasional.groupby("turvar", dropna=False):
            tahun_ada = sorted({int(t) for t in grup["tahun"].tolist()})
            rentang = range(min(tahun_ada), max(tahun_ada) + 1)
            tahun_hilang = [t for t in rentang if t not in tahun_ada]
            ringkas.append(
                {
                    "sumber": "bps",
                    "seri_kode": seri,
                    "nama_seri": nama,
                    "peran": "utama",
                    "cakupan_wilayah": "Nasional (wilayah_kode 9999) + 38 provinsi",
                    "dimensi_rincian": dimensi,
                    "rincian": str(rincian),
                    "satuan": satuan,
                    "periode_awal": min(tahun_ada),
                    "periode_akhir": max(tahun_ada),
                    "jumlah_periode": len(tahun_ada),
                    "periode_tersedia": _periode_teks(tahun_ada),
                    "periode_hilang": _periode_teks(tahun_hilang),
                    "tahun_terbit": md.get("last_update", ""),
                    "berkas_raw": rel,
                    "kandidat_sebanding": kandidat["kandidat"],
                    "pasangan_seri_utama": kandidat["pasangan"],
                    "alasan": kandidat["alasan"],
                    "sumber_organisasi": "BPS (Susenas)",
                }
            )

            for _, baris in grup.iterrows():
                panjang.append(
                    {
                        "sumber": "bps",
                        "seri_kode": seri,
                        "peran": "utama",
                        "cakupan_wilayah": "Indonesia",
                        "dimensi_rincian": dimensi,
                        "rincian": str(rincian),
                        "periode": int(baris["tahun"]),
                        "jenis_periode": "tahun",
                        "nilai": "" if pd.isna(baris["nilai"]) else float(baris["nilai"]),
                        "tersedia": int(pd.notna(baris["nilai"])),
                        "satuan": satuan,
                        "berkas_raw": rel,
                    }
                )

    return ringkas, panjang


def hitung_irisan(ringkas: pd.DataFrame) -> dict:
    """Irisan periode SE.TER.ENRR (total) dengan var1443 pada tingkat nasional."""
    def tahun(seri: str) -> set:
        baris = ringkas[(ringkas["seri_kode"] == seri) & (ringkas["rincian"] != "(tidak tersedia di sumber)")]
        if baris.empty:
            return set()
        return {int(t) for t in str(baris.iloc[0]["periode_tersedia"]).split(";") if t}

    wdi = tahun("SE.TER.ENRR")
    bps = tahun("var1443")
    irisan = sorted(wdi & bps)
    return {
        "seri_pembanding": "SE.TER.ENRR",
        "seri_utama": "var1443",
        "periode_irisan": _periode_teks(irisan),
        "jumlah_tahun_irisan": len(irisan),
    }


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)

    wdi = muat_wdi()
    meta_wdi = muat_metadata_wdi()
    meta_bps = muat_metadata_bps()

    ringkas_wdi, panjang_wdi = profil_wdi(wdi, meta_wdi)
    ringkas_bps, panjang_bps = profil_bps(meta_bps)

    ringkas = pd.DataFrame(ringkas_wdi + ringkas_bps)
    panjang = pd.DataFrame(panjang_wdi + panjang_bps)
    panjang = panjang.sort_values(["sumber", "seri_kode", "dimensi_rincian", "rincian", "periode"])

    keluar_ringkas = DOCS / "tabel_ketersediaan_seri_pembanding.csv"
    keluar_panjang = DOCS / "ketersediaan_seri_periode_rincian.csv"
    ringkas.to_csv(keluar_ringkas, index=False)
    panjang.to_csv(keluar_panjang, index=False)

    irisan = hitung_irisan(ringkas)
    print("=== PROFIL SERI PEMBANDING SE.TER.ENRR (NIM 124450043) ===")
    print(f"Berkas mentah WDI : {_berkas_rel(WDI_DATA)}")
    print(f"Ringkasan         : {keluar_ringkas.relative_to(ROOT).as_posix()} ({len(ringkas)} baris)")
    print(f"Seri x periode    : {keluar_panjang.relative_to(ROOT).as_posix()} ({len(panjang)} baris)")
    print("--- Ringkasan ketersediaan ---")
    kolom = ["sumber", "seri_kode", "rincian", "periode_awal", "periode_akhir",
             "jumlah_periode", "kandidat_sebanding"]
    print(ringkas[kolom].to_string(index=False))
    print("--- Irisan periode dengan seri utama ---")
    print(irisan)


if __name__ == "__main__":
    main()
