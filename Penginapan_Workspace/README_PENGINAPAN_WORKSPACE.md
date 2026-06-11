# Penginapan Workspace

Workspace ini memisahkan proses dataset penginapan/hotel dari proses dataset wisata Muter Bandung.

## Struktur Folder

| Folder | Isi |
| --- | --- |
| `01_Raw_Data/dataset_hotel_original/` | Dataset hotel lama dari folder `dataset_hotel`. |
| `01_Raw_Data/google_hotels_search_json/` | JSON hasil Google Hotels Search Scraper. |
| `01_Raw_Data/generated_raw_csv/` | CSV raw hasil flatten/generate dari pipeline hotel. |
| `02_Curated/` | Dataset hotel canonical, training, summary, validation, dan target review scraping. |
| `03_Notebooks/` | Notebook khusus hotel/penginapan. |
| `04_Dokumentasi/` | Audit, validation report, pipeline report, dan scraping plan hotel. |
| `05_Apify_Review_Batches/` | JSON batch Apify untuk scraping review Google Maps hotel. |
| `06_Scripts/` | Script khusus pipeline hotel/penginapan. |

## Dataset Utama

| File | Fungsi |
| --- | --- |
| `02_Curated/HOTEL_CANONICAL_CIMAHI_2026-05-29.csv` | Dataset canonical hotel lama, 181 data. |
| `02_Curated/HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv` | Dataset training dari Google Hotels Search, 446 data unik. |
| `02_Curated/hotel_old_csv_google_maps_review_targets_2026-06-01.csv` | Target scraping review untuk dataset hotel lama. |
| `03_Notebooks/penginapan_training.ipynb` | Notebook khusus penginapan training. |

## Catatan Penting

- Dataset wisata tetap berada di folder `Dataset/` dan `Notebooks/wisata_training.ipynb`.
- Hotel/penginapan tidak boleh digabung langsung dengan wisata tanpa pipeline integrasi.
- Dataset hotel lama 181 data lebih aman untuk tahap scraping review pertama.
- Dataset Google Hotels Search 446 data berguna untuk perluasan, tetapi perlu dedup/fuzzy matching sebelum digabung.
- Semua script hotel di `06_Scripts/` sudah diarahkan agar membaca/menulis ke `Penginapan_Workspace`.

## Cara Menjalankan Pipeline Hotel

Jalankan dari root project `PIJAK`:

```powershell
.\.venv_clean_verify\Scripts\python.exe -B .\Penginapan_Workspace\06_Scripts\build_hotel_canonical_dataset.py
.\.venv_clean_verify\Scripts\python.exe -B .\Penginapan_Workspace\06_Scripts\validate_hotel_canonical_dataset.py
.\.venv_clean_verify\Scripts\python.exe -B .\Penginapan_Workspace\06_Scripts\build_hotel_training_from_google_hotels_json.py
.\.venv_clean_verify\Scripts\python.exe -B .\Penginapan_Workspace\06_Scripts\generate_hotel_google_maps_review_batches.py
```
