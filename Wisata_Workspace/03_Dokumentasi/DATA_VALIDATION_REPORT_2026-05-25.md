# Data Validation Report - 2026-05-25

Schema version: `muterbandung.data_validation.v1`
Dataset: `Wisata_Workspace\01_Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
Data version: `DATABASE_WISATA_LABELED_V2_REVIEWED.csv:1779841323:514264`
Validated at: `2026-06-02T03:47:41.925336Z`

## Gate Status

DATA VALIDATION GATE: **PASS_WITH_WARNINGS**

| Metric | Value |
| --- | ---: |
| Rows | 234 |
| Columns | 87 |
| Unique location IDs | 234 |
| Active candidates | 209 |
| Error rows counted | 0 |
| Warning rows counted | 375 |
| Info rows counted | 139 |

## Status Distribution

| display_status | Count |
| --- | ---: |
| `active_candidate` | 209 |
| `exclude_scope` | 19 |
| `temporarily_hidden` | 3 |
| `status_uncertain` | 3 |

## Issues

| Severity | Code | Field | Count | Message |
| --- | --- | --- | ---: | --- |
| WARNING | `W_ACTIVE_COORDINATE_UNVERIFIED` | `coordinate_verified` | 9 | Active candidates with coordinate_verified=False should be treated carefully for distance claims. |
| WARNING | `W_ACTIVE_FACILITY_VERIFICATION_SPARSE` | `facility_verified_flags` | 146 | Active candidates with no verified facility flags require conservative LLM wording. |
| WARNING | `W_ACTIVE_MEDIA_UNAVAILABLE` | `media_available` | 39 | Active candidates without media need conservative UI/LLM presentation. |
| WARNING | `W_ACTIVE_RATING_MISSING` | `avg_rating` | 16 | Active candidates with missing avg_rating rely on runtime median fallback. |
| WARNING | `W_ACTIVE_SENTIMENT_UNAVAILABLE` | `sentiment_available` | 16 | Active candidates with unavailable sentiment need neutral/caveated LLM wording. |
| WARNING | `W_ACTIVE_VERIFICATION_MISSING` | `is_active_verified` | 147 | Active candidates missing is_active_verified must not be described as verified. |
| WARNING | `W_OPEN_24H_FLAG_HOURS_MISMATCH` | `open_24h_verified` | 1 | open_24h_verified=True should align with 00:00-23:59 weekday/weekend hours. |
| WARNING | `W_ZERO_PRICE_NOT_MARKED_FREE` | `price_type,price_max` | 1 | Rows with zero max price should usually be marked Gratis. |
| INFO | `I_ACTIVE_WEBSITE_MISSING` | `media_website` | 139 | Active candidates without official/reference website. |

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

### WARNING - W_ACTIVE_MEDIA_UNAVAILABLE

| Row | location_id | location_name |
| ---: | --- | --- |
| 18 | `LOC-017` | Cihampelas Walk |
| 121 | `LOC-120` | Rumah Guguk |
| 122 | `LOC-121` | NuArt Sculpture Park |
| 134 | `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) |
| 135 | `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) |
| 136 | `LOC-135` | Taman Main Mili-Mili & Hutan Mycelia |
| 140 | `LOC-139` | Kawah Rengganis Ciwidey |
| 149 | `LOC-148` | Pesona Nirwana Waterpark |
| 150 | `LOC-149` | Taman Wisata Alam Cimanggu |
| 159 | `LOC-158` | Situ Ninah (Situ Datar) |

### WARNING - W_ACTIVE_RATING_MISSING

| Row | location_id | location_name |
| ---: | --- | --- |
| 30 | `LOC-029` | Dusun Bambu |
| 69 | `LOC-068` | Pasar Cimindi |
| 134 | `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) |
| 135 | `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) |
| 153 | `LOC-152` | Kebun Teh Rancabali |
| 156 | `LOC-155` | Curug Panganten |
| 163 | `LOC-162` | Rumah Putih Cukul |
| 175 | `LOC-174` | Lereng Anteng Panoramic Coffee |
| 177 | `LOC-176` | Padepokan Dayang Sumbi |
| 193 | `LOC-192` | Curug Ngebul Gununghalu |

### WARNING - W_ACTIVE_SENTIMENT_UNAVAILABLE

| Row | location_id | location_name |
| ---: | --- | --- |
| 30 | `LOC-029` | Dusun Bambu |
| 69 | `LOC-068` | Pasar Cimindi |
| 134 | `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) |
| 135 | `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) |
| 153 | `LOC-152` | Kebun Teh Rancabali |
| 156 | `LOC-155` | Curug Panganten |
| 163 | `LOC-162` | Rumah Putih Cukul |
| 175 | `LOC-174` | Lereng Anteng Panoramic Coffee |
| 177 | `LOC-176` | Padepokan Dayang Sumbi |
| 193 | `LOC-192` | Curug Ngebul Gununghalu |

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

### WARNING - W_OPEN_24H_FLAG_HOURS_MISMATCH

| Row | location_id | location_name |
| ---: | --- | --- |
| 135 | `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) |

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
