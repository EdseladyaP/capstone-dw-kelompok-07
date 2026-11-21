"""Keputusan wrangling Kasus 07 — Partisipasi dan lama sekolah.

Semua keputusan khas kasus ada di berkas ini supaya mudah ditinjau: identitas seri, satuan dan kode
SDG beserta buktinya, kamus jenjang dan kelompok umur, pergantian definisi, ambang anomali, dan
pasangan rekonsiliasi. Setiap keputusan juga tercatat di log-keputusan.csv.
Ini salah satu jawaban yang dapat dipertahankan, bukan satu-satunya.
"""

KASUS = 7
SLUG = "partisipasi-lama-sekolah"
JUDUL = "Partisipasi dan lama sekolah"

FORMAT_BPS = "json"

# Angka partisipasi kasar bisa melebihi 100 (siswa di luar umur jenjang ikut dihitung): satuan sendiri.
APK = "persen_apk"

SERI = {
    "var303": dict(
        sumber="bps", tingkat="provinsi",
        nama="Angka Partisipasi Kasar (APK) menurut jenjang SD, SMP, SM",
        satuan=APK, katalog_satuan="tidak_ada",
        bukti_satuan="judul 'Angka Partisipasi Kasar'; var.unit kosong; nilai di atas 100 ada (APK menghitung siswa semua umur)",
        sdg="4.1", katalog_sdg="4.3.1",
        bukti_sdg="turvar hanya SD/sederajat, SMP/sederajat, SM/sederajat: jenjang dasar-menengah (target 4.1), bukan pendidikan "
                  "tinggi 4.3.1; berkas tidak menulis kode indikator",
        cakupan="Susenas; 2003–2025; mulai 2007 termasuk paket A/B/C (var.note)",
        koreksi="satuan tidak_ada -> persen_apk; kode SDG 4.3.1 -> 4.1 (tidak ada jenjang PT di turvar)",
    ),
    "var1443": dict(
        sumber="bps", tingkat="provinsi",
        nama="Angka Partisipasi Kasar (APK) perguruan tinggi",
        satuan=APK, katalog_satuan="tidak_ada", bukti_satuan="judul 'Angka Partisipasi Kasar'; var.unit kosong",
        sdg="4.3.1", katalog_sdg="4.3.1", bukti_sdg="judul = APK perguruan tinggi",
        cakupan="kelompok umur acuan 19–23 tahun (var.note); Susenas; 2015–2025",
        koreksi="satuan tidak_ada -> persen_apk",
    ),
    "var2685": dict(
        sumber="bps", tingkat="provinsi",
        nama="Tingkat partisipasi remaja dan dewasa dalam pendidikan dan pelatihan formal dan nonformal 12 bulan terakhir",
        satuan="persen", katalog_satuan="persen", bukti_satuan="var.unit: 'Persen'",
        sdg="4.3.1", katalog_sdg="4.3.1", bukti_sdg="var.label diawali '4.3.1*'",
        cakupan="empat kelompok umur yang tumpang tindih (15–64 mencakup yang lain); 2022–2024",
    ),
    "var417": dict(
        sumber="bps", tingkat="provinsi",
        nama="Harapan lama sekolah (IPM metode baru)",
        satuan="tahun", katalog_satuan="tahun", bukti_satuan="var.unit: 'Tahun'",
        sdg="—", katalog_sdg="—", bukti_sdg="komponen IPM; tidak ada kode SDG di berkas",
        cakupan="anak umur 7 tahun; 2010–2025; berkas juga memuat kabupaten/kota (dikeluarkan)",
    ),
    "var1429": dict(
        sumber="bps", tingkat="provinsi",
        nama="Rata-rata lama sekolah penduduk umur 15 tahun ke atas",
        satuan="tahun", katalog_satuan="tidak_ada", bukti_satuan="judul 'Rata-Rata Lama Sekolah'; var.unit kosong; nilai 6–12",
        sdg="—", katalog_sdg="—", bukti_sdg="tidak ada kode SDG di berkas",
        cakupan="penduduk 15+; Susenas; 2015–2025", koreksi="satuan tidak_ada -> tahun",
    ),
    "SE.TER.ENRR": dict(
        sumber="wdi", tingkat="nasional", nama="School enrollment, tertiary (% gross)",
        satuan=APK, katalog_satuan="—", bukti_satuan="name: '(% gross)'; sourceNote: rasio kasar, bisa > 100",
        sdg="4.3.1", katalog_sdg="—", bukti_sdg="tercantum di metadata/sumber46_indikator.json",
        cakupan="UNESCO UIS; kelompok umur resmi jenjang tersier (umur tidak disebut di sourceNote)",
        koreksi="kode SDG kosong -> 4.3.1",
    ),
}

RINCIAN_TOTAL_BPS = {"tidak ada"}
RINCIAN_BPS = {
    "var303": ("jenjang", {"SD/sederajat": "sd", "SMP/sederajat": "smp", "SM/sederajat": "sm"}),
    "var2685": ("umur", {"Usia 15-24 tahun": "15-24", "Usia 15-64 tahun": "15-64",
                         "Usia 25-54 tahun": "25-54", "Usia 55-64 tahun": "55-64"}),
}
RINCIAN_TOTAL_WHO = {"TOTAL", ""}
RINCIAN_DIMENSI = {}
RINCIAN_NILAI = {}
KODE_RINCIAN = {"jenjang": {"sd", "smp", "sm"}, "umur": {"15-24", "15-64", "25-54", "55-64"}}

# K-004: seri tanpa total diprofilkan per jenjang / kelompok umur terluas
DERET = {"var303": ["jenjang=sd", "jenjang=smp", "jenjang=sm"], "var2685": ["umur=15-64"]}

RUJUKAN_TAHUN = {}
TIDAK_TERBIT = {}
TAHUN_TERBIT = {}

PATAHAN_DEFINISI = {"var303": {"2007": "var.note: mulai 2007 APK mencakup pendidikan nonformal (paket A, B, C)"}}

RENTANG = {"persen": (0, 100), APK: (0, 250), "tahun": (0, 25)}

ANOMALI = {"k_iqr": 1.5, "min_titik_samping": 6, "lompat_relatif": 0.20, "porsi_patahan": 0.70}

PASANGAN = [
    dict(id="P1", judul="APK perguruan tinggi: BPS (umur 19–23) vs WDI (umur resmi jenjang tersier)",
         utama="var1443", rincian_utama="total", pembanding=[("SE.TER.ENRR", "total")],
         jenis="selisih", kategori="definisi (kelompok umur acuan penyebut) dan metode (Susenas vs data administrasi UNESCO)",
         alasan_rincian="tanpa rincian",
         pertanyaan=[
             ("Kelompok umur BPS?", "19–23 tahun (var.note var1443)."),
             ("Kelompok umur WDI?", "Kelompok umur resmi jenjang tersier; sourceNote tidak menyebut angkanya."),
             ("Mengapa bukan var303?", "turvar var303 hanya SD, SMP, SM; tidak ada jenjang PT."),
         ]),
    dict(id="P2", judul="Lama sekolah (HLS, RLS): tanpa pembanding di paket",
         utama="var417", rincian_utama="total", pembanding=[("var1429", "total")],
         jenis="konteks", kategori="dua ukuran berbeda (harapan anak 7 tahun vs rata-rata penduduk 15+); variabel penjelas panel",
         alasan_rincian="tanpa rincian",
         pertanyaan=[("Bolehkah dibandingkan?", "Tidak sebagai selisih: HLS proyeksi untuk anak 7 tahun, RLS capaian penduduk 15+.")]),
]
