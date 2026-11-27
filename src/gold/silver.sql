-- DDL DuckDB untuk Silver dan Gold
-- Seluruh tabel memiliki primary key.

CREATE TABLE seri (
    seri_kode VARCHAR PRIMARY KEY,
    sumber VARCHAR NOT NULL,
    tingkat VARCHAR NOT NULL,
    nama_baku VARCHAR NOT NULL,
    satuan VARCHAR NOT NULL,
    sdg_kode VARCHAR
);

CREATE TABLE silver (
    sumber VARCHAR NOT NULL,
    seri_kode VARCHAR NOT NULL REFERENCES seri(seri_kode),
    wilayah_kode BIGINT NOT NULL,
    nama_wilayah VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL,
    rincian VARCHAR NOT NULL,
    nilai DOUBLE NOT NULL,
    satuan VARCHAR NOT NULL,
    sdg_kode VARCHAR,
    batas_bawah DOUBLE,
    batas_atas DOUBLE,
    rujukan_tahun BIGINT,
    _berkas_raw VARCHAR NOT NULL,
    _sha256_raw VARCHAR NOT NULL,
    CHECK (length(_sha256_raw) = 64),
    CHECK (batas_bawah IS NULL OR batas_bawah <= nilai),
    CHECK (batas_atas IS NULL OR nilai <= batas_atas),
    PRIMARY KEY (
        sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw
    )
);

CREATE TABLE panel_provinsi_tahun (
    wilayah_id BIGINT NOT NULL,
    nama_wilayah VARCHAR,
    tahun BIGINT NOT NULL,
    rata_rata_lama_sekolah_tahun DOUBLE,
    apk_perguruan_tinggi_persen DOUBLE,
    harapan_lama_sekolah_tahun DOUBLE,
    status_rata_rata_lama_sekolah_tahun VARCHAR,
    status_apk_perguruan_tinggi_persen VARCHAR,
    status_harapan_lama_sekolah_tahun VARCHAR,
    outlier_rata_rata_lama_sekolah_tahun BOOLEAN,
    outlier_apk_perguruan_tinggi_persen BOOLEAN,
    outlier_harapan_lama_sekolah_tahun BOOLEAN,
    PRIMARY KEY (wilayah_id, tahun)
);

CREATE TABLE panel_indikator_gold (
    seri_kode VARCHAR NOT NULL,
    tahun BIGINT NOT NULL,
    wilayah_id BIGINT NOT NULL,
    wilayah VARCHAR,
    kategori VARCHAR NOT NULL,
    tahun_mulai_target BIGINT,
    status VARCHAR,
    nama_wilayah VARCHAR,
    nilai DOUBLE,
    satuan VARCHAR,
    _berkas_raw VARCHAR,
    _sha256_raw VARCHAR,
    outlier_asli BOOLEAN,
    PRIMARY KEY (seri_kode, tahun, wilayah_id, kategori)
);

CREATE TABLE anomali_gold (
    seri_kode VARCHAR NOT NULL,
    kategori VARCHAR NOT NULL,
    wilayah_id BIGINT NOT NULL,
    provinsi VARCHAR,
    tahun BIGINT NOT NULL,
    periode VARCHAR,
    nilai_klasifikasi DOUBLE,
    Q1 DOUBLE,
    Q3 DOUBLE,
    IQR DOUBLE,
    batas_bawah DOUBLE,
    batas_atas DOUBLE,
    alasan_ditandai VARCHAR,
    klasifikasi VARCHAR,
    verifikasi_sumber VARCHAR,
    tindakan VARCHAR,
    nilai_silver DOUBLE,
    _berkas_raw VARCHAR,
    _sha256_raw VARCHAR,
    outlier_asli BOOLEAN,
    PRIMARY KEY (seri_kode, wilayah_id, tahun, kategori)
);

CREATE TABLE audit_snapshot_gold (
    seri_kode VARCHAR NOT NULL,
    wilayah_kode BIGINT NOT NULL,
    periode VARCHAR NOT NULL,
    rincian VARCHAR NOT NULL,
    jumlah_baris_snapshot BIGINT NOT NULL,
    jumlah_baris_tidak_dipilih BIGINT NOT NULL,
    snapshot_dipilih VARCHAR NOT NULL,
    nilai_dipilih DOUBLE,
    PRIMARY KEY (seri_kode, wilayah_kode, periode, rincian)
);

CREATE TABLE nasional (
    sumber VARCHAR NOT NULL,
    seri_kode VARCHAR NOT NULL REFERENCES seri(seri_kode),
    wilayah_kode BIGINT NOT NULL,
    nama_wilayah VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL,
    rincian VARCHAR NOT NULL,
    nilai DOUBLE NOT NULL,
    satuan VARCHAR NOT NULL,
    sdg_kode VARCHAR,
    batas_bawah DOUBLE,
    batas_atas DOUBLE,
    rujukan_tahun BIGINT,
    _berkas_raw VARCHAR NOT NULL,
    _sha256_raw VARCHAR NOT NULL,
    CHECK (length(_sha256_raw) = 64),
    CHECK (batas_bawah IS NULL OR batas_bawah <= nilai),
    CHECK (batas_atas IS NULL OR nilai <= batas_atas),
    PRIMARY KEY (
        sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw
    )
);

CREATE TABLE nasional_gold (
    seri_kode VARCHAR NOT NULL,
    rincian VARCHAR NOT NULL,
    sumber VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL,
    nilai DOUBLE NOT NULL,
    satuan VARCHAR,
    batas_bawah DOUBLE,
    batas_atas DOUBLE,
    rujukan_tahun BIGINT,
    asal VARCHAR NOT NULL,
    catatan VARCHAR,
    _berkas_raw VARCHAR NOT NULL,
    _sha256_raw VARCHAR,
    PRIMARY KEY (seri_kode, rincian, periode)
);

CREATE TABLE pasangan_rekonsiliasi (
    id VARCHAR PRIMARY KEY,
    seri_utama VARCHAR NOT NULL,
    pembanding VARCHAR NOT NULL,
    jenis VARCHAR NOT NULL,
    periode_beririsan BIGINT NOT NULL,
    tahun VARCHAR NOT NULL,
    dugaan_kategori VARCHAR NOT NULL
);

CREATE TABLE rekonsiliasi_nasional (
    id VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    seri_utama VARCHAR NOT NULL,
    nilai_utama DOUBLE,
    seri_pembanding VARCHAR,
    nilai_pembanding DOUBLE,
    selisih DOUBLE,
    status_pasangan VARCHAR NOT NULL,
    kategori VARCHAR,
    dugaan VARCHAR,
    bukti VARCHAR,
    PRIMARY KEY (id, periode, seri_utama)
);
