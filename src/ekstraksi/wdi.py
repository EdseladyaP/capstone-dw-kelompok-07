"""Pembaca WDI (World Bank API v2): berkas data berisi banyak indikator, dan metadata indikator.

Respons WDI adalah daftar dua unsur: [keterangan halaman, daftar baris]. Seri kasus disaring dengan
pencocokan kode persis (bukan awalan), karena di berkas yang sama ada kode yang bertetangga,
misalnya rincian per jenis kelamin. Nilai null dibawa apa adanya; dibuang saat menyusun Silver.
"""
import json

import pandas as pd

from src.common.manifest import RAW, sha256_raw


def _halaman(jalur):
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    if not (isinstance(isi, list) and len(isi) == 2 and isinstance(isi[0], dict)):
        raise ValueError(f"{jalur}: bukan respons WDI [keterangan, baris]")
    ket = isi[0]
    if int(ket.get("pages", 1)) != 1:
        raise ValueError(f"{jalur}: respons {ket['pages']} halaman; paket ini mengharapkan satu halaman per berkas")
    return ket, isi[1] or []


def baca_data(jalur, seri):
    """Baris data untuk kode di `seri`. Mengembalikan (DataFrame, jumlah baris di berkas sebelum disaring)."""
    ket, baris = _halaman(jalur)
    pilih = [b for b in baris if b["indicator"]["id"] in set(seri)]
    df = pd.DataFrame([{"indicator_id": b["indicator"]["id"], "indicator_nama": b["indicator"]["value"],
                        "country_id": b["country"]["id"], "countryiso3code": b.get("countryiso3code"),
                        "date": b["date"], "value": b["value"], "unit": b.get("unit"),
                        "obs_status": b.get("obs_status"), "decimal": b.get("decimal")} for b in pilih])
    df["_lastupdated"] = ket.get("lastupdated")
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df, len(baris)


def baca_metadata(jalur, seri=None):
    """Metadata indikator (metadata/sumberN_indikator.json) atau daftar sumber (metadata/sumber.json)."""
    _, baris = _halaman(jalur)
    if seri is not None:
        baris = [b for b in baris if b.get("id") in set(seri)]
    df = pd.DataFrame([{k: (v.get("value") if isinstance(v, dict) else
                            (json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v))
                        for k, v in b.items()} for b in baris])
    df["_berkas_raw"] = jalur
    return df
