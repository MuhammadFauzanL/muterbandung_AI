# Hotel Dataset Audit - 2026-05-28

## Files Checked

- `dataset_hotel/dataset_hotel_cimahi_semua_kolom (2).csv`
- `dataset_hotel/dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471 (1).csv`

## Summary

The hotel dataset is usable as a hotel/property master, but still needs cleaning and enrichment before becoming a reliable recommendation dataset.

The Google Maps review scraper file is not a hotel review dataset. It contains reviews for 11 places, mostly tourist/public places, not hotel properties. It should not be directly merged into the hotel dataset.

## Hotel Master Condition

- Rows: `181`
- Columns: `34`
- Unique hotel/property names: `181`
- Duplicate names: `0`
- Duplicate property tokens: `0`
- Rows with coordinates: `181/181`
- Rows with images: `180/181`
- Rows with overall rating: `128/181`
- Rows with review count: `128/181`
- Rows with amenities: `121/181`
- Rows with nightly price: `89/181`
- Rows with description: `24/181`
- Rows with hotel class: `40/181`

### Type Breakdown

- `hotel`: `133`
- `vacation rental`: `48`

### Rating And Price

- `overall_rating` count: `128`
- rating median: `4.3`
- rating min-max: `1.0` to `5.0`
- review count median: `55.5`
- review count max: `2426`
- nightly price median: `354145`
- nightly price min-max: `119271` to `2768916`

## Review Scraper Condition

- Rows: `8354`
- Columns: `139`
- Unique review IDs: `8354`
- Duplicate review IDs: `0`
- Unique Google place IDs: `11`
- Rows with stars: `8354/8354`
- Rows with text: `3753/8354`
- Rows without text: `4601/8354`
- Rows with translated text: `652/8354`
- Date range: `2017-09-29` to `2026-05-20`
- NLP-ready rows with stars and text: `3753`

### Places In Review File

- Sudut Pandang Bandung: `2420`
- Taman Alun-Alun Kota Cimahi: `1720`
- TOKO GOBERZ AUDIO MOBIL 97: `1654`
- Tahura Gunung Kunci: `1293`
- Taman Kartini: `540`
- Taman Lembah DEWATA: `476`
- Taman Love Soreang: `115`
- Taman Dewi Sartika: `40`
- Tafso Barn: `40`
- Taman Endog: `40`
- Southland Camp: `16`

## Main Risks

- The review file does not match the hotel master by exact name: `0` matches.
- In the review file, `name` is reviewer name, while `title` is the place name.
- Review dataset contains non-hotel and irrelevant place types, including `TOKO GOBERZ AUDIO MOBIL 97`.
- `Tafso Barn` is marked `permanentlyClosed=true`.
- Several review places are outside the intended hotel scope.
- Hotel master has many missing descriptions, amenities, prices, ratings, and hotel class values.

## Recommendation

Use `dataset_hotel_cimahi_semua_kolom (2).csv` as the base hotel master after cleaning.

Do not merge `dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471 (1).csv` into the hotel master as hotel sentiment. It should be treated as a separate tourism review dataset unless a new hotel-specific review scrape is available.

Recommended next actions:

1. Clean hotel master schema.
2. Normalize JSON-like fields: images, nearby places, ratings, reviews breakdown.
3. Normalize price columns into integer rupiah.
4. Add data quality labels: `rating_available`, `price_available`, `amenities_available`, `description_available`.
5. Remove or separate room-level/apartment listing variants from actual hotel-level entities.
6. Scrape or collect hotel-specific reviews if hotel sentiment/recommendation is required.
