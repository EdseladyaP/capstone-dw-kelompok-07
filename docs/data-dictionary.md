# Data Dictionary

## Silver

| Kolom | Keterangan |
|---|---|
| sumber | Sumber data |
| seri_kode | Kode indikator |
| wilayah_kode | Kode wilayah |
| nama_wilayah | Nama wilayah |
| periode | Periode observasi |
| jenis_periode | Jenis periode: tahun, semester, atau bulan |
| rincian | Kategori/rincian indikator |
| nilai | Nilai observasi |
| satuan | Satuan nilai |
| _berkas_raw | Lokasi berkas sumber |
| _sha256_raw | Hash berkas sumber |

Silver mempertahankan observasi asli, termasuk rincian,
periode, dan informasi sumber.

## Gold

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

Berisi observasi detail tiga indikator utama:
var1429 (RLS), var1443 (APK perguruan tinggi),
dan var417 (HLS).

Kolom nilai menyimpan nilai observasi sesuai satuannya.
Kolom outlier_asli menunjukkan apakah observasi
termasuk anomali yang dipertahankan.

### anomali_gold

Menyimpan hasil klasifikasi anomali, nilai Silver,
batas IQR, verifikasi sumber, dan tindakan.

### audit_snapshot_gold

Menyimpan catatan snapshot yang tidak dipilih
ketika terdapat lebih dari satu snapshot.

## Aturan satuan dan wilayah

- Persen memiliki rentang 0 sampai 100.
- Lama sekolah dalam tahun memiliki rentang 0 sampai 30.
- Panel utama berisi 38 provinsi.
- Kode nasional 9999 tidak dimasukkan ke panel provinsi.
- Nilai kosong tidak otomatis diganti dengan nol.
- Penanda outlier asli tetap dipertahankan.
