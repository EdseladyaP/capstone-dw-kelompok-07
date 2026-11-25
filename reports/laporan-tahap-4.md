LAPORAN TAHAP 4

Persiapan Pemeriksaan Katalog Indikator BPS dan WDI

1. Pendahuluan

Tahap 4 merupakan tahap persiapan pemeriksaan katalog indikator yang bersumber dari Badan Pusat Statistik (BPS) dan World Development Indicators (WDI). Pemeriksaan dilakukan untuk memastikan kesesuaian nama seri, kode SDG, satuan, dan periode berdasarkan metadata serta berkas mentah yang tersedia dalam repositori capstone.

Kegiatan ini bertujuan mengidentifikasi ketidaksesuaian informasi pada katalog awal, menetapkan satuan yang sesuai dengan karakteristik indikator, serta mendokumentasikan setiap keputusan pemeriksaan ke dalam file "log-keputusan.csv".

2. Tujuan

Tujuan pelaksanaan Tahap 4 adalah:

1. Memeriksa enam seri indikator yang berasal dari BPS dan WDI.
2. Memastikan kesesuaian kode SDG berdasarkan informasi dan sumber metadata.
3. Memeriksa serta menetapkan satuan setiap indikator.
4. Mencatat periode awal dan akhir setiap seri.
5. Mendokumentasikan seluruh koreksi dan keputusan dalam "log-keputusan.csv".
6. Memastikan periode asli data tetap dipertahankan dan tidak dilakukan perataan periode semesteran atau bulanan menjadi tahunan di Silver.

3. Data dan Sumber yang Digunakan

Data yang diperiksa terdiri dari enam seri indikator, yaitu lima seri dari BPS dan satu seri dari WDI.

No.| Sumber| Kode Seri| Nama Indikator
1| BPS| var303| Angka Partisipasi Kasar (APK) Menurut Provinsi dan Jenjang Pendidikan
2| BPS| var1443| Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT)
3| BPS| var2685| Tingkat Partisipasi Remaja dan Dewasa dalam Pendidikan dan Pelatihan Formal dan Non Formal
4| BPS| var417| Harapan Lama Sekolah
5| BPS| var1429| Rata-Rata Lama Sekolah Penduduk Umur 15 Tahun ke Atas
6| WDI| SE.TER.ENRR| School Enrollment, Tertiary (% Gross)

Sumber pemeriksaan meliputi berkas CSV dan JSON pada direktori "data/raw/", metadata BPS, metadata WDI, serta dokumen pemetaan indikator SDGs yang dicatat dalam log keputusan.

4. Hasil Pemeriksaan Katalog

Berdasarkan pemeriksaan judul indikator, metadata, dan karakteristik nilai, diperoleh hasil sebagai berikut.

Kode Seri| Kode SDG dalam Katalog| Satuan| Periode
var303| 4.1.1.(d), 4.1.1.(e), 4.1.1.(f)| Persen| 2003–2025
var1443| 4.3.1.(b)| Persen| 2015–2025
var2685| 4.3.1| Persen| 2022–2024
var417| Belum terpetakan| Tahun| 2010–2025
var1429| 4.1.1.(g)| Tahun| 2015–2025
SE.TER.ENRR| 4.3.2| Persen| 1970–2023

4.1 Pemeriksaan Satuan

Pemeriksaan satuan dilakukan dengan membandingkan informasi satuan pada metadata dengan judul indikator dan karakteristik nilai pada data mentah.

Hasil pemeriksaan menunjukkan bahwa:

- var303 ditetapkan menggunakan satuan Persen karena merupakan indikator Angka Partisipasi Kasar.
- var1443 ditetapkan menggunakan satuan Persen karena mengukur Angka Partisipasi Kasar Perguruan Tinggi.
- var2685 menggunakan satuan Persen sesuai metadata BPS.
- var417 menggunakan satuan Tahun sesuai metadata BPS.
- var1429 ditetapkan menggunakan satuan Tahun berdasarkan judul indikator dan karakteristik nilainya.
- SE.TER.ENRR menggunakan satuan Persen karena merupakan indikator Gross Enrollment Ratio.

Dengan demikian, keenam seri telah memiliki satuan yang tercatat dalam katalog hasil pemeriksaan.

4.2 Pemeriksaan Kode SDG

Pemeriksaan kode SDG dilakukan dengan mengacu pada metadata dan dokumen pemetaan indikator yang dicatat dalam log keputusan.

Beberapa hasil pemetaan yang dicatat adalah:

1. var303 memiliki pemetaan berbeda berdasarkan jenjang pendidikan, yaitu 4.1.1.(d) untuk SD, 4.1.1.(e) untuk SMP, dan 4.1.1.(f) untuk SMA/SMK.
2. var1443 menggunakan kode 4.3.1.(b) berdasarkan publikasi indikator TPB/SDGs BPS yang dicatat pada log keputusan.
3. var2685 menggunakan kode 4.3.1 sesuai metadata BPS.
4. var417 masih dicatat sebagai Belum terpetakan karena belum ditemukan kode indikator SDG spesifik pada metadata yang diperiksa.
5. var1429 menggunakan kode 4.1.1.(g) berdasarkan pemetaan yang dicatat dari Pedoman RAN TPB/SDGs Bappenas.
6. SE.TER.ENRR menggunakan kode 4.3.2 berdasarkan metadata World Bank dan UNESCO UIS.

Khusus var417, keputusan untuk mempertahankan status Belum terpetakan dilakukan agar tidak menetapkan kode SDG tanpa bukti sumber yang memadai.

5. Pemeriksaan Periode Data

Berdasarkan metadata enam seri yang diperiksa, periode data masing-masing indikator tercatat dalam bentuk tahunan.

Dalam persiapan pengolahan data Silver, periode asli harus tetap dipertahankan. Apabila terdapat data dengan periode semesteran atau bulanan pada sumber lain, data tersebut tidak boleh dirata-ratakan atau digabungkan menjadi periode tahunan secara langsung.

Setiap kombinasi seri, wilayah, periode, rincian, dan berkas sumber harus tetap dipertahankan sebagai observasi tersendiri. Data dari sumber yang berbeda juga tidak boleh digabungkan pada tahap Silver karena proses rekonsiliasi dilakukan pada tahap Gold.

6. Pemeriksaan Manifest dan Integritas Berkas

Pemeriksaan juga dilakukan terhadap "data/raw/MANIFEST.csv" untuk memastikan setiap berkas mentah memiliki informasi ukuran berkas dan SHA-256.

Pada proses pemeriksaan ditemukan satu entri duplikat untuk berkas "sdg4_apk_pt.json". Entri duplikat tersebut kemudian dihapus.

Selanjutnya dilakukan validasi menggunakan Python dengan membandingkan ukuran dan SHA-256 setiap berkas terhadap informasi pada manifest.

Hasil validasi menunjukkan:

- Jumlah entri manifest: 15.
- Jumlah berkas mentah: 15.
- Berkas yang belum tercatat: tidak ada.
- Kesalahan ukuran atau SHA-256: tidak ditemukan.
- Status validasi: True.

Hasil tersebut menunjukkan bahwa seluruh berkas mentah yang diperiksa telah sesuai dengan informasi manifest.

7. Dokumentasi Keputusan

Seluruh hasil pemeriksaan dan koreksi dicatat dalam file "log-keputusan.csv".

Log keputusan digunakan untuk mendokumentasikan seri yang diperiksa, keputusan yang diambil, alternatif yang ditolak, alasan keputusan, dan dampak terhadap data.

Hingga pemeriksaan terakhir, log keputusan memiliki 15 baris data dengan 9 kolom. Validasi menggunakan Python menunjukkan bahwa seluruh baris memiliki jumlah kolom yang konsisten.

8. Hasil Validasi

Validasi dilakukan terhadap dua file utama, yaitu "data/katalog-hasil-pemeriksaan.csv" dan "log-keputusan.csv".

Hasil validasi adalah sebagai berikut:

File| Jumlah Kolom| Jumlah Baris Data| Hasil
katalog-hasil-pemeriksaan.csv| 8| 6| True
log-keputusan.csv| 9| 15| True

Berdasarkan hasil tersebut, kedua file telah memiliki struktur CSV yang konsisten dan dapat dibaca menggunakan Python.

Perlu diperhatikan bahwa validasi struktur CSV dan manifest tidak dengan sendirinya membuktikan seluruh pemetaan kode SDG telah terverifikasi secara independen.

9. Kesimpulan

Berdasarkan kegiatan yang telah dilakukan, Tahap 4 (persiapan) telah menghasilkan katalog pemeriksaan untuk enam seri indikator BPS dan WDI, penetapan satuan, pencatatan periode, serta dokumentasi keputusan dalam "log-keputusan.csv".

Pemeriksaan integritas berkas melalui manifest juga telah berhasil dilakukan dengan hasil validasi True. Selain itu, aturan pengolahan periode telah dicatat sebagai pedoman agar data semesteran dan bulanan tidak dirata-ratakan menjadi tahunan pada tahap Silver.

Masih terdapat keterbatasan pada pemetaan kode SDG untuk indikator Harapan Lama Sekolah (var417), karena kode indikator spesifik belum dapat dipastikan berdasarkan metadata yang diperiksa. Oleh karena itu, seri tersebut tetap dicatat sebagai Belum terpetakan sampai tersedia sumber pemetaan resmi yang mendukungnya.

Dengan demikian, hasil pekerjaan persiapan telah didokumentasikan dalam katalog dan log keputusan serta dikirimkan ke repositori GitHub melalui branch "124450068/kerja".