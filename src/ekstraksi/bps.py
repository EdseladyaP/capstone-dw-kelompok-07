import json
from pathlib import Path
import pandas as pd
from src.common.manifest import sha256_raw

def jalankan() -> dict:
    """
    Membaca berkas CSV dan JSON BPS (var192, var2190, var2191),
    mengubahnya ke tabel panjang, serta menempelkan _berkas_raw dan _sha256_raw.
    """
    raw_dir = Path("data/raw/bps")
    records = []
    
    # Mencari seluruh file CSV dan JSON BPS di dalam direktori raw BPS
    file_list = list(raw_dir.glob("**/*.csv")) + list(raw_dir.glob("**/*.json"))
    
    for file_path in file_list:
        # Abaikan file manifest atau folder metadata
        if "manifest" in file_path.name or "metadata" in file_path.parts:
            continue
            
        rel_path = str(file_path.relative_to("data/raw")).replace("\\", "/")
        sha_val = sha256_raw(rel_path)
        
        # Identifikasi kode seri dari nama file
        seri_kode = "lainnya"
        if "v192" in file_path.name:
            seri_kode = "var192"
        elif "v2190" in file_path.name:
            seri_kode = "var2190"
        elif "v2191" in file_path.name:
            seri_kode = "var2191"
            
        # Membaca berdasarkan format file
        if file_path.suffix == ".csv":
            try:
                df_csv = pd.read_csv(file_path)
                # Menambahkan kolom lineage ke setiap baris DataFrame mentah
                df_csv["sumber"] = "bps"
                df_csv["seri_kode"] = seri_kode
                df_csv["_berkas_raw"] = rel_path
                df_csv["_sha256_raw"] = sha_val
                
                # Konversi ke record/tabel panjang secara fleksibel
                for _, row in df_csv.iterrows():
                    records.append(row.to_dict())
            except Exception as e:
                print(f"Gagal membaca CSV {file_path.name}: {e}")
                
        elif file_path.suffix == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Struktur JSON BPS dinamis (datacontent, vervar, turvar, dll.)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    records.append({
                        "sumber": "bps",
                        "seri_kode": seri_kode,
                        "raw_data": str(item),
                        "_berkas_raw": rel_path,
                        "_sha256_raw": sha_val
                    })
            except Exception as e:
                print(f"Gagal membaca JSON {file_path.name}: {e}")
                
    df_bps = pd.DataFrame(records)
    return {"bps_kasus_15": df_bps}