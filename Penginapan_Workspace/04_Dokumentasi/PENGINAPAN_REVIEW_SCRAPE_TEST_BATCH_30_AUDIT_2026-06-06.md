# Audit Test Scrape Review Penginapan 30 Target - 2026-06-06

## Ringkasan

| Metrik | Jumlah |
|---|---:|
| Target batch test | 30 |
| Record JSON hasil scrape | 30 |
| Review berhasil masuk | 0 |
| Place berhasil dikenali tanpa review | 0 |
| Gagal resolve place | 30 |
| Baris dengan teks review | 0 |
| Baris dengan placeName | 0 |

## Kesimpulan

Batch test ini belum bisa dipakai untuk sentiment. Semua target gagal di-resolve sebagai Google Maps place, sehingga tidak ada `reviewId`, `text`, atau `placeName` yang valid.

Penyebab paling mungkin: actor yang dipakai membutuhkan URL place Google Maps yang spesifik, sedangkan input kita memakai URL search seperti `/maps/search/?api=1&query=...`.

## Keputusan

Jangan lanjut scraping massal dari format URL ini. Langkah berikutnya adalah mendapatkan `placeUrl` atau `placeId` dulu, atau memakai actor yang memang menerima search query dan bisa memilih hasil pertama.

## Output Audit

- CSV audit: `PENGINAPAN_REVIEW_SCRAPE_TEST_BATCH_30_AUDIT_2026-06-06.csv`
- JSON summary: `penginapan_review_scrape_test_batch_30_audit_2026-06-06.json`
