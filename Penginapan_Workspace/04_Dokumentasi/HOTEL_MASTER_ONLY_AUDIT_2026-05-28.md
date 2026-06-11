# Hotel Master Only Audit - 2026-05-28

File audited:

`dataset_hotel/dataset_hotel_cimahi_semua_kolom (2).csv`

## Executive Summary

File ini layak dipakai sebagai **base dataset hotel/properti**, tetapi belum siap langsung menjadi dataset final rekomendasi.

Masalah utama:

- Banyak field penting kosong.
- Hotel, guest house, villa, homestay, apartemen, dan room-level listing masih bercampur.
- Beberapa entitas terlihat sebagai unit/kamar, bukan properti utama.
- Harga hanya tersedia untuk sekitar setengah data.
- Rating/review tersedia untuk sekitar 70% data, tetapi sebagian review count rendah.
- Data JSON seperti `images`, `nearby_places`, `ratings`, dan `reviews_breakdown` perlu dinormalisasi.

## Shape

- Rows: `181`
- Columns: `34`
- Unique names: `181`
- Duplicate names: `0`
- Duplicate property tokens: `0`
- Coordinate filled: `181/181`

## Type Breakdown

| Type | Count |
| --- | ---: |
| `hotel` | 133 |
| `vacation rental` | 48 |

## Important Completeness

| Field | Filled | Missing | Missing % |
| --- | ---: | ---: | ---: |
| `name` | 181 | 0 | 0.0 |
| `property_token` | 181 | 0 | 0.0 |
| `gps_coordinates_latitude/longitude` | 181 | 0 | 0.0 |
| `images` | 180 | 1 | 0.6 |
| `location_rating` | 157 | 24 | 13.3 |
| `overall_rating` | 128 | 53 | 29.3 |
| `reviews` | 128 | 53 | 29.3 |
| `amenities` | 121 | 60 | 33.1 |
| `link` | 94 | 87 | 48.1 |
| `rate_per_night_extracted_lowest` | 89 | 92 | 50.8 |
| `check_in_time` | 91 | 90 | 49.7 |
| `check_out_time` | 89 | 92 | 50.8 |
| `hotel_class` | 40 | 141 | 77.9 |
| `description` | 24 | 157 | 86.7 |
| `reviews_breakdown` | 18 | 163 | 90.1 |

## Numeric Summary

| Metric | Count | Median | Min | Max |
| --- | ---: | ---: | ---: | ---: |
| `overall_rating` | 128 | 4.3 | 1.0 | 5.0 |
| `reviews` | 128 | 55.5 | 1 | 2426 |
| `location_rating` | 157 | 3.2 | 2.6 | 4.5 |
| `rate_per_night_extracted_lowest` | 89 | 354145 | 119271 | 2768916 |
| `extracted_hotel_class` | 40 | 2 | 1 | 4 |

## Readiness Estimate

| Readiness Definition | Count |
| --- | ---: |
| Strong core ready: coordinates + image + rating + reviews + price + amenities | 41 |
| Usable without requiring price: coordinates + image + rating + reviews + amenities | 83 |
| Minimal usable: coordinates + image + at least one of rating/price/amenities | 166 |
| Needs major completion | 15 |

## Rating Confidence

| Review Count Bucket | Count |
| --- | ---: |
| Missing rating/reviews | 53 |
| 0-9 reviews | 40 |
| 10-49 reviews | 21 |
| 50-199 reviews | 40 |
| 200+ reviews | 27 |

Interpretation:

Many rows have low review confidence. A hotel with rating `5.0` but only a few reviews should not outrank a hotel with rating `4.3` and hundreds/thousands of reviews without adjustment.

## JSON Field Audit

| Field | Parsed | Failed | Blank | Notes |
| --- | ---: | ---: | ---: | --- |
| `nearby_places` | 157 | 0 | 24 | List data; should be normalized. |
| `images` | 180 | 0 | 1 | Mostly 9 images per row. |
| `ratings` | 118 | 0 | 63 | Star distribution available for some rows. |
| `reviews_breakdown` | 18 | 0 | 163 | Sparse but useful for sentiment-like hotel aspects. |

## Duplicate / Entity Quality

No exact duplicate names or property tokens were found.

However, there are coordinate duplicates, mainly around Gateway Pasteur apartment listings:

- `OYO 94155 Gateway Pasteur Apartment By Goodtime`
- `OYO 94150 Gateway Apartment Pasteur By Eldian`
- `OYO 94158 Gateway Pasteur Apartment By Iyan`
- `Ouma Gateway Pasteur Apartment`
- `Sewa Apartemen Bandung`

These should be reviewed because they may represent different room/unit listings in the same building, not unique hotel destinations.

## Suspicious Entity Groups

| Group | Count | Meaning |
| --- | ---: | --- |
| Room-level keywords | 18 | Looks like room/unit packages, not property-level entities. |
| Apartment/unit keywords | 63 | Many apartment and Gateway Pasteur unit listings. |
| OYO/RedDoorz/Collection/Sans | 41 | Chain/budget listings; may contain duplicates or room-level variants. |
| Villa/homestay/guesthouse/residence | 51 | Should be separated from hotel category or tagged carefully. |

## Top Reviewed Properties

- Valore Hotel Cimahi: rating `4.0`, reviews `2426`
- Sari Ater Kamboti Bandung: rating `4.6`, reviews `1808`
- Hotel Cassadua: rating `3.8`, reviews `935`
- Cottonwood Bed & Breakfast House Bandung: rating `4.6`, reviews `853`
- Hotel Tjimahi: rating `3.9`, reviews `761`
- Collection O 818 Micasa Residence: rating `3.5`, reviews `751`
- LN9 Bandung Guest House: rating `4.3`, reviews `585`
- Homestay Budihouse: rating `4.1`, reviews `577`

## Low-Rating Rows With Meaningful Review Count

These should not be ranked highly without caveats:

- Collection O 90205 Queen Rent Apartment Gateway Pasteur: rating `1.8`, reviews `89`
- OYO 94118 Homestayque Syariah: rating `2.2`, reviews `10`
- SPOT ON 91832 Pondok Aqueduct: rating `2.4`, reviews `18`
- RedDoorz near Exit Toll Pasteur 4: rating `2.8`, reviews `74`
- High Livin Apartment Pasteur: rating `3.0`, reviews `50`

## Cleaning Recommendations

1. Create canonical hotel schema.
2. Keep these core fields:
   - `hotel_id`
   - `name`
   - `property_type`
   - `latitude`
   - `longitude`
   - `overall_rating`
   - `reviews`
   - `price_lowest`
   - `check_in_time`
   - `check_out_time`
   - `hotel_class`
   - `amenities`
   - `primary_image_url`
   - `source_link`
3. Parse JSON-like columns into normalized helper columns:
   - `primary_image_url`
   - `image_count`
   - `nearby_place_count`
   - `rating_5_count`
   - `rating_1_count`
4. Add quality flags:
   - `rating_available`
   - `price_available`
   - `amenities_available`
   - `description_available`
   - `is_room_level_listing`
   - `is_apartment_listing`
   - `review_confidence`
5. Separate hotels from:
   - vacation rentals
   - apartment units
   - room-level listings
   - villas/homestays/guesthouses
6. Apply adjusted scoring:
   - Bayesian rating adjustment
   - review confidence labels
   - price availability penalty
   - low-rating warning

## Final Assessment

Use this file as the **starting point for hotel recommendation data**, not as final production data.

Current state:

`GOOD BASE DATASET, NEEDS CLEANING BEFORE LLM/RECOMMENDER`
