import json
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


def _adalah_provinsi_atau_nasional(wilayah_id: str) -> bool:
    wid = str(wilayah_id).strip()
    return wid.endswith("00") or wid in {"9999", "0"}


def _saring_hls_csv(df: pd.DataFrame, rel_path: str) -> pd.DataFrame:
    awal = len(df)
    mask_simpan = df["wilayah_id"].apply(_adalah_provinsi_atau_nasional)
    df_hasil = df[mask_simpan].copy()
    dikeluarkan = awal - len(df_hasil)
    print(
        f"[HLS FILTER] {rel_path}: {dikeluarkan} baris kabupaten/kota dikeluarkan "
        f"(tersisa {len(df_hasil)} dari {awal} baris)."
    )
    return df_hasil


def _urai_json_bps(data, rel_path: str, is_hls: bool) -> pd.DataFrame:
    payload = None
    if isinstance(data, dict):
        payload = data
    elif isinstance(data, list):
        for elem in data:
            if isinstance(elem, dict) and "datacontent" in elem:
                payload = elem
                break

    if payload and "datacontent" in payload:
        vervar_list = payload.get("vervar", [])
        vervar_sorted = sorted(vervar_list, key=lambda v: len(str(v["val"])), reverse=True)
        vervar_map = {str(v["val"]): str(v["label"]) for v in vervar_sorted}

        turvar_map = {str(v["val"]): str(v["label"]) for v in payload.get("turvar", [])}
        tahun_map = {str(v["val"]): str(v["label"]) for v in payload.get("tahun", [])}
        turtahun_map = {str(v["val"]): str(v["label"]) for v in payload.get("turtahun", [])}
        var_info = payload.get("var", [{}])[0] if isinstance(payload.get("var"), list) and payload.get("var") else {}
        var_id = str(var_info.get("val", ""))

        rows = []
        dikeluarkan = 0

        for kode_komposit, nilai in payload["datacontent"].items():
            kode_str = str(kode_komposit)
            wilayah_id = next((vid for vid in vervar_map if kode_str.startswith(vid)), "")

            if is_hls and not _adalah_provinsi_atau_nasional(wilayah_id):
                dikeluarkan += 1
                continue

            rows.append({
                "kode_komposit": kode_str,
                "var_id": var_id,
                "var_label": var_info.get("label", ""),
                "wilayah_id": wilayah_id,
                "wilayah": vervar_map.get(wilayah_id, ""),
                "turvar_opsi": json.dumps(turvar_map, ensure_ascii=False),
                "tahun_opsi": json.dumps(tahun_map, ensure_ascii=False),
                "periode_opsi": json.dumps(turtahun_map, ensure_ascii=False),
                "nilai": nilai,
                "satuan": var_info.get("unit", ""),
            })

        if is_hls:
            total_awal = len(rows) + dikeluarkan
            print(
                f"[HLS FILTER] {rel_path}: {dikeluarkan} baris kabupaten/kota dikeluarkan "
                f"(tersisa {len(rows)} dari {total_awal} baris)."
            )

        return pd.DataFrame(rows)

    items = data if isinstance(data, list) else [data]
    return pd.json_normalize(items)


def jalankan() -> dict:
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

            df_json = _urai_json_bps(data, rel_path, is_hls=("hls" in file_path.name.lower()))
            df_json["sumber"] = "bps"
            df_json["seri_kode"] = seri_kode
            df_json["_berkas_raw"] = rel_path
            df_json["_sha256_raw"] = sha_val
            hasil[kunci_df] = df_json

    return hasil
