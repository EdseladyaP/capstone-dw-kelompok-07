# Bukti eksekusi pipeline dan artefak metrik validasi

Dokumen ini merekam eksekusi `python pipeline.py` terhadap Silver pertama serta artefak
`results/124450043/metrics.json` yang dipakai untuk kartu Papan Tim
**“Validasi tidak menunggu Sprint 3”**.

| Keterangan | Nilai |
|---|---|
| NIM | 124450043 |
| Komponen | Validasi dan Dokumentasi |
| Commit yang diuji | `f26a951d15c6834b2b695cbf0afb81143480e2a4` (`f26a951`) |
| Lingkungan | Windows AMD64, Python 3.15.2, `.venv` repo |
| Perintah | `python pipeline.py` |
| Status keluar | `0` (berhasil) |

## 1. Log eksekusi

Dijalankan dari akar repo `capstone-data-wrangling` memakai `.venv\Scripts\python.exe`:

```text
data/raw: 15 berkas cocok dengan MANIFEST.csv
ekstraksi  selesai dalam 0.6 s
           Silver: 4,216 baris -> data\silver\silver.parquet
silver     selesai dalam 10.5 s
gold       selesai dalam 0.3 s
validasi   selesai dalam 0.2 s
Periksa skema minimal: python -m src.common.skema data/silver/silver.parquet
```

Pipeline berhenti dengan kode `0`; tidak ada aturan keras yang gagal. Angka `baris_silver`
pada log (4.216) sama dengan `baris_silver` di metrik.

## 2. Hasil validasi Silver

Ringkasan dari `reports/validasi.md` (dihasilkan ulang oleh pipeline):

| aturan | jenis | hasil |
|---|---|---|
| kolom dan tipe | keras (umum) | LOLOS |
| rincian_dari_kamus | keras (umum) | LOLOS |
| satu_satuan_per_seri | keras (umum) | LOLOS |
| nilai_dalam_rentang_satuan | keras (umum) | LOLOS |
| batas_bawah_le_nilai_le_batas_atas | keras (umum) | LOLOS |
| kunci unik | keras (umum) | LOLOS |
| wilayah dan periode | keras (umum) | LOLOS |
| lama_sekolah_masuk_akal | keras (kasus) | LOLOS |
| var303_tanpa_perguruan_tinggi | keras (kasus) | LOLOS |
| umur_var2685_tidak_dijumlah | keras (kasus) | LOLOS |
| provinsi_saja | keras (kasus) | LOLOS |
| rls_di_bawah_hls | peringatan (kasus) | LOLOS |

Total: **12 aturan, 12 lolos, 0 peringatan** (7 aturan umum + 4 aturan khas + 1 aturan
peringatan khas).

## 3. Metrik yang dikirim

`results/124450043/metrics.json`:

```json
{
  "metrik": {
    "aturan_validasi": 12,
    "aturan_lolos": 12,
    "aturan_peringatan": 0,
    "aturan_umum": 7,
    "aturan_khas": 4,
    "baris_silver": 4216
  },
  "seed": 0,
  "data_hash": "47a36c7c376bfc28458f66b5b1370271ed253205e4c57fd7c1c748c4849a438e",
  "perangkat": "Windows AMD64 Python 3.15.2"
}
```

## 4. Bukti berkas sudah di-commit

```text
HEAD                                    f26a951d15c6834b2b695cbf0afb81143480e2a4
sha256 results/124450043/metrics.json   269eba5cedb66434b4a1ab781878abc8fd95cabf0147df6ee6bf0b576a80e469
sha256 blob di HEAD                     269eba5cedb66434b4a1ab781878abc8fd95cabf0147df6ee6bf0b576a80e469
git status --short (berkas ini)         (kosong)
```

## 5. Pemeriksaan artefak `capstone.artifact`

Pemeriksaan yang sama dengan yang dijalankan Papan Tim (membaca berkas, memeriksa skema,
dan memastikan isinya identik dengan HEAD):

```json
{
  "path": "results/124450043/metrics.json",
  "exists": true,
  "sizeBytes": 312,
  "sha256": "269eba5cedb66434b4a1ab781878abc8fd95cabf0147df6ee6bf0b576a80e469",
  "valid": true,
  "committed": true,
  "headSha": "f26a951d15c6834b2b695cbf0afb81143480e2a4",
  "problems": [],
  "summary": {
    "metrik": [
      "aturan_khas",
      "aturan_lolos",
      "aturan_peringatan",
      "aturan_umum",
      "aturan_validasi",
      "baris_silver"
    ],
    "seed": 0,
    "dataHash": "47a36c7c376bfc28458f66b5b1370271ed253205e4c57fd7c1c748c4849a438e",
    "durasiDetik": null
  }
}
```

## 6. Pengiriman dari Papan Tim

Endpoint capstone sengaja tidak tersedia dari aplikasi/CLI
(`GET /api/me/capstone` → `403 di_luar_cakupan_aplikasi`, “Buka di Workbench web”).
Karena itu tombol **Kirim** harus ditekan di Workbench web, lalu resi/tangkapan layarnya
disimpan di repo ini.

Ringkasan siap tempel di kartu Papan Tim:

```text
aturan_validasi=12
aturan_lolos=12
aturan_peringatan=0
aturan_umum=7
aturan_khas=4
baris_silver=4216
seed=0
data_hash=47a36c7c376bfc28458f66b5b1370271ed253205e4c57fd7c1c748c4849a438e
commit=f26a951
```

Setelah pengiriman, isi bukti berikut:

| Bukti | Isi |
|---|---|
| Waktu kirim (WIB) | _belum diisi_ |
| Nama kartu / ID | Validasi tidak menunggu Sprint 3 |
| Resi / ID pengiriman | _belum diisi_ |
| Tangkapan layar | `reports/bukti-papan-tim.png` (simpan berkasnya di sini) |
