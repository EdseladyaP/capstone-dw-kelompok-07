from pathlib import Path
import hashlib

import duckdb
import pandas as pd


# =========================================================
# 1. Tentukan lokasi proyek dan file
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FILE_RAW = ROOT / "data" / "raw" / "bps" / "2026-10-17" / "sdg4_apk_pt.csv"
FILE_MANIFEST = ROOT / "data" / "raw" / "MANIFEST.csv"
FILE_SCHEMA = ROOT / "src" / "silver" / "schema.sql"
FILE_DB = ROOT / "data" / "silver" / "silver_apk_pt.duckdb"

BERKAS_RAW = "bps/2026-10-17/sdg4_apk_pt.csv"


# =========================================================
# 2. Ambil SHA-256 dari manifest
# =========================================================

manifest = pd.read_csv(FILE_MANIFEST)

baris_manifest = manifest.loc[
    manifest["berkas"] == BERKAS_RAW
]

if len(baris_manifest) != 1:
    raise ValueError("File raw tidak ditemukan secara unik di MANIFEST.csv")

SHA256_RAW = baris_manifest.iloc[0]["sha256"]


# =========================================================
# 3. Verifikasi integritas file raw
# =========================================================

hash_aktual = hashlib.sha256(FILE_RAW.read_bytes()).hexdigest()

if hash_aktual != SHA256_RAW:
    raise ValueError("SHA-256 file raw tidak cocok dengan manifest")

print("Verifikasi SHA-256 berhasil.")


# =========================================================
# 4. Baca data raw
# =========================================================

df_raw = pd.read_csv(FILE_RAW)


# =========================================================
# 5. Transformasi ke struktur Silver
# =========================================================

df_silver = pd.DataFrame({
    "sumber": "BPS",
    "seri_kode": "var1443",
    "wilayah_kode": df_raw["wilayah_id"].astype(int),
    "nama_wilayah": df_raw["wilayah"],
    "periode": df_raw["tahun"].astype(str),
    "jenis_periode": "tahun",
    "rincian": (
        df_raw["turvar_id"].astype(str)
        + ": "
        + df_raw["turvar"].astype(str)
    ),
    "nilai": pd.to_numeric(df_raw["nilai"], errors="raise"),
    "satuan": "persen",
    "_berkas_raw": BERKAS_RAW,
    "_sha256_raw": SHA256_RAW,
})


# =========================================================
# 6. Validasi awal
# =========================================================

if df_silver.empty:
    raise ValueError("Data Silver kosong")

if df_silver.isnull().any().any():
    raise ValueError("Terdapat nilai NULL di data Silver")

if not df_silver["nilai"].apply(
    lambda x: isinstance(x, (int, float))
).all():
    raise ValueError("Kolom nilai harus numerik")


# =========================================================
# 7. Buat database dan tabel
# =========================================================

FILE_DB.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(FILE_DB))

# Membuat ulang tabel agar hasil loader reproducible
con.execute("DROP TABLE IF EXISTS silver_apk_pt")

sql_schema = FILE_SCHEMA.read_text(encoding="utf-8-sig")
con.execute(sql_schema)


# =========================================================
# 8. Masukkan data ke DuckDB
# =========================================================

con.register("df_silver", df_silver)

con.execute("""
    INSERT INTO silver_apk_pt
    SELECT * FROM df_silver
""")

con.unregister("df_silver")


# =========================================================
# 9. Tampilkan ringkasan hasil
# =========================================================

jumlah_baris = con.execute(
    "SELECT COUNT(*) FROM silver_apk_pt"
).fetchone()[0]

print(f"Jumlah data berhasil dimuat: {jumlah_baris}")
print(f"Database tersimpan di: {FILE_DB.relative_to(ROOT)}")

print("\nPreview data Silver:")
print(
    con.execute(
        "SELECT * FROM silver_apk_pt LIMIT 5"
    ).fetchdf().to_string(index=False)
)

con.close()