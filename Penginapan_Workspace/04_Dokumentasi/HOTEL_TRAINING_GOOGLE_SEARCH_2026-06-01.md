# Hotel Training Google Search Pipeline - 2026-06-01

Generated at: `2026-06-02T03:19:26.087141Z`
Input JSON: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\01_Raw_Data\google_hotels_search_json\dataset_google-hotels-search-scraper_2026-06-01_15-03-10-905.json`
Raw CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\01_Raw_Data\generated_raw_csv\HOTEL_GOOGLE_SEARCH_RAW_2026-06-01.csv`
Training CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv`

## Ringkasan Data

- Halaman hasil pencarian: `29`
- Record properti mentah: `511`
- Properti unik berdasarkan `property_token`: `446`
- Grup duplikat: `61`
- Baris duplikat yang disatukan: `65`

## Parameter Pencarian

| Parameter | Value |
| --- | ---: |
| `q` | penginapan in Kabupaten Bandung, Jawa Barat |
| `gl` | id |
| `hl` | id |
| `currency` | IDR |
| `check_in_date` | 2026-07-02 |
| `check_out_date` | 2026-07-03 |
| `adults` | 2 |
| `children` | 0 |
| `vacation_rentals` | True |
| `max_pages` | 55 |

## Segment Training

| Segment | Jumlah |
| --- | ---: |
| `vacation_rental` | 75 |
| `room_level_listing` | 24 |
| `villa` | 97 |
| `apartment` | 208 |
| `hotel` | 21 |
| `guest_house` | 21 |

## Quality Flags Training

| Flag | Terisi |
| --- | ---: |
| `coordinate_available` | 446 |
| `rating_available` | 270 |
| `price_available` | 414 |
| `amenities_available` | 430 |
| `image_available` | 445 |
| `source_link_available` | 288 |
| `checkin_checkout_available` | 364 |
| `nearby_places_available` | 264 |

## Review Confidence

| Label | Jumlah |
| --- | ---: |
| `low_review_confidence` | 229 |
| `missing_review_confidence` | 176 |
| `high_review_confidence` | 9 |
| `medium_review_confidence` | 32 |

## Readiness Training

| Level | Jumlah |
| --- | ---: |
| `strong_core_ready` | 255 |
| `recommendation_usable` | 431 |
| `minimal_usable` | 446 |

## Catatan Engineering

- File JSON berisi hasil pencarian Google Hotels per halaman, jadi proses pertama adalah flatten `properties` menjadi baris CSV.
- CSV raw menyimpan semua occurrence dari halaman pencarian.
- CSV training menyatukan duplikat berdasarkan `property_token` dan memilih baris dengan quality score terbaik.
- Dataset ini berasal dari pencarian dengan `vacation_rentals=True`, sehingga komposisinya cenderung kuat untuk villa, apartment, dan penginapan sewa.
- Sentiment di dataset ini adalah rating-based sentiment dari `overall_rating` dan `reviews`, bukan NLP komentar.
- Bayesian shrinkage tetap dipakai agar properti dengan review sedikit tidak terlalu percaya diri.
- Untuk LLM, gunakan `quality_flags`, `review_confidence_label`, dan `data_quality_score` sebelum membuat klaim harga, fasilitas, rating, atau visual.
