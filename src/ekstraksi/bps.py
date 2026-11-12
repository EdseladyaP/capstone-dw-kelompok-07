import json
import re
from pathlib import Path
import pandas as pd
from src.common.manifest import sha256_raw


def _deteksi_seri_bps(nama_file: str) -> str:
    nama = nama_file.lower()
    if "v2685" in nama:
        return "var2685"
    elif "apk_pt" in nama:
        return "var1443"
    elif "apk" in nama:
        return "var303"
    elif "hls" in nama:
        return "var417"
    elif "rls" in nama:
        return "var1429"
    elif "manifest" in nama:
        return "manifest_asal"
    return "lainnya"


def _saring_hls_csv(df: pd.DataFrame, rel_path: str) -> pd.DataFrame:
    """Saring sdg4_hls ke tingkat provinsi & nasional, keluarkan kabupaten/kota."""
    awal = len(df)
    # Cari kolom teks wilayah (umumnya kolom pertama atau yang memuat 'provinsi'/'wilayah'/'vervar')
    kandidat_kolom = [
        c for c in df.columns
        if any(k in c.lower() for k in ("wilayah", "provinsi", "vervar", "daerah", "nama"))
    ]
    kol_wilayah = kandidat_kolom[0] if kandidat_kolom else df.columns[0]

    # Baris kabupaten/kota di BPS diawali "Kab." atau "Kota " (atau kode BPS 4 digit)
    teks_wilayah = df[kol_wilayah].astype(str).str.strip()
    mask_kabkota = teks_wilayah.str.match(r"^(kab\.|kota\s)", case=False, na=False)

    df_hasil = df[~mask_kabkota].copy()
    dikeluarkan = awal - len(df_hasil)
    print(
        f"[HLS FILTER] {rel_path}: {dikeluarkan} baris kabupaten/kota dikeluarkan "
        f"(tersisa {len(df_hasil)} dari {awal} baris)."
    )
    return df_hasil


def jalankan() -> dict:
    """
    Membaca seluruh 11 berkas BPS (CSV, JSON data, dan manifest_asal.json) untuk Kasus 7,
    menyaring wilayah HLS ke provinsi & nasional, dan mempertahankan kolom asal.
    """
    raw_dir = Path("data/raw/bps")
    hasil = {}

    file_list = sorted(list(raw_dir.glob("**/*.csv")) + list(raw_dir.glob("**/*.json")))

    for file_path in file_list:
        rel_path = str(file_path.relative_to("data/raw")).replace("\\", "/")
        sha_val = sha256_raw(rel_path)
        seri_kode = _deteksi_seri_bps(file_path.name)
        kunci_df = f"bps_{file_path.stem}_{file_path.suffix.lstrip('.')}"

        if file_path.suffix == ".csv":
            df_csv = pd.read_csv(file_path)

            # Catatan khusus kasus 7: saring berkas harapan lama sekolah (sdg4_hls)
            if "hls" in file_path.name.lower():
                df_csv = _saring_hls_csv(df_csv, rel_path)

            df_csv["sumber"] = "bps"
            df_csv["seri_kode"] = seri_kode
            df_csv["_berkas_raw"] = rel_path
            df_csv["_sha256_raw"] = sha_val
            hasil[kunci_df] = df_csv

        elif file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Jika JSON format BPS WebAPI (memiliki key 'datacontent' & 'vervar')
            if isinstance(data, dict) and "datacontent" in data and "vervar" in data:
                vervar_map = {str(v["val"]): str(v["label"]) for v in data.get("vervar", [])}
                turvar_map = {str(v["val"]): str(v["label"]) for v in data.get("turvar", [])}
                tahun_map = {str(v["val"]): str(v["label"]) for v in data.get("tahun", [])}
                turtahun_map = {str(v["val"]): str(v["label"]) for v in data.get("turtahun", [])}
                var_info = data.get("var", [{}])[0] if isinstance(data.get("var"), list) else {}

                rows = []
                dikeluarkan_json = 0
                is_hls = "hls" in file_path.name.lower()

                for kode_komposit, nilai in data["datacontent"].items():
                    # Cocokkan kode vervar (wilayah) di awal kode komposit BPS
                    vervar_id = next((vid for vid in vervar_map if str(kode_komposit).startswith(vid)), "")
                    wilayah_label = vervar_map.get(vervar_id, "")

                    # Saring kabupaten/kota khusus sdg4_hls.json
                    if is_hls and re.match(r"^(kab\.|kota\s)", wilayah_label.strip(), flags=re.IGNORECASE):
                        dikeluarkan_json += 1
                        continue

                    rows.append({
                        "kode_komposit": kode_komposit,
                        "vervar_id": vervar_id,
                        "vervar": wilayah_label,
                        "var_label": var_info.get("label", ""),
                        "unit": var_info.get("unit", ""),
                        "turvar_map": json.dumps(turvar_map, ensure_ascii=False),
                        "tahun_map": json.dumps(tahun_map, ensure_ascii=False),
                        "turtahun_map": json.dumps(turtahun_map, ensure_ascii=False),
                        "nilai": nilai,
                    })

                if is_hls:
                    total_awal_json = len(rows) + dikeluarkan_json
                    print(
                        f"[HLS FILTER] {rel_path}: {dikeluarkan_json} baris kabupaten/kota dikeluarkan "
                        f"(tersisa {len(rows)} dari {total_awal_json} baris)."
                    )

                df_json = pd.DataFrame(rows)
            else:
                # Untuk manifest_asal.json atau JSON struktur datar/list
                items = data if isinstance(data, list) else [data]
                df_json = pd.json_normalize(items)

            df_json["sumber"] = "bps"
            df_json["seri_kode"] = seri_kode
            df_json["_berkas_raw"] = rel_path
            df_json["_sha256_raw"] = sha_val
            hasil[kunci_df] = df_json

    return hasil