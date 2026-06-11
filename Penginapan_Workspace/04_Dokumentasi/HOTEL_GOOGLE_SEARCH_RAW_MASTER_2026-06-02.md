# Hotel Google Search Raw Master - 2026-06-02

Dokumen ini mencatat proses konversi JSON Google Hotels Search menjadi CSV tabular raw master.

## Output

- Raw master CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\01_Raw_Data\generated_raw_csv\HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.csv`
- Source inventory CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\01_Raw_Data\generated_raw_csv\HOTEL_GOOGLE_SEARCH_JSON_SOURCE_INVENTORY_2026-06-02.csv`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| JSON source terdeteksi | 18 |
| JSON diproses | 17 |
| JSON duplicate file | 1 |
| Raw records | 2840 |
| Unique names raw | 1377 |
| Unique property token | 1519 |

## Source Bucket

| Bucket | Jumlah |
|---|---:|
| ads | 72 |
| properties | 2768 |

## Segment Properti

| Segment | Jumlah |
|---|---:|
| apartment | 415 |
| guest_house | 212 |
| hotel | 677 |
| room_level_listing | 99 |
| vacation_rental | 615 |
| villa | 822 |

## Query Area

| Query area | Jumlah |
|---|---:|
| Batujajar, Kabupaten Bandung Barat | 26 |
| Cikalongwetan, Kabupaten Bandung Barat | 186 |
| Cililin, Kabupaten Bandung Barat | 151 |
| Cipatat, Kabupaten Bandung Barat | 78 |
| Cipeundeuy, Kabupaten Bandung Barat | 164 |
| Cipongkor, Kabupaten Bandung Barat | 83 |
| Gununghalu, Kabupaten Bandung Barat | 115 |
| Kabupaten Bandung | 511 |
| Kota Bandung | 609 |
| Ngamprah, Kabupaten Bandung Barat | 14 |
| Padalarang, Kabupaten Bandung Barat | 83 |
| Pangalengan, Kabupaten Bandung | 106 |
| Pasirjambu, Kabupaten Bandung | 94 |
| Rongga, Kabupaten Bandung Barat | 211 |
| Saguling, Kabupaten Bandung Barat | 82 |
| Sindangkerta, Kabupaten Bandung Barat | 118 |
| West Bandung Regency | 209 |

## Duplicate File

- `dataset_google-hotels-search-scraper_2026-06-02_06-11-36-200.json` duplicate of `dataset_google-hotels-search-scraper_2026-06-02_06-11-36-200 (1).json`

## Catatan

- Tahap ini belum melakukan dedupe properti/canonical.
- File duplikat penuh berdasarkan SHA256 tidak diproses ke raw master.
- CSV raw master dipakai sebagai input tahap berikutnya: dedupe, region validation, property classification, dan canonical candidate.
