# Ekstraksi: jumlah baris per berkas

Dihasilkan `python pipeline.py`. Peran *data* berisi angka; *meta* berisi judul, definisi, atau catatan unduhan. Semua baris `data/raw/MANIFEST.csv` tertangani.

| berkas | pembaca | peran | baris | catatan |
|---|---|---|---|---|
| bps/2026-10-17/json/sdg4_4_3_1_v2685.json | bps_json | data | 436 | 1 halaman |
| bps/2026-10-17/json/sdg4_apk.json | bps_json | data | 2376 | 8 halaman |
| bps/2026-10-17/json/sdg4_apk_pt.json | bps_json | data | 393 | 4 halaman |
| bps/2026-10-17/json/sdg4_hls.json | bps_json | data | 8732 | 6 halaman |
| bps/2026-10-17/json/sdg4_rls.json | bps_json | data | 393 | 4 halaman |
| bps/2026-10-17/manifest_asal.json | bps_manifest_asal | meta | 42 | semua tabel unduhan BPS, bukan hanya kasus ini |
| bps/2026-10-17/sdg4_4_3_1_v2685.csv | bps_csv | data | 436 |  |
| bps/2026-10-17/sdg4_apk.csv | bps_csv | data | 2376 |  |
| bps/2026-10-17/sdg4_apk_pt.csv | bps_csv | data | 393 |  |
| bps/2026-10-17/sdg4_hls.csv | bps_csv | data | 8732 |  |
| bps/2026-10-17/sdg4_rls.csv | bps_csv | data | 393 |  |
| wdi/2026-10-20/data/kelompok-05-hal-01.json | wdi_data | data | 66 | 3,960 baris di berkas, 1 seri kasus disaring |
| wdi/2026-10-20/metadata/sumber.json | wdi_sumber | meta | 71 |  |
| wdi/2026-10-20/metadata/sumber2_indikator.json | wdi_meta | meta | 1 | metadata seri kasus saja |
| wdi/2026-10-20/metadata/sumber46_indikator.json | wdi_meta | meta | 1 | metadata seri kasus saja |

Jumlah: 15 berkas dari 15 di MANIFEST, 24,726 baris mentah di berkas data.
