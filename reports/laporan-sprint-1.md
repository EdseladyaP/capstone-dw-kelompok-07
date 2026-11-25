# LAPORAN SPRINT 1
## Capstone Data Wrangling — Indikator SDG Indonesia dari Banyak Sumber

**Nama:** [Gustin H. Tampubolon]  
**NIM:** 124450068  
**Kelompok:** 07  
**Kasus:** 07 — Partisipasi Pendidikan Tinggi dan Lama Sekolah  
**Branch GitHub:** `124450068/kerja`

---

## 1. Pendahuluan

Sprint 1 merupakan tahap pengerjaan proyek Capstone Data Wrangling yang bertujuan membangun proses pengolahan data dari berbagai sumber menjadi data yang terstruktur, konsisten, dan dapat digunakan untuk analisis lebih lanjut.

Pada proyek ini, data yang digunakan berasal dari Badan Pusat Statistik (BPS) dan World Development Indicators (WDI). Pengolahan dilakukan melalui beberapa tahapan, mulai dari pemeriksaan data mentah, ekstraksi, pemeriksaan metadata, pencatatan keputusan wrangling, hingga pembentukan dan validasi data Silver.

Pengerjaan dilakukan menggunakan Python melalui Visual Studio Code dan dikelola menggunakan GitHub agar setiap perubahan dan hasil pekerjaan dapat didokumentasikan dengan baik.

## 2. Tujuan Sprint 1

Tujuan pelaksanaan Sprint 1 adalah:

1. Memastikan data mentah yang digunakan sesuai dengan manifest.
2. Memeriksa dan memahami struktur dataset dari sumber BPS dan WDI.
3. Memeriksa kesesuaian kode indikator, nama seri, satuan, dan periode.
4. Mendokumentasikan keputusan pengolahan data dalam log keputusan.
5. Menghasilkan data Silver dengan struktur yang telah ditentukan.
6. Melakukan validasi terhadap hasil pengolahan data.
7. Menyimpan hasil pekerjaan dan dokumentasi pada repository GitHub kelompok.

## 3. Persiapan Lingkungan Kerja

Tahap awal dilakukan dengan mempersiapkan repository proyek Capstone Data Wrangling pada Visual Studio Code.

Beberapa kegiatan yang dilakukan meliputi:

- Membuka repository proyek kelompok.
- Memastikan branch kerja yang digunakan adalah `124450068/kerja`.
- Memeriksa struktur direktori proyek.
- Menyiapkan lingkungan Python dan kebutuhan library.
- Memeriksa file serta dataset yang tersedia pada direktori `data/raw/`.

Repository yang digunakan:

`https://github.com/EdseladyaP/capstone-dw-kelompok-07`

Struktur direktori yang digunakan mencakup `data/`, `docs/`, `reports/`, `results/`, `sprint/`, dan `src/`.

## 4. Pemeriksaan Data dan Metadata

### 4.1 Sumber Data

Data yang digunakan terdiri atas enam seri indikator, yaitu lima seri dari BPS dan satu seri dari WDI.

| No. | Kode Seri | Indikator | Sumber |
|---|---|---|---|
| 1 | var303 | Angka Partisipasi Kasar (APK) Menurut Provinsi dan Jenjang Pendidikan | BPS |
| 2 | var1443 | Angka Partisipasi Kasar (APK) Perguruan Tinggi | BPS |
| 3 | var2685 | Tingkat Partisipasi Remaja dan Dewasa dalam Pendidikan dan Pelatihan Formal dan Nonformal | BPS |
| 4 | var417 | Harapan Lama Sekolah | BPS |
| 5 | var1429 | Rata-Rata Lama Sekolah Penduduk Umur 15 Tahun ke Atas | BPS |
| 6 | SE.TER.ENRR | School Enrollment, Tertiary (% Gross) | WDI |

### 4.2 Pemeriksaan Satuan dan Periode

Pemeriksaan dilakukan dengan membandingkan judul indikator, metadata sumber, dan karakteristik nilai pada data mentah.

Hasil pemeriksaan satuan:

- var303: Persen.
- var1443: Persen.
- var2685: Persen.
- var417: Tahun.
- var1429: Tahun.
- SE.TER.ENRR: Persen.

Periode data yang diperiksa:

| Kode Seri | Periode |
|---|---|
| var303 | 2003–2025 |
| var1443 | 2015–2025 |
| var2685 | 2022–2024 |
| var417 | 2010–2025 |
| var1429 | 2015–2025 |
| SE.TER.ENRR | 1970–2023 |

Pemeriksaan periode dilakukan agar informasi waktu pada setiap indikator tetap terjaga dan tidak mengalami perubahan yang dapat menghilangkan informasi dari sumber aslinya.

### 4.3 Pemeriksaan Kode SDG

Pemeriksaan kode SDG dilakukan berdasarkan metadata dan dokumen pemetaan indikator.

Salah satu hasil penting adalah seri var417 (Harapan Lama Sekolah) yang masih dicatat sebagai Belum Terpetakan karena belum ditemukan bukti pemetaan kode SDG spesifik yang memadai.

Keputusan tersebut dilakukan agar tidak menetapkan kode indikator tanpa sumber resmi yang mendukung.

## 5. Pemeriksaan Integritas Data

Pemeriksaan integritas dilakukan terhadap file `data/raw/MANIFEST.csv`.

Pada pemeriksaan awal ditemukan satu entri duplikat untuk file `sdg4_apk_pt.json`. Jumlah entri manifest awal adalah 16, sedangkan jumlah file mentah yang tersedia adalah 15.

Setelah dilakukan pemeriksaan dan penghapusan entri duplikat, jumlah entri manifest menjadi 15 dan sesuai dengan jumlah file mentah.

Pemeriksaan selanjutnya dilakukan dengan membandingkan ukuran file dan nilai SHA-256 setiap file.

Hasil pemeriksaan:

| Komponen | Hasil |
|---|---:|
| Jumlah entri manifest | 15 |
| Jumlah file mentah | 15 |
| File belum tercatat | 0 |
| Kesalahan ukuran file | 0 |
| Kesalahan SHA-256 | 0 |
| Status validasi | True |

Hasil tersebut menunjukkan bahwa seluruh file mentah telah sesuai dengan informasi yang tercatat dalam manifest.

## 6. Dokumentasi Keputusan Wrangling

Setiap keputusan pengolahan data dicatat dalam file `log-keputusan.csv`.

Dokumentasi tersebut berisi keputusan yang diambil, alternatif yang ditolak, alasan pemilihan keputusan, serta dampaknya terhadap proses pengolahan data.

Dua keputusan penting yang dicatat adalah:

**1. Keputusan K-034**

Seri var417 (Harapan Lama Sekolah) tetap dicatat sebagai Belum Terpetakan karena belum ditemukan kode SDG spesifik yang dapat dipastikan berdasarkan metadata yang diperiksa.

**2. Keputusan K-035**

Periode asli setiap indikator dipertahankan dan tidak dilakukan perataan data semesteran atau bulanan menjadi tahunan pada tahap Silver.

Keputusan ini bertujuan mempertahankan informasi periode asli dan mencegah perubahan karakteristik data sumber.

## 7. Proses Pembentukan Data Silver

Tahap Silver bertujuan menghasilkan data yang telah dibersihkan dan diseragamkan agar memiliki struktur yang konsisten.

Proses dilakukan melalui pipeline Python yang mencakup ekstraksi data mentah, pengolahan data, dan penyimpanan hasil ke format Parquet.

Struktur kolom Silver yang digunakan meliputi:

1. `sumber`
2. `seri_kode`
3. `wilayah_kode`
4. `nama_wilayah`
5. `periode`
6. `jenis_periode`
7. `rincian`
8. `nilai`
9. `satuan`
10. `_berkas_raw`
11. `_sha256_raw`

Berdasarkan hasil pengujian pipeline yang dikerjakan, diperoleh ringkasan hasil Silver sebagai berikut:

| Komponen | Hasil |
|---|---:|
| Jumlah baris Silver | 4.216 |
| Jumlah seri | 6 |
| Jumlah wilayah unik | 39 |
| Jumlah duplikat kunci | 0 |
| Jumlah baris dengan nilai kosong | 0 |
| Jumlah baris BPS | 4.163 |
| Jumlah baris WDI | 53 |

Hasil tersebut menunjukkan bahwa data dari kedua sumber telah berhasil disusun ke dalam satu struktur Silver dengan tetap mempertahankan informasi sumber data.

## 8. Validasi Hasil Pengolahan

Validasi dilakukan untuk memastikan hasil pengolahan memiliki struktur dan karakteristik sesuai ketentuan proyek.

Pemeriksaan meliputi:

- Pemeriksaan struktur kolom Silver.
- Pemeriksaan jumlah baris.
- Pemeriksaan jumlah wilayah dan seri.
- Pemeriksaan duplikasi kunci Silver.
- Pemeriksaan nilai kosong.
- Pemeriksaan informasi sumber dan lineage data.

Validasi skema dilakukan menggunakan modul yang telah disediakan dalam repository, yaitu `src.common.skema`.

Hasil pengolahan menunjukkan bahwa jumlah duplikat kunci Silver adalah 0 dan jumlah baris dengan nilai kosong adalah 0.

## 9. Dokumentasi dan Pengiriman ke GitHub

Seluruh hasil pekerjaan didokumentasikan dalam repository kelompok.

Dokumentasi yang dikerjakan meliputi:

- `data/katalog-hasil-pemeriksaan.csv`
- `log-keputusan.csv`
- `reports/individu/124450068.md`
- `reports/laporan-tahap-4.md`

File laporan Tahap 4 telah dikirimkan ke repository GitHub melalui branch `124450068/kerja`.

Proses pengiriman dilakukan menggunakan perintah Git:

```bash
git add reports/laporan-tahap-4.md
git commit -m "docs: tambah laporan tahap 4"
git push origin 124450068/kerja
```

Push berhasil dilakukan dan menghasilkan commit `6fff112`.

## 10. Kendala dan Solusi

Selama pelaksanaan Sprint 1 terdapat beberapa kendala yang ditemukan.

**1. Entri duplikat pada manifest**

Ditemukan satu entri duplikat pada file MANIFEST.csv. Solusinya adalah memeriksa daftar file dan menghapus entri yang tercatat dua kali.

**2. Pemetaan kode SDG belum dapat dipastikan**

Pada seri var417 belum ditemukan bukti pemetaan kode SDG yang spesifik. Solusinya adalah mempertahankan status Belum Terpetakan sampai tersedia sumber resmi yang mendukung.

**3. Kesalahan lokasi repository Git**

Pada saat melakukan push laporan, folder kerja awal tidak dikenali sebagai repository Git karena tidak memiliki direktori `.git`.

Solusinya adalah menemukan repository asli yang berada di `workbench-workspace`, kemudian menyalin file laporan ke repository tersebut.

**4. Pemisahan perubahan file saat commit**

Repository memiliki perubahan lain pada file Silver dan metrics. Oleh karena itu, proses staging dilakukan secara spesifik hanya terhadap file laporan agar perubahan lainnya tidak ikut masuk ke commit laporan.

## 11. Kesimpulan

Berdasarkan pelaksanaan Sprint 1, proses pemeriksaan data, metadata, integritas file, dokumentasi keputusan, serta pengolahan data Silver telah memberikan hasil yang dapat digunakan sebagai dasar pengerjaan tahap selanjutnya.

Pemeriksaan manifest berhasil dilakukan terhadap 15 file mentah tanpa ditemukan kesalahan ukuran maupun SHA-256. Enam seri indikator dari BPS dan WDI juga telah diperiksa satuan, periode, serta pemetaan kode SDG-nya.

Hasil pengujian pipeline menghasilkan 4.216 baris data Silver, dengan enam seri dan 39 wilayah unik. Selain itu, tidak ditemukan duplikasi kunci maupun nilai kosong pada ringkasan hasil yang diperoleh.

Seluruh pekerjaan dokumentasi Tahap 4 telah dikirimkan ke repository GitHub kelompok melalui branch `124450068/kerja`.

Dengan demikian, Sprint 1 menghasilkan dokumentasi pemeriksaan data dan hasil pengolahan yang dapat menjadi dasar untuk melanjutkan proses integrasi serta analisis pada tahap berikutnya.

## 12. Saran

Untuk pengembangan selanjutnya, beberapa hal yang perlu diperhatikan adalah:

1. Melakukan pemeriksaan metadata secara berkala berdasarkan sumber resmi.
2. Melengkapi pemetaan kode SDG yang belum dapat dipastikan.
3. Mempertahankan informasi periode dan sumber asli dalam setiap proses pengolahan.
4. Melakukan validasi otomatis setiap kali pipeline dijalankan.
5. Memastikan seluruh keputusan wrangling terdokumentasi agar proses pengolahan dapat ditelusuri kembali.

