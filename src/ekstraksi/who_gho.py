"""Pembaca WHO GHO: CSV per indikator (DATADOT) dan metadata indikator (JSON).

Kolom DIM_* dibawa utuh: sel kosong berarti dimensi tidak dipakai di baris itu, bukan data hilang.
Kolom nilai dikenali dari akhiran _N / _NL / _NU, bukan dari namanya, karena namanya berbeda antarberkas
(RATE_PER_100_N, RATE_PER_10000_N, PERCENT_POP_N, INDEX_N, MONEY_N, ...) dan tidak setiap berkas punya
batas bawah/atas. Penyebut RATE_PER_x ikut tertulis di nama kolom.
"""
import json

import pandas as pd

from src.common.manifest import RAW, sha256_raw


def baca_csv(jalur):
    df = pd.read_csv(RAW / jalur, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df


def kolom_nilai(df):
    """{'nilai': ..., 'bawah': ... atau None, 'atas': ... atau None, 'penyebut': 100/1000/100000}."""
    n = [k for k in df.columns if k.endswith("_N") and not k.startswith(("DIM_", "IND_", "GEO_"))]
    if len(n) != 1:
        raise ValueError(f"kolom nilai WHO tidak tunggal: {n}")
    awal = n[0][:-2]
    penyebut = int(awal.removeprefix("RATE_PER_")) if awal.startswith("RATE_PER_") else None
    return {"nilai": n[0], "bawah": awal + "_NL" if awal + "_NL" in df.columns else None,
            "atas": awal + "_NU" if awal + "_NU" in df.columns else None, "penyebut": penyebut}


def baca_metadata_ddi(jalur, seri):
    """datadot/ddiindicators_*.json: definisi lengkap per indikator (DefinitionText, Numerator, ...)."""
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    pilih = []
    for it in isi.get("value", []):
        kode = json.loads(it.get("DataVisualizationConfiguration") or "{}").get("indicator") \
            or it.get("AlternativeCodes")
        if kode in set(seri):
            pilih.append({"seri_kode": kode, **{k: v for k, v in it.items() if isinstance(v, (str, int, float))}})
    df = pd.DataFrame(pilih)
    df["_berkas_raw"] = jalur
    return df


def baca_metadata_odata(jalur, seri):
    """odata/Indicator.json: daftar kode dan nama indikator."""
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    df = pd.DataFrame([x for x in isi.get("value", []) if x.get("IndicatorCode") in set(seri)])
    df["_berkas_raw"] = jalur
    return df
