# Media Fill Google Colab Workflow

## Status

```text
READY - MEDIA ONLY
```

Workflow ini dibuat karena Apify terlalu berat untuk kebutuhan pengisian media manual. Colab dipakai untuk membantu review dan validasi URL, bukan untuk menulis langsung ke dataset utama.

## Notebook

```text
Notebooks/Media_Fill_Google_Colab.ipynb
```

Input utama:

```text
Dataset/3_Curated/manual_media_fill_queue.csv
```

Output dari Colab:

```text
manual_media_fill_queue_completed.csv
media_manual_apply_ready.csv
```

## Alur

1. Upload `manual_media_fill_queue.csv` ke Colab.
2. Colab menampilkan link bantu Google Search, Google Maps, dan Google Images.
3. Isi kolom:
   - `new_media_image_url`
   - `new_media_destination_url`
   - `new_media_website`
   - `new_media_source_note`
   - `reviewer_status`
   - `reviewer_note`
4. Set `reviewer_status=approved` untuk baris yang siap diterapkan.
5. Jalankan validasi URL.
6. Download `media_manual_apply_ready.csv`.
7. Taruh file hasil download ke:

```text
Dataset/3_Curated/media_manual_apply_ready.csv
```

8. Jalankan preview lokal:

```powershell
python -B Scripts/apply_manual_media_updates.py --input Dataset/3_Curated/media_manual_apply_ready.csv --dry-run
```

9. Jika preview benar, apply ke dataset curated:

```powershell
python -B Scripts/apply_manual_media_updates.py --input Dataset/3_Curated/media_manual_apply_ready.csv --apply
```

Script apply selalu membuat backup sebelum menulis dataset utama.

## Safety Rules

- Minimal isi salah satu `new_media_image_url` atau `new_media_destination_url`.
- URL harus diawali `http://` atau `https://`.
- Colab hanya mengekspor hasil review; dataset utama tidak berubah sampai script apply lokal dijalankan.
- Setelah apply, jalankan unit test, groundtruth, dan QC live.

## Current Queue

Saat workflow dibuat:

- media missing rows: 53
- active candidate media missing: 44
- file queue sudah punya kolom link bantu:
  - `google_search_url`
  - `google_maps_search_url`
  - `google_image_search_url`
