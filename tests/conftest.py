"""Fixture bersama: Silver yang dihasilkan `python pipeline.py`."""
from pathlib import Path

import pandas as pd
import pytest

SILVER = Path(__file__).resolve().parents[1] / "data" / "silver" / "silver.parquet"


@pytest.fixture
def silver_contoh():
    if not SILVER.exists():
        pytest.skip("jalankan python pipeline.py dulu untuk membuat data/silver/silver.parquet")
    return pd.read_parquet(SILVER)
