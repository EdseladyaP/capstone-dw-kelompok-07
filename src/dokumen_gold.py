"""Tambahan Gold untuk docs/data-dictionary.md (kolom tabel nasional).

Diadaptasi dari kunci Sprint 2 `k07-partisipasi-lama-sekolah/src/dokumen_gold.py`: kolom
dijelaskan dengan asal dan arti, lalu contoh penelusuran satu baris sampai `_berkas_raw`.
"""
import pandas as pd

from src.laporan import ROOT, tabel_md

ARTI = {
    "seri_kode": ("K.SERI_UTAMA, K.SERI_PEMBANDING", "identitas seri utama BPS atau pembanding WDI"),
    "rincian": ("rincian baku Silver (jenjang/umur/total)", "bagian dari kunci; jenjang dan umur tidak dijumlah"),
    "sumber": ("src/ekstraksi; Silver", "lembaga penerbit: bps atau wdi"),
    "periode": ("periode Silver", "tahun, atau tahun-S1/-Q3/-bulan sesuai sumber"),
    "jenis_periode": ("periode Silver", "jenis periode asli; tidak diagregasi otomatis"),
    "nilai": ("nilai Silver pada wilayah 9999", "angka nasional sesuai satuan seri"),
    "satuan": ("src/konfigurasi.py; Silver", "persen_apk, persen, atau tahun; APK boleh melebihi 100"),
    "batas_bawah": ("Silver (WHO; kosong untuk kasus 07)", "batas bawah ketidakpastian bila tersedia"),
    "batas_atas": ("Silver (WHO; kosong untuk kasus 07)", "batas atas ketidakpastian bila tersedia"),
    "rujukan_tahun": ("var.note BPS di Silver", "lebar jendela rujukan survei; kosong bila tidak berlaku"),
    "asal": ("src/gold/nasional_gold.py", "baris_indonesia | pembanding | agregat; sumber angka nasional"),
    "catatan": ("src/gold/nasional_gold.py; log K-042", "aturan pemilihan baris dan alasan tidak ada agregat"),
    "_berkas_raw": ("pembaca ekstraksi; Silver", "lineage: berkas asal baris ini (wajib ada di setiap baris Gold)"),
    "_sha256_raw": ("src.common.manifest.sha256_raw", "sidik berkas asal; kosong hanya pada baris agregat"),
}


def tulis_dokumen_gold(gold):
    """Tambahkan potongan Gold ke kamus yang baru saja ditulis src/dokumen.py."""
    nas = gold.get("nasional_gold")
    if nas is None:
        return
    jalur = ROOT / "docs" / "data-dictionary.md"
    if not jalur.exists():
        return
    baris = []
    for kolom in nas.columns:
        asal, arti = ARTI.get(kolom, ("", ""))
        baris.append({"kolom": kolom, "tipe": str(nas[kolom].dtype), "asal": asal, "arti": arti})
    contoh = nas.iloc[0]
    teks = "\n\n".join([
        "## data/gold/nasional.parquet (tabel nasional Gold)",
        "Ditulis ulang oleh `python pipeline.py` (`src/gold/nasional_gold.py`). Satu baris = satu "
        "seri x rincian x periode; kunci unik `seri_kode` + `rincian` + `periode`.",
        tabel_md(pd.DataFrame(baris)),
        "Nilai `asal` dibaca dari satu kolom: `baris_indonesia` (BPS wilayah 9999), `pembanding` "
        "(WDI), atau `agregat` (hanya ada bila ada bobot yang sah). Kelima seri utama menerbitkan baris "
        "Indonesia, jadi tidak ada baris agregat di kasus ini (K-042).",
        f"Contoh penelusuran: seri `{contoh['seri_kode']}`, rincian `{contoh['rincian']}`, "
        f"periode `{contoh['periode']}` berasal dari `{contoh['_berkas_raw']}` dengan asal "
        f"`{contoh['asal']}`.",
    ])
    with jalur.open("a", encoding="utf-8") as f:
        f.write("\n\n" + teks + "\n")
