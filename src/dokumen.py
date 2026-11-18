"""docs/data-dictionary.md ditulis ulang dari data setiap `python pipeline.py`.

Tipe, rentang, dan jumlah kosong dihitung dari Silver; arti dan asal kolom ditulis di ARTI.
Bagian khusus: kamus rincian, satuan per seri (dari docs/seri.csv), kode wilayah, dan contoh
penelusuran satu baris sampai berkas mentahnya.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, tabel_md

ARTI = {
    "sumber": ("nama folder sumber di data/raw/", "lembaga penerbit: bps, wdi, who_gho, ilostat, bnpb"),
    "seri_kode": ("kode seri di sumbernya (BPS: 'var' + var.val)", "identitas seri; arti lengkap di docs/seri.csv"),
    "wilayah_kode": ("kamus src/wilayah.py; log K-001", "kode BPS dua digit x 100; 9999 = Indonesia"),
    "nama_wilayah": ("kamus src/wilayah.py", "nama baku susunan 38 provinsi 2025, bukan label sumber"),
    "periode": ("tahun/turtahun BPS, date WDI, DIM_TIME WHO", "bentuk baku: 2019, 2019-S1, 2019-Q3, 2019-07"),
    "jenis_periode": ("diturunkan dari periode", "tahun, semester, triwulan, atau bulan"),
    "rincian": ("turvar BPS; kolom DIM_* WHO yang bervariasi", "'total' atau 'dimensi=kode;...'; lihat kamus di bawah"),
    "nilai": ("datacontent BPS; value WDI; RATE_*_N WHO", "angka sesuai satuan; baris tanpa angka tidak masuk Silver"),
    "satuan": ("src/konfigurasi.py, bukti di docs/seri.csv", "satuan baku; satu satuan per seri"),
    "sdg_kode": ("src/konfigurasi.py, bukti di docs/seri.csv", "kode indikator SDG (kolom tambahan)"),
    "batas_bawah": ("RATE_*_NL WHO", "batas bawah ketidakpastian; kosong bila sumber tidak memberi"),
    "batas_atas": ("RATE_*_NU WHO", "batas atas ketidakpastian; kosong bila sumber tidak memberi"),
    "status_obs": ("OBS_STATUS CSV ILOSTAT", "kode status pengamatan ILOSTAT apa adanya (B = patahan seri menurut NOTE_INDICATOR; "
                   "arti kode lain tidak ada di paket, lihat reports/ilostat-status.csv); kosong untuk sumber lain"),
    "rujukan_tahun": ("var.note BPS; log", "lebar jendela rujukan survei (tahun sebelum survei); kosong bila tidak berlaku"),
    "_berkas_raw": ("jalur berkas mentah relatif data/raw/", "lineage: berkas asal baris ini"),
    "_sha256_raw": ("src.common.manifest.sha256_raw", "lineage: sidik isi berkas asal, dicocokkan dengan MANIFEST.csv"),
}


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
        baris.append({"kolom": k, "tipe": str(silver[k].dtype), "kosong": int(silver[k].isna().sum()),
                      "rentang_atau_nilai": _rentang(silver[k]), "asal": asal, "arti": arti})
    seri = pd.read_csv(ROOT / "docs" / "seri.csv", keep_default_na=False)
    rinci = silver.groupby("rincian")["seri_kode"].agg(lambda x: ", ".join(sorted(set(x)))).reset_index()
    rinci.columns = ["rincian", "dipakai_seri"]
    contoh = silver[silver["sumber"] == silver["sumber"].iloc[0]].iloc[0]
    kode_dim = "\n".join(f"- `{dim}`: " + (", ".join(f"`{x}`" for x in sorted(v)) if v else "kode sumber apa adanya")
                         for dim, v in {d: K.KODE_RINCIAN.get(d) for d in sorted(set(K.RINCIAN_DIMENSI.values()) | set(K.KODE_RINCIAN))}.items())
    for kode_seri, (dim, kamus) in getattr(K, "RINCIAN_BPS", {}).items():
        kode_dim += f"\n- `{dim}` ({kode_seri}, dari turvar BPS): " + ", ".join(f"`{v}` = {k}" for k, v in kamus.items())
    teks = [
        f"# Data dictionary — Kasus {K.KASUS:02d} {K.JUDUL}",
        "Ditulis ulang otomatis oleh `python pipeline.py` (`src/dokumen.py`). Tipe, rentang, dan jumlah kosong "
        "dihitung dari `data/silver/silver.parquet`.",
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
        tabel_md(pd.DataFrame([contoh[["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "nilai", "_berkas_raw", "_sha256_raw"]]])),
        f"1. `_berkas_raw` menunjuk `data/raw/{contoh['_berkas_raw']}`.",
        f"2. Baris berkas itu di `data/raw/MANIFEST.csv` memuat sha256 `{contoh['_sha256_raw'][:12]}…`; nilainya sama dengan "
        "`_sha256_raw`, jadi berkas yang dibaca adalah berkas yang tercatat.",
        "3. Di berkas mentah, angka ditemukan pada wilayah, periode, dan rincian yang sama (untuk JSON BPS: kunci "
        "`datacontent` = kode wilayah + var + turvar + kode tahun + turtahun).",
    ]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "data-dictionary.md").write_text("\n\n".join(teks) + "\n", encoding="utf-8")
