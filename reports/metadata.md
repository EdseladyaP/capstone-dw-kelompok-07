# Metadata seri: nama, satuan, kode SDG

Dihasilkan `python pipeline.py` dari berkas mentah dan `src/konfigurasi.py`. Tabel lengkap ada di `docs/seri.csv`. Bila katalog dan berkas mentah berbeda, berkas mentah yang dipakai dan koreksinya dicatat di `log-keputusan.csv`.

## Nama di berkas mentah dan nama baku

| seri_kode | nama_di_berkas | nama_baku |
|---|---|---|
| var303 | Angka Partisipasi Kasar (APK) Menurut Provinsi dan Jenjang Pendidikan | Angka Partisipasi Kasar (APK) menurut jenjang SD, SMP, SM |
| var1443 | Angka Partisipasi Kasar (APK) Perguruan Tinggi (PT) Menurut Provinsi | Angka Partisipasi Kasar (APK) perguruan tinggi |
| var2685 | 4.3.1* Tingkat Partisipasi Remaja dan Dewasa dalam Pendidikan dan Pelatihan Formal dan Non Formal dalam 12 Bulan Terakhir Menurut Provinsi | Tingkat partisipasi remaja dan dewasa dalam pendidikan dan pelatihan formal dan nonformal 12 bulan terakhir |
| var417 | [Metode Baru] Harapan Lama Sekolah | Harapan lama sekolah (IPM metode baru) |
| var1429 | Rata-Rata Lama Sekolah Penduduk Umur 15 Tahun ke Atas Menurut Provinsi | Rata-rata lama sekolah penduduk umur 15 tahun ke atas |
| SE.TER.ENRR | School enrollment, tertiary (% gross) | School enrollment, tertiary (% gross) |

## Satuan dan kode SDG

| seri_kode | katalog_satuan | satuan | bukti_satuan | katalog_sdg | sdg_kode |
|---|---|---|---|---|---|
| var303 | tidak_ada | persen_apk | judul 'Angka Partisipasi Kasar'; var.unit kosong; nilai di atas 100 ada (APK menghitung siswa semua umur) | 4.3.1 | 4.1 |
| var1443 | tidak_ada | persen_apk | judul 'Angka Partisipasi Kasar'; var.unit kosong | 4.3.1 | 4.3.1 |
| var2685 | persen | persen | var.unit: 'Persen' | 4.3.1 | 4.3.1 |
| var417 | tahun | tahun | var.unit: 'Tahun' | — | — |
| var1429 | tidak_ada | tahun | judul 'Rata-Rata Lama Sekolah'; var.unit kosong; nilai 6–12 | — | — |
| SE.TER.ENRR | — | persen_apk | name: '(% gross)'; sourceNote: rasio kasar, bisa > 100 | — | 4.3.1 |

## Koreksi katalog

| seri_kode | koreksi_katalog |
|---|---|
| var303 | satuan tidak_ada -> persen_apk; kode SDG 4.3.1 -> 4.1 (tidak ada jenjang PT di turvar) |
| var1443 | satuan tidak_ada -> persen_apk |
| var1429 | satuan tidak_ada -> tahun |
| SE.TER.ENRR | kode SDG kosong -> 4.3.1 |

## Catatan BPS (var.note)

| var_id | catatan (tanpa tag HTML) |
|---|---|
| 2685 | Sumber: Badan Pusat Statistik |
| 303 | Sumber: BPS, Susenas Catatan: Mulai tahun 2007, APK mencakup pendidikan non-formal (paket A setara SD sederajat, paket B setara SMP sederajat dan paket C setara SMA/SMK sederajat) |
| 1443 | Sumber: BPS, Susenas Catatan: Kelompok umur perguruan tinggi yang digunakan adalah 19-23 tahun |
| 417 | Untuk penjelasan lebih lanjut mengenai IPM metode baru silahkan klik link di bawah ini -Booklet IPM metode Baru -Bahan Sosialisasi IPM metode baru |
| 1429 | Sumber: BPS, Susenas |

## Metadata WDI yang muncul di lebih dari satu berkas

| seri | jumlah_entri | berkas | isi_sama |
|---|---|---|---|
| SE.TER.ENRR | 2 | sumber2_indikator.json, sumber46_indikator.json | ya |

## Judul dengan spasi di awal/akhir

Tidak ada.
