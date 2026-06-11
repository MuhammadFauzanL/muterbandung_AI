# Hotel Validation Report - 2026-05-29

Generated at: `2026-06-02T03:19:12.631791Z`
Dataset: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\HOTEL_CANONICAL_CIMAHI_2026-05-29.csv`
Gate: `PASS_WITH_WARNINGS`

## Summary

- Rows: `181`
- Columns: `76`
- Unique hotel IDs: `181`
- Errors: `0`
- Warnings: `469`

## Issues

| Severity | Code | Field | Count | Message |
| --- | --- | --- | ---: | --- |
| WARNING | `W_RATING_MISSING` | `rating_available` | 53 | Rows without rating/review count cannot be ranked by rating confidence. |
| WARNING | `W_PRICE_MISSING` | `price_available` | 92 | Rows without price should not be used for budget claims. |
| WARNING | `W_AMENITIES_MISSING` | `amenities_available` | 60 | Rows without amenities require conservative LLM wording. |
| WARNING | `W_DESCRIPTION_MISSING` | `description_available` | 157 | Rows without description need generated/curated description before rich LLM explanation. |
| WARNING | `W_IMAGE_MISSING` | `image_available` | 1 | Rows without primary image should not be used for visual cards. |
| WARNING | `W_LOW_REVIEW_CONFIDENCE` | `review_confidence_label` | 106 | Low/missing review confidence rows need shrinkage and cautious explanations. |

## Property Segments

| Segment | Count |
| --- | ---: |
| `apartment` | 65 |
| `hotel` | 64 |
| `guest_house` | 36 |
| `villa` | 10 |
| `room_level_listing` | 5 |
| `vacation_rental` | 1 |

## Review Confidence

| Label | Count |
| --- | ---: |
| `missing_review_confidence` | 53 |
| `low_review_confidence` | 53 |
| `medium_review_confidence` | 48 |
| `high_review_confidence` | 27 |

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
