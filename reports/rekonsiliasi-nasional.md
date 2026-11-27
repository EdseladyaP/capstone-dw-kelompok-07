# Rekonsiliasi Seri Nasional - Kasus 07

Tabel dibuat dari `data/gold/nasional.parquet` melalui pipeline.

Selisih dihitung sebagai nilai BPS dikurangi nilai WDI. Periode tanpa pasangan tetap dipertahankan, tetapi tidak dihitung sebagai selisih.

Seri var417 dan var1429 dicatat sebagai seri tanpa pembanding, bukan sebagai pasangan rekonsiliasi.

## Ringkasan Status dan Kategori

| id | seri_utama | status_pasangan | kategori | jumlah_periode |
|---|---|---|---|---|
| P1 | var1443 | berpasangan | definisi berbeda | 9 |
| P1 | var1443 | tanpa pasangan | cakupan berbeda | 46 |
| P2 | var1429 | tanpa pembanding |  | 11 |
| P2 | var417 | tanpa pembanding |  | 16 |

## Statistik Selisih

- Jumlah periode berpasangan: 9

- Median selisih BPS - WDI: -7.199020

## Tabel Rekonsiliasi

| id | periode | seri_utama | nilai_utama | seri_pembanding | nilai_pembanding | selisih | status_pasangan | kategori | dugaan | bukti |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 1970 | var1443 |  | SE.TER.ENRR | 2.80 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.7995400428772. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1972 | var1443 |  | SE.TER.ENRR | 2.73 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.72563004493713. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1973 | var1443 |  | SE.TER.ENRR | 2.66 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.65714001655579. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1974 | var1443 |  | SE.TER.ENRR | 2.56 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.55682992935181. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1975 | var1443 |  | SE.TER.ENRR | 2.56 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.55683994293213. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1976 | var1443 |  | SE.TER.ENRR | 2.59 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.59382009506226. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1977 | var1443 |  | SE.TER.ENRR | 2.30 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.29890990257263. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1978 | var1443 |  | SE.TER.ENRR | 2.44 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.43842005729675. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1979 | var1443 |  | SE.TER.ENRR | 2.34 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 2.3416600227356. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1980 | var1443 |  | SE.TER.ENRR | 3.37 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 3.36890006065369. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1981 | var1443 |  | SE.TER.ENRR | 3.85 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 3.84965991973877. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1982 | var1443 |  | SE.TER.ENRR | 3.87 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 3.86715006828308. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1983 | var1443 |  | SE.TER.ENRR | 4.07 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 4.07499980926514. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1984 | var1443 |  | SE.TER.ENRR | 5.33 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 5.33014011383057. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1985 | var1443 |  | SE.TER.ENRR | 6.10 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 6.09567022323608. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1986 | var1443 |  | SE.TER.ENRR | 6.33 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 6.33362007141113. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1987 | var1443 |  | SE.TER.ENRR | 7.51 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 7.50644016265869. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1988 | var1443 |  | SE.TER.ENRR | 6.79 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 6.79020977020264. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1989 | var1443 |  | SE.TER.ENRR | 7.85 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 7.84708976745605. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1990 | var1443 |  | SE.TER.ENRR | 8.30 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 8.29506015777588. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1991 | var1443 |  | SE.TER.ENRR | 8.55 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 8.55126953125. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1992 | var1443 |  | SE.TER.ENRR | 9.38 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 9.37843990325928. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1993 | var1443 |  | SE.TER.ENRR | 9.34 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 9.33967018127441. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1994 | var1443 |  | SE.TER.ENRR | 10.50 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 10.4964103698731. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1995 | var1443 |  | SE.TER.ENRR | 11.30 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 11.301739692688. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1996 | var1443 |  | SE.TER.ENRR | 11.52 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 11.5222902297974. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1997 | var1443 |  | SE.TER.ENRR | 13.36 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 13.3638401031494. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1998 | var1443 |  | SE.TER.ENRR | 13.33 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 13.3347997665405. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 1999 | var1443 |  | SE.TER.ENRR | 14.69 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 14.6863803863525. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |
| P1 | 2000 | var1443 |  | SE.TER.ENRR | 14.81 |  | tanpa pasangan | cakupan berbeda | Periode ini belum dapat dibandingkan karena salah satu sumber tidak menyediakan nilai pada cakupan periode yang tersedia. | Nilai BPS: nan; nilai WDI: 14.810640335083. Periode dipertahankan melalui outer join, tanpa melakukan imputasi atau mengisi selisih. |

File lengkap: `data/gold/rekonsiliasi_nasional.parquet` dan `reports/rekonsiliasi-nasional.csv`.
