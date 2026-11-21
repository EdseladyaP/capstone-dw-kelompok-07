"""Kamus dimensi ILOSTAT (SDMX) -> rincian Silver. Tanpa impor supaya bisa dipakai pemeriksa luar.

Setiap kode dimensi ILOSTAT diawali nama dimensinya (SEX_F, AGE_YTHADULT_Y15-24, ECO_SECTOR_AGR). Kode
rincian = kode tanpa awalan itu, kecuali jenis kelamin yang memakai MALE/FEMALE seperti sumber lain.
Klasifikasi ikut ditulis (YTHADULT_Y15-24, 10YRBANDS_Y15-24; SECTOR_AGR, AGGREGATE_AGR) karena kelompok yang
sama bisa muncul di beberapa klasifikasi. Satu kode total utama per dimensi (TOTAL); total klasifikasi lain
(misalnya ECO_AGGREGATE_TOTAL, OCU_ISCO08_TOTAL, AGE_AGGREGATE_YGE15) tetap menjadi rincian supaya kunci tidak
kembar; nilainya sama dengan total utama.
"""

DIMENSI = {"SEX": "jenis_kelamin", "AGE": "umur", "DSB": "disabilitas", "ECO": "sektor", "OCU": "jabatan",
           "SOC": "perlindungan_sosial", "EDU": "pendidikan", "GEO": "daerah", "STE": "status_pekerjaan"}
NILAI_KHUSUS = {"SEX_M": "MALE", "SEX_F": "FEMALE"}
TOTAL = {"SEX_T", "AGE_YTHADULT_YGE15", "DSB_STATUS_TOTAL", "ECO_SECTOR_TOTAL", "OCU_SKILL_TOTAL", "SOC_CONTIG_TOTAL"}


def kode(dim, nilai):
    """('SEX', 'SEX_F') -> ('jenis_kelamin', 'FEMALE'); ('AGE', 'AGE_YTHADULT_Y15-24') -> ('umur', 'YTHADULT_Y15-24');
    kode total -> None."""
    if nilai in TOTAL or nilai == "":
        return None
    return DIMENSI.get(dim, dim.lower()), NILAI_KHUSUS.get(nilai, nilai.removeprefix(dim + "_"))


def balik(nama_dim, nilai):
    """Kebalikan kode(): ('jenis_kelamin', 'FEMALE') -> ('SEX', 'SEX_F')."""
    dim = next((d for d, n in DIMENSI.items() if n == nama_dim), nama_dim.upper())
    asal = next((k for k, v in NILAI_KHUSUS.items() if v == nilai and k.startswith(dim)), f"{dim}_{nilai}")
    return dim, asal
