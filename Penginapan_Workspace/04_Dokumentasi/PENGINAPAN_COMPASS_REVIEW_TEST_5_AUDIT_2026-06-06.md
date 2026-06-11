# Audit Compass Google Maps Reviews Test 5 - 2026-06-06

## Ringkasan

| Metrik | Jumlah |
|---|---:|
| Target test | 5 |
| Review rows masuk | 121 |
| Review rows cocok ke query target | 121 |
| Baris dengan teks review | 80 |
| Baris dengan placeId | 121 |
| Unique searchString | 4 |
| Unique place title | 4 |
| Unique placeId | 5 |

## Kesimpulan

Actor Compass berhasil mengambil review dari URL search yang sebelumnya gagal di actor lain. Hasil test 5 menghasilkan review text, placeId, cid, title, URL place, dan metadata review.

## Keputusan

Compass bisa dipakai untuk tahap test berikutnya. Sebelum scraping massal, tetap perlu cek match per target dari file audit per-target.

## Output Audit

- Review normalized: `PENGINAPAN_COMPASS_REVIEW_TEST_5_RAW_NORMALIZED_2026-06-06.csv`
- Audit per target: `PENGINAPAN_COMPASS_REVIEW_TEST_5_PER_TARGET_AUDIT_2026-06-06.csv`
- Summary JSON: `penginapan_compass_review_test_5_audit_2026-06-06.json`
