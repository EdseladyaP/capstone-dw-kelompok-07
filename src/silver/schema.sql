CREATE TABLE IF NOT EXISTS silver_apk_pt (
    sumber          VARCHAR NOT NULL,
    seri_kode      VARCHAR NOT NULL,
    wilayah_kode   INTEGER NOT NULL,
    nama_wilayah  VARCHAR NOT NULL,
    periode        VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL,
    rincian        VARCHAR NOT NULL,
    nilai          DOUBLE NOT NULL,
    satuan         VARCHAR NOT NULL,
    _berkas_raw    VARCHAR NOT NULL,
    _sha256_raw    VARCHAR NOT NULL,

    PRIMARY KEY (
        sumber,
        seri_kode,
        wilayah_kode,
        periode,
        rincian,
        _berkas_raw
    )
);
