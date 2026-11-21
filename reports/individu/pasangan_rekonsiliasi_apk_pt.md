# Pasangan Rekonsiliasi — APK Perguruan Tinggi Indonesia

## 1. Pasangan indikator

| Peran | Sumber | Kode seri | Nama indikator |
|---|---|---|---|
| Seri utama | BPS | var1443 | Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) Menurut Provinsi |
| Seri pembanding | World Bank (WDI) | SE.TER.ENRR | School enrollment, tertiary (% gross) |

## 2. Periode data

- BPS: 2015–2025
- WDI: nilai tersedia hingga 2023 pada data yang diekstrak
- Periode beririsan dengan nilai pada kedua seri: 2015–2023 (9 tahun)
- Tahun 2024–2025: nilai BPS tersedia, sedangkan nilai WDI kosong (missing)

## 3. Keterbandingan definisi

BPS var1443 mencatat APK Perguruan Tinggi. Metadata JSON BPS mencantumkan bahwa kelompok umur perguruan tinggi yang digunakan adalah 19–23 tahun.

WDI SE.TER.ENRR mengukur gross enrollment ratio pada pendidikan tertiary. Numerator mencakup seluruh mahasiswa terdaftar tanpa memandang usia, sedangkan denominator menggunakan populasi kelompok usia yang secara resmi sesuai dengan tingkat pendidikan tertiary. Metadata WDI menyebut kelompok usia 5 tahun setelah upper secondary.

Kedua indikator memiliki konsep yang sejenis, yaitu partisipasi atau enrollment pendidikan tinggi secara bruto, tetapi kelompok usia denominator perlu diperhatikan. Rentang usia denominator WDI untuk Indonesia belum diverifikasi identik dengan kelompok usia 19–23 tahun yang digunakan BPS.

## 4. Catatan perbedaan nilai

Pada periode 2015–2023, nilai WDI lebih tinggi dibanding BPS pada seluruh tahun yang beririsan. Selisih BPS terhadap WDI berkisar sekitar -6,04 hingga -13,43 poin.

Perbedaan ini tidak langsung dianggap sebagai kesalahan data karena dapat berkaitan dengan definisi, denominator usia, cakupan, atau metodologi sumber. Nilai kedua seri dipertahankan tanpa koreksi atau penggabungan langsung.

## 5. Keputusan rekonsiliasi

- BPS var1443 dipertahankan sebagai seri utama nasional.
- WDI SE.TER.ENRR dipertahankan sebagai seri pembanding nasional.
- Kedua seri tidak digabungkan menjadi satu nilai karena terdapat perbedaan sumber dan catatan denominator.
- Perbandingan langsung dilakukan pada periode beririsan 2015–2023.
- Missing value WDI pada 2024–2025 tetap dibiarkan kosong dan tidak diimputasi.

## 6. Artefak

Tabel nasional periode × seri disimpan pada:

`reports/individu/tabel_nasional_apk_pt.csv`

## 7. Sumber metadata

- BPS: `data/raw/bps/2026-10-17/json/sdg4_apk_pt.json`
- WDI: World Bank DataBank Metadata Glossary — SE.TER.ENRR  
  https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SE.TER.ENRR
