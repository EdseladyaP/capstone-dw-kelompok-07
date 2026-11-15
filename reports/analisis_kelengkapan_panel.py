
from pathlib import Path
import sys
import re
import html
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ekstraksi import jalankan

FOLDER = ROOT / "reports"

DAFTAR_SERI = {
    "var303": "bps_sdg4_apk_csv",
    "var1443": "bps_sdg4_apk_pt_csv",
    "var417": "bps_sdg4_hls_csv",
    "var1429": "bps_sdg4_rls_csv",
    "var2685": "bps_sdg4_4_3_1_v2685_csv",
}

PROVINSI = {
    1100: ("ACEH", 2003),
    1200: ("SUMATERA UTARA", 2003),
    1300: ("SUMATERA BARAT", 2003),
    1400: ("RIAU", 2003),
    1500: ("JAMBI", 2003),
    1600: ("SUMATERA SELATAN", 2003),
    1700: ("BENGKULU", 2003),
    1800: ("LAMPUNG", 2003),
    1900: ("KEP. BANGKA BELITUNG", 2003),
    2100: ("KEP. RIAU", 2003),
    3100: ("DKI JAKARTA", 2003),
    3200: ("JAWA BARAT", 2003),
    3300: ("JAWA TENGAH", 2003),
    3400: ("DI YOGYAKARTA", 2003),
    3500: ("JAWA TIMUR", 2003),
    3600: ("BANTEN", 2003),
    5100: ("BALI", 2003),
    5200: ("NUSA TENGGARA BARAT", 2003),
    5300: ("NUSA TENGGARA TIMUR", 2003),
    6100: ("KALIMANTAN BARAT", 2003),
    6200: ("KALIMANTAN TENGAH", 2003),
    6300: ("KALIMANTAN SELATAN", 2003),
    6400: ("KALIMANTAN TIMUR", 2003),
    6500: ("KALIMANTAN UTARA", 2013),
    7100: ("SULAWESI UTARA", 2003),
    7200: ("SULAWESI TENGAH", 2003),
    7300: ("SULAWESI SELATAN", 2003),
    7400: ("SULAWESI TENGGARA", 2003),
    7500: ("GORONTALO", 2003),
    7600: ("SULAWESI BARAT", 2005),
    8100: ("MALUKU", 2003),
    8200: ("MALUKU UTARA", 2003),
    9100: ("PAPUA BARAT", 2004),
    9200: ("PAPUA BARAT DAYA", 2023),
    9400: ("PAPUA", 2003),
    9500: ("PAPUA SELATAN", 2023),
    9600: ("PAPUA TENGAH", 2023),
    9700: ("PAPUA PEGUNUNGAN", 2023),
}

def bersihkan_nama(teks):
    teks = html.unescape(str(teks))
    teks = re.sub(r"<[^>]*>", "", teks)
    return teks.strip()

def muat_data():
    mentah = jalankan()
    hasil = []

    for seri, nama_df in DAFTAR_SERI.items():
        df = mentah[nama_df].copy()
        df["wilayah_id"] = pd.to_numeric(df["wilayah_id"], errors="coerce")
        df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
        df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
        df = df.dropna(subset=["wilayah_id", "tahun", "nilai", "turvar"]).copy()

        df["wilayah_id"] = df["wilayah_id"].astype(int)
        df["tahun"] = df["tahun"].astype(int)
        df["turvar"] = df["turvar"].astype(str)
        df = df[df["wilayah_id"].isin(PROVINSI)].copy()

        kunci = ["wilayah_id", "tahun", "turvar"]
        if df.duplicated(kunci).any():
            raise ValueError(f"Ditemukan duplikat pada seri {seri}")

        df["seri_kode"] = seri
        df["wilayah"] = df["wilayah"].apply(bersihkan_nama)
        hasil.append(
            df[["seri_kode", "wilayah_id", "wilayah", "tahun", "turvar", "nilai"]]
        )

    return pd.concat(hasil, ignore_index=True)

def bentuk_grid(data):
    semua_grid = []

    for seri, df_seri in data.groupby("seri_kode"):
        tahun_list = sorted(df_seri["tahun"].unique())
        kategori_list = sorted(df_seri["turvar"].unique())
        bagian = []

        for tahun in tahun_list:
            for kode, (nama, mulai) in PROVINSI.items():
                for kategori in kategori_list:
                    bagian.append({
                        "seri_kode": seri,
                        "tahun": tahun,
                        "wilayah_id": kode,
                        "wilayah": nama,
                        "kategori": kategori,
                        "tahun_mulai_target": mulai,
                    })

        grid = pd.DataFrame(bagian)

        aktual = df_seri[
            ["wilayah_id", "tahun", "turvar", "nilai"]
        ].rename(columns={"turvar": "kategori"})

        grid = grid.merge(
            aktual,
            on=["wilayah_id", "tahun", "kategori"],
            how="left",
            validate="one_to_one",
        )

        grid["status"] = "missing"
        grid.loc[
            grid["tahun"] < grid["tahun_mulai_target"], "status"
        ] = "belum_terbentuk"
        grid.loc[grid["nilai"].notna(), "status"] = "terisi"

        semua_grid.append(grid)

    return pd.concat(semua_grid, ignore_index=True)

def hitung_kelengkapan(grid):
    hasil = []

    for (seri, tahun), df in grid.groupby(["seri_kode", "tahun"]):
        target = df[df["status"] != "belum_terbentuk"]
        jumlah_target = len(target)
        jumlah_terisi = (target["status"] == "terisi").sum()
        jumlah_kosong = (target["status"] == "missing").sum()

        persen = (
            jumlah_terisi / jumlah_target * 100
            if jumlah_target else 0
        )

        hasil.append({
            "seri_kode": seri,
            "tahun": tahun,
            "sel_target": jumlah_target,
            "sel_terisi": int(jumlah_terisi),
            "sel_kosong": int(jumlah_kosong),
            "sel_belum_terbentuk": int(
                (df["status"] == "belum_terbentuk").sum()
            ),
            "persen_terisi": round(persen, 2),
        })

    return pd.DataFrame(hasil)

def main():
    print("MEMUAT DATA...")
    data = muat_data()

    print("MEMBENTUK GRID 38 PROVINSI...")
    grid = bentuk_grid(data)

    print("MENGHITUNG KELENGKAPAN...")
    kelengkapan = hitung_kelengkapan(grid)

    missing = grid[grid["status"] == "missing"].copy()

    grid.to_csv(FOLDER / "grid_panel.csv", index=False)
    kelengkapan.to_csv(FOLDER / "kelengkapan_panel.csv", index=False)
    missing.to_csv(FOLDER / "missing_panel.csv", index=False)

    print("\nRINGKASAN KELENGKAPAN")
    print(kelengkapan.to_string(index=False))

    print("\nTOTAL GRID:", len(grid))
    print("TOTAL SEL KOSONG:", len(missing))
    print("TOTAL SEL TERISI:", (grid["status"] == "terisi").sum())
    print(
        "TOTAL BELUM TERBENTUK:",
        (grid["status"] == "belum_terbentuk").sum()
    )

    print("\nFILE BERHASIL DISIMPAN:")
    print("reports/grid_panel.csv")
    print("reports/kelengkapan_panel.csv")
    print("reports/missing_panel.csv")

if __name__ == "__main__":
    main()
