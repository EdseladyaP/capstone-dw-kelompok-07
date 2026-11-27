
"""Rekonsiliasi seri utama dan pembanding nasional untuk Kasus 07."""

import pandas as pd

from src.laporan import ROOT, catat, tabel_md, tulis


KOLOM = [
    "id",
    "periode",
    "seri_utama",
    "nilai_utama",
    "seri_pembanding",
    "nilai_pembanding",
    "selisih",
    "status_pasangan",
    "kategori",
    "dugaan",
    "bukti",
]

KATEGORI = {
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
}


def _ambil_seri(nasional, kode, rincian="total"):
    """Ambil satu seri nasional Gold berdasarkan kode dan rincian."""
    hasil = nasional[
        (nasional["seri_kode"] == kode)
        & (nasional["rincian"] == rincian)
    ][["periode", "nilai"]].copy()

    if hasil["periode"].duplicated().any():
        raise ValueError(f"Periode duplikat pada seri {kode}")

    hasil["periode"] = hasil["periode"].astype(str)
    hasil["nilai"] = pd.to_numeric(
        hasil["nilai"],
        errors="coerce",
    )

    return hasil


def _rekonsiliasi_p1(nasional):
    """Rekonsiliasi APK perguruan tinggi BPS dengan WDI."""
    bps = _ambil_seri(nasional, "var1443")
    wdi = _ambil_seri(nasional, "SE.TER.ENRR")

    gabung = bps.merge(
        wdi,
        on="periode",
        how="outer",
        suffixes=("_utama", "_pembanding"),
    ).sort_values("periode")

    baris = []

    for r in gabung.itertuples(index=False):
        ada_bps = pd.notna(r.nilai_utama)
        ada_wdi = pd.notna(r.nilai_pembanding)

        if ada_bps and ada_wdi:
            # Kedua sumber memiliki nilai pada periode yang sama.
            selisih = float(
                r.nilai_utama - r.nilai_pembanding
            )
            status = "berpasangan"
            kategori = "definisi berbeda"

            dugaan = (
                "Perbedaan nilai diduga berkaitan dengan perbedaan "
                "kelompok umur acuan dan metode pengumpulan data. "
                "BPS menggunakan kelompok umur 19–23 tahun dan "
                "Susenas, sedangkan WDI menggunakan kelompok umur "
                "resmi jenjang tersier dengan sumber UNESCO UIS."
            )

            bukti = (
                "Catatan konfigurasi var1443 menyebut kelompok umur "
                "19–23 tahun dan Susenas. Catatan SE.TER.ENRR "
                "menyebut kelompok umur resmi jenjang tersier dan "
                "sumber UNESCO UIS. Angka kelompok umur WDI tidak "
                "dirinci dalam sourceNote yang tersedia."
            )

        else:
            # Salah satu sumber tidak memiliki nilai pada periode ini.
            selisih = None
            status = "tanpa pasangan"
            kategori = "cakupan berbeda"

            dugaan = (
                "Periode ini belum dapat dibandingkan karena salah "
                "satu sumber tidak menyediakan nilai pada cakupan "
                "periode yang tersedia."
            )

            bukti = (
                f"Nilai BPS: {r.nilai_utama}; "
                f"nilai WDI: {r.nilai_pembanding}. "
                "Periode dipertahankan melalui outer join, "
                "tanpa melakukan imputasi atau mengisi selisih."
            )

        baris.append({
            "id": "P1",
            "periode": r.periode,
            "seri_utama": "var1443",
            "nilai_utama": r.nilai_utama,
            "seri_pembanding": "SE.TER.ENRR",
            "nilai_pembanding": r.nilai_pembanding,
            "selisih": selisih,
            "status_pasangan": status,
            "kategori": kategori,
            "dugaan": dugaan,
            "bukti": bukti,
        })

    return pd.DataFrame(baris, columns=KOLOM)


def _seri_tanpa_pembanding(nasional):
    """Catat HLS dan RLS sebagai seri tanpa pembanding."""
    baris = []

    seri_tanpa_pembanding = [
        ("var417", "Harapan Lama Sekolah"),
        ("var1429", "Rata-rata Lama Sekolah"),
    ]

    for kode, nama in seri_tanpa_pembanding:
        data = _ambil_seri(nasional, kode)

        for r in data.itertuples(index=False):
            baris.append({
                "id": "P2",
                "periode": r.periode,
                "seri_utama": kode,
                "nilai_utama": r.nilai,
                "seri_pembanding": None,
                "nilai_pembanding": None,
                "selisih": None,
                "status_pasangan": "tanpa pembanding",
                "kategori": None,
                "dugaan": (
                    f"{nama} tidak memiliki seri pembanding "
                    "dalam paket data Kasus 07. Seri ini dapat "
                    "dipertimbangkan sebagai variabel penjelas "
                    "dalam analisis panel sesuai keputusan kelompok."
                ),
                "bukti": (
                    "Panduan kelompok bagian 3 menyatakan bahwa "
                    "seri lama sekolah var417 dan var1429 "
                    "tidak memiliki pembanding."
                ),
            })

    return pd.DataFrame(baris, columns=KOLOM)


def jalankan(nasional):
    """Buat tabel rekonsiliasi dari tabel nasional Gold."""

    # Rekonsiliasi BPS dengan WDI.
    p1 = _rekonsiliasi_p1(nasional)

    # Catat seri yang tidak memiliki pembanding.
    p2 = _seri_tanpa_pembanding(nasional)

    hasil = pd.concat(
        [p1, p2],
        ignore_index=True,
    )

    hasil = hasil[KOLOM].sort_values(
        ["id", "seri_utama", "periode"]
    ).reset_index(drop=True)

    # Validasi kategori hanya untuk baris yang berpasangan.
    berpasangan = hasil[
        hasil["status_pasangan"] == "berpasangan"
    ]

    if berpasangan.empty:
        raise ValueError(
            "Tidak ditemukan periode yang memiliki pasangan nilai."
        )

    kategori_tidak_valid = (
        set(berpasangan["kategori"].dropna().unique())
        - KATEGORI
    )

    if kategori_tidak_valid:
        raise ValueError(
            f"Kategori tidak valid: {kategori_tidak_valid}"
        )

    if berpasangan["kategori"].isna().any():
        raise ValueError(
            "Baris berpasangan harus memiliki kategori."
        )

    # Pastikan baris tanpa pasangan tidak memiliki selisih.
    tanpa_pasangan = hasil[
        hasil["status_pasangan"] != "berpasangan"
    ]

    if tanpa_pasangan["selisih"].notna().any():
        raise ValueError(
            "Baris tanpa pasangan tidak boleh memiliki selisih."
        )

    # Simpan tabel hasil.
    folder = ROOT / "data" / "gold"
    folder.mkdir(parents=True, exist_ok=True)

    hasil.to_parquet(
        folder / "rekonsiliasi_nasional.parquet",
        index=False,
    )

    hasil.to_csv(
        ROOT / "reports" / "rekonsiliasi-nasional.csv",
        index=False,
    )

    # Ringkasan jumlah periode berdasarkan status dan kategori.
    ringkasan = (
        hasil.groupby(
            ["id", "seri_utama", "status_pasangan", "kategori"],
            dropna=False,
        )
        .size()
        .reset_index(name="jumlah_periode")
    )

    # Statistik hanya dihitung dari periode yang berpasangan.
    jumlah_pasangan = int(
        berpasangan["selisih"].notna().sum()
    )

    median_selisih = float(
        berpasangan["selisih"].median()
    )

    # Buat laporan Markdown.
    tulis(
        "rekonsiliasi-nasional.md",
        "\n\n".join([
            "# Rekonsiliasi Seri Nasional - Kasus 07",

            "Tabel dibuat dari `data/gold/nasional.parquet` "
            "melalui pipeline.",

            "Selisih dihitung sebagai nilai BPS dikurangi nilai WDI. "
            "Periode tanpa pasangan tetap dipertahankan, tetapi "
            "tidak dihitung sebagai selisih.",

            "Seri var417 dan var1429 dicatat sebagai seri tanpa "
            "pembanding, bukan sebagai pasangan rekonsiliasi.",

            "## Ringkasan Status dan Kategori",
            tabel_md(ringkasan),

            "## Statistik Selisih",
            f"- Jumlah periode berpasangan: {jumlah_pasangan}",
            f"- Median selisih BPS - WDI: {median_selisih:.6f}",

            "## Tabel Rekonsiliasi",
            tabel_md(hasil.head(30)),

            "File lengkap: `data/gold/rekonsiliasi_nasional.parquet` "
            "dan `reports/rekonsiliasi-nasional.csv`.",
        ]),
    )

    # Catat metrik hasil rekonsiliasi.
    catat(
        pasangan_rekonsiliasi=jumlah_pasangan,
        selisih_median=median_selisih,
    )

    return hasil
