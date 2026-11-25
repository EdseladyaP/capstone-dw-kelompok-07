# Tabel nasional dan pasangan rekonsiliasi

Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver dan `src/konfigurasi.py`. Selisih dihitung di Sprint 2; Sprint 1 memastikan setiap pasangan memang sebanding dan mencatat tahun yang beririsan.

Tabel nasional (periode x seri, rincian total, tampilan lebar): `reports/tabel-nasional.csv`. Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.

## Ringkasan pasangan

| id | seri_utama | pembanding | jenis | periode_beririsan | tahun | dugaan_kategori |
|---|---|---|---|---|---|---|
| P1 | var1443 | SE.TER.ENRR [total] | selisih | 9 | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | definisi (kelompok umur acuan penyebut) dan metode (Susenas vs data administrasi UNESCO) |
| P2 | var417 | var1429 [total] | konteks | 11 | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | dua ukuran berbeda (harapan anak 7 tahun vs rata-rata penduduk 15+); variabel penjelas panel |

## Rincian per pasangan

### P1: APK perguruan tinggi: BPS (umur 19–23) vs WDI (umur resmi jenjang tersier)
- Seri utama: `var1443` (rincian `total`)
- Pembanding: `SE.TER.ENRR` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
- Dugaan kategori selisih (diuji di Sprint 2): definisi (kelompok umur acuan penyebut) dan metode (Susenas vs data administrasi UNESCO)

Pertanyaan keterbandingan dan jawabannya:

1. **Kelompok umur BPS?** 19–23 tahun (var.note var1443).
2. **Kelompok umur WDI?** Kelompok umur resmi jenjang tersier; sourceNote tidak menyebut angkanya.
3. **Mengapa bukan var303?** turvar var303 hanya SD, SMP, SM; tidak ada jenjang PT.

### P2: Lama sekolah (HLS, RLS): tanpa pembanding di paket
- Seri utama: `var417` (rincian `total`)
- Pembanding: `var1429` (rincian `total`)
- Jenis: **konteks**; tahun beririsan: 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
- Dugaan kategori selisih (diuji di Sprint 2): dua ukuran berbeda (harapan anak 7 tahun vs rata-rata penduduk 15+); variabel penjelas panel

Pertanyaan keterbandingan dan jawabannya:

1. **Bolehkah dibandingkan?** Tidak sebagai selisih: HLS proyeksi untuk anak 7 tahun, RLS capaian penduduk 15+.
