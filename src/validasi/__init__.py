"""Tahap 8 — Validasi dan dokumentasi. Dijalankan dari `python pipeline.py` setiap kali.

Aturan keras (umum di aturan.py, khas kasus di khusus.py) menghentikan pipeline bila gagal. Aturan
peringatan hanya dilaporkan. Hasilnya di reports/validasi.md; data dictionary ditulis ulang dari data.
Di akhir, angka semua komponen ditulis ke results/kunci/metrics.json.
"""
import pandera.pandas as pa

from src.common.hasil import tulis_hasil
from src.dokumen import tulis_data_dictionary
from src.laporan import angka, catat, simpan_angka, tabel_md, tulis
from src.validasi import aturan, khusus

import pandas as pd


def jalankan(silver, gold):
    gagal_umum = pd.DataFrame()
    try:
        aturan.skema().validate(silver, lazy=True)
    except pa.errors.SchemaErrors as e:
        gagal_umum = e.failure_cases[["column", "check", "failure_case", "index"]]
    hasil = [{"aturan": nama, "jenis": "keras (umum)", "keterangan": ket,
              "hasil": "GAGAL" if aturan.kena(nama, gagal_umum) else "LOLOS"} for nama, ket in aturan.DAFTAR]
    rinci_khusus = []
    for nama, ket, keras, fungsi in khusus.ATURAN:
        buruk = fungsi(silver)
        hasil.append({"aturan": nama, "jenis": "keras (kasus)" if keras else "peringatan (kasus)", "keterangan": ket,
                      "hasil": "LOLOS" if buruk.empty else ("GAGAL" if keras else f"PERINGATAN ({len(buruk)} baris)")})
        if not buruk.empty:
            rinci_khusus.append(f"### {nama}\n\n" + tabel_md(buruk.head(30)))
    tabel = pd.DataFrame(hasil)
    keras_gagal = tabel[tabel["hasil"] == "GAGAL"]
    catat(aturan_validasi=len(tabel), aturan_lolos=int((tabel["hasil"] == "LOLOS").sum()),
          aturan_peringatan=int(tabel["hasil"].str.startswith("PERINGATAN").sum()),
          aturan_umum=len(aturan.DAFTAR), aturan_khas=sum(1 for a in khusus.ATURAN if a[2]),
          aturan_khas_peringatan=sum(1 for a in khusus.ATURAN if not a[2]))
    tulis("validasi.md", "\n\n".join([
        "# Hasil validasi Silver",
        "Dihasilkan `python pipeline.py` (`src/validasi/`). Aturan keras menghentikan pipeline bila gagal; "
        "peringatan dilaporkan untuk diperiksa manusia. Aturan juga diuji dengan baris yang sengaja dirusak "
        "(`pytest`, berkas `tests/test_validasi.py`).",
        tabel_md(tabel),
        "## Kegagalan aturan umum", tabel_md(gagal_umum.head(50)) if len(gagal_umum) else "Tidak ada.",
        "## Baris yang memicu aturan kasus", "\n\n".join(rinci_khusus) or "Tidak ada.",
    ]))
    tulis_data_dictionary(silver)
    simpan_angka()
    a = angka()
    metrik = {k: v for k, v in a.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    tulis_hasil("kunci", metrik)
    if len(keras_gagal):
        raise SystemExit(f"Validasi gagal: {', '.join(keras_gagal['aturan'])}. Lihat reports/validasi.md")
    return tabel
