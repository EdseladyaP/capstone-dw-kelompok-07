import json
from pathlib import Path
import pandas as pd
from src.common.manifest import sha256_raw


def jalankan() -> dict:
    """
    Membaca seluruh 4 berkas JSON WDI (data utama & metadata) untuk Kasus 7 (SE.TER.ENRR)
    dengan mempertahankan struktur/kolom asal serta menempelkan _berkas_raw dan _sha256_raw.
    """
    raw_dir = Path("data/raw/wdi")
    hasil = {}

    json_files = sorted(list(raw_dir.glob("**/*.json")))

    for file_path in json_files:
        rel_path = str(file_path.relative_to("data/raw")).replace("\\", "/")
        sha_val = sha256_raw(rel_path)
        kunci_df = f"wdi_{file_path.stem}"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Format API World Bank biasanya berupa list: [header_paging_dict, [list_of_records]]
        if isinstance(data, list) and len(data) == 2 and isinstance(data[1], list):
            records = data[1]
        elif isinstance(data, dict):
            # Ambil list record di dalam dict jika ada (misal key 'data' atau 'source')
            list_vals = [v for v in data.values() if isinstance(v, list)]
            records = list_vals[0] if list_vals else [data]
        elif isinstance(data, list):
            records = data
        else:
            records = [data]

        df_wdi = pd.json_normalize(records)
        df_wdi["sumber"] = "wdi"
        df_wdi["seri_kode"] = "SE.TER.ENRR" if "metadata" not in file_path.parts else "wdi_metadata"
        df_wdi["_berkas_raw"] = rel_path
        df_wdi["_sha256_raw"] = sha_val

        hasil[kunci_df] = df_wdi

    return hasil