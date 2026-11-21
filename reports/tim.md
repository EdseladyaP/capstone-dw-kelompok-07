# Laporan tim — <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.

## Masalah data dan penanganannya

Draf Sprint 1 (NIM 124450095; disusun dengan berbanding acuan `k07-partisipasi-lama-sekolah`).
Setiap angka di bawah dapat ditarik ulang dari `data/silver/silver.parquet`, turunannya
(`reports/angka.json`, `reports/grid-sel-kosong.csv`, `reports/anomali.csv`), atau
`log-keputusan.csv`. Id `K-xxx` tanpa keterangan adalah id log tim; entri `K-022`–`K-035`
adalah hasil pemeriksaan yang status finalnya direkonsiliasi di `K-036`.

| Masalah | Bukti di data mentah/Silver | Keputusan | Baris/sel terdampak | Alternatif yang ditolak | Sumber angka & log |
|---|---|---|---:|---|---|
| Dua seri APK berkode SDG 4.3.1 di katalog | `turvar` `var303` hanya SD/SMP/SM; `var1443` = APK PT | `var303` → 4.1, APK PT hanya `var1443` | 2.376 baris | Menerima kode katalog untuk kedua seri | Silver `seri_kode=var303`; `docs/seri.csv`; K-018, K-031, K-032, K-036 (acuan K-003) |
| Satuan APK kosong dan nilai > 100 (APK SD sampai > 120) | `var.unit` kosong; `nilai` melebihi batas `persen` | satuan `persen_apk`, rentang sah 0–250 | 2.822 baris `persen_apk` (2.376 `var303` + 393 `var1443` + 53 WDI) | Satuan `persen` 0–100 yang menolak APK > 100 | Silver `satuan.value_counts()`; K-021, K-023, K-024, K-027 (acuan K-007) |
| Satuan RLS kosong, nilai 6–12 tahun | judul `var1429`; `var.unit` kosong | `tahun` (0–25) | 393 baris | Membiarkan `tidak_ada` | Silver `seri_kode=var1429`; K-022, K-033 (acuan K-007) |
| Berkas HLS memuat kabupaten/kota | kode wilayah tidak berakhiran `00`; 8.732 baris di berkas | disaring di Silver; hanya provinsi (38) + Indonesia (9999) | 8.167 baris dikeluarkan; 565 dipertahankan | Menyimpan kabupaten/kota di panel provinsi; mencocokkan nama HTML | Silver `seri_kode=var417` = 565; `angka.baris_kabkota_dibuang`; K-003, K-021 (acuan K-005) |
| Kelompok umur `var2685` tumpang tindih (15–64 mencakup yang lain) | 4 `turvar` umur; 8 rincian di Silver | rincian `umur=...` tersendiri, tanpa total buatan | 436 baris `var2685` (4 × 109) | Menjumlahkan kelompok umur | Silver `rincian.value_counts()`; K-019 (acuan K-006) |
| Celah panel provinsi × periode | grid 38 provinsi × periode = 4.180 sel | `belum_ada` untuk provinsi yang belum terbentuk, `batas_lama` untuk angka induk, `missing` tidak diisi | 454 sel kosong: 402 `belum_ada`, 49 `batas_lama`, 3 `missing`, 0 `tidak_diterbitkan` | Memecah angka induk, mengisi 0, atau menginterpolasi | `grid-sel-kosong.csv` (454 baris); `angka.sel_*`; K-001, K-008–K-013, K-028 (acuan K-001, K-013) |
| Aceh 2005 tidak tersedia di ketiga jenjang APK | provinsi sudah ada, tanpa catatan penerbit | `missing`, tidak diisi di Silver | 3 sel (sd, smp, sm) | Interpolasi 2004–2006; `tidak_diterbitkan` tanpa bukti | `grid-sel-kosong.csv` `kategori=missing`; K-013 (acuan K-013) |
| Calon anomali & outlier | IQR × 1,5, perubahan, dan irisan samping ≥ 6 periode | ditandai, nilai tidak diubah; 0 galat input | 367 calon: 262 `outlier`, 82 `perbedaan_struktural` pada 4 provinsi | z-score > 3; profil gabungan semua jenjang; mengoreksi nilai tanpa bukti galat | `anomali.csv`/`calon-anomali.csv` (367 baris); `angka.*`; K-004 (acuan K-004) |
| Patahan definisi dan patahan seri | `var.note` var303: mulai 2007 termasuk paket A/B/C | `PATAHAN_DEFINISI`; deret tidak dibandingkan lintas 2007 | 1 pergantian definisi; 9 calon anomali `patahan_seri` (4 sd + 4 smp + 1 sm) | Membandingkan tren 2006→2007 tanpa catatan; menyambung seri hanya karena tema | `anomali.csv` `kategori=patahan_seri`; `src/konfigurasi.py`; K-012, K-014 (acuan K-012) |
| Judul HLS `[Metode Baru]` | seluruh tahun 2010–2025 sudah metode baru | bukan patahan; catatan pemeriksaan saja | 0 baris diubah | Menetapkan patahan 2010 hanya dari judul | K-015 (acuan K-009) |
| Patahan wilayah saat pemekaran | provinsi induk kehilangan wilayah (Papua, Papua Barat, Kalimantan Timur) | `patahan_wilayah`; induk tidak dibandingkan lintas pemekaran | 27 peristiwa; 14 masuk calon anomali | Menyebutnya outlier biasa; memecah angka induk | `angka.patahan_wilayah=27`; `anomali.csv` 14 baris; K-011, K-028 (acuan K-001, K-011) |
| Revisi/duplikasi antar-snapshot | hanya satu snapshot BPS (2026-10-17); CSV dan JSON adalah dua format pada snapshot yang sama | angka sama = konsisten; angka berbeda akan dicatat sebagai revisi, bukan dihapus | 0 angka berbeda, 0 snapshot ganda; 0 revisi diterapkan | Menghapus salah satu format karena dianggap duplikat; menghapus nilai revisi | `angka.bps_snapshot_beda/ganda=0`; K-016, K-017 |
| WDI `value: null` dan kode SDG kosong | 66 baris `SE.TER.ENRR` terpilih, 13 di antaranya null; kode di `sumber46_indikator.json` | null dibuang; kode SDG → 4.3.1 | 13 baris null dibuang, 53 masuk Silver; 1 kode metadata | Menyimpan NaN; membiarkan kode kosong | `angka.wdi_null_dibuang=13`; Silver `seri_kode=SE.TER.ENRR` = 53; K-020 (acuan K-008, K-010) |
| Koreksi katalog menyeluruh | 4 seri punya `koreksi_katalog` di `docs/seri.csv` | satuan/SDG mengikuti berkas mentah, bukan katalog | 4 entri; 2.376 baris SDG, 3.162 baris satuan | Usulan 4.1.1.(d/e/f), 4.3.1.(b), 4.3.2 (K-030–K-034) sebagai keputusan final | `docs/seri.csv`; `angka.koreksi_katalog/baris_koreksi_*`; K-018, K-021, K-036 |

Catatan: 3.162 baris koreksi satuan = 2.376 `var303` + 393 `var1443` (`tidak_ada` → `persen_apk`)
+ 393 `var1429` (`tidak_ada` → `tahun`); 53 baris WDI sudah ber-satuan `persen_apk` dari name
`(% gross)` dan tidak dihitung sebagai koreksi katalog. Tidak ada galat input (0) yang diubah.

### Cara tarik ulang angka draf ini

```bash
python pipeline.py                                  # tulis ulang Silver + reports/angka.json
python -m src.common.skema data/silver/silver.parquet
```

```python
import csv, json
import pandas as pd

s = pd.read_parquet("data/silver/silver.parquet")
g = pd.read_csv("reports/grid-sel-kosong.csv")
a = pd.read_csv("reports/anomali.csv")
k = json.load(open("reports/angka.json", encoding="utf-8"))
log = list(csv.DictReader(open("log-keputusan.csv", encoding="utf-8-sig")))

assert len(s) == 4216 and s.seri_kode.nunique() == 6
assert (s.seri_kode == "var303").sum() == 2376
assert (s.satuan == "persen_apk").sum() == 2822       # 2376 + 393 + 53
assert (s.seri_kode == "var417").sum() == 565          # 8732 - 8167
assert (s.seri_kode == "var2685").sum() == 436 == 4 * 109
assert len(g) == 454 and g.kategori.value_counts().to_dict() == {
    "belum_ada": 402, "batas_lama": 49, "missing": 3}
assert len(a) == 367 and a.kategori.value_counts().to_dict() == {
    "outlier": 262, "perbedaan_struktural": 82,
    "patahan_wilayah": 14, "patahan_seri": 9}
assert k["galat_input"] == 0 and k["patahan_wilayah"] == 27
assert k["baris_koreksi_satuan"] == 3162 and k["baris_koreksi_sdg"] == 2376
assert k["koreksi_katalog"] == 4 and k["wdi_null_dibuang"] == 13
assert {r["id"] for r in log} >= {"K-018", "K-019", "K-020", "K-021", "K-036"}
```

## Integrasi dan rekonsiliasi
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
