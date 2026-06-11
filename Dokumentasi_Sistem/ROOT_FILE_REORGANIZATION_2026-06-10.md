# Root File Reorganization - 2026-06-10

Tujuan: merapikan file proses yang masih berada di root project agar masuk ke workspace yang sesuai.

## File Dipindahkan

| File asal | Lokasi baru | Catatan |
|---|---|---|
| `Penginapan_Workspace/Untitled3.ipynb` | `Penginapan_Workspace/03_Notebooks/penginapan_sentiment_training.ipynb` | Notebook training sentiment penginapan |
| `Penginapan_Workspace/model_sentimen_muterbandung (1).pkl` | `Penginapan_Workspace/07_Models/model_sentimen_muterbandung.pkl` | Model TF-IDF + SVM sentiment penginapan |
| `dataset_Google-Maps-Reviews-Scraper_2026-06-09_01-55-17-270.json` | `Wisata_Workspace/04_Apify_Workspace/Outputs/` | Raw review wisata |
| `dataset_Google-Maps-Reviews-Scraper_2026-06-09_02-16-12-254.json` | `Wisata_Workspace/04_Apify_Workspace/Outputs/` | Raw review wisata |
| `dataset_Google-Maps-Reviews-Scraper_2026-06-09_12-16-50-058.json` | `OlehOleh_Workspace/05_Review_Scraping/raw_outputs/duplicate_root_copies_2026-06-10/` | Root copy, target utama sudah ada |
| `dataset_Google-Maps-Reviews-Scraper_2026-06-09_13-42-53-867.json` | `OlehOleh_Workspace/05_Review_Scraping/raw_outputs/duplicate_root_copies_2026-06-10/` | Root copy, target utama sudah ada |
| `dataset_crawler-google-places_2026-06-09_09-19-46-159.csv` | `OlehOleh_Workspace/01_Raw_Data/google_maps_search_csv/duplicate_root_copies_2026-06-10/` | Root copy, target utama sudah ada |
| `Salinan dataset_google-hotels-search-scraper_2026-06-01_04-11-29-697.json` | `Penginapan_Workspace/01_Raw_Data/google_hotels_search_json/duplicate_root_copies_2026-06-10/` | Root copy, target utama sudah ada |
| `OLEH_OLEH_MANUAL_COMPLETION_PRICE_PRODUCT_FILLED_2026-06-10.csv` | `OlehOleh_Workspace/03_Curated/` | Manual completion oleh-oleh |
| `Daftar_Destinasi_Wisata_Bandung_Professional.xlsx` | `Wisata_Workspace/01_Dataset/3_Curated/media_manual_workbook_backup_2026-06-09/` | Workbook manual media wisata |

## Kondisi Setelah Dipindahkan

Root project hanya menyisakan file konfigurasi, dokumentasi utama, dan folder workspace.

File raw dan file proses sekarang masuk ke workspace masing-masing:

| Workspace | Isi utama |
|---|---|
| `Wisata_Workspace` | Dataset, raw review wisata, manual workbook wisata |
| `OlehOleh_Workspace` | Raw discovery, raw review, curated oleh-oleh |
| `Penginapan_Workspace` | Dataset hotel, notebook sentiment, model sentiment |

Catatan: file duplikat yang hash-nya sama tidak dihapus. Root copy dipindahkan ke folder `duplicate_root_copies_2026-06-10`.
