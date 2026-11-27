"""Persiapan tahap 6 — tabel nasional Gold, lanjutan `reports/tabel-nasional.csv`.

Satu baris = satu seri x rincian x periode. Nilainya seluruhnya berada di tingkat Indonesia
(`wilayah_kode = 9999`, BPS/WDI), atau merupakan pembanding nasional yang diterbitkan WDI.
Kolom `asal` menjawab asal setiap angka dalam satu kolom:

- `baris_indonesia`: baris Indonesia yang benar-benar diterbitkan penerbit seri;
- `pembanding`: seri nasional dari sumber pembanding (WDI `SE.TER.ENRR`);
- `agregat`: hanya bila `K.GOLD_AGREGAT` diisi dengan bobot yang sah.

Aturan agregasi provinsi: paket kasus 07 **tidak memuat bobot penduduk**. Rata-rata provinsi
tanpa bobot bukan angka nasional; APK dan lama sekolah juga tidak bisa dijumlahkan antarjenjang
atau antarkelompok umur yang tumpang tindih. Karena kelima seri utama menerbitkan baris Indonesia,
tidak ada agregat yang dibuat. Bila suatu seri tidak punya baris Indonesia dan tidak ada bobot,
seri itu dinyatakan **tidak punya padanan nasional** (dicatat di laporan, bukan di Angka).

Keluaran: `data/gold/nasional.parquet`, `reports/tabel-nasional-gold.csv`,
`reports/tabel-nasional-gold.md`.
"""
import csv
import io

import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis
from src.silver import deret

KOLOM = [
    "seri_kode", "rincian", "sumber", "periode", "jenis_periode", "nilai", "satuan",
    "batas_bawah", "batas_atas", "rujukan_tahun", "asal", "catatan", "_berkas_raw", "_sha256_raw",
]

CATATAN = {
    "var303": "Baris Indonesia diterbitkan per jenjang (SD/SMP/SM). Jenjang tidak dijumlah: APK bukan besaran aditif dan tidak ada baris Indonesia total.",
    "var1443": "Baris Indonesia total diterbitkan BPS. Pembanding WDI memakai kelompok umur jenjang tersier resmi; selisih dijelaskan sebagai perbedaan definisi dan metode.",
    "var2685": "Baris Indonesia diterbitkan per kelompok umur. Kelompok umur tumpang tindih (15-64 mencakup yang lain), jadi tidak dijumlah.",
    "var417": "Baris Indonesia total diterbitkan BPS. Tidak ada pembanding eksternal di paket kasus 07.",
    "var1429": "Baris Indonesia total diterbitkan BPS. Pasangan dengan var417 adalah konteks (dua ukuran berbeda), bukan selisih yang dihitung.",
    "SE.TER.ENRR": "Seri pembanding nasional WDI (UNESCO UIS); bukan baris Indonesia BPS.",
}

ALASAN_TANPA_AGREGAT = (
    "Tidak ada baris Indonesia yang diterbitkan dan paket tidak menyediakan bobot penduduk; "
    "rata-rata provinsi tanpa bobot ditolak, jadi seri ini tidak punya padanan nasional."
)


def seri_dipakai():
    """Lima seri utama kasus 07 dilengkapi satu seri pembanding nasional."""
    return list(K.SERI_UTAMA) + list(K.SERI_PEMBANDING)


def satu_per_sel(g):
    """Satu angka untuk satu seri x rincian x periode; berkas dipilih menurut URUTAN_BERKAS."""
    kunci = ["seri_kode", "rincian", "periode"]
    if not g.duplicated(kunci).any():
        return g.drop(columns="_peringkat", errors="ignore")
    g = g.assign(_peringkat=g["_berkas_raw"].map(deret.peringkat)) \
          .sort_values(["_peringkat", "_berkas_raw"])
    return g.drop_duplicates(kunci).drop(columns="_peringkat")


def agregat(silver):
    """Agregat provinsi hanya jika ada bobot; kosong untuk kasus 07 (lihat docstring)."""
    bagian = []
    for seri, aturan in getattr(K, "GOLD_AGREGAT", {}).items():
        rincian = aturan.get("rincian", "total")
        kolom_bobot = aturan.get("bobot")
        if not kolom_bobot:
            raise ValueError(
                f"GOLD_AGREGAT[{seri}] tidak punya bobot. Rata-rata provinsi tanpa bobot ditolak."
            )
        s = silver[(silver["seri_kode"] == seri)
                   & (silver["rincian"] == rincian)
                   & (silver["wilayah_kode"] != W.INDONESIA)].copy()
        s = satu_per_sel(s)
        if s.empty:
            continue
        g = s.groupby("periode", as_index=False).apply(
            lambda x: pd.Series({
                "nilai": float((x["nilai"] * x[kolom_bobot]).sum() / x[kolom_bobot].sum()),
                "sumber": x["sumber"].iloc[0],
                "jenis_periode": x["jenis_periode"].iloc[0],
                "satuan": x["satuan"].iloc[0],
                "_berkas_raw": ";".join(sorted(set(x["_berkas_raw"].dropna().astype(str)))),
                "rujukan_tahun": x["rujukan_tahun"].iloc[0],
            }), include_groups=False
        )
        g = g.assign(seri_kode=seri, rincian=rincian, asal="agregat",
                     catatan=aturan.get("alasan", "agregat provinsi berbobot penduduk"),
                     _sha256_raw=None, batas_bawah=None, batas_atas=None)
        bagian.append(g)
    return bagian


def status_series(silver):
    """Status nasional setiap seri: dipakai di laporan dan untuk menolak angka rekaan."""
    baris = []
    for seri in seri_dipakai():
        tingkat = K.SERI.get(seri, {}).get("tingkat", "—")
        s = silver[silver["seri_kode"] == seri]
        n_ind = int((s["wilayah_kode"] == W.INDONESIA).sum())
        if tingkat == "nasional":
            asal, aturan = "pembanding", "baris nasional dari sumber pembanding dipakai apa adanya"
        elif n_ind:
            asal = "baris_indonesia"
            aturan = "memakai baris Indonesia yang diterbitkan penerbit"
        elif seri in getattr(K, "GOLD_AGREGAT", {}):
            asal = "agregat"
            aturan = "agregat provinsi berbobot penduduk (K.GOLD_AGREGAT)"
        else:
            asal = "tidak punya padanan nasional"
            aturan = ALASAN_TANPA_AGREGAT
        baris.append({
            "seri_kode": seri, "tingkat": tingkat, "baris_indonesia": n_ind,
            "rincian": ", ".join(sorted(s.loc[s["wilayah_kode"] == W.INDONESIA, "rincian"].unique())) or "—",
            "asal": asal, "aturan": aturan,
            "alasan": CATATAN.get(seri, ALASAN_TANPA_AGREGAT),
        })
    return pd.DataFrame(baris)


def _catat_keputusan(entri):
    """Tambah keputusan sekali; BOM dan isi log lama tidak diubah."""
    jalur = ROOT / "log-keputusan.csv"
    lama = jalur.read_bytes() if jalur.exists() else b""
    teks = lama.decode("utf-8-sig")
    ada = {r.get("id") for r in csv.DictReader(io.StringIO(teks))}
    if entri["id"] in ada:
        return
    keluaran = io.StringIO()
    csv.writer(keluaran, lineterminator="\n").writerow([entri[k] for k in [
        "id", "tanggal", "nim", "tahap", "seri_kode", "keputusan",
        "alternatif_ditolak", "alasan", "dampak_baris",
    ]])
    with jalur.open("ab") as f:
        if lama and not lama.endswith(b"\n"):
            f.write(b"\n")
        f.write(keluaran.getvalue().encode("utf-8"))


def jalankan(silver):
    Status = status_series(silver)
    nas = silver[(silver["seri_kode"].isin(seri_dipakai()))
                 & (silver["wilayah_kode"] == W.INDONESIA)].copy()
    nas = satu_per_sel(nas)
    tingkat = {k: v.get("tingkat") for k, v in K.SERI.items()}
    nas["asal"] = nas["seri_kode"].map(
        lambda s: "pembanding" if tingkat.get(s) == "nasional" else "baris_indonesia"
    )
    nas["catatan"] = nas["seri_kode"].map(CATATAN).fillna("")
    t = pd.concat([nas, *agregat(silver)], ignore_index=True)
    for kolom in KOLOM:
        if kolom not in t:
            t[kolom] = None
    t = t[KOLOM].sort_values(["seri_kode", "rincian", "periode"]).reset_index(drop=True)
    for kolom in ("nilai", "batas_bawah", "batas_atas", "rujukan_tahun"):
        t[kolom] = pd.to_numeric(t[kolom], errors="coerce")
    if t["_berkas_raw"].isna().any() or (t["_berkas_raw"].astype(str).str.strip() == "").any():
        raise ValueError("Ada baris nasional Gold tanpa _berkas_raw.")

    folder = ROOT / "data" / "gold"
    folder.mkdir(parents=True, exist_ok=True)
    t.to_parquet(folder / "nasional.parquet", index=False)
    t.to_csv(ROOT / "reports" / "tabel-nasional-gold.csv", index=False)

    asal = t["asal"].value_counts().to_dict()
    ringkas = (t.groupby(["seri_kode", "asal"], as_index=False)
                 .agg(baris=("periode", "size"), periode_awal=("periode", "min"),
                      periode_akhir=("periode", "max")))
    tulis("tabel-nasional-gold.md", "\n\n".join([
        "# Tabel nasional Gold — Kasus 07",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional_gold.py`) dari Silver. Ini lanjutan "
        "`reports/tabel-nasional.csv` (Sprint 1, tampilan lebar) menjadi satu baris per seri x rincian "
        "x periode. File siap pakai: `data/gold/nasional.parquet`; salinan mudah dibaca: "
        "`reports/tabel-nasional-gold.csv`.",
        "Kolom **`asal`** menunjukkan sumber setiap angka: `baris_indonesia`, `pembanding`, atau `agregat`. "
        "Setiap baris tetap membawa `_berkas_raw` (dan `_sha256_raw` untuk baris yang berasal dari Silver) "
        "sehingga angka dapat ditelusuri ke `data/raw/`.",
        "## Ringkasan",
        f"- Baris: {len(t):,}; seri: {t['seri_kode'].nunique()}; asal: {asal}.",
        "- Kunci unik: `seri_kode` + `rincian` + `periode`. Satu berkas dipilih per sel menurut "
        "`URUTAN_BERKAS` (`src/silver/deret.py`).",
        tabel_md(ringkas),
        "## Aturan nasional per seri",
        "Kelima seri utama menerbitkan baris Indonesia sehingga **tidak ada agregat provinsi yang dibuat**. "
        "Bila baris Indonesia tidak ada, aturannya bukan rata-rata provinsi: paket tidak memuat bobot "
        "penduduk, jadi seri dinyatakan tidak punya padanan nasional dan tidak diisi dengan angka rekaan.",
        tabel_md(Status),
        "## Contoh baris",
        tabel_md(t.groupby("seri_kode", group_keys=False).head(2)[
            ["seri_kode", "rincian", "periode", "nilai", "satuan", "asal", "_berkas_raw"]
        ]),
        "Seluruh baris ada di `reports/tabel-nasional-gold.csv`; kolom `catatan` memuat alasan "
        "pemilihan baris Indonesia/pembanding dan larangan agregasi yang relevan.",
    ]))

    catat(baris_nasional_gold=len(t), seri_nasional_gold=int(t["seri_kode"].nunique()),
          **{f"nasional_{k}": int(v) for k, v in asal.items()})
    _catat_keputusan({
        "id": "K-042", "tanggal": "2026-11-26", "nim": "124450095",
        "tahap": "integrasi", "seri_kode": ";".join(seri_dipakai()),
        "keputusan": "Tabel nasional Gold memakai baris Indonesia yang diterbitkan untuk kelima seri utama dan baris WDI untuk pembanding; tidak ada agregat provinsi karena paket tanpa bobot penduduk",
        "alternatif_ditolak": "Rata-rata provinsi tanpa bobot; menjumlahkan jenjang/kelompok umur; mengisi nol pada tahun tanpa baris Indonesia",
        "alasan": "APK dan lama sekolah memerlukan bobot penduduk sesuai definisi; jenjang APK dan kelompok umur var2685 tidak aditif; setiap baris tetap membawa _berkas_raw",
        "dampak_baris": str(len(t)),
    })
    return t
