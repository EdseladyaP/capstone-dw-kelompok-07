# Tahap 2 — Profil seri pembanding SE.TER.ENRR

**Kasus 07 — Partisipasi pendidikan tinggi dan lama sekolah** · Kelompok 07
**Penanggung jawab:** Difanya Husakina (124450043) · Sprint 1 · Tugas #5

Dokumen ini memprofil seri **pembanding nasional** `wdi/SE.TER.ENRR`, membandingkan
ketersediaannya dengan **seri utama BPS**, lalu menandai rincian yang **sebanding** untuk dipakai
pada Tahap 6 (integrasi). Seluruh angka diambil dari berkas mentah di `data/raw/`; tidak ada
periode, kategori, satuan, atau nilai yang dikarang.

---

## 1. Sumber data

| Peran | Berkas mentah | sha256 (MANIFEST.csv) |
|---|---|---|
| Observasi pembanding | `wdi/2026-10-20/data/kelompok-05-hal-01.json` | `ad8155b7117914929b2c91b16ade1654b94c0632b3364bbfc97dc4214b9abc8e` |
| Metadata pembanding (WDI) | `wdi/2026-10-20/metadata/sumber2_indikator.json` | `93874b4575260d1b05cc8996ddbff372e58ea53b69309503136453940076314f` |
| Metadata pembanding (SDG) | `wdi/2026-10-20/metadata/sumber46_indikator.json` | `899b4a45ea57fe03286bf8739517a92920970ec096d54051180fa11c71a341d3` |
| Seri utama (APK PT) | `bps/2026-10-17/sdg4_apk_pt.csv` | `0e473602a53a445081df3120a8686009a7eb05f2f6a340a1696de0c0764dd4a0` |
| Seri utama (APK jenjang) | `bps/2026-10-17/sdg4_apk.csv` | `872d257caeb3f6e918fd02ec9ec0755cf2a6c48fd95393b3a7469d3a0367885e` |
| Seri utama (HLS) | `bps/2026-10-17/sdg4_hls.csv` | `c279b020226df13b14362d2aea01c37035be96efbe97d3298842cfacc752f792` |
| Seri utama (RLS) | `bps/2026-10-17/sdg4_rls.csv` | `4684b19beaf1b9f8bf53c613f6557b26954042e13f548161e29d2541df05bbac` |
| Seri utama (4.3.1) | `bps/2026-10-17/sdg4_4_3_1_v2685.csv` | `5ffaca4b708b57f1af0659122da50f57b60db0ed470e8b9a20b3f11e43139463` |

Penerbit pembanding: **UNESCO Institute for Statistics (UIS)** lewat **World Bank WDI**; indikator
juga terdaftar pada sumber SDG (`sumber46`). Penerbit seri utama: **BPS (Susenas)**.

---

## 2. Metode

Skrip reprodusibel: **`scripts/profil_seri_pembanding.py`**

```bash
python scripts/profil_seri_pembanding.py
```

Skrip hanya membaca `data/raw/` (tidak mengubah berkas mentah), deterministik, lalu menulis dua
keluaran:

1. `docs/tabel_ketersediaan_seri_pembanding.csv` — ringkasan **seri × rincian** (rentang periode,
   daftar periode tersedia, periode hilang, satuan, tahun terbit, penanda sebanding + alasan).
2. `docs/ketersediaan_seri_periode_rincian.csv` — tabel **seri × periode × rincian** tingkat
   nasional (satu baris per seri × rincian × tahun, kolom `tersedia` 1/0).

---

## 3. Profil seri pembanding SE.TER.ENRR

| Seri | Nama | Rincian | Cakupan | Satuan | Periode | Jml | Periode hilang |
|---|---|---|---|---|---|---|---|
| `SE.TER.ENRR` | School enrollment, tertiary (% gross) | Total | Nasional (IDN) | persen (% gross) | 1970–2023 | 53 | 1971 |
| `SE.TER.ENRR.FE` | … female (% gross) | Perempuan | Nasional (IDN) | persen (% gross) | 1970–2023 | 34 | 1971, 1973–1975, 1977–1981, 1986–1992, 1994, 1997–1998, 2005 |
| `SE.TER.ENRR.MA` | … male (% gross) | Laki-laki | Nasional (IDN) | persen (% gross) | 1970–2023 | 34 | sama dengan FE |

**Temuan profil:**

- **Dimensi rincian yang tersedia hanya jenis kelamin** (total/perempuan/laki-laki). Tidak ada
  dimensi **daerah/provinsi** maupun **kelompok umur** — seluruh baris pada berkas mentah hanya
  untuk Indonesia nasional (`countryiso3code = IDN`).
- **Satuan:** kolom `unit` pada berkas mentah **kosong**; satuan dipastikan dari nama indikator
  (`% gross`). Nilai total 1970–2023 berkisar **2,30–44,88**.
- **Tahun terbit:** dipublikasi UIS/UNESCO **2026-02**; snapshot WDI diunduh **2026-10-20**
  (`lastupdated` basis data WDI 2026-10-08).
- **Kualitas data:** tidak ada **duplikasi** tahun untuk satu indikator; nilai kosong tersimpan
  sebagai `null` (bukan 0). Rincian total relatif lengkap (hanya 1 tahun hilang); rincian jenis
  kelamin baru lengkap tanpa putus **sejak 2006**.
- **Anomali metadata:** indikator muncul pada dua sumber WDI (`sumber2`, WDI) dan SDG
  (`sumber46`) dengan definisi identik; hal ini wajar dan bukan konflik nilai.

---

## 4. Perbandingan dengan seri utama

| Aspek | Seri pembanding `SE.TER.ENRR` | Seri utama terkait `var1443` (APK PT) |
|---|---|---|
| Konstruk | Gross Enrollment Ratio jenjang tersier | Angka Partisipasi Kasar Perguruan Tinggi |
| Kelompok umur | usia resmi jenjang tersier (19–23 tahun) | **19–23 tahun** (catatan BPS) |
| Satuan | persen (% gross) | persen |
| Cakupan | Nasional saja | Nasional (`wilayah_kode` 9999) + 38 provinsi |
| Periode | 1970–2023 | 2015–2025 |
| **Irisan periode** | **2015–2023 (9 tahun)** | idem |
| Tahun terbit | UIS 2026-02 / snapshot 2026-10-20 | 2025-12-12 |
| Dimensi rincian | jenis kelamin (total/FE/MA) | tidak ada |

**Catatan seri utama lain:**

- `var303` (APK menurut jenjang) **tidak memuat jenjang perguruan tinggi** — kategorinya hanya
  SD/SMP/SM — sehingga bukan pasangan `SE.TER.ENRR`.
- `var417` (Harapan Lama Sekolah) dan `var1429` (Rata-rata Lama Sekolah) bersatuan **tahun**;
  konstruknya lama sekolah, bukan rasio partisipasi tersier.
- `var2685` (4.3.1) mengukur **tingkat partisipasi** pada kelompok umur 15-24/25-54/55-64/15-64,
  bukan rasio enrollment, dan hanya 2022–2024.

**Potensi perbedaan definisi/metodologi:** sumber pembanding (UIS) memakai pembilang seluruh
mahasiswa lintas usia dibagi populasi usia resmi tersier (rasio *gross*, boleh >100%), sedangkan
APK BPS dihitung dari Susenas dengan kelompok umur 19–23 tahun. Keduanya secara konsep sebanding,
tetapi selisih angka antar-sumber wajar terjadi karena perbedaan **sumber data, waktu rilis, dan
definisi populasi**.

---

## 5. Kandidat rincian yang sebanding

| Kandidat | Seri | Rincian | Status | Alasan |
|---|---|---|---|---|
| 1 | `SE.TER.ENRR` ↔ `var1443` | Total ↔ Tidak ada | **YA** | Sama-sama GER tersier usia 19–23, satuan persen, tersedia di tingkat nasional. Dipakai pada irisan **2015–2023**. |
| 2 | `SE.TER.ENRR.FE` / `.MA` | Perempuan / Laki-laki | **TIDAK (bersyarat)** | Seri utama `var1443` tidak memiliki rincian jenis kelamin → tidak dapat dipasangkan; hanya konteks deskriptif. |
| 3 | Dimensi daerah/provinsi | — | **TIDAK** | WDI hanya menerbitkan agregat nasional; tidak ada pecahan provinsi. |
| 4 | Dimensi kelompok umur | — | **TIDAK** | Berkas mentah tidak memuat pemecahan umur untuk SE.TER.ENRR. |
| 5 | `var303`, `var417`, `var1429`, `var2685` | — | **TIDAK** | Konstruk, satuan, atau periode berbeda (lihat bagian 4). |

> Rekomendasi Tahap 6: gunakan pasangan **`SE.TER.ENRR` (nasional) ↔ `var1443` wilayah `9999`**
> pada **2015–2023**, dan sajikan selisih antar-sumber sebagai bagian rekonsiliasi (jangan dihapus).

---

## 6. Keluaran & reproduksi

- `scripts/profil_seri_pembanding.py` — skrip profiling.
- `docs/tabel_ketersediaan_seri_pembanding.csv` — tabel ketersediaan seri × rincian (15 baris).
- `docs/ketersediaan_seri_periode_rincian.csv` — tabel seri × periode × rincian (281 baris).
- Keputusan terkait dicatat di `log-keputusan.csv` (K-004, K-005).

---

## 7. Keterbatasan & yang perlu dikonfirmasi

- Seri pembanding **tidak punya dimensi provinsi**, sehingga rekonsiliasi dengan seri utama hanya
  mungkin pada tingkat **nasional**.
- Perbandingan gender tertunda sampai ada seri utama dengan rincian jenis kelamin.
- Perlu konfirmasi anggota **Integrasi/Penyimpanan (Tahap 6)** apakah `var1443` wilayah `9999`
  yang dipakai sebagai titik banding nasional, dan apakah perlu penyeragaman satuan/definisi.
