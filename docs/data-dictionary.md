# Data dictionary — Kasus 07 Partisipasi dan lama sekolah

Ditulis ulang otomatis oleh `python pipeline.py` (`src/dokumen.py`). Tipe, rentang, dan jumlah kosong dihitung dari `data/silver/silver.parquet`.

Dokumen ini mendaftarkan **setiap kolom Silver** dengan nama, tipe, satuan/format, arti, dan asal (berkas mentah atau keputusan di `log-keputusan.csv`). Dokumentasi Gold tersedia pada bagian Data Dictionary Gold di bawah ini.

## data/silver/silver.parquet (4,216 baris)

Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Kunci unik: sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw.

| kolom | tipe | satuan/format | kosong | rentang_atau_nilai | asal | arti |
|---|---|---|---|---|---|---|
| sumber | str | kategori (nama folder) | 0 | bps, wdi | nama folder sumber di data/raw/ (berkas mentah) | lembaga penerbit: bps, wdi, who_gho, ilostat, bnpb |
| seri_kode | str | kode seri | 0 | SE.TER.ENRR, var1429, var1443, var2685, var303, var417 | kolom var BPS / indicator.id WDI (berkas mentah) | identitas seri; arti lengkap di docs/seri.csv |
| wilayah_kode | int64 | kode BPS (2 digit x 100) | 0 | 1100 – 9999 | kamus src/wilayah.py; log K-002 | kode BPS dua digit x 100; 9999 = Indonesia |
| nama_wilayah | str | teks | 0 | Aceh, Bali, Banten, Bengkulu, DI Yogyakarta, DKI Jakarta, … (39 nilai) | kamus src/wilayah.py; log K-002 | nama baku susunan 38 provinsi 2025, bukan label sumber |
| periode | str | tahun / tahun-S1 / tahun-Q1 / tahun-bulan | 0 | 1970, 1972, 1973, 1974, 1975, 1976, … (55 nilai) | tahun/turtahun BPS, date WDI, DIM_TIME WHO (berkas mentah) | bentuk baku: 2019, 2019-S1, 2019-Q3, 2019-07 |
| jenis_periode | str | kategori | 0 | tahun | diturunkan dari periode (berkas mentah) | tahun, semester, triwulan, atau bulan |
| rincian | str | dimensi=kode;... | 0 | jenjang=sd, jenjang=sm, jenjang=smp, total, umur=15-24, umur=15-64, … (8 nilai) | turvar BPS; kolom DIM_* WHO (berkas mentah); log K-018, K-019 | 'total' atau 'dimensi=kode;...'; lihat kamus di bawah |
| nilai | float64 | mengikuti satuan seri (persen, persen_apk, tahun) | 0 | 0.35 – 121.31 | datacontent BPS; value WDI; RATE_*_N WHO (berkas mentah) | angka sesuai satuan; baris tanpa angka tidak masuk Silver |
| satuan | str | nama satuan | 0 | persen, persen_apk, tahun | src/konfigurasi.py, bukti di docs/seri.csv; log K-018 | satuan baku; satu satuan per seri |
| sdg_kode | str | kode indikator SDG | 0 | 4.1, 4.3.1, — | src/konfigurasi.py, bukti di docs/seri.csv; log K-018 | kode indikator SDG (kolom tambahan) |
| batas_bawah | float64 | sama dengan satuan nilai | 4216 | — | RATE_*_NL WHO (tidak ada di paket kasus ini) | batas bawah ketidakpastian; kosong bila sumber tidak memberi |
| batas_atas | float64 | sama dengan satuan nilai | 4216 | — | RATE_*_NU WHO (tidak ada di paket kasus ini) | batas atas ketidakpastian; kosong bila sumber tidak memberi |
| rujukan_tahun | Int64 | tahun | 4216 | — | var.note BPS (berkas mentah) | lebar jendela rujukan survei (tahun sebelum survei); kosong bila tidak berlaku |
| _berkas_raw | str | jalur relatif data/raw/ | 0 | bps/2026-10-17/json/sdg4_4_3_1_v2685.json, bps/2026-10-17/json/sdg4_apk.json, bps/2026-10-17/json/sdg4_apk_pt.json, bps/2026-10-17/json/sdg4_hls.json, bps/2026-10-17/json/sdg4_rls.json, wdi/2026-10-20/data/kelompok-05-hal-01.json | pembaca ekstraksi src/ekstraksi; log K-004 | lineage: berkas asal baris ini |
| _sha256_raw | str | hex 64 karakter | 0 | 15b9d56e3e2b30cd190900fe758e7a97548e030cf425d618afd37bbc64d726a8, 2bd4a4dc8b92d7b9e10dd187596ee1345218a155a76d2ed51dec09af507cc33f, 3b8245e001bc3614dbddb323e92588c0fcef41e3c7b39838419d817548347c2a, 6e14806cf21835715abbc50745253bfbed82e88ba5fc41f202a2a8150103c47e, ad8155b7117914929b2c91b16ade1654b94c0632b3364bbfc97dc4214b9abc8e, bc081b82fe1fa9326027434b5e883f1ef14d4c30efab6a34b87e379b2f642689 | src.common.manifest.sha256_raw, dicocokkan dengan MANIFEST.csv; log K-004 | lineage: sidik isi berkas asal |

## Kamus rincian

Aturan menulis rincian (log): dimensi yang bervariasi ditulis `nama=kode`, dipisah `;`, urut abjad; nilai total sumber dibuang; baris tanpa dimensi bervariasi ditulis `total`. Dimensi yang nilainya tetap di seluruh berkas dianggap bagian definisi seri dan dicatat di kolom `cakupan` docs/seri.csv.

Nama dimensi dan kode yang sah:

- `jenjang`: `sd`, `sm`, `smp`
- `umur`: `15-24`, `15-64`, `25-54`, `55-64`
- `jenjang` (var303, dari turvar BPS): `sd` = SD/sederajat, `smp` = SMP/sederajat, `sm` = SM/sederajat
- `umur` (var2685, dari turvar BPS): `15-24` = Usia 15-24 tahun, `15-64` = Usia 15-64 tahun, `25-54` = Usia 25-54 tahun, `55-64` = Usia 55-64 tahun

| rincian | dipakai_seri |
|---|---|
| jenjang=sd | var303 |
| jenjang=sm | var303 |
| jenjang=smp | var303 |
| total | SE.TER.ENRR, var1429, var1443, var417 |
| umur=15-24 | var2685 |
| umur=15-64 | var2685 |
| umur=25-54 | var2685 |
| umur=55-64 | var2685 |

## Satuan, kode SDG, dan cakupan per seri

| seri_kode | satuan | sdg_kode | cakupan | bukti_satuan |
|---|---|---|---|---|
| var303 | persen_apk | 4.1 | Susenas; 2003–2025; mulai 2007 termasuk paket A/B/C (var.note) | judul 'Angka Partisipasi Kasar'; var.unit kosong; nilai di atas 100 ada (APK menghitung siswa semua umur) |
| var1443 | persen_apk | 4.3.1 | kelompok umur acuan 19–23 tahun (var.note); Susenas; 2015–2025 | judul 'Angka Partisipasi Kasar'; var.unit kosong |
| var2685 | persen | 4.3.1 | empat kelompok umur yang tumpang tindih (15–64 mencakup yang lain); 2022–2024 | var.unit: 'Persen' |
| var417 | tahun | — | anak umur 7 tahun; 2010–2025; berkas juga memuat kabupaten/kota (dikeluarkan) | var.unit: 'Tahun' |
| var1429 | tahun | — | penduduk 15+; Susenas; 2015–2025 | judul 'Rata-Rata Lama Sekolah'; var.unit kosong; nilai 6–12 |
| SE.TER.ENRR | persen_apk | 4.3.1 | UNESCO UIS; kelompok umur resmi jenjang tersier (umur tidak disebut di sourceNote) | name: '(% gross)'; sourceNote: rasio kasar, bisa > 100 |

## Kode wilayah

9999 = Indonesia; provinsi = kode BPS dua digit x 100, susunan 38 provinsi 2025 (38 kode). WDI menulis Indonesia `ID`/`IDN`, WHO GHO menulis `360` (M49); keduanya dipetakan ke 9999 di `src/wilayah.py`.

## Contoh penelusuran satu baris

Contoh baris Silver berikut ditelusuri sampai berkas mentahnya dan dicocokkan dengan `MANIFEST.csv`.

| sumber | seri_kode | wilayah_kode | periode | rincian | nilai | satuan | _berkas_raw | _sha256_raw |
|---|---|---|---|---|---|---|---|---|
| bps | var1429 | 1100 | 2015 | total | 9.32 | tahun | bps/2026-10-17/json/sdg4_rls.json | bc081b82fe1fa9326027434b5e883f1ef14d4c30efab6a34b87e379b2f642689 |

1. `_berkas_raw` = `bps/2026-10-17/json/sdg4_rls.json` menunjuk `data/raw/bps/2026-10-17/json/sdg4_rls.json` (jalur relatif terhadap `data/raw/`).

2. Baris `bps/2026-10-17/json/sdg4_rls.json` di `data/raw/MANIFEST.csv` berisi `bait=22101` dan `sha256=bc081b82fe1fa9326027434b5e883f1ef14d4c30efab6a34b87e379b2f642689`; nilai sha256 ini sama dengan `_sha256_raw` baris Silver.

3. sha256 isi berkas mentah dihitung ulang juga `bc081b82fe1fa9326027434b5e883f1ef14d4c30efab6a34b87e379b2f642689`; hasilnya sama dengan `_sha256_raw`. Jadi berkas yang dibaca benar-benar berkas yang tercatat.

4. Di berkas mentah JSON BPS, angka 9.32 ada pada kunci `datacontent` `1100142901150` = wilayah 1100 + var 1429 + turvar 'Tidak ada' + tahun 2015 + turtahun 'Tahun'.


## Data Dictionary Gold

### panel_provinsi_tahun

| Kolom | Keterangan |
|---|---|
| wilayah_id | Kode provinsi |
| nama_wilayah | Nama baku provinsi |
| tahun | Tahun observasi |
| rata_rata_lama_sekolah_tahun | Rata-rata lama sekolah, satuan tahun |
| apk_perguruan_tinggi_persen | APK perguruan tinggi, satuan persen |
| harapan_lama_sekolah_tahun | Harapan lama sekolah, satuan tahun |
| status_* | Status ketersediaan nilai indikator |
| outlier_* | Penanda outlier asli |

### panel_indikator_gold

Berisi observasi detail tiga indikator utama: var1429 (RLS), var1443 (APK perguruan tinggi), dan var417 (HLS).

Kolom nilai menyimpan nilai observasi sesuai satuannya. Kolom outlier_asli menunjukkan apakah observasi termasuk anomali yang dipertahankan.

### anomali_gold

Menyimpan hasil klasifikasi anomali, nilai Silver, batas IQR, verifikasi sumber, dan tindakan.

### audit_snapshot_gold

Menyimpan catatan snapshot yang tidak dipilih ketika terdapat lebih dari satu snapshot.

## Aturan Satuan dan Wilayah Gold

- Persen memiliki rentang 0 sampai 100.
- Lama sekolah dalam tahun memiliki rentang 0 sampai 30.
- Panel utama berisi 38 provinsi.
- Kode nasional 9999 tidak dimasukkan ke panel provinsi.
- Nilai kosong tidak otomatis diganti dengan nol.
- Penanda outlier asli tetap dipertahankan.