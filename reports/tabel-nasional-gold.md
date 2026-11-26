# Tabel nasional Gold — Kasus 07

Dihasilkan `python pipeline.py` (`src/gold/nasional_gold.py`) dari Silver. Ini lanjutan `reports/tabel-nasional.csv` (Sprint 1, tampilan lebar) menjadi satu baris per seri x rincian x periode. File siap pakai: `data/gold/nasional.parquet`; salinan mudah dibaca: `reports/tabel-nasional-gold.csv`.

Kolom **`asal`** menunjukkan sumber setiap angka: `baris_indonesia`, `pembanding`, atau `agregat`. Setiap baris tetap membawa `_berkas_raw` (dan `_sha256_raw` untuk baris yang berasal dari Silver) sehingga angka dapat ditelusuri ke `data/raw/`.

## Ringkasan

- Baris: 172; seri: 6; asal: {'baris_indonesia': 119, 'pembanding': 53}.

- Kunci unik: `seri_kode` + `rincian` + `periode`. Satu berkas dipilih per sel menurut `URUTAN_BERKAS` (`src/silver/deret.py`).

| seri_kode | asal | baris | periode_awal | periode_akhir |
|---|---|---|---|---|
| SE.TER.ENRR | pembanding | 53 | 1970 | 2023 |
| var1429 | baris_indonesia | 11 | 2015 | 2025 |
| var1443 | baris_indonesia | 11 | 2015 | 2025 |
| var2685 | baris_indonesia | 12 | 2022 | 2024 |
| var303 | baris_indonesia | 69 | 2003 | 2025 |
| var417 | baris_indonesia | 16 | 2010 | 2025 |

## Aturan nasional per seri

Kelima seri utama menerbitkan baris Indonesia sehingga **tidak ada agregat provinsi yang dibuat**. Bila baris Indonesia tidak ada, aturannya bukan rata-rata provinsi: paket tidak memuat bobot penduduk, jadi seri dinyatakan tidak punya padanan nasional dan tidak diisi dengan angka rekaan.

| seri_kode | tingkat | baris_indonesia | rincian | asal | aturan | alasan |
|---|---|---|---|---|---|---|
| var303 | provinsi | 69 | jenjang=sd, jenjang=sm, jenjang=smp | baris_indonesia | memakai baris Indonesia yang diterbitkan penerbit | Baris Indonesia diterbitkan per jenjang (SD/SMP/SM). Jenjang tidak dijumlah: APK bukan besaran aditif dan tidak ada baris Indonesia total. |
| var1443 | provinsi | 11 | total | baris_indonesia | memakai baris Indonesia yang diterbitkan penerbit | Baris Indonesia total diterbitkan BPS. Pembanding WDI memakai kelompok umur jenjang tersier resmi; selisih dijelaskan sebagai perbedaan definisi dan metode. |
| var2685 | provinsi | 12 | umur=15-24, umur=15-64, umur=25-54, umur=55-64 | baris_indonesia | memakai baris Indonesia yang diterbitkan penerbit | Baris Indonesia diterbitkan per kelompok umur. Kelompok umur tumpang tindih (15-64 mencakup yang lain), jadi tidak dijumlah. |
| var417 | provinsi | 16 | total | baris_indonesia | memakai baris Indonesia yang diterbitkan penerbit | Baris Indonesia total diterbitkan BPS. Tidak ada pembanding eksternal di paket kasus 07. |
| var1429 | provinsi | 11 | total | baris_indonesia | memakai baris Indonesia yang diterbitkan penerbit | Baris Indonesia total diterbitkan BPS. Pasangan dengan var417 adalah konteks (dua ukuran berbeda), bukan selisih yang dihitung. |
| SE.TER.ENRR | nasional | 53 | total | pembanding | baris nasional dari sumber pembanding dipakai apa adanya | Seri pembanding nasional WDI (UNESCO UIS); bukan baris Indonesia BPS. |

## Contoh baris

| seri_kode | rincian | periode | nilai | satuan | asal | _berkas_raw |
|---|---|---|---|---|---|---|
| SE.TER.ENRR | total | 1970 | 2.80 | persen_apk | pembanding | wdi/2026-10-20/data/kelompok-05-hal-01.json |
| SE.TER.ENRR | total | 1972 | 2.73 | persen_apk | pembanding | wdi/2026-10-20/data/kelompok-05-hal-01.json |
| var1429 | total | 2015 | 8.32 | tahun | baris_indonesia | bps/2026-10-17/json/sdg4_rls.json |
| var1429 | total | 2016 | 8.42 | tahun | baris_indonesia | bps/2026-10-17/json/sdg4_rls.json |
| var1443 | total | 2015 | 25.26 | persen_apk | baris_indonesia | bps/2026-10-17/json/sdg4_apk_pt.json |
| var1443 | total | 2016 | 27.98 | persen_apk | baris_indonesia | bps/2026-10-17/json/sdg4_apk_pt.json |
| var2685 | umur=15-24 | 2022 | 51.67 | persen | baris_indonesia | bps/2026-10-17/json/sdg4_4_3_1_v2685.json |
| var2685 | umur=15-24 | 2023 | 50.02 | persen | baris_indonesia | bps/2026-10-17/json/sdg4_4_3_1_v2685.json |
| var303 | jenjang=sd | 2003 | 105.80 | persen_apk | baris_indonesia | bps/2026-10-17/json/sdg4_apk.json |
| var303 | jenjang=sd | 2004 | 107.13 | persen_apk | baris_indonesia | bps/2026-10-17/json/sdg4_apk.json |
| var417 | total | 2010 | 11.29 | tahun | baris_indonesia | bps/2026-10-17/json/sdg4_hls.json |
| var417 | total | 2011 | 11.44 | tahun | baris_indonesia | bps/2026-10-17/json/sdg4_hls.json |

Seluruh baris ada di `reports/tabel-nasional-gold.csv`; kolom `catatan` memuat alasan pemilihan baris Indonesia/pembanding dan larangan agregasi yang relevan.
