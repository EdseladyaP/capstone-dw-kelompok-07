"""Kamus wilayah: susunan 38 provinsi tahun 2025 dan kode Indonesia dari setiap sumber.

Aturan Sprint 0 (log K-001): wilayah_kode = kode dua digit BPS x 100, Indonesia = 9999. Angka sebelum
sebuah provinsi dibentuk tidak dipecah dari provinsi induknya; sel provinsi baru pada tahun-tahun itu
dikategorikan "belum_ada" di grid, bukan missing.
"""

INDONESIA = 9999

# kode: (nama baku, tahun pertama provinsi punya data setahun penuh)
PROVINSI = {
    1100: ("Aceh", 1950), 1200: ("Sumatera Utara", 1950), 1300: ("Sumatera Barat", 1958),
    1400: ("Riau", 1958), 1500: ("Jambi", 1958), 1600: ("Sumatera Selatan", 1950),
    1700: ("Bengkulu", 1968), 1800: ("Lampung", 1964), 1900: ("Kepulauan Bangka Belitung", 2001),
    2100: ("Kepulauan Riau", 2003), 3100: ("DKI Jakarta", 1950), 3200: ("Jawa Barat", 1950),
    3300: ("Jawa Tengah", 1950), 3400: ("DI Yogyakarta", 1950), 3500: ("Jawa Timur", 1950),
    3600: ("Banten", 2001), 5100: ("Bali", 1958), 5200: ("Nusa Tenggara Barat", 1958),
    5300: ("Nusa Tenggara Timur", 1958), 6100: ("Kalimantan Barat", 1956), 6200: ("Kalimantan Tengah", 1958),
    6300: ("Kalimantan Selatan", 1956), 6400: ("Kalimantan Timur", 1956), 6500: ("Kalimantan Utara", 2013),
    7100: ("Sulawesi Utara", 1964), 7200: ("Sulawesi Tengah", 1964), 7300: ("Sulawesi Selatan", 1964),
    7400: ("Sulawesi Tenggara", 1964), 7500: ("Gorontalo", 2001), 7600: ("Sulawesi Barat", 2005),
    8100: ("Maluku", 1950), 8200: ("Maluku Utara", 2000), 9100: ("Papua Barat", 2004),
    9200: ("Papua Barat Daya", 2023), 9400: ("Papua", 1969), 9500: ("Papua Selatan", 2023),
    9600: ("Papua Tengah", 2023), 9700: ("Papua Pegunungan", 2023),
}

# Provinsi pemekaran -> provinsi induk. Sebelum pemekaran, angka induk mencakup wilayah provinsi baru;
# sesudahnya tidak lagi. Karena itu nilai induk sebelum dan sesudah pemekaran tidak sebanding (K-001).
INDUK = {1900: 1600, 2100: 1400, 3600: 3200, 6500: 6400, 7500: 7100, 7600: 7300, 8200: 8100, 9100: 9400,
         9200: 9100, 9500: 9400, 9600: 9400, 9700: 9400}

NAMA = {kode: nama for kode, (nama, _) in PROVINSI.items()} | {INDONESIA: "Indonesia"}

# Cara sumber internasional menulis Indonesia (hanya baris nasional; tidak ada provinsi di sumber ini).
KODE_NEGARA = {
    ("wdi", "ID"): INDONESIA, ("wdi", "IDN"): INDONESIA,
    ("who_gho", "360"): INDONESIA,          # DIM_GEO_CODE_M49
    ("ilostat", "IDN"): INDONESIA,
}

# Kode wilayah Kemendagri (dipakai BNPB, lembar Keterangan: "Kode Wilayah Administrasi Provinsi Menurut Peraturan
# Menteri Dalam Negeri"). Sama dengan kode BPS kecuali enam provinsi Papua, yang urutannya berbeda.
KEMENDAGRI_BEDA = {91: 9400, 92: 9100, 93: 9500, 94: 9600, 95: 9700, 96: 9200}


def sudah_ada(kode, tahun):
    """True bila provinsi `kode` sudah dibentuk pada `tahun` (Indonesia selalu True)."""
    if kode == INDONESIA:
        return True
    return int(str(tahun)[:4]) >= PROVINSI[kode][1]


def dari_negara(sumber, kode):
    try:
        return KODE_NEGARA[(sumber, str(kode).strip())]
    except KeyError:
        raise KeyError(f"kode wilayah {kode!r} dari {sumber} belum ada di kamus KODE_NEGARA") from None


def _baku(nama):
    import re
    t = re.sub(r"<[^>]+>", "", str(nama)).upper().replace("KEP. ", "KEPULAUAN ")
    return re.sub(r"[^A-Z ]+", " ", t).split()


# Ejaan yang pernah muncul di berkas mentah tetapi berbeda dari nama baku (bukan salah ketik kita)
ALIAS = {("PAPUA", "PENGUNUNGAN"): 9700, ("D", "I", "YOGYAKARTA"): 3400, ("DAERAH", "ISTIMEWA", "YOGYAKARTA"): 3400,
         ("DKI", "JAKARTA", "RAYA"): 3100, ("JAKARTA", "RAYA"): 3100, ("NANGGROE", "ACEH", "DARUSSALAM"): 1100,
         ("P", "A", "P", "U", "A"): 9400}


def dari_nama(nama):
    """Nama wilayah di tabel statis BPS ('KEP. RIAU', 'DI YOGYAKARTA', 'INDONESIA') -> kode."""
    k = tuple(_baku(nama))
    if k[:1] == ("PROVINSI",):          # 'PROVINSI SULAWESI BARAT' (tabel nilai kerusakan BNPB)
        k = k[1:]
    if k == ("INDONESIA",):
        return INDONESIA
    for kode, n in NAMA.items():
        if tuple(_baku(n)) == k:
            return kode
    if k in ALIAS:
        return ALIAS[k]
    raise KeyError(f"nama wilayah {nama!r} belum ada di kamus (tambahkan ke ALIAS bila hanya beda ejaan)")


def dari_kemendagri(kode, nama=""):
    """Kode provinsi Kemendagri (dua digit, atau empat digit kab/kota -> dua digit awal) -> kode kunci.
    Bila nama provinsi juga ada, keduanya harus menunjuk provinsi yang sama; kalau tidak, galat."""
    k = int(str(kode)[:2])
    hasil = KEMENDAGRI_BEDA.get(k, k * 100)
    if hasil not in PROVINSI:
        raise KeyError(f"kode Kemendagri {kode!r} tidak dikenal")
    if nama and len(str(kode)) <= 2 and dari_nama(nama) != hasil:
        raise ValueError(f"kode Kemendagri {kode} -> {NAMA[hasil]}, tetapi nama di baris yang sama {nama!r}")
    return hasil
