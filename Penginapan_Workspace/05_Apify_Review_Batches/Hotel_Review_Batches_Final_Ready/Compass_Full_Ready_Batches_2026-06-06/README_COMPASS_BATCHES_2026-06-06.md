# Compass Review Batches Penginapan - 2026-06-06

Folder ini berisi batch JSON untuk actor Compass Google Maps Reviews Scraper.

## Rekomendasi Pakai

Gunakan folder `remaining_1110_after_test30` terlebih dahulu, karena 30 target pertama sudah pernah discrape sebagai batch test.

Kalau ingin re-run semuanya dari awal, gunakan folder `all_1140`.

## Ringkasan

| Set | Target | Batch | Catatan |
|---|---:|---:|---|
| `remaining_1110_after_test30` | 1110 | 12 | Recommended, tidak mengulang batch test 30 |
| `all_1140` | 1140 | 12 | Re-run semua target final |
| skipped test batch | 30 | - | Sudah ada hasil scrape test |

## Setting JSON

```json
{
  "language": "id",
  "maxReviews": 30,
  "personalData": true,
  "startUrls": [
    {"url": "https://www.google.com/maps/search/?api=1&query=..."}
  ]
}
```

## Cara Bagi ke Teman

1. Bagikan satu file JSON batch ke satu orang.
2. Bagikan juga file `_index.csv` pasangannya.
3. Setelah scraping selesai, simpan output JSON dengan nama batch yang sama.
4. Audit wajib dilakukan per batch: jumlah target yang muncul, match title, review text, dan target missing.

## Catatan

Jangan langsung menggabungkan hasil scrape ke sentiment sebelum audit match selesai.
