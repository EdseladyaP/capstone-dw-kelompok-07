"""Kamus BNPB: nama ukuran dari judul resource atau kepala kolom, dan label jenis bencana.

Tabel BNPB tidak membawa kode seri. Ukuran dibaca dari dua tempat:
- judul resource di katalog CKAN ("Jumlah Korban Hilang Akibat Bencana Menurut Provinsi, 2024") untuk tabel
  yang hanya memuat satu ukuran (kolom per jenis bencana atau per tahun);
- kepala kolom untuk tabel rekap yang memuat banyak ukuran ("Meninggal", "Rumah Rusak Berat", ...).
Urutan UKURAN_RESOURCE penting: pola yang lebih khusus ditulis lebih dulu ("meninggal dan hilang per 100"
sebelum "korban meninggal").
"""
import re

# kolom jenis bencana pada tabel "per jenis" (huruf besar, seperti di berkas)
KOLOM_JENIS = ("BANJIR", "CUACA EKSTREM", "ERUPSI GUNUNG API", "GELOMBANG PASANG DAN ABRASI", "GEMPABUMI",
               "KEBAKARAN HUTAN DAN LAHAN", "KEKERINGAN", "TANAH LONGSOR", "TSUNAMI")

# ejaan lain di rekap 2021/2022 -> slug baku (slug dari KOLOM_JENIS)
JENIS_SAMA = {"gempa_bumi": "gempabumi", "letusan_gunung_api": "erupsi_gunung_api",
              "gelombang_pasang_abrasi": "gelombang_pasang_dan_abrasi"}

JENIS_BAKU = {re.sub(r"[^a-z0-9]+", "_", j.lower()) for j in KOLOM_JENIS}

# judul resource (huruf kecil) -> seri
UKURAN_RESOURCE = (
    ("meninggal dan hilang per 100", "korban_meninggal_hilang_per_100rb"),
    ("mengungsi per 100", "korban_mengungsi_per_100rb"),
    ("kejadian bencana", "kejadian"),
    ("korban meninggal", "korban_meninggal"),
    ("korban hilang", "korban_hilang"),
    ("korban luka", "korban_luka_sakit"),
    ("korban mengungsi", "korban_mengungsi"),
    ("korban terdampak", "korban_terdampak"),
    ("rumah ibadat", "rumah_ibadat_rusak"),
    ("rumah rusak", "rumah_rusak"),
    ("kantor", "kantor_rusak"),
    ("jembatan", "jembatan_rusak"),
    ("fasilitas pelayanan kesehatan", "fasyankes_rusak"),
    ("kios", "kios_toko_rusak"),
    ("pabrik", "pabrik_rusak"),
    ("satuan pendidikan", "satuan_pendidikan_rusak"),
    ("luas sawah", "luas_sawah_rusak"),
    ("luas lahan", "luas_lahan_kebun_hutan_rusak"),
)

# kepala kolom (huruf kecil) -> (seri, rincian tambahan)
UKURAN_LABEL = {
    "jumlah kejadian": ("kejadian", {}),
    "meninggal": ("korban_meninggal", {}),
    "hilang": ("korban_hilang", {}),
    "luka-luka": ("korban_luka_sakit", {}),
    "luka": ("korban_luka_sakit", {}),
    "terdampak - mengungsi": ("korban_terdampak_mengungsi", {}),
    "terdampak": ("korban_terdampak", {}),
    "mengungsi": ("korban_mengungsi", {}),
    "jumlah penduduk": ("jumlah_penduduk", {}),
    "rumah rusak berat": ("rumah_rusak", {"tingkat_kerusakan": "berat"}),
    "rumah rusak sedang": ("rumah_rusak", {"tingkat_kerusakan": "sedang"}),
    "rumah rusak ringan": ("rumah_rusak", {"tingkat_kerusakan": "ringan"}),
    "rumah terendam": ("rumah_terendam", {}),
    "sarana pendidikan": ("satuan_pendidikan_rusak", {}),
    "satuan pendidikan rusak": ("satuan_pendidikan_rusak", {}),
    "sarana peribadatan": ("rumah_ibadat_rusak", {}),
    "rumah ibadat rusak": ("rumah_ibadat_rusak", {}),
    "sarana kesehatan": ("fasyankes_rusak", {}),
    "fasilitas pelayanan kesehatan rusak": ("fasyankes_rusak", {}),
    "perkantoran": ("kantor_rusak", {}),
    "kantor rusak": ("kantor_rusak", {}),
    "jembatan": ("jembatan_rusak", {}),
    "jembatan rusak": ("jembatan_rusak", {}),
    "nilai kerusakan": ("nilai_kerusakan", {}),
    "nilai kerugian": ("nilai_kerugian", {}),
}

# satuan cacah: nilainya harus bilangan bulat
CACAH = {"jiwa", "kejadian", "unit"}


def jenis(teks):
    """'Gempa Bumi' / 'GEMPABUMI' / 'GELOMBANG PASANG / ABRASI' -> slug baku; 'Total'/'Jumlah' -> None (= total)."""
    j = re.sub(r"[^a-z0-9]+", "_", str(teks or "").lower()).strip("_")
    if j in ("", "total", "jumlah"):
        return None
    j = JENIS_SAMA.get(j, j)
    if j not in JENIS_BAKU:
        raise KeyError(f"jenis bencana {teks!r} belum ada di kamus (tambahkan ke JENIS_SAMA bila hanya beda ejaan)")
    return j


def ukuran_resource(nama):
    n = str(nama or "").lower()
    return next((seri for pola, seri in UKURAN_RESOURCE if pola in n), None)


def ukuran_label(label):
    """(seri, rincian tambahan) dari kepala kolom; None bila bukan kolom ukuran yang dikenal."""
    return UKURAN_LABEL.get(re.sub(r"\s+", " ", str(label or "")).strip().lower())
