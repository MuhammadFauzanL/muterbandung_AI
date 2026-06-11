# Hotel Canonical Pipeline - 2026-05-29

Generated at: `2026-05-29T06:18:52.528241Z`
Input: `dataset_hotel\dataset_hotel_cimahi_semua_kolom (2).csv`
Output: `Dataset\3_Curated\HOTEL_CANONICAL_CIMAHI_2026-05-29.csv`

## Summary

- Rows: `181`
- Columns: `76`
- Rating sentiment model version: `hotel_rating_sentiment_v1`
- Rating sentiment prior score: `0.6377`
- Review count p95 cap: `582.2`

## Property Segments

| Segment | Count |
| --- | ---: |
| `apartment` | 65 |
| `hotel` | 64 |
| `guest_house` | 36 |
| `villa` | 10 |
| `room_level_listing` | 5 |
| `vacation_rental` | 1 |

## Quality Flags

| Flag | Count |
| --- | ---: |
| `rating_available` | 128 |
| `price_available` | 89 |
| `amenities_available` | 121 |
| `image_available` | 180 |
| `description_available` | 24 |
| `source_link_available` | 94 |
| `reviews_breakdown_available` | 18 |

## Readiness

| Definition | Count |
| --- | ---: |
| `strong_core_ready` | 41 |
| `usable_without_price_required` | 83 |
| `minimal_usable` | 166 |

## Review Confidence

| Label | Count |
| --- | ---: |
| `missing_review_confidence` | 53 |
| `low_review_confidence` | 53 |
| `medium_review_confidence` | 48 |
| `high_review_confidence` | 27 |

## Rating Sentiment Source

| Source | Count |
| --- | ---: |
| `rating_distribution` | 118 |
| `unavailable` | 53 |
| `overall_rating_fallback` | 10 |

## Notes

- Sentiment here is `rating-derived sentiment`, not NLP over raw comments.
- `ratings` distribution is preferred when available.
- `overall_rating` is used only as fallback when star distribution is missing.
- Bayesian shrinkage is applied using p95 review count cap so very high review-count outliers do not dominate.
- Mixed entities are retained and labeled through `property_segment` instead of being removed.
