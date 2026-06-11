# Recommender Runtime Decision 2026-06-09

## Keputusan

Dataset runtime wisata memakai:

`Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv`

Alasannya sederhana: media active candidate sudah penuh, sentiment sudah hampir penuh, dan dataset ini memuat update manual/fallback terbaru tanpa menimpa checkpoint lama.

## Contract

- `tfidf_linearsvc` tetap sumber utama sentiment NLP.
- `google_maps_stars_fallback` boleh dipakai sebagai fallback sentiment, tetapi harus tetap terlihat sebagai fallback.
- `manual_accepted` boleh dipakai untuk media hasil review manual.
- Data tanpa sentiment tetap boleh masuk sistem, tetapi confidence harus lebih rendah.

## Runtime

App sekarang diarahkan ke dataset runtime candidate secara default. Jika nanti perlu memakai file lain, gunakan environment variable:

`MUTERBANDUNG_DATASET_PATH`

## Audit

Audit API runtime terakhir:

- Gate: `PASS_WITH_WARNINGS`
- Query passed: `11`
- Warning: `1`
- Failed: `0`

Warning hanya untuk query oleh-oleh. Sistem tidak memaksakan hasil karena data khusus oleh-oleh belum kuat.

## Langkah Berikutnya

Lanjutkan tuning kecil pada query yang masih warning, lalu gunakan evaluation set yang sama setiap ada perubahan scoring.
