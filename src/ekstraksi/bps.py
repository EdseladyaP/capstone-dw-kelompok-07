"""Pembaca BPS: JSON WebAPI (respons asli, berhalaman) dan CSV hasil ratakan.

Pembaca tidak membersihkan apa pun. Keluarannya tabel panjang yang setia pada berkas, ditambah
_berkas_raw dan _sha256_raw. Metadata seri (judul, satuan, catatan) dibaca ke tabel terpisah.
"""
import html
import json
import re
from html.parser import HTMLParser

import pandas as pd

from src.common.manifest import RAW, sha256_raw


def _kamus(daftar):
    """[{'val': 1100, 'label': 'ACEH'}, ...] -> {'1100': 'ACEH'} dengan kode sebagai teks."""
    return {str(x["val"]): x["label"] for x in daftar}


def potong_kunci(kunci, kode_var, wilayah, rincian, tahun, periode):
    """Potong kunci datacontent = wilayah + var + turvar + tahun + turtahun (bersambung tanpa pemisah).

    Panjang setiap potongan diambil dari panjang kode di daftar labelnya, bukan dihafal. Satu daftar bisa
    berisi kode dengan panjang berbeda (misalnya kode tahun 93–99 dua digit dan 100 ke atas tiga digit),
    jadi semua kombinasi panjang dicoba dan hanya potongan yang semua bagiannya ada di daftar yang diterima.
    Lebih dari satu potongan yang sah: pembaca berhenti (ambigu). Tidak ada potongan yang sah: None, dan
    kunci itu dilaporkan oleh baca_json (bukan diam-diam dibuang).
    """
    pjg = lambda kamus: sorted({len(k) for k in kamus})  # noqa: E731
    sah = []
    for lw in pjg(wilayah):
        for lr in pjg(rincian):
            for lp in pjg(periode):
                lt = len(kunci) - lw - len(kode_var) - lr - lp
                if lt not in pjg(tahun):
                    continue
                i = 0
                k_wil = kunci[i:i + lw]; i += lw
                k_var = kunci[i:i + len(kode_var)]; i += len(kode_var)
                k_rin = kunci[i:i + lr]; i += lr
                k_th = kunci[i:i + lt]; i += lt
                k_per = kunci[i:]
                if k_var == kode_var and k_wil in wilayah and k_rin in rincian and k_th in tahun and k_per in periode:
                    sah.append((k_wil, k_rin, k_th, k_per))
    if len(sah) > 1:
        raise ValueError(f"kunci {kunci}: {len(sah)} cara memotong yang sah (seharusnya tepat satu)")
    return sah[0] if sah else None


tak_terbaca = []      # kunci datacontent yang tidak cocok dengan daftar label (dilaporkan di reports/)


def baca_json(jalur):
    """Baca satu JSON WebAPI BPS. Mengembalikan (data_panjang, metadata_seri)."""
    halaman_semua = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    baris, meta = [], []
    for no_hal, hal in enumerate(halaman_semua, start=1):
        var = hal["var"][0]
        wilayah = _kamus(hal["vervar"])
        rincian = _kamus(hal["turvar"])
        tahun = _kamus(hal["tahun"])
        periode = _kamus(hal["turtahun"])
        kode_var = str(var["val"])
        for kunci, nilai in hal["datacontent"].items():
            potong = potong_kunci(kunci, kode_var, wilayah, rincian, tahun, periode)
            if potong is None:
                tak_terbaca.append({"_berkas_raw": jalur, "halaman": no_hal, "kunci": kunci, "nilai": nilai})
                continue
            k_wil, k_rin, k_th, k_per = potong
            baris.append({"var_id": kode_var, "wilayah_id": k_wil, "wilayah": wilayah[k_wil],
                          "turvar_id": k_rin, "turvar": rincian[k_rin], "tahun_id": k_th, "tahun": tahun[k_th],
                          "turtahun_id": k_per, "turtahun": periode[k_per], "nilai": nilai, "_halaman": no_hal})
        meta.append({"var_id": kode_var, "judul": var["label"], "satuan": var.get("unit", ""),
                     "catatan": var.get("note", ""), "definisi": var.get("def", ""), "desimal": var.get("decimal"),
                     "last_update": hal.get("last_update"), "tahun_terbit": ",".join(tahun.values()),
                     "_halaman": no_hal})
    df = pd.DataFrame(baris)
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    m = pd.DataFrame(meta)
    m["_berkas_raw"] = jalur
    return df, m


def statis(jalur):
    """True bila JSON adalah tabel statis (kunci 'data' berisi tabel HTML), bukan respons tabel dinamis."""
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    return isinstance(isi, dict) and isinstance(isi.get("data"), dict) and "table" in isi["data"]


class _PembacaTabel(HTMLParser):
    """Kumpulkan sel <tr>/<td> beserta colspan dan rowspan (pustaka standar, tanpa lxml)."""

    def __init__(self):
        super().__init__()
        self.baris, self.sel = [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.baris.append([])
        elif tag in ("td", "th") and self.baris:
            self.sel = {"teks": "", "colspan": int(a.get("colspan") or 1), "rowspan": int(a.get("rowspan") or 1)}

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.sel is not None:
            self.baris[-1].append(self.sel)
            self.sel = None

    def handle_data(self, data):
        if self.sel is not None:
            self.sel["teks"] += data


def grid_html(teks):
    """Tabel HTML -> daftar baris berisi teks sel, dengan colspan/rowspan diratakan ke setiap kolom."""
    p = _PembacaTabel()
    p.feed(html.unescape(teks))
    hasil, tunda = [], {}
    for sel_baris in p.baris:
        baris, kol, i = [], 0, 0
        while i < len(sel_baris) or kol in tunda:
            if kol in tunda:
                isi, sisa = tunda.pop(kol)
                baris.append(isi)
                if sisa > 1:
                    tunda[kol] = (isi, sisa - 1)
                kol += 1
                continue
            s = sel_baris[i]
            i += 1
            isi = re.sub(r"\s+", " ", s["teks"].replace("\xa0", " ")).strip()
            for _ in range(s["colspan"]):
                baris.append(isi)
                if s["rowspan"] > 1:
                    tunda[kol] = (isi, s["rowspan"] - 1)
                kol += 1
        hasil.append(baris)
    return hasil


def angka_html(teks):
    """'3 156.7' -> 3156.7; '1,234.5' -> 1234.5; '77,94' -> 77.94; '-' atau kosong -> None.

    Ribuan di tabel statis BPS dipisah spasi, jadi koma tanpa titik dibaca sebagai koma desimal
    (satu tabel bisa mencampur titik dan koma desimal antarkolom)."""
    t = str(teks).replace(" ", "")
    if "," in t and "." in t:
        t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def baca_json_statis(jalur):
    """Tabel statis: JSON berisi tabel HTML Excel yang di-escape. Diratakan menjadi tabel panjang:
    satu baris per (wilayah, kolom), kolom h1..hN = isi baris header bertingkat di atas kolom itu.
    Baris data = baris yang sel namanya dikenali sebagai wilayah; baris judul, nomor kolom (1), (2), ...,
    catatan, dan sumber dilewati. Tabel yang terdiri atas beberapa blok bertumpuk (header berulang) dibaca
    blok demi blok. Nilai '-' dibawa sebagai teks (artinya ditentukan saat menyusun Silver)."""
    from src import wilayah as W
    d = json.loads((RAW / jalur).read_text(encoding="utf-8"))["data"]
    g = grid_html(d["table"])

    def kode(teks):
        try:
            return W.dari_nama(teks)
        except KeyError:
            return None
    data = {}
    for i, r in enumerate(g):
        for j, c in enumerate(r[:3]):
            if c and kode(c) is not None:
                data[i] = (j, kode(c))      # sel nama pertama di baris (nama bisa melebar beberapa kolom)
                break
    if not data:
        raise ValueError(f"{jalur}: tidak ada baris wilayah yang dikenali")
    # kolom nama = posisi yang paling sering memuat nama wilayah (baris Indonesia bisa melebar ke kolom nomor)
    posisi = [j for j, _ in data.values()]
    kol_nama = max(set(posisi), key=posisi.count)
    data = {i: (kol_nama, kode(g[i][kol_nama])) for i in data if kol_nama < len(g[i]) and kode(g[i][kol_nama]) is not None}

    def baris_header(r):
        return (len({c for c in r if c}) > 1 and any(c for c in r[kol_nama + 1:])
                and not re.fullmatch(r"\(\d+\)", r[-1] or ""))
    # tabel bisa berisi beberapa blok bertumpuk, masing-masing dengan baris header sendiri:
    # header aktif diganti setiap kali baris header muncul lagi sesudah baris data
    baris, header, sesudah_data, blok = [], [], False, 0
    for i, r in enumerate(g):
        if i in data and data[i][0] == kol_nama:
            sesudah_data = True
            for c in range(kol_nama + 1, len(r)):
                if not r[c]:
                    continue
                judul = [h[c] if c < len(h) else "" for h in header]
                if not judul or any(x == "" for x in judul):
                    continue
                baris.append({"wilayah": r[kol_nama], "wilayah_kode": data[i][1], "blok": blok,
                              **{f"h{n + 1}": x for n, x in enumerate(judul)},
                              "nilai_teks": r[c], "nilai": angka_html(r[c])})
        elif i not in data and baris_header(r):
            if sesudah_data:
                header, sesudah_data, blok = [], False, blok + 1
            header.append(r)
    df = pd.DataFrame(baris)
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    meta = pd.DataFrame([{k: d.get(k) for k in ("table_id", "title", "subcsa", "cr_date", "updt_date", "size")}])
    meta["_berkas_raw"] = jalur
    meta["tingkat_header"] = len(header)
    meta["sel_koma_desimal"] = int(df["nilai_teks"].str.fullmatch(r"-?[\d ]+,\d+").sum()) if len(df) else 0
    meta["blok"] = blok + 1
    return df, meta


def baca_csv(jalur):
    """Baca satu CSV BPS apa adanya (semua kolom sebagai teks)."""
    df = pd.read_csv(RAW / jalur, dtype=str, keep_default_na=False, encoding="utf-8")
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df


def baca_manifest_asal(jalur):
    """manifest_asal.json: catatan unduhan BPS untuk semua tabel (bukan hanya tabel kasus ini)."""
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    baris = [{"tabel": nama, **{k: (",".join(map(str, v)) if isinstance(v, list) else v) for k, v in t.items()}}
             for nama, t in isi["tabel"].items()]
    df = pd.DataFrame(baris)
    df["_berkas_raw"] = jalur
    return df
