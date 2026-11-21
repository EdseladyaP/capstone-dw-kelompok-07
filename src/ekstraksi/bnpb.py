"""Pembaca BNPB: katalog CKAN, DataStore CKAN (JSON per resource), dan XLSX unduhan tangan.

Satu resource BNPB = satu tabel dengan tata letaknya sendiri. Semua tabel diubah ke satu bentuk panjang
"satu sel = satu baris" tanpa menafsirkan ukurannya (itu tugas src/silver/bangun.py):

- jenis:  satu ukuran per resource (dari judul resource), kolom per jenis bencana, baris per provinsi atau
          kabupaten/kota plus baris INDONESIA;
- tahun:  satu ukuran per resource, kolom per tahun ('2010.0' ...), baris per provinsi, kabupaten/kota,
          atau jenis bencana (tabel nasional);
- rekap:  rekap 2021/2022 (XLSX), baris per (provinsi[, kabupaten/kota], jenis bencana), banyak ukuran;
          kepala dua tingkat ('Korban' > 'Meninggal') dan satu baris satuan '(jiwa)';
- rekap_nasional: rekap 2025, baris per jenis bencana plus 'Total';
- nilai:  nilai kerusakan dan kerugian per kabupaten (usulan rehabilitasi-rekonstruksi), tahun dari
          kolom 'Tahun Kejadian'.
Lembar 'Keterangan' (definisi istilah) dibaca sebagai metadata.

Sel XLSX yang digabung (merged) diisi ulang dari sel kiri atasnya, karena openpyxl hanya memberi nilai di
sel itu; sel Provinsi rekap tergabung beberapa baris ke bawah. Sel kosong tidak menjadi baris (dihitung).
"""
import json
import re
from functools import lru_cache
from pathlib import PurePosixPath

import pandas as pd

from src.common.manifest import RAW, sha256_raw
from src.kamus_bnpb import KOLOM_JENIS

POLA_TAHUN = re.compile(r"^((?:19|20)\d\d)(?:\.0)?$")
PROV_KODE = "Kode Wilayah Provinsi"
PROV_NAMA = ("Nama Provinsi", "Provinsi")
KAB_KODE = "Kode Wilayah Kabupaten / Kota"
KAB_NAMA = ("Nama Kabupaten/Kota", "Kabupaten/Kota", "Kabupaten")
JENIS = ("Jenis Bencana", "JENIS BENCANA")
PENGENAL = {"No", "No.", "Latitude", "Longitude", PROV_KODE, KAB_KODE, *PROV_NAMA, *KAB_NAMA, *JENIS,
            "Kode Bencana", "Tahun Proposal", "Tahun Kejadian", "Waktu Kejadian"}
KOLOM = ["_berkas_raw", "_sha256_raw", "resource_id", "resource_nama", "lembar", "tata", "tingkat_tabel", "baris",
         "kode_wilayah", "nama_wilayah", "provinsi", "jenis_baris", "periode_teks", "kolom", "nilai_teks"]


@lru_cache(maxsize=None)
def katalog():
    """{resource_id: {dataset, nama, format, url}} dari semua berkas bnpb/*/ckan/*.json."""
    hasil = {}
    for f in sorted(RAW.glob("bnpb/*/ckan/*.json")):
        for p in json.loads(f.read_text(encoding="utf-8"))["result"]["results"]:
            for r in p.get("resources", []):
                hasil[r["id"]] = {"dataset": p["name"], "nama": (r.get("name") or "").strip(),
                                  "format": r.get("format") or "", "url": r.get("url") or ""}
    return hasil


def baca_ckan(jalur):
    """Daftar resource di katalog (metadata): satu baris per resource."""
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))["result"]["results"]
    return pd.DataFrame([{"dataset": p["name"], "resource_id": r["id"], "nama": (r.get("name") or "").strip(),
                          "format": r.get("format") or "", "datastore_aktif": bool(r.get("datastore_active")),
                          "_berkas_raw": jalur} for p in isi for r in p.get("resources", [])])


def teks(v):
    """Nilai sel apa adanya sebagai teks: 5 -> '5', 11.000000000000002 -> '11.000000000000002', None -> ''."""
    if v is None:
        return ""
    if isinstance(v, float):
        return repr(v)
    return str(v).strip()


def kode_teks(v):
    """Kode wilayah dari sel (11, 11.0, '1101.0') -> '11' / '1101'; kosong -> ''."""
    t = teks(v)
    return t[:-2] if t.endswith(".0") else t


def tahun_dari_nama(nama):
    th = set(re.findall(r"(?<!\d)((?:19|20)\d\d)(?!\d)", nama or ""))
    return th.pop() if len(th) == 1 else ""


def tata_letak(label):
    L = set(label)
    if "Tahun Kejadian" in L:
        tata = "nilai"
    elif "Kode Bencana" in L:
        tata = "rekap_nasional"
    elif "Jumlah Kejadian" in L and L & set(JENIS):
        tata = "rekap"
    elif any(POLA_TAHUN.match(c) for c in L):
        tata = "tahun"
    elif L & set(KOLOM_JENIS):
        tata = "jenis"
    else:
        raise ValueError(f"tata letak BNPB tidak dikenali dari kepala kolom {sorted(L)}")
    if tata == "nilai" or KAB_KODE in L or L & {"Nama Kabupaten/Kota", "Kabupaten/Kota"}:
        tingkat = "kabkota"
    elif PROV_KODE in L or L & set(PROV_NAMA):
        tingkat = "provinsi"
    else:
        tingkat = "nasional"
    return tata, tingkat


def sel(label, baris, nomor, info):
    """Tabel (kepala, baris) -> DataFrame sel. `info`: berkas, resource, lembar. Kembalikan (sel, keterangan hitung)."""
    tata, tingkat = tata_letak(label)
    idx = {c: i for i, c in enumerate(label)}
    ambil = lambda r, nama: r[idx[nama]] if nama in idx else None  # noqa: E731
    ukuran = [c for c in label if c not in PENGENAL and not c.startswith("kolom_")]
    kolom_jenis = next((c for c in JENIS if c in idx), None)
    nama_prov = next((c for c in PROV_NAMA if c in idx), None)
    nama_kab = next((c for c in KAB_NAMA if c in idx), None)
    periode_resource = tahun_dari_nama(info["resource_nama"]) or tahun_dari_nama(PurePosixPath(info["berkas"]).name)
    keluar, kosong, isi_bawah = [], 0, 0
    terakhir = {"prov": "", "kab": ""}
    for r, no in zip(baris, nomor):
        if all(teks(v) == "" for v in r):
            continue
        prov = teks(ambil(r, nama_prov)) if nama_prov else ""
        kab = teks(ambil(r, nama_kab)) if nama_kab else ""
        if tata == "rekap":
            if not teks(ambil(r, kolom_jenis)) and all(teks(ambil(r, c)) == "" for c in ukuran):
                continue                       # sisa kepala
            if not prov and terakhir["prov"]:   # sel tergabung yang tidak tercatat sebagai merged
                prov, isi_bawah = terakhir["prov"], isi_bawah + 1
            if nama_kab and nama_kab != nama_prov and not kab and terakhir["kab"]:
                kab, isi_bawah = terakhir["kab"], isi_bawah + 1
            terakhir = {"prov": prov, "kab": kab}
        if tingkat == "kabkota":
            kode, nama = kode_teks(ambil(r, KAB_KODE)), kab
            if nama.upper() == "INDONESIA":
                tingkat_baris = "indonesia"
            else:
                tingkat_baris = "kabkota"
        elif tingkat == "provinsi":
            kode, nama = kode_teks(ambil(r, PROV_KODE)), prov
            tingkat_baris = "indonesia" if nama.upper() == "INDONESIA" and not kode else "provinsi"
            prov = ""
        else:
            kode, nama, tingkat_baris, prov = "", "INDONESIA", "indonesia", ""
        jenis = teks(ambil(r, kolom_jenis)) if kolom_jenis else ""
        for c in ukuran:
            v = teks(r[idx[c]])
            if v == "":
                kosong += 1
                continue
            m = POLA_TAHUN.match(c)
            per = m.group(1) if m else (teks(ambil(r, "Tahun Kejadian")) if tata == "nilai" else periode_resource)
            keluar.append([info["berkas"], info["sha"], info["resource_id"], info["resource_nama"], info["lembar"], tata,
                           tingkat_baris if tingkat_baris != "kabkota" else "kabkota", no, kode, nama,
                           prov if tingkat_baris == "kabkota" else "", jenis, per, c, v])
    df = pd.DataFrame(keluar, columns=KOLOM)
    return df, {"tata": tata, "tingkat": tingkat, "kosong": kosong, "isi_ke_bawah": isi_bawah}


def baca_datastore(jalur):
    """JSON DataStore {'resource_id', 'halaman': [{'result': {'records': [...]}}]} -> (sel, ringkasan)."""
    j = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    rec = [r for h in j["halaman"] for r in h["result"]["records"]]
    label = [k for k in rec[0] if k != "_id"] if rec else []
    res = katalog().get(j["resource_id"], {})
    info = {"berkas": jalur, "sha": sha256_raw(jalur), "resource_id": j["resource_id"],
            "resource_nama": res.get("nama", ""), "lembar": ""}
    df, hit = sel(label, [[r.get(k) for k in label] for r in rec], [r.get("_id", i + 1) for i, r in enumerate(rec)], info)
    hit["record"] = len(rec)
    return df, hit


def _isi_merged(ws, grid):
    for rng in ws.merged_cells.ranges:
        v = grid[rng.min_row - 1][rng.min_col - 1]
        for i in range(rng.min_row - 1, rng.max_row):
            for k in range(rng.min_col - 1, rng.max_col):
                if i < len(grid) and k < len(grid[i]):
                    grid[i][k] = v


def _kepala(grid):
    """(indeks baris pertama data, label). Kepala = baris pertama dengan >= 2 sel teks; baris berikutnya yang
    semuanya teks menjadi sub-kepala (label = sub bila ada, kalau tidak kepala atas); baris satuan '(jiwa)' dilewati."""
    angka = lambda r: any(isinstance(v, (int, float)) for v in r)  # noqa: E731
    jml_teks = lambda r: sum(isinstance(v, str) and v.strip() != "" for v in r)  # noqa: E731
    i = next(i for i, r in enumerate(grid) if jml_teks(r) >= 2)
    atas = grid[i]
    sub = grid[i + 1] if i + 1 < len(grid) and jml_teks(grid[i + 1]) >= 2 and not angka(grid[i + 1]) else None
    mulai = i + (2 if sub else 1)

    def satuan(r):   # baris satuan: semua sel terisi berbentuk '(jiwa)' atau sama dengan kepala kolomnya (sel tergabung)
        terisi = [(k, v) for k, v in enumerate(r) if v not in (None, "")]
        return terisi and any(re.fullmatch(r"\(.*\)", str(v).strip()) for _, v in terisi) and all(
            re.fullmatch(r"\(.*\)", str(v).strip()) or v == atas[k] or (sub and v == sub[k]) for k, v in terisi)
    while mulai < len(grid) and satuan(grid[mulai]):
        mulai += 1
    label, dipakai = [], set()
    for k, v in enumerate(atas):
        s = sub[k] if sub and k < len(sub) and str(sub[k] or "").strip() and sub[k] != v else v
        lab = re.sub(r"\s+", " ", str(s)).strip() if s not in (None, "") else f"kolom_{k}"
        while lab in dipakai:
            lab += "_"
        dipakai.add(lab)
        label.append(lab)
    return mulai, label


def baca_xlsx(jalur):
    """XLSX unduhan tangan -> (sel, keterangan, ringkasan). Nama berkas = '<resource_id>-<judul>.xlsx'."""
    import openpyxl
    nama = PurePosixPath(jalur).name
    rid = nama[:36]
    res = katalog().get(rid, {})
    wb = openpyxl.load_workbook(RAW / jalur, data_only=True)
    potong, ket, hit = [], [], {"lembar": 0, "kosong": 0, "isi_ke_bawah": 0, "tata": "", "tingkat": ""}
    for ws in wb.worksheets:
        grid = [list(r) for r in ws.iter_rows(values_only=True)]
        _isi_merged(ws, grid)
        if ws.title.strip().lower() == "keterangan" or any(len(r) > 1 and r[1] == ":" for r in grid):
            istilah = ""
            for r in grid:
                if len(r) > 2 and r[2] not in (None, ""):
                    istilah = teks(r[0]) or istilah
                    ket.append({"lembar": ws.title, "istilah": istilah, "keterangan": teks(r[2]), "_berkas_raw": jalur})
            continue
        mulai, label = _kepala(grid)
        lebar = len(label)
        baris = [(r + [None] * lebar)[:lebar] for r in grid[mulai:]]
        info = {"berkas": jalur, "sha": sha256_raw(jalur), "resource_id": rid,
                "resource_nama": res.get("nama", "") or nama[37:], "lembar": ws.title}
        df, h = sel(label, baris, list(range(mulai + 1, mulai + 1 + len(baris))), info)
        potong.append(df)
        hit = {"lembar": hit["lembar"] + 1, "kosong": hit["kosong"] + h["kosong"],
               "isi_ke_bawah": hit["isi_ke_bawah"] + h["isi_ke_bawah"], "tata": h["tata"], "tingkat": h["tingkat"]}
    wb.close()
    return pd.concat(potong, ignore_index=True), pd.DataFrame(ket), hit
