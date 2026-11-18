-- Skema SQL Silver (DuckDB). Dimuat oleh src/gold/muat_sql.py.
-- Kunci primer = kunci unik skema minimal. Basis data menjadi lapis validasi terakhir:
-- baris yang melanggar kunci, rentang batas, atau rujukan seri ditolak saat dimuat.

CREATE TABLE seri (
    seri_kode       VARCHAR PRIMARY KEY,
    sumber          VARCHAR NOT NULL,
    tingkat         VARCHAR NOT NULL CHECK (tingkat IN ('provinsi', 'nasional')),
    nama_baku       VARCHAR NOT NULL,
    satuan          VARCHAR NOT NULL,
    sdg_kode        VARCHAR
);

CREATE TABLE silver (
    sumber          VARCHAR  NOT NULL,
    seri_kode       VARCHAR  NOT NULL REFERENCES seri (seri_kode),
    wilayah_kode    INTEGER  NOT NULL CHECK (wilayah_kode = 9999 OR wilayah_kode BETWEEN 1100 AND 9799),
    nama_wilayah    VARCHAR  NOT NULL,
    periode         VARCHAR  NOT NULL,
    jenis_periode   VARCHAR  NOT NULL CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    rincian         VARCHAR  NOT NULL,
    nilai           DOUBLE   NOT NULL,
    satuan          VARCHAR  NOT NULL,
    sdg_kode        VARCHAR,
    batas_bawah     DOUBLE,
    batas_atas      DOUBLE,
    rujukan_tahun   INTEGER,
    status_obs      VARCHAR,
    _berkas_raw     VARCHAR  NOT NULL,
    _sha256_raw     VARCHAR  NOT NULL CHECK (length(_sha256_raw) = 64),
    CHECK (batas_bawah IS NULL OR batas_bawah <= nilai),
    CHECK (batas_atas IS NULL OR nilai <= batas_atas),
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)
);
