
# ============================================================
# ANALISIS TAHAP 2
# Statistik, Visualisasi, dan Calon Anomali Data Pendidikan
# SDG 4
# NIM: 124450078
# ============================================================

from pathlib import Path
import sys
import re
import html

import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 1. PERSIAPAN LOKASI PROYEK
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ekstraksi import jalankan

FOLDER_LAPORAN = ROOT / "reports"
FOLDER_GAMBAR = FOLDER_LAPORAN / "gambar"
FOLDER_INDIVIDU = FOLDER_GAMBAR / "individu"

FOLDER_LAPORAN.mkdir(parents=True, exist_ok=True)
FOLDER_INDIVIDU.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. DAFTAR SERI YANG DIANALISIS
# ============================================================

DAFTAR_SERI = {
    "var303": "bps_sdg4_apk_csv",
    "var1443": "bps_sdg4_apk_pt_csv",
    "var2685": "bps_sdg4_4_3_1_v2685_csv",
    "var417": "bps_sdg4_hls_csv",
    "var1429": "bps_sdg4_rls_csv"
}


# ============================================================
# 3. MEMUAT DAN MENYIAPKAN DATA
# ============================================================

def muat_data():

    data_mentah = jalankan()
    seluruh_data = []

    for kode_seri, nama_dataframe in DAFTAR_SERI.items():

        df = data_mentah[nama_dataframe].copy()

        # Membersihkan tag HTML pada nama wilayah
        df["wilayah"] = (
            df["wilayah"]
            .astype(str)
            .apply(
                lambda x: html.unescape(
                    re.sub(r"<[^>]*>", "", x)
                )
            )
            .str.strip()
        )

        # Memastikan nilai dan tahun berbentuk angka
        df["nilai"] = pd.to_numeric(
            df["nilai"],
            errors="coerce"
        )

        df["tahun"] = pd.to_numeric(
            df["tahun"],
            errors="coerce"
        )

        # Mengambil data provinsi saja.
        # Data nasional (kode 9999) tidak disertakan.
        df = df[df["wilayah_id"] != 9999].copy()

        # Menghapus baris yang nilai atau tahunnya kosong
        df = df.dropna(
            subset=["nilai", "tahun"]
        ).copy()

        # Menetapkan kode seri
        df["seri_kode"] = kode_seri

        seluruh_data.append(df)

    data = pd.concat(
        seluruh_data,
        ignore_index=True
    )

    return data


# ============================================================
# 4. FUNGSI NAMA FILE
# ============================================================

def buat_slug(teks):

    teks = str(teks).lower()
    teks = re.sub(r"[^a-z0-9]+", "_", teks)
    teks = teks.strip("_")

    return teks


# ============================================================
# 5. STATISTIK DESKRIPTIF
# ============================================================

def hitung_statistik(data):

    kolom_statistik = {
        "jumlah_data": ("nilai", "count"),
        "rata_rata": ("nilai", "mean"),
        "median": ("nilai", "median"),
        "standar_deviasi": ("nilai", "std"),
        "minimum": ("nilai", "min"),
        "Q1": ("nilai", lambda x: x.quantile(0.25)),
        "Q3": ("nilai", lambda x: x.quantile(0.75)),
        "maksimum": ("nilai", "max")
    }

    # Statistik berdasarkan seri dan kategori
    statistik_seri = (
        data.groupby(
            ["seri_kode", "turvar"],
            dropna=False
        )
        .agg(**kolom_statistik)
        .reset_index()
    )

    # Statistik berdasarkan seri, provinsi, dan kategori
    statistik_provinsi = (
        data.groupby(
            [
                "seri_kode",
                "wilayah_id",
                "wilayah",
                "turvar"
            ],
            dropna=False
        )
        .agg(**kolom_statistik)
        .reset_index()
    )

    statistik_seri.to_csv(
        FOLDER_LAPORAN / "statistik_per_seri.csv",
        index=False
    )

    statistik_provinsi.to_csv(
        FOLDER_LAPORAN / "statistik_per_provinsi.csv",
        index=False
    )

    print("\nSTATISTIK DESKRIPTIF BERHASIL")
    print("Jumlah baris statistik provinsi:", len(statistik_provinsi))
    print("File statistik berhasil disimpan.")


# ============================================================
# 6. MEMBUAT BOXPLOT
# ============================================================

def buat_boxplot(data):

    print("\nMEMBUAT BOXPLOT...")

    kelompok = data.groupby(
        ["seri_kode", "turvar"],
        dropna=False
    )

    jumlah_gambar = 0

    for (seri, kategori), df_grup in kelompok:

        data_per_tahun = (
            df_grup.groupby("tahun")["nilai"]
            .apply(list)
            .sort_index()
        )

        if data_per_tahun.empty:
            continue

        daftar_nilai = data_per_tahun.tolist()
        label_tahun = [
            str(int(tahun))
            for tahun in data_per_tahun.index
        ]

        plt.figure(figsize=(12, 6))

        plt.boxplot(
            daftar_nilai,
            tick_labels=label_tahun,
            showfliers=True
        )

        plt.title(
            f"Boxplot {seri} - {kategori}"
        )
        plt.xlabel("Tahun")
        plt.ylabel("Nilai")
        plt.xticks(rotation=45)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        nama_file = (
            f"boxplot_{seri}_{buat_slug(kategori)}.png"
        )

        plt.savefig(
            FOLDER_INDIVIDU / nama_file,
            dpi=300
        )

        plt.close()
        jumlah_gambar += 1

    print("Jumlah boxplot dibuat:", jumlah_gambar)


# ============================================================
# 7. MEMBUAT GRAFIK DERET WAKTU
# ============================================================

def buat_grafik_deret_waktu(data):

    print("\nMEMBUAT GRAFIK DERET WAKTU...")

    kelompok = data.groupby(
        ["seri_kode", "turvar"],
        dropna=False
    )

    jumlah_gambar = 0

    for (seri, kategori), df_grup in kelompok:

        ringkasan = (
            df_grup.groupby("tahun")["nilai"]
            .agg(
                median="median",
                Q1=lambda x: x.quantile(0.25),
                Q3=lambda x: x.quantile(0.75)
            )
            .reset_index()
            .sort_values("tahun")
        )

        if ringkasan.empty:
            continue

        plt.figure(figsize=(12, 6))

        # Garis median antarprovinsi
        plt.plot(
            ringkasan["tahun"],
            ringkasan["median"],
            marker="o",
            linewidth=2,
            label="Median nilai provinsi"
        )

        # Area rentang Q1 sampai Q3
        plt.fill_between(
            ringkasan["tahun"],
            ringkasan["Q1"],
            ringkasan["Q3"],
            alpha=0.2,
            label="Rentang Q1-Q3"
        )

        plt.title(
            f"Deret Waktu {seri} - {kategori}"
        )
        plt.xlabel("Tahun")
        plt.ylabel("Nilai")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        nama_file = (
            f"deret_waktu_{seri}_{buat_slug(kategori)}.png"
        )

        plt.savefig(
            FOLDER_INDIVIDU / nama_file,
            dpi=300
        )

        plt.close()
        jumlah_gambar += 1

    print("Jumlah grafik deret waktu dibuat:", jumlah_gambar)


# ============================================================
# 8. DETEKSI CALON ANOMALI DENGAN METODE IQR
# ============================================================

def deteksi_anomali(data):

    print("\nMENDETEKSI CALON ANOMALI...")

    daftar_anomali = []

    kelompok = data.groupby(
        ["seri_kode", "turvar", "tahun"],
        dropna=False
    )

    for (seri, kategori, tahun), df_grup in kelompok:

        # Menghitung Q1, Q3, dan IQR
        q1 = df_grup["nilai"].quantile(0.25)
        q3 = df_grup["nilai"].quantile(0.75)

        iqr = q3 - q1

        batas_bawah = q1 - (1.5 * iqr)
        batas_atas = q3 + (1.5 * iqr)

        # Memilih nilai yang berada di luar batas IQR
        calon = df_grup[
            (df_grup["nilai"] < batas_bawah) |
            (df_grup["nilai"] > batas_atas)
        ]

        for _, baris in calon.iterrows():

            if baris["nilai"] < batas_bawah:
                alasan = "Nilai di bawah batas bawah IQR"
            else:
                alasan = "Nilai di atas batas atas IQR"

            periode = (
                baris["periode"]
                if "periode" in baris.index
                else "Tahun"
            )

            daftar_anomali.append({
                "seri_kode": seri,
                "kategori": kategori,
                "wilayah_id": baris["wilayah_id"],
                "provinsi": baris["wilayah"],
                "tahun": int(tahun),
                "periode": periode,
                "nilai": baris["nilai"],
                "Q1": q1,
                "Q3": q3,
                "IQR": iqr,
                "batas_bawah": batas_bawah,
                "batas_atas": batas_atas,
                "alasan_ditandai": alasan
            })

    kolom = [
        "seri_kode",
        "kategori",
        "wilayah_id",
        "provinsi",
        "tahun",
        "periode",
        "nilai",
        "Q1",
        "Q3",
        "IQR",
        "batas_bawah",
        "batas_atas",
        "alasan_ditandai"
    ]

    hasil = pd.DataFrame(
        daftar_anomali,
        columns=kolom
    )

    if not hasil.empty:
        hasil = hasil.sort_values(
            ["seri_kode", "kategori", "tahun", "provinsi"]
        )

    hasil.to_csv(
        FOLDER_LAPORAN / "calon_anomali.csv",
        index=False
    )

    print("Jumlah calon anomali:", len(hasil))
    print("File disimpan: reports/calon_anomali.csv")

    if hasil.empty:
        print("Tidak ditemukan nilai di luar batas IQR.")


# ============================================================
# 9. PROGRAM UTAMA
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("ANALISIS DATA TAHAP 2")
    print("========================================")

    # Memuat data
    data = muat_data()

    print("\nINFORMASI DATA")
    print("Total baris:", len(data))
    print("Jumlah seri:", data["seri_kode"].nunique())
    print("Jumlah provinsi:", data["wilayah_id"].nunique())
    print("Jumlah tahun:", data["tahun"].nunique())

    print("\nJUMLAH DATA PER SERI")
    print(data.groupby("seri_kode").size())

    # Statistik deskriptif
    hitung_statistik(data)

    # Visualisasi
    buat_boxplot(data)
    buat_grafik_deret_waktu(data)

    # Deteksi calon anomali
    deteksi_anomali(data)

    print("\n========================================")
    print("SELURUH ANALISIS TAHAP 2 SELESAI")
    print("========================================")
