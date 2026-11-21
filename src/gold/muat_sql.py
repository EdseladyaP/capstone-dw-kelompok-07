"""Persiapan tahap 5 — memuat Silver ke DuckDB dengan kunci primer dan batasan.

Basis data dibuat ulang setiap kali (berkas lama dihapus), jadi hasilnya selalu sama dengan
data/silver/silver.parquet. Berkas .duckdb tidak di-commit; jalankan pipeline untuk membuatnya.
"""
from pathlib import Path

import duckdb
import pandas as pd

from src.laporan import ROOT, catat

DB = ROOT / "data" / "gold" / "gudang.duckdb"
DDL = Path(__file__).with_name("silver.sql")


def jalankan(silver):
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)
    seri = pd.read_csv(ROOT / "docs" / "seri.csv")[["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "sdg_kode"]]
    seri["sdg_kode"] = seri["sdg_kode"].astype(str)
    s = silver.copy()
    s["rujukan_tahun"] = s["rujukan_tahun"].astype("float64")
    with duckdb.connect(str(DB)) as con:
        con.execute(DDL.read_text(encoding="utf-8"))
        con.register("seri_df", seri)
        con.execute("INSERT INTO seri SELECT * FROM seri_df")
        con.register("silver_df", s)
        kolom = ", ".join(s.columns)
        con.execute(f"INSERT INTO silver ({kolom}) SELECT {kolom} FROM silver_df")
        n = con.execute("SELECT count(*) FROM silver").fetchone()[0]
    if n != len(silver):
        raise AssertionError(f"DuckDB memuat {n} baris, Silver {len(silver)} baris")
    catat(baris_sql=n)
    return n
