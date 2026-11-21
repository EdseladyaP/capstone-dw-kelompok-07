"""Pembaca ILOSTAT: CSV SDMX per dataflow, struktur data (DSD) per dataflow, dan daftar dataflow.

CSV dibawa utuh. Kolom tetap SDMX (DATAFLOW, REF_AREA, FREQ, MEASURE, TIME_PERIOD, OBS_VALUE, atribut);
kolom lain adalah dimensi rincian (SEX, AGE, DSB, ECO, OCU, SOC). Sel OBS_VALUE kosong dibawa apa adanya.
"""
import json
import re

import pandas as pd

from src.common.manifest import RAW, sha256_raw

TETAP = {"DATAFLOW", "REF_AREA", "FREQ", "MEASURE", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "UNIT_MEASURE_TYPE",
         "UNIT_MEASURE", "UNIT_MULT", "SOURCE", "NOTE_SOURCE", "NOTE_INDICATOR", "NOTE_CLASSIF", "DECIMALS",
         "UPPER_BOUND", "LOWER_BOUND"}


def seri_dari_dataflow(teks):
    """'ILO:DF_SDG_0852_SEX_AGE_RT(1.0)' -> 'SDG_0852_SEX_AGE_RT'."""
    return re.sub(r"^ILO:DF_|\(.*\)$", "", str(teks))


def baca_csv(jalur):
    df = pd.read_csv(RAW / jalur, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df["seri_kode"] = df["DATAFLOW"].map(seri_dari_dataflow)
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df


def dimensi(df):
    return [k for k in df.columns if k not in TETAP and not k.startswith("_") and k != "seri_kode"]


def baca_dsd(jalur):
    """dsd/<seri>.json: nama dan deskripsi struktur data, daftar dimensi."""
    ds = json.loads((RAW / jalur).read_text(encoding="utf-8"))["data"]["dataStructures"][0]
    dims = [d["id"] for d in ds["dataStructureComponents"]["dimensionList"]["dimensions"]]
    return pd.DataFrame([{"seri_kode": ds["id"], "nama": ds.get("name", ""), "deskripsi": ds.get("description", ""),
                          "dimensi": ",".join(dims), "_berkas_raw": jalur}])


def baca_dataflow(jalur, seri):
    """metadata/dataflow.json: daftar semua dataflow ILOSTAT; disaring ke seri kasus."""
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))["data"]["dataflows"]
    pilih = []
    for f in isi:
        kode = f["id"].removeprefix("DF_")
        if kode in set(seri):
            pembaruan = next((a["title"] for a in f.get("annotations", []) if a.get("type") == "LAST_UPDATE"), "")
            pilih.append({"seri_kode": kode, "nama": f.get("name", ""), "deskripsi": f.get("description", ""),
                          "last_update": pembaruan, "_berkas_raw": jalur})
    return pd.DataFrame(pilih), len(isi)
