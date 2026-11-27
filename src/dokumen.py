"""docs/data-dictionary.md ditulis ulang dari data setiap `python pipeline.py`.

Tipe, rentang, dan jumlah kosong dihitung dari Silver; arti dan asal kolom ditulis di ARTI.
Bagian khusus: kamus rincian, satuan per seri (dari docs/seri.csv), kode wilayah, dan contoh
penelusuran satu baris sampai berkas mentahnya.
"""
import csv
import json

import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.common.manifest import sha256
from src.ekstraksi.bps import potong_kunci
from src.laporan import ROOT, tabel_md

ARTI = {
    "sumber": ("nama folder sumber di data/raw/ (berkas mentah)", "lembaga penerbit: bps, wdi, who_gho, ilostat, bnpb"),
    "seri_kode": ("kolom var BPS / indicator.id WDI (berkas mentah)", "identitas seri; arti lengkap di docs/seri.csv"),
    "wilayah_kode": ("kamus src/wilayah.py; log K-002", "kode BPS dua digit x 100; 9999 = Indonesia"),
    "nama_wilayah": ("kamus src/wilayah.py; log K-002", "nama baku susunan 38 provinsi 2025, bukan label sumber"),
    "periode": ("tahun/turtahun BPS, date WDI, DIM_TIME WHO (berkas mentah)",
                "bentuk baku: 2019, 2019-S1, 2019-Q3, 2019-07"),
    "jenis_periode": ("diturunkan dari periode (berkas mentah)", "tahun, semester, triwulan, atau bulan"),
    "rincian": ("turvar BPS; kolom DIM_* WHO (berkas mentah); log K-018, K-019",
                "'total' atau 'dimensi=kode;...'; lihat kamus di bawah"),
    "nilai": ("datacontent BPS; value WDI; RATE_*_N WHO (berkas mentah)",
              "angka sesuai satuan; baris tanpa angka tidak masuk Silver"),
    "satuan": ("src/konfigurasi.py, bukti di docs/seri.csv; log K-018", "satuan baku; satu satuan per seri"),
    "sdg_kode": ("src/konfigurasi.py, bukti di docs/seri.csv; log K-018", "kode indikator SDG (kolom tambahan)"),
    "batas_bawah": ("RATE_*_NL WHO (tidak ada di paket kasus ini)", "batas bawah ketidakpastian; kosong bila sumber tidak memberi"),
    "batas_atas": ("RATE_*_NU WHO (tidak ada di paket kasus ini)", "batas atas ketidakpastian; kosong bila sumber tidak memberi"),
    "status_obs": ("OBS_STATUS CSV ILOSTAT", "kode status pengamatan ILOSTAT apa adanya (B = patahan seri menurut NOTE_INDICATOR; "
                   "arti kode lain tidak ada di paket, lihat reports/ilostat-status.csv); kosong untuk sumber lain"),
    "rujukan_tahun": ("var.note BPS (berkas mentah)", "lebar jendela rujukan survei (tahun sebelum survei); kosong bila tidak berlaku"),
    "_berkas_raw": ("pembaca ekstraksi src/ekstraksi; log K-004", "lineage: berkas asal baris ini"),
    "_sha256_raw": ("src.common.manifest.sha256_raw, dicocokkan dengan MANIFEST.csv; log K-004",
                    "lineage: sidik isi berkas asal"),
}

SATUAN = {
    "sumber": "kategori (nama folder)",
    "seri_kode": "kode seri",
    "wilayah_kode": "kode BPS (2 digit x 100)",
    "nama_wilayah": "teks",
    "periode": "tahun / tahun-S1 / tahun-Q1 / tahun-bulan",
    "jenis_periode": "kategori",
    "rincian": "dimensi=kode;...",
    "nilai": "mengikuti satuan seri (persen, persen_apk, tahun)",
    "satuan": "nama satuan",
    "sdg_kode": "kode indikator SDG",
    "batas_bawah": "sama dengan satuan nilai",
    "batas_atas": "sama dengan satuan nilai",
    "status_obs": "kode status observasi",
    "rujukan_tahun": "tahun",
    "_berkas_raw": "jalur relatif data/raw/",
    "_sha256_raw": "hex 64 karakter",
}


def _baris_manifest(berkas):
    jalur = ROOT / "data" / "raw" / "MANIFEST.csv"
    if not jalur.exists():
        return {}
    with open(jalur, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["berkas"] == berkas:
                return r
    return {}


def _sha_aktual(berkas):
    jalur = ROOT / "data" / "raw" / str(berkas)
    return sha256(jalur) if jalur.exists() else None


def _kunci_bps(contoh):
    """Kunci datacontent yang memuat baris contoh (hanya untuk berkas JSON BPS)."""
    berkas = str(contoh["_berkas_raw"])
    seri = str(contoh["seri_kode"])
    jalur = ROOT / "data" / "raw" / berkas
    if not (berkas.startswith("bps/") and berkas.endswith(".json") and seri.startswith("var") and jalur.exists()):
        return None
    try:
        halaman = json.loads(jalur.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(halaman, list):
        return None
    kode_var = seri[3:]
    target = float(contoh["nilai"])
    for hal in halaman:
        if not isinstance(hal, dict) or "datacontent" not in hal:
            continue
        if str(hal.get("var", [{}])[0].get("val")) != kode_var:
            continue
        kamus = {nama: {str(x["val"]): x["label"] for x in hal.get(nama, [])}
                 for nama in ("vervar", "turvar", "tahun", "turtahun")}
        for kunci, nilai in hal["datacontent"].items():
            potong = potong_kunci(kunci, kode_var, kamus["vervar"], kamus["turvar"], kamus["tahun"], kamus["turtahun"])
            if potong is None:
                continue
            k_wil, k_rin, k_th, k_per = potong
            if (k_wil == str(contoh["wilayah_kode"]) and kamus["tahun"][k_th] == str(contoh["periode"])
                    and abs(float(nilai) - target) < 1e-9):
                return kunci, kamus["turvar"][k_rin], kamus["tahun"][k_th], kamus["turtahun"][k_per]
    return None


def _rentang(s):
    if pd.api.types.is_numeric_dtype(s):
        x = s.dropna()
        return f"{x.min():g} – {x.max():g}" if len(x) else "—"
    u = s.dropna().astype(str).unique()
    return ", ".join(sorted(u)[:6]) + (f", … ({len(u)} nilai)" if len(u) > 6 else "")


def tulis_data_dictionary(silver):
    baris = []
    for k in silver.columns:
        asal, arti = ARTI.get(k, ("", ""))
        baris.append({"kolom": k, "tipe": str(silver[k].dtype), "satuan/format": SATUAN.get(k, "—"),
                      "kosong": int(silver[k].isna().sum()), "rentang_atau_nilai": _rentang(silver[k]),
                      "asal": asal, "arti": arti})
    seri = pd.read_csv(ROOT / "docs" / "seri.csv", keep_default_na=False)
    rinci = silver.groupby("rincian")["seri_kode"].agg(lambda x: ", ".join(sorted(set(x)))).reset_index()
    rinci.columns = ["rincian", "dipakai_seri"]
    contoh = silver[silver["sumber"] == silver["sumber"].iloc[0]].iloc[0]
    berkas = str(contoh["_berkas_raw"])
    sidik = str(contoh["_sha256_raw"])
    manifes = _baris_manifest(berkas)
    sha_aktual = _sha_aktual(berkas)
    kunci_bps = _kunci_bps(contoh)
    kode_dim = "\n".join(f"- `{dim}`: " + (", ".join(f"`{x}`" for x in sorted(v)) if v else "kode sumber apa adanya")
                         for dim, v in {d: K.KODE_RINCIAN.get(d) for d in sorted(set(K.RINCIAN_DIMENSI.values()) | set(K.KODE_RINCIAN))}.items())
    for kode_seri, (dim, kamus) in getattr(K, "RINCIAN_BPS", {}).items():
        kode_dim += f"\n- `{dim}` ({kode_seri}, dari turvar BPS): " + ", ".join(f"`{v}` = {k}" for k, v in kamus.items())
    teks = [
        f"# Data dictionary — Kasus {K.KASUS:02d} {K.JUDUL}",
        "Ditulis ulang otomatis oleh `python pipeline.py` (`src/dokumen.py`). Tipe, rentang, dan jumlah kosong "
        "dihitung dari `data/silver/silver.parquet`.",
        "Dokumen ini mendaftarkan **setiap kolom Silver** dengan nama, tipe, satuan/format, arti, dan asal "
        "(berkas mentah atau keputusan di `log-keputusan.csv`). Dokumentasi Gold tersedia pada bagian "
        "Data Dictionary Gold di bawah ini.",
        f"## data/silver/silver.parquet ({len(silver):,} baris)",
        "Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Kunci unik: sumber, seri_kode, "
        "wilayah_kode, periode, rincian, _berkas_raw.",
        tabel_md(pd.DataFrame(baris)),
        "## Kamus rincian",
        "Aturan menulis rincian (log): dimensi yang bervariasi ditulis `nama=kode`, dipisah `;`, urut abjad; nilai "
        "total sumber dibuang; baris tanpa dimensi bervariasi ditulis `total`. Dimensi yang nilainya tetap di seluruh "
        "berkas dianggap bagian definisi seri dan dicatat di kolom `cakupan` docs/seri.csv.",
        "Nama dimensi dan kode yang sah:", kode_dim or "- (tidak ada dimensi)",
        tabel_md(rinci),
        "## Satuan, kode SDG, dan cakupan per seri",
        tabel_md(seri[["seri_kode", "satuan", "sdg_kode", "cakupan", "bukti_satuan"]]),
        "## Kode wilayah",
        f"9999 = Indonesia; provinsi = kode BPS dua digit x 100, susunan 38 provinsi 2025 ({len(W.PROVINSI)} kode). "
        "WDI menulis Indonesia `ID`/`IDN`, WHO GHO menulis `360` (M49); keduanya dipetakan ke 9999 di `src/wilayah.py`.",
        "## Contoh penelusuran satu baris",
        "Contoh baris Silver berikut ditelusuri sampai berkas mentahnya dan dicocokkan dengan `MANIFEST.csv`.",
        tabel_md(pd.DataFrame([contoh[["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "nilai",
                                       "satuan", "_berkas_raw", "_sha256_raw"]]])),
        f"1. `_berkas_raw` = `{berkas}` menunjuk `data/raw/{berkas}` (jalur relatif terhadap `data/raw/`).",
        f"2. Baris `{berkas}` di `data/raw/MANIFEST.csv` berisi `bait={manifes.get('bait', '—')}` dan "
        f"`sha256={manifes.get('sha256', '—')}`; nilai sha256 ini sama dengan `_sha256_raw` baris Silver.",
        (f"3. sha256 isi berkas mentah dihitung ulang juga `{sha_aktual}`; hasilnya sama dengan `_sha256_raw`. "
         "Jadi berkas yang dibaca benar-benar berkas yang tercatat."
         if sha_aktual else "3. Berkas mentah tidak ada di salinan ini; `_sha256_raw` tetap dapat dicocokkan dengan `MANIFEST.csv`."),
        (f"4. Di berkas mentah JSON BPS, angka {contoh['nilai']} ada pada kunci `datacontent` `{kunci_bps[0]}` "
         f"= wilayah {contoh['wilayah_kode']} + var {str(contoh['seri_kode']).removeprefix('var')} + "
         f"turvar '{kunci_bps[1]}' + tahun {kunci_bps[2]} + turtahun '{kunci_bps[3]}'."
         if kunci_bps else
         "4. Di berkas mentah, angka ditemukan pada seri, wilayah, periode, dan rincian yang sama "
         "(WDI: `value` dengan `indicator.id` dan `date`; BPS: `datacontent` = kode wilayah + var + turvar + "
         "kode tahun + turtahun)."),
    ]
    (ROOT / "docs").mkdir(exist_ok=True)
    # Bagian Gold ditulis tim secara statis agar tidak hilang saat kamus Silver dibuat ulang.
    statis = ROOT / "docs" / "gold-dictionary.md"
    if statis.exists():
        teks.append(statis.read_text(encoding="utf-8").strip())
    (ROOT / "docs" / "data-dictionary.md").write_text("\n\n".join(teks) + "\n", encoding="utf-8")
