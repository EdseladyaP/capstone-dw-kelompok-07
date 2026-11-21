# Rancangan Skema SQL Silver

## 1. Tujuan

Tahap ini bertujuan merancang skema SQL untuk penyimpanan data Silver, menentukan primary key, tipe data setiap kolom, memilih DBMS, serta melakukan pengujian pemuatan data awal dari data raw ke Silver.

Dataset uji yang digunakan adalah data Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) menurut provinsi dari BPS, dengan kode seri `var1443`.

## 2. Pemilihan DBMS

DBMS yang dipilih adalah DuckDB.

DuckDB dipilih karena bersifat embedded sehingga dapat digunakan tanpa menjalankan server database terpisah. DuckDB juga sesuai untuk kebutuhan analisis data, mendukung query SQL, dan memiliki integrasi yang baik dengan Pandas serta format data Parquet. Hal ini sesuai dengan karakteristik proyek Data Wrangling yang berfokus pada pengolahan, transformasi, dan analisis data.

### Perbandingan DBMS

| Aspek | DuckDB | SQLite | PostgreSQL |
|---|---|---|---|
| Jenis | Embedded analytical DBMS | Embedded relational DBMS | Client-server RDBMS |
| Instalasi | Ringan, tanpa server | Ringan, tanpa server | Membutuhkan server |
| Fokus | Analisis data | Penyimpanan aplikasi | Database relasional umum |
| Analisis data | Sangat sesuai | Cukup | Sesuai |
| Integrasi Parquet | Sangat baik | Terbatas | Memerlukan dukungan tambahan |
| Kebutuhan proyek | Sesuai | Bisa digunakan | Lebih kompleks dari kebutuhan saat ini |

## 3. Rancangan Tabel Silver

Tabel yang dirancang bernama `silver_apk_pt` dengan 11 kolom sesuai skema Silver proyek.

| Kolom | Tipe Data | Constraint | Keterangan |
|---|---|---|---|
| sumber | VARCHAR | NOT NULL | Sumber data |
| seri_kode | VARCHAR | NOT NULL | Kode seri indikator |
| wilayah_kode | INTEGER | NOT NULL | Kode wilayah |
| nama_wilayah | VARCHAR | NOT NULL | Nama wilayah |
| periode | VARCHAR | NOT NULL | Tahun pengamatan |
| jenis_periode | VARCHAR | NOT NULL | Jenis periode |
| rincian | VARCHAR | NOT NULL | Informasi rincian |
| nilai | DOUBLE | NOT NULL | Nilai indikator |
| satuan | VARCHAR | NOT NULL | Satuan indikator |
| _berkas_raw | VARCHAR | NOT NULL | Identitas file raw |
| _sha256_raw | VARCHAR | NOT NULL | Hash file raw |

### Primary Key

Primary key yang digunakan adalah composite primary key dengan kombinasi:

- `sumber`
- `seri_kode`
- `wilayah_kode`
- `periode`
- `rincian`
- `_berkas_raw`

Composite primary key digunakan karena satu baris data diidentifikasi melalui kombinasi sumber, seri, wilayah, periode, rincian, dan file asalnya. Dengan demikian, kombinasi tersebut tidak boleh memiliki duplikasi.

## 4. Implementasi DDL

DDL disimpan pada:

`src/silver/schema.sql`

Tabel dibuat menggunakan tipe data SQL dan constraint NOT NULL serta PRIMARY KEY untuk menjaga struktur dan integritas data.

## 5. Proses Loading Data

Loader disimpan pada:

`src/silver/loader_apk_pt.py`

Proses loading yang dilakukan:

1. Membaca MANIFEST.csv.
2. Mengambil SHA-256 file raw yang sesuai.
3. Menghitung SHA-256 aktual file.
4. Memeriksa kesesuaian hash.
5. Membaca data raw CSV.
6. Mengubah struktur raw menjadi skema Silver.
7. Melakukan validasi awal.
8. Membuat database DuckDB.
9. Membuat tabel berdasarkan DDL.
10. Memasukkan data ke tabel Silver.

File database lokal yang dihasilkan:

`data/silver/silver_apk_pt.duckdb`

Database tersebut tidak diikutsertakan ke Git karena file database lokal (`*.duckdb`) telah masuk `.gitignore`.

## 6. Perbandingan Raw dan Silver

Data raw CSV mempertahankan struktur asli dari sumber BPS, seperti `var_id`, `wilayah_id`, `wilayah`, `turvar_id`, `turvar`, `tahun`, `periode`, `nilai`, dan `satuan`.

Data Silver memiliki struktur yang diseragamkan menjadi 11 kolom. Transformasi yang dilakukan antara lain:

- `var_id` diubah menjadi `seri_kode` dengan format `var1443`.
- `wilayah_id` menjadi `wilayah_kode`.
- `wilayah` menjadi `nama_wilayah`.
- `tahun` menjadi `periode`.
- `jenis_periode` diisi `tahun`.
- `rincian` dibentuk dari `turvar_id` dan `turvar`.
- `nilai` dikonversi ke tipe numerik.
- `sumber` diisi `BPS`.
- `_berkas_raw` dan `_sha256_raw` ditambahkan sebagai lineage data.

Raw berfungsi sebagai penyimpanan data asli, sedangkan Silver menyediakan struktur yang konsisten, tipe data yang jelas, dan lebih mudah digunakan untuk query serta proses analisis berikutnya.

## 7. Catatan Satuan Data

Kolom `satuan` pada CSV raw yang digunakan tidak berisi satuan. Dalam proses loading, satuan Silver diisi `persen` berdasarkan interpretasi indikator Angka Partisipasi Kasar (APK).

Pengisian tersebut merupakan asumsi/interpretasi pada tahap transformasi, bukan nilai satuan eksplisit dari metadata raw. Hal ini dicatat agar proses transformasi tetap transparan.

## 8. Hasil Pengujian

Dataset yang berhasil dimuat berasal dari:

`data/raw/bps/2026-10-17/sdg4_apk_pt.csv`

Hasil pengujian:

| Pemeriksaan | Hasil |
|---|---:|
| Jumlah baris Silver | 393 |
| Wilayah unik | 39 |
| Rentang periode | 2015–2025 |
| Nilai minimum | 11.13 |
| Nilai maksimum | 75.59 |
| Rata-rata nilai | 33.012137 |
| Data NULL pada kolom wajib | 0 |
| Duplikasi composite primary key | 0 |
| Verifikasi SHA-256 | Berhasil |

Jumlah data per tahun:

- 2015–2023: 35 baris per tahun.
- 2024–2025: 39 baris per tahun.

Perbedaan jumlah baris per tahun menunjukkan bahwa cakupan wilayah pada dataset tidak selalu sama untuk setiap periode dan perlu diperhatikan dalam analisis lanjutan.

Data nasional dengan `wilayah_kode = 9999` juga berhasil diperiksa. Data tersedia lengkap untuk periode 2015–2025, dengan nilai APK PT nasional meningkat dari 25.26 pada 2015 menjadi 32.89 pada 2025.

## 9. Kesimpulan

DuckDB berhasil digunakan untuk membuat tabel Silver dan memuat data awal APK Perguruan Tinggi BPS. Rancangan tabel menggunakan 11 kolom dengan composite primary key sesuai kontrak skema proyek. Proses loading berhasil memuat 393 baris tanpa NULL pada kolom wajib dan tanpa duplikasi primary key. Verifikasi SHA-256 juga berhasil, sehingga file raw yang digunakan sesuai dengan manifest.

Implementasi ini menjadi percobaan awal rancangan SQL Silver sebelum penerapan proses transformasi yang lebih luas untuk seluruh dataset dalam pipeline proyek.
