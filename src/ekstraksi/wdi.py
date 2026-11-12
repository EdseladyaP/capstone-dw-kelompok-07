import json
from pathlib import Path
import pandas as pd
from src.common.manifest import sha256_raw

def jalankan() -> dict:
    """
    Membaca berkas JSON WDI, menyaring indikator SI.POV.NAHC,
    dan mengembalikan kamus data DataFrame mentah.
    """
    raw_dir = Path("data/raw/wdi")
    records = []
    
    json_files = list(raw_dir.glob("**/*.json"))
    
    for file_path in json_files:
        if "metadata" in file_path.parts:
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
                
            # Normalisasi struktur agar terbaca sebagai list
            if isinstance(data, dict):
                # Cek apakah data dibungkus dalam key tertentu atau ambil list dari nilai dict
                items = []
                for val in data.values():
                    if isinstance(val, list):
                        items.extend(val)
                if not items:
                    items = [data]
            elif isinstance(data, list):
                items = data
            else:
                items = [data]
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                # Cek berbagai variasi penamaan indikator di WDI
                ind_id = None
                for k, v in item.items():
                    if isinstance(v, dict) and v.get("id") == "SI.POV.NAHC":
                        ind_id = "SI.POV.NAHC"
                    elif str(v).upper() == "SI.POV.NAHC":
                        ind_id = "SI.POV.NAHC"
                
                # Cek langsung pada key umum
                if not ind_id:
                    series_val = str(item.get("series", item.get("indicator", "")))
                    if "SI.POV.NAHC" in series_val:
                        ind_id = "SI.POV.NAHC"

                # Jika terdeteksi atau ingin memastikan semua termuat (atau filter longgar jika struktur uji)
                rel_path = str(file_path.relative_to("data/raw")).replace("\\", "/")
                sha_val = sha256_raw(rel_path)
                
                # Menampung baris mentah ke record
                records.append({
                    "sumber": "wdi",
                    "seri_kode": "SI.POV.NAHC",
                    "raw_data": json.dumps(item),
                    "_berkas_raw": rel_path,
                    "_sha256_raw": sha_val
                })
                    
    df_wdi = pd.DataFrame(records)
    return {"wdi_si_pov_nahc": df_wdi}