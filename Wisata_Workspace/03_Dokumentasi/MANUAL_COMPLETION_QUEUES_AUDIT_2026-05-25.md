# Manual Completion Queues Audit - 2026-05-25

## Summary

- Media missing rows: 53
- Non-media data issues: 60
- Real-world verification rows: 213

## Output CSV

- `Dataset\3_Curated\manual_media_fill_queue.csv`
- `Dataset\3_Curated\manual_data_fill_queue.csv`
- `Dataset\3_Curated\manual_realworld_verification_queue.csv`

## Media Queue

```json
{
  "HIGH": 44,
  "LOW": 9
}
```

## Non-Media Data Queue

Issue counts:

```json
{
  "missing_value": 28,
  "sentiment_unavailable": 22,
  "verification_needed": 10
}
```

Priority counts:

```json
{
  "HIGH": 16,
  "LOW": 10,
  "MEDIUM": 34
}
```

## Real-World Verification Queue

```json
{
  "HIGH": 144,
  "MEDIUM": 69
}
```

## Fill Rules

- Isi kolom `new_*` atau `new_value` saja; jangan ubah kolom konteks lama saat review manual.
- Untuk media, minimal isi `new_media_image_url` atau `new_media_destination_url` dengan URL HTTP yang benar.
- Untuk data non-media, isi `source_url` bila mengambil dari sumber eksternal.
- Untuk real-world flags, isi `verified_flags_to_set_true` dengan nama flag yang sudah terbukti benar, dipisahkan `|`.
- Setelah selesai, jalankan pipeline apply/merge terpisah agar perubahan tetap auditable.
