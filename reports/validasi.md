# Laporan Validasi Silver dan Gold

Validasi dilakukan menggunakan Pandera.

- **Struktur dan rentang nilai Silver: LULUS** — Lolos
- **Keunikan kunci dan kelengkapan panel Gold: LULUS** — Lolos
- **Keunikan dan rentang detail Gold: LULUS** — Lolos
- **Konsistensi catatan anomali: LULUS** — Lolos

## Ringkasan jumlah data

- Baris Silver: 4216
- Baris panel provinsi-tahun: 608
- Baris detail indikator: 1444
- Baris anomali: 140
- Jumlah provinsi panel: 38
- Rentang tahun panel: 2010–2025

## Catatan

- Silver dapat menyimpan beberapa observasi untuk satu sel.
- Gold harus memiliki kunci unik sesuai bentuk tabelnya.
- Nilai kosong tidak diimputasi menjadi nol.
- Penanda outlier dipertahankan.
- Audit snapshot kosong berarti tidak ada baris snapshot yang dieliminasi.
