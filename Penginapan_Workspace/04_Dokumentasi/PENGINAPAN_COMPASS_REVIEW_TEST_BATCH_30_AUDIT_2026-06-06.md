# Audit Compass Google Maps Reviews Batch 30 - 2026-06-06

## Ringkasan

| Metrik | Jumlah |
|---|---:|
| Target batch | 30 |
| Target dengan review masuk | 28 |
| Target tidak muncul | 2 |
| Review rows masuk | 971 |
| Review dengan teks | 626 |
| Baris dengan placeId | 971 |
| Unique searchString | 28 |
| Unique place title | 33 |
| Unique placeId | 33 |

## Match Status

| Status | Jumlah |
|---|---:|
| strong_match | 27 |
| review_match | 1 |

## Kesimpulan

Compass berhasil mengambil review untuk mayoritas target batch 30. Hasil ini bisa dipakai sebagai bukti bahwa actor Compass lebih cocok untuk pipeline review penginapan dibanding actor sebelumnya.

Tetap perlu audit per target sebelum scraping massal, karena ada target yang tidak menghasilkan review dan ada kemungkinan satu query menghasilkan lebih dari satu placeId.

## Keputusan

Lanjutkan dengan pendekatan bertahap. Jangan langsung 1.140 target. Setelah batch 30 dicek, buat batch berikutnya 100-200 target dengan audit match yang sama.

## Output Audit

- Normalized review CSV: `PENGINAPAN_COMPASS_REVIEW_TEST_BATCH_30_RAW_NORMALIZED_2026-06-06.csv`
- Audit per target: `PENGINAPAN_COMPASS_REVIEW_TEST_BATCH_30_PER_TARGET_AUDIT_2026-06-06.csv`
- Missing targets: `PENGINAPAN_COMPASS_REVIEW_TEST_BATCH_30_MISSING_TARGETS_2026-06-06.csv`
- Summary JSON: `penginapan_compass_review_test_batch_30_audit_2026-06-06.json`
