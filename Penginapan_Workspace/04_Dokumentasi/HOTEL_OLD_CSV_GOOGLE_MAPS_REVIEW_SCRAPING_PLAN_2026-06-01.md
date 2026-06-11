# Hotel Google Maps Review Scraping Plan - 2026-06-01

Generated at: `2026-06-01T15:32:55.925500Z`
Source dataset: `dataset_hotel\dataset_hotel_cimahi_semua_kolom (2).csv`
Target CSV: `Dataset\3_Curated\hotel_old_csv_google_maps_review_targets_2026-06-01.csv`
Batch folder: `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV`

## Ringkasan

- Total target hotel/penginapan: `181`
- Batch size: `25`
- Total batch: `8`
- Max reviews per target: `50`
- Estimasi maksimum review kalau semua berhasil: `9050`

## Segment Target

| Segment | Jumlah |
| --- | ---: |
| `apartment` | 65 |
| `guest_house` | 36 |
| `hotel` | 64 |
| `room_level_listing` | 5 |
| `vacation_rental` | 1 |
| `villa` | 10 |

## Prioritas Scraping

| Priority | Jumlah |
| --- | ---: |
| `P0_missing_rating_review` | 53 |
| `P1_low_review_confidence` | 53 |
| `P2_medium_review_confidence` | 48 |
| `P3_high_review_confidence` | 27 |

## File JSON Yang Dibuat

- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_test_10.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_all_181.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_01.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_02.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_03.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_04.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_05.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_06.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_07.json`
- `Apify_Workspace\Inputs\Hotel_Review_Batches_Old_CSV\apify_hotel_google_maps_reviews_batch_08.json`

## Cara Pakai

1. Jalankan batch test dulu: `apify_hotel_google_maps_reviews_test_10.json`. Test batch ini sengaja berisi target yang relatif jelas, bukan hanya data P0.
2. Setelah hasil test cocok dengan nama hotel/penginapan target, lanjutkan batch 01, 02, dan seterusnya.
3. Simpan output hasil scraper sebagai dataset baru, jangan langsung timpa dataset training.
4. Setelah review comment terkumpul, baru jalankan pipeline NLP/sentiment hotel.

## Catatan Penting

- Dataset hotel saat ini tidak punya `query_place_id` Google Maps, jadi target dibuat memakai Google Maps search URL berbasis nama dan koordinat.
- Karena belum memakai place id langsung, hasil scraper wajib dicek match-nya: nama hasil, koordinat, rating, dan alamat harus cocok.
- `maxCrawledPlacesPerSearch` dibuat `1` agar tiap query hanya mengambil satu tempat paling relevan.
- `reviewsSort` memakai `newest` agar komentar terbaru masuk terlebih dahulu.
- Untuk training NLP, jangan campur komentar hotel dengan wisata sebelum diberi label domain `hotel_review`.
