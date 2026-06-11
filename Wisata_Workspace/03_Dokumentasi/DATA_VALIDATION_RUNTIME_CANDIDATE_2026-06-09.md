# Data Validation Report - 2026-05-25

Schema version: `muterbandung.data_validation.v1`
Dataset: `.\Wisata_Workspace\01_Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv`
Data version: `DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv:1780976783:563685`
Validated at: `2026-06-09T03:46:40.120369Z`

## Gate Status

DATA VALIDATION GATE: **PASS_WITH_WARNINGS**

| Metric | Value |
| --- | ---: |
| Rows | 234 |
| Columns | 87 |
| Unique location IDs | 234 |
| Active candidates | 207 |
| Error rows counted | 0 |
| Warning rows counted | 300 |
| Info rows counted | 137 |

## Status Distribution

| display_status | Count |
| --- | ---: |
| `active_candidate` | 207 |
| `exclude_scope` | 21 |
| `temporarily_hidden` | 3 |
| `status_uncertain` | 3 |

## Issues

| Severity | Code | Field | Count | Message |
| --- | --- | --- | ---: | --- |
| WARNING | `W_ACTIVE_COORDINATE_UNVERIFIED` | `coordinate_verified` | 9 | Active candidates with coordinate_verified=False should be treated carefully for distance claims. |
| WARNING | `W_ACTIVE_FACILITY_VERIFICATION_SPARSE` | `facility_verified_flags` | 144 | Active candidates with no verified facility flags require conservative LLM wording. |
| WARNING | `W_ACTIVE_VERIFICATION_MISSING` | `is_active_verified` | 146 | Active candidates missing is_active_verified must not be described as verified. |
| WARNING | `W_ZERO_PRICE_NOT_MARKED_FREE` | `price_type,price_max` | 1 | Rows with zero max price should usually be marked Gratis. |
| INFO | `I_ACTIVE_WEBSITE_MISSING` | `media_website` | 137 | Active candidates without official/reference website. |

## Sample Rows

### WARNING - W_ACTIVE_COORDINATE_UNVERIFIED

| Row | location_id | location_name |
| ---: | --- | --- |
| 24 | `LOC-023` | Curug Malela |
| 45 | `LOC-044` | Jans Park (Jatinangor National Park) |
| 70 | `LOC-069` | Pemandian Cipanas Cileungsing |
| 117 | `LOC-116` | Wisata Kampoeng Ciherang |
| 139 | `LOC-138` | Kebun Teh Sukawana |
| 156 | `LOC-155` | Curug Panganten |
| 159 | `LOC-158` | Situ Ninah (Situ Datar) |
| 163 | `LOC-162` | Rumah Putih Cukul |
| 167 | `LOC-166` | Muara Rahong Hills |

### WARNING - W_ACTIVE_FACILITY_VERIFICATION_SPARSE

| Row | location_id | location_name |
| ---: | --- | --- |
| 12 | `LOC-011` | Bukit Jamur Rancabolang Pasirjambu |
| 13 | `LOC-012` | Bukit Moko Bandung |
| 14 | `LOC-013` | Bukit Senyum |
| 15 | `LOC-014` | Bumi Perkemahan Ranca Upas Bandung |
| 20 | `LOC-019` | Cimahi Techno Park |
| 21 | `LOC-020` | Ciwidey Valley Resort |
| 22 | `LOC-021` | Curug Cipanas |
| 23 | `LOC-022` | Curug Gorobog |
| 24 | `LOC-023` | Curug Malela |
| 25 | `LOC-024` | Curug Maribaya |

### WARNING - W_ACTIVE_VERIFICATION_MISSING

| Row | location_id | location_name |
| ---: | --- | --- |
| 2 | `LOC-001` | 23 Paskal Shopping Center |
| 3 | `LOC-002` | Alam Wisata Cimahi |
| 4 | `LOC-003` | Alun-Alun Kota Bandung |
| 6 | `LOC-005` | Amazing Artgames |
| 7 | `LOC-006` | Bandung Carnival Land |
| 8 | `LOC-007` | Bandung Indah Plaza |
| 11 | `LOC-010` | Braga Citywalk |
| 12 | `LOC-011` | Bukit Jamur Rancabolang Pasirjambu |
| 13 | `LOC-012` | Bukit Moko Bandung |
| 14 | `LOC-013` | Bukit Senyum |

### WARNING - W_ZERO_PRICE_NOT_MARKED_FREE

| Row | location_id | location_name |
| ---: | --- | --- |
| 234 | `LOC-233` | Kampung Wisata Pangjugjugan |

### INFO - I_ACTIVE_WEBSITE_MISSING

| Row | location_id | location_name |
| ---: | --- | --- |
| 3 | `LOC-002` | Alam Wisata Cimahi |
| 4 | `LOC-003` | Alun-Alun Kota Bandung |
| 7 | `LOC-006` | Bandung Carnival Land |
| 12 | `LOC-011` | Bukit Jamur Rancabolang Pasirjambu |
| 13 | `LOC-012` | Bukit Moko Bandung |
| 14 | `LOC-013` | Bukit Senyum |
| 18 | `LOC-017` | Cihampelas Walk |
| 19 | `LOC-018` | Cimahi Mall |
| 23 | `LOC-022` | Curug Gorobog |
| 24 | `LOC-023` | Curug Malela |

## LLM Readiness Interpretation

No blocking data contract errors were found. LLM integration can only proceed if warning fields remain guarded by evidence-pack caveats.
