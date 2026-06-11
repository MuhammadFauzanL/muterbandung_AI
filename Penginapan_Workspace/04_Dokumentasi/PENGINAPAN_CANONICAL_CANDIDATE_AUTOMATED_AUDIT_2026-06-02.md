# Penginapan Canonical Candidate Automated Audit - 2026-06-02

Audit ini membaca `PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv` tanpa mengubah isi dataset.

## Gate

| Metrik | Nilai |
|---|---:|
| Gate | PASS_WITH_WARNINGS |
| Rows | 1656 |
| Columns | 44 |
| Total findings | 2944 |
| Rows affected | 1274 |

## Severity

| Severity | Jumlah |
|---|---:|
| MANUAL_REVIEW | 2474 |
| WARNING | 470 |

## Top Finding Codes

| Code | Jumlah |
|---|---:|
| OVERALL_RATING_MISSING | 666 |
| REVIEWS_MISSING | 666 |
| PRICE_LOWEST_MISSING | 637 |
| LINK_MISSING | 470 |
| POSSIBLE_DUPLICATE_NAME_COORD | 247 |
| AMENITIES_MISSING | 154 |
| ROOM_LEVEL_LISTING | 54 |
| PRIMARY_IMAGE_URL_MISSING | 50 |

## Property Type

| Property type | Jumlah |
|---|---:|
| hotel | 487 |
| apartment | 352 |
| villa | 342 |
| vacation_rental | 269 |
| guest_house | 152 |
| room_level_listing | 54 |

## Region Validation

| Region | Jumlah |
|---|---:|
| bandung_raya_valid | 1656 |

## Data Quality

| Quality label | Jumlah |
|---|---:|
| high | 1070 |
| medium | 541 |
| low | 45 |

## Output

- Findings CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_CANONICAL_CANDIDATE_AUTOMATED_AUDIT_FINDINGS_2026-06-02.csv`
- Manual review queue CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_MANUAL_REVIEW_QUEUE_AUTOMATED_AUDIT_2026-06-02.csv`
- Adjustment priority queue CSV: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_AUTOMATED_AUDIT_ADJUSTMENT_PRIORITY_2026-06-02.csv`

## Adjustment Priority Queue

| Priority | Jumlah |
|---|---:|
| P1 | 278 |

## Langkah Penyesuaian Yang Disarankan

1. P0: Jika ada ERROR, perbaiki sebelum candidate dipakai.
2. P1: Data tanpa koordinat tidak boleh dipakai untuk ranking jarak.
3. P1: Room-level listing jangan dihapus otomatis, tetapi turunkan prioritas ranking.
4. P1: Data tanpa amenities/gambar/harga/rating boleh dipakai dengan caveat, jangan diklaim lengkap oleh LLM.
5. P2: Possible duplicate name+coordinate perlu review manual sebelum final canonical.

## Catatan

- Banyak finding bertipe `MANUAL_REVIEW` bukan berarti data salah. Itu berarti data boleh dipakai, tetapi klaim/ranking harus hati-hati.
- Audit ini otomatis. Manual review utama cukup fokus ke `Adjustment Priority Queue`, bukan semua findings.
