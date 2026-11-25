"""Tahap 1 — Ekstraksi: satu pintu untuk semua pembaca.

MANIFEST.csv adalah daftar pekerjaan. Setiap berkas dicocokkan dengan pola jalurnya (pola pertama
yang cocok menang, jadi pola yang lebih khusus ditulis lebih dulu). Di akhir, tidak boleh ada berkas
yang belum ditangani: berkas yang terlewat tidak menimbulkan galat, hanya diam-diam hilang dari Silver.
"""
from fnmatch import fnmatch

import pandas as pd

from src import konfigurasi as K
from src.common.manifest import baca as baca_manifest
from src.ekstraksi import bnpb, bps, ilostat, wdi, who_gho
from src.laporan import ROOT, catat, tabel_md, tulis


def _seri(sumber):
    return [kode for kode, s in K.SERI.items() if s["sumber"] == sumber]


# (pola jalur, nama pembaca, peran) — urutan penting
POLA = [
    ("bps/*/json/*.json", "bps_json", "data"),
    ("bps/*/manifest_asal.json", "bps_manifest_asal", "meta"),
    ("bps/*/*.csv", "bps_csv", "data"),
    ("wdi/*/data/*.json", "wdi_data", "data"),
    ("wdi/*/metadata/sumber.json", "wdi_sumber", "meta"),
    ("wdi/*/metadata/*_indikator.json", "wdi_meta", "meta"),
    ("who_gho/*/datadot/ddiindicators*.json", "who_ddi", "meta"),
    ("who_gho/*/datadot/*.csv", "who_csv", "data"),
    ("who_gho/*/odata/Indicator.json", "who_odata", "meta"),
    ("ilostat/*/data/*.csv", "ilo_csv", "data"),
    ("ilostat/*/dsd/*.json", "ilo_dsd", "meta"),
    ("ilostat/*/metadata/dataflow.json", "ilo_dataflow", "meta"),
    ("bnpb/*/ckan/*.json", "bnpb_ckan", "meta"),
    ("bnpb/*/datastore/*/*.json", "bnpb_sel", "data"),
    ("bnpb/*/tangan/*/*.xlsx", "bnpb_sel", "data"),
]


def jalankan():
    """Kembalikan {nama: DataFrame mentah} (WHO: {jalur: DataFrame}, karena kolomnya berbeda per berkas)."""
    kumpul = {nama: [] for _, nama, _ in POLA}
    bps.tak_terbaca.clear()
    who = {}
    hitung = []
    for berkas in baca_manifest():
        cocok = next(((nama, peran) for pola, nama, peran in POLA if fnmatch(berkas, pola)), None)
        if cocok is None:
            continue
        nama, peran = cocok
        catatan = ""
        if nama == "bps_json" and bps.statis(berkas):
            nama = "bps_statis_html"
            df, meta = bps.baca_json_statis(berkas)
            kumpul.setdefault("bps_statis_meta", []).append(meta)
            catatan = (f"tabel statis: HTML diratakan, {meta['blok'].iloc[0]} blok x {meta['tingkat_header'].iloc[0]} tingkat header"
                       + (f", {meta['sel_koma_desimal'].iloc[0]} sel berkoma desimal" if meta["sel_koma_desimal"].iloc[0] else ""))
            catat(**{f"koma_desimal_{berkas.split('/')[-1].split('.')[0]}": int(meta["sel_koma_desimal"].iloc[0])})
        elif nama == "bps_json":
            df, meta = bps.baca_json(berkas)
            kumpul["bps_meta"] = kumpul.get("bps_meta", []) + [meta]
            catatan = f"{meta['_halaman'].max()} halaman"
        elif nama == "bps_csv":
            df = bps.baca_csv(berkas)
            if "var_id" not in df.columns:
                nama, catatan = "bps_statis", "tabel statis (nama wilayah, tanpa var_id)"
        elif nama == "bps_manifest_asal":
            df = bps.baca_manifest_asal(berkas)
            catatan = "semua tabel unduhan BPS, bukan hanya kasus ini"
        elif nama == "wdi_data":
            df, total = wdi.baca_data(berkas, _seri("wdi"))
            catatan = f"{total:,} baris di berkas, {df['indicator_id'].nunique()} seri kasus disaring"
        elif nama == "wdi_sumber":
            df = wdi.baca_metadata(berkas)
        elif nama == "wdi_meta":
            df = wdi.baca_metadata(berkas, _seri("wdi"))
            catatan = "metadata seri kasus saja"
        elif nama == "who_csv":
            df = who_gho.baca_csv(berkas)
            who[berkas] = df
        elif nama == "who_ddi":
            df = who_gho.baca_metadata_ddi(berkas, _seri("who_gho"))
            catatan = "definisi lengkap seri kasus"
        elif nama == "ilo_csv":
            df = ilostat.baca_csv(berkas)
            catatan = f"dimensi: {', '.join(ilostat.dimensi(df)) or '(tanpa rincian)'}; FREQ {'/'.join(sorted(df['FREQ'].unique()))}"
        elif nama == "ilo_dsd":
            df = ilostat.baca_dsd(berkas)
        elif nama == "ilo_dataflow":
            df, total = ilostat.baca_dataflow(berkas, _seri("ilostat"))
            catatan = f"{total:,} dataflow ILOSTAT, {len(df)} seri kasus disaring"
        elif nama == "bnpb_ckan":
            df = bnpb.baca_ckan(berkas)
            catatan = f"{df['dataset'].nunique()} dataset, {len(df)} resource; judul resource = nama ukuran"
        elif nama == "bnpb_sel" and berkas.endswith(".json"):
            df, h = bnpb.baca_datastore(berkas)
            catatan = f"DataStore {h['record']} record; tata {h['tata']}/{h['tingkat']}; {h['kosong']} sel kosong"
        elif nama == "bnpb_sel":
            df, ket, h = bnpb.baca_xlsx(berkas)
            if len(ket):
                kumpul.setdefault("bnpb_keterangan", []).append(ket)
            catatan = (f"XLSX {h['lembar']} lembar data; tata {h['tata']}/{h['tingkat']}; {h['kosong']} sel kosong"
                       + (f"; lembar Keterangan {len(ket)} baris" if len(ket) else ""))
        elif nama == "who_odata":
            df = who_gho.baca_metadata_odata(berkas, _seri("who_gho"))
        kumpul.setdefault(nama, []).append(df)
        hitung.append({"berkas": berkas, "pembaca": nama, "peran": peran, "baris": len(df), "catatan": catatan})

    if bps.tak_terbaca:
        pd.DataFrame(bps.tak_terbaca).to_csv(ROOT / "reports" / "kunci-bps-tak-terbaca.csv", index=False)
    catat(kunci_bps_tak_terbaca=len(bps.tak_terbaca))
    semua = set(baca_manifest())
    tertangani = {h["berkas"] for h in hitung}
    sisa = sorted(semua - tertangani)
    assert not sisa, f"berkas di MANIFEST.csv belum punya pembaca: {sisa}"

    hasil = {nama: pd.concat(daftar, ignore_index=True) for nama, daftar in kumpul.items() if daftar}
    hasil["who_csv"] = who
    hasil["_hitung"] = pd.DataFrame(hitung)

    t = hasil["_hitung"]
    data = t[t["peran"] == "data"]
    catat(berkas_manifest=len(semua), berkas_dibaca=len(t), berkas_data=len(data), baris_mentah=int(data["baris"].sum()))
    tulis("ekstraksi.md", "\n\n".join([
        "# Ekstraksi: jumlah baris per berkas",
        "Dihasilkan `python pipeline.py`. Peran *data* berisi angka; *meta* berisi judul, definisi, atau catatan "
        "unduhan. Semua baris `data/raw/MANIFEST.csv` tertangani.",
        tabel_md(t),
        f"Jumlah: {len(t)} berkas dari {len(semua)} di MANIFEST, {int(data['baris'].sum()):,} baris mentah di berkas data.",
    ]))
    return hasil
