# PETA LENGKAP PROYEK MUTERBANDUNG (VERSI FINAL)
## Rekam Jejak Data dari Langkah Pertama Hingga Terakhir
**Tanggal Audit Menyeluruh:** 21 Mei 2026 (Revisi ke-2 - Penggalian Mendalam)

---

## FASE 0: PENGAMBILAN DATA AWAL (Open Data Bandung + Google Colab)
**Sumber:** API `opendata.bandung.go.id` (3 Endpoint Pemerintah)
**Didokumentasikan di:** `Notebooks/wisata_traning.ipynb` (Cell 1-6, dijalankan di Google Colab)
**Proses yang Terjadi:**
1. Cell 1-2: Mengambil 326 data wisata belanja dari endpoint `objek_wisata_belanja_di_kota_bandung_2`. Kolom asli: `nama_objek_wisata`, `kategori`, `alamat`, `titik_koordinat`. Kemudian di-rename menjadi `location_name`, `category_official`, `address`, `coordinate`.
2. Cell 3: Mengambil 34 data wisata sejarah/religi dari endpoint `objek_wisata_pendidikan_sejarah_religi_budaya`. Dilengkapi proses *Geocoding* (mencari GPS dari alamat) menggunakan `geopy.Nominatim`. Hasilnya: hanya 3 dari 34 berhasil mendapat koordinat.
3. Cell 4: Mengambil 44 data tempat wisata dari endpoint `tempat_wisata_di_kota_bandung`. Juga di-*Geocode*. Hasilnya: hanya 5 dari 44 berhasil.
4. Cell 5: Fungsi `audit_folder()` yang mengaudit 3 file CSV hasil download dari Google Drive. Menemukan bahwa banyak kolom kritis (`latitude`, `longitude`, `category`) yang belum lengkap.
5. Cell 6: Audit kedua yang memindai 8 file CSV ulasan mentah di Google Drive (termasuk `datatset_mentah_kabbandungbarat.csv` yang berisi data dari Bukit Senyum, dll).
**Output File:**
- `Dataset/data_pariwisata_clean.csv` (326 baris)
- `Dataset/data_tempat_wisata_bandung_2024.csv` (44 baris)
- `Dataset/jenis_kawasan_wisata_primer_di_kota_bandung_2.csv` (91 baris, referensi kawasan ekowisata)
- `Dataset/daftar_perusahaan_jasa_perjalanan_wisata_di_kota_bandung.csv` (239 baris, daftar perusahaan travel - TIDAK dipakai di pipeline utama)

---

## FASE 1: SCRAPING ULASAN GOOGLE MAPS (Selenium Manual + Chrome Extension)
**Sumber:** Google Maps via Selenium Python
**Lokasi Skrip:**
- `Scraping/place_scraper.py` (Skrip utama, 5.9 KB)
- `Scraping/coba.py` (Skrip eksperimental, 26 KB - kemungkinan versi awal/percobaan)
- `Scraping/coba1.py` (Versi mini, 2.2 KB)
**Daftar URL Target:**
- `Scraping/urls_kota_bandung.txt` (1.4 KB)
- `Scraping/urls_kabupaten_bandung.txt` (0.8 KB)
- `Scraping/urls_kabupaten_bandung_barat.txt` (0.6 KB)
- `Scraping/urls_kota_cimahi.txt` (0.5 KB)
- `Scraping/urls_sumedang.txt` (0.5 KB)
- `Scraping/places_urls.txt` (2 KB - daftar gabungan)
**Output Mentah:**
- `Dataset/dataset_mentah_kabbandung.csv` (1.55 MB - Ulasan raw Kab. Bandung)
- `Dataset/datatset_mentah_kotabandung.csv` (2.37 MB - Ulasan raw Kota Bandung. Catatan: ada typo "datatset")
- `Scraping/ulasan_jl_braga.csv` (138 KB - Ulasan khusus Jl. Braga, kemungkinan hasil uji coba awal)
**Output Setelah Cleaning Manual:**
- `Dataset/dataset_cleaned_kabbandung.csv` (1.42 MB)
- `Dataset/dataset_cleaned_kotabandung.csv` (2.09 MB)
**Catatan Penting:** Folder `Scraping/` juga berisi folder `venv/` (virtual environment Python) dan folder `.git/` (version control).

---

## FASE 2: SCRAPING ULASAN MASSAL (Apify Cloud Platform)
**Sumber:** Apify Actor `Google Maps Reviews Scraper` & `Google Maps Extractor`
**Konfigurasi:** `Apify_Workspace/Inputs/` (berisi file JSON konfigurasi)
**Proses:** Menjalankan scraper di cloud Apify untuk batch scraping ribuan ulasan Google Maps secara otomatis.
**Output Utama (Barang Bukti Mentah Tersimpan):**

| File | Ukuran | Isi |
|---|---|---|
| `Dataset/apify_reviews_tambahan_batch1.csv` | 15 MB | Ulasan batch scraping terbesar |
| `Dataset/apify_reviews_tambahan_batch2.csv` | 12.8 MB | Ulasan batch scraping kedua |
| `Dataset/apify_reviews_tambahan.csv` | 0.21 MB | Batch minor awal |
| `Dataset/apify_reviews_tambahan2.csv` | 0.14 MB | Batch minor kedua |
| `Dataset/apify_reviews_tambahan_v3_partial.csv` | 2.91 MB | Batch parsial ketiga |
| `Dataset/apify_reviews_part1.json` | 3.98 MB | Format JSON batch 1 |
| `Dataset/apify_reviews_part2.json` | 2.42 MB | Format JSON batch 2 |
| `dataset_Google-Maps-Reviews-Scraper_*_13-14-48.csv` | 10.09 MB | File scraper di root (belum dipindahkan) |
| `dataset_Google-Maps-Reviews-Scraper_*_14-29-27.csv` | 8.26 MB | File scraper di root |
| `dataset_Google-Maps-Reviews-Scraper_*_14-33-45.csv` | 1.09 MB | File scraper di root |
| `dataset_Google-Maps-Reviews-Scraper_*_14-58-36.csv` | 14.16 MB | File scraper terbesar di root |

**Metadata Lokasi (Google Maps Extractor):**
| File | Ukuran | Isi |
|---|---|---|
| `Dataset/dataset_google-maps-extractor_*.csv` | 0.10 MB | Phone, Website, Alamat untuk 230 lokasi |
| `Dataset/apify_jam_buka_semua_lokasi_raw.csv` | 1.20 MB | Jam buka/tutup mentah dari Apify (digunakan oleh `enrich_tourism_metadata.py`) |

---

## FASE 3: PENGGABUNGAN & NORMALISASI (Data Engineering)
**Proses Utama:**

### 3A. Penggabungan Ulasan
**Skrip:** `Scripts/gabung_semua_review.py`
**Logika:** Skrip ini membaca `MASTER_REVIEWS_LABELED.csv` (data lama yang sudah punya label sentimen) sebagai BASE, lalu menggabungkannya dengan semua file `apify_reviews_tambahan*.csv`. Kolom Apify (`title`, `text`, `stars`, `name`) di-rename menjadi format seragam (`location_name`, `review_text`, `rating`, `reviewer_name`). Setelah itu dilakukan deduplikasi berdasarkan kunci `location_name + review_text`.
**Output:** `Dataset/MASTER_REVIEWS_ENRICHED.csv` (versi mentah ~42k baris)

### 3B. Normalisasi Nama Lokasi (14 Batch Manual!)
**Skrip:** `Scripts/apply_manual_batch1.py` hingga `Scripts/apply_manual_batch14.py` (14 file!)
**Logika:** Setiap batch berisi mapping manual dari nama lokasi yang salah/berbeda ke nama resmi di Master Database. Contoh: `'Alun-alun Kota Bandung'` -> `'Alun-Alun Kota Bandung'`, `'Bird Pavilion'` -> `'Bird & Bromelia Pavilion'`. Total ada ratusan pemetaan yang dikerjakan secara manual oleh AI Agent + User.
**Skrip Pendukung:**
- `Scripts/generate_mapping.py` (Pembuat peta otomatis via fuzzy matching)
- `Scripts/apply_normalization.py` (Skrip normalisasi gabungan)
**File Log:** `mismatched_locations.txt`, `proposed_location_mapping.json`

### 3C. File Arsip Antara (Intermediate Files)
Selama proses penggabungan yang panjang, beberapa file "antara" sempat lahir:
- `Dataset/master_reviews_gabungan.csv` (3.81 MB) - Gabungan mentah paling awal
- `Dataset/MASTER_REVIEWS_CLEANED.csv` (8.14 MB) - Versi awal setelah deduplikasi
- `Dataset/MASTER_REVIEWS_FINAL.csv` (4.57 MB) - Versi "final" sebelum enrichment

---

## FASE 4: ANALISIS SENTIMEN AWAL & ASPEK (Machine Learning Tradisional - SVM)
**Skrip Utama:**
- `Scripts/run_binary_sentiment.py` (Sentimen biner Positif/Negatif, model SVM)
- `Scripts/run_fase5_sentiment.py` (Pipeline sentimen + ekstraksi 5 aspek: Pemandangan, Harga, Fasilitas, Pelayanan, Keluarga)
- `Scripts/nlp_pipeline_step1.py` (Preprocessing NLP: lowercase, hapus stopwords via Sastrawi)
- `Scripts/run_nlp_full.py` (Pipeline NLP lengkap end-to-end)
**Input:** `Dataset/MASTER_REVIEWS_CLEANED.csv` (~15k ulasan lama)
**Output:**
- `Dataset/MASTER_REVIEWS_LABELED_BINARY.csv` (10.05 MB - Label biner)
- `Dataset/MASTER_REVIEWS_NLP.csv` (10.53 MB - Teks yang sudah dipreprocessing)
**Catatan:** Fase ini hanya memproses ~15k data lama. Setelah ~18k data baru dari Apify masuk, model ini menjadi usang.

---

## FASE METADATA: PENGAYAAN DATABASE WISATA
**Proses yang BELUM TERCATAT di laporan sebelumnya:**

### Pengisian Jam Buka dari Apify
**Skrip:** `Scripts/enrich_tourism_metadata.py`
**Input:**
1. `DATABASE_WISATA_DENGAN_METADATA.csv` (Master)
2. `Dataset/apify_jam_buka_semua_lokasi_raw.csv` (Data mentah jam buka dari Apify scraper)
3. `DATABASE_WISATA_VERIFIKASI_INTERNET_BATCH1.xlsx` (Data yang sudah diverifikasi manual via internet)
**Proses:** Skrip ini membaca jam operasional dari data Apify (format `openingHours/0/day`, `openingHours/0/hours`), lalu mem-*parse* string waktu (misal `08.00-17.00`) menjadi kolom terpisah (`jam_buka_weekday`, `jam_tutup_weekday`, `jam_buka_weekend`, `jam_tutup_weekend`). Jika ada data yang sudah diverifikasi di Excel, data Excel menimpa data Apify.
**Output:** `DATABASE_WISATA_DENGAN_METADATA.csv` (diperbarui *in-place*)

### Pengisian Deskripsi & Metadata Sintetis
**Skrip:** `Scripts/generate_metadata_sintetis.py`
**Proses:** Untuk lokasi yang deskripsinya masih kosong, skrip ini membuat deskripsi faktual otomatis berdasarkan nama lokasi dan kategorinya.

### Update Jam Buka
**Skrip:** `Scripts/update_opening_hours.py`
**Proses:** Pembaruan jam buka berdasarkan data scraping terbaru.

---

## FASE A (KRITIS): DEEP DATA CLEANSING (Credible Data Cleaning)
**Skrip:** `Scripts/credible_data_cleaning.py`
**Didokumentasikan di:** `Notebooks/wisata_traning.ipynb` (Sel bagian akhir)
**Proses 10 Langkah (Detil dari membaca kode sumber):**
1. **Backup Otomatis** ke `Dataset/Archives/MASTER_REVIEWS_ENRICHED_backup_preclean_*.csv`
2. **Muat data** dari `Dataset/MASTER_REVIEWS_ENRICHED.csv`
3. **Feature Selection:** Memangkas dari 160+ kolom menjadi 14 kolom inti: `location_name, reviewer_name, rating, review_text, source_file, panjang_teks, review_text_clean, review_nlp, aspek_pemandangan, aspek_harga, aspek_fasilitas, aspek_pelayanan, aspek_keluarga, jumlah_aspek_terdeteksi`
4. **Hapus Missing Values:** Buang baris tanpa `review_text`, `rating`, atau `location_name`
5. **Noise Filtering:** Buang teks < 5 karakter (spam)
6. **Deduplikasi:** Kunci `location_name + reviewer_name + review_text`
7. **Outlier Removal:** Hapus lokasi di luar cakupan (Gunung Pancar, Google Ann Arbor, Toko Goberz Audio Mobil, Curug Ngebul Cianjur, dll)
8. **Entity Resolution:** Normalisasi nama menggunakan `proposed_location_mapping.json` + mapping manual
9. **Referential Integrity Check:** Filter hanya ulasan yang `location_name`-nya ada di `DATABASE_WISATA_DENGAN_METADATA.csv`
10. **Simpan** hasil bersih kembali ke `Dataset/MASTER_REVIEWS_ENRICHED.csv` (overwrite)
**Input:** `Dataset/MASTER_REVIEWS_ENRICHED.csv` (~42k baris)
**Output:** `Dataset/MASTER_REVIEWS_ENRICHED.csv` (34.150 baris bersih)
**Backup:** `Dataset/Archives/MASTER_REVIEWS_ENRICHED_backup_preclean_20260521_105325.csv` (55 MB - bukti fisik data sebelum dicuci)

---

## FASE B (KRITIS): RETRAINING MODEL SENTIMEN

### B1: Model SVM Baseline (Lokal)
**Skrip:** `Scripts/run_nlp_pipeline_v2.py`
**Input:** `Dataset/MASTER_REVIEWS_ENRICHED.csv` (34.150 baris)
**Proses:** Text preprocessing (lowercase, regex), TF-IDF (10k fitur, unigram+bigram), LinearSVC training
**Output:**
- `Dataset/MASTER_REVIEWS_LABELED.csv` (18.37 MB - 34.003 ulasan + prediksi)
- `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv` (0.02 MB)
**Akurasi:** 86.47%

### B2: Model IndoBERT (Google Colab - GPU T4)
**Skrip Generator:** `Scripts/create_colab_notebook.py`
**Notebook Colab:** `MuterBandung_Colab_Package/Train_IndoBERT_MuterBandung.ipynb`
**Data Upload:** `MuterBandung_Colab_Package/MASTER_REVIEWS_ENRICHED.csv`
**Proses:** Fine-Tuning `indobenchmark/indobert-base-p1`, 3 Epochs, batch_size 16, warmup 500
**Output:**
- `Models/MuterBandung-IndoBERT-Sentiment/model.safetensors` (474.74 MB)
- `Models/MuterBandung-IndoBERT-Sentiment/tokenizer.json` (0.68 MB)
- `Models/MuterBandung-IndoBERT-Sentiment/config.json` (Arsitektur: BertForSequenceClassification, 50k vocab, 512 max_pos)
**Akurasi:** 89.91%, F1-Score: 87.68%

---

## FASE 7: MULTI-LABEL AUTO-TAGGING & DATABASE FINAL MERGING
**Skrip:** `Scripts/run_fase7_multilabel.py`
**Input:**
1. `Dataset/MASTER_REVIEWS_LABELED.csv` (34k ulasan + sentimen)
2. `DATABASE_WISATA_DENGAN_METADATA.csv` (234 lokasi + metadata)
3. `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv` (Rapor sentimen per lokasi)
**Proses:** Rule-Based Keyword Frequency Extraction (8 kategori: Alam, Ramah Anak, Spot Foto, Edukasi, Kuliner, Belanja, Santai/Healing, Wahana Ekstrem). Threshold 8% kemunculan kata kunci.
**Output:** `DATABASE_WISATA_FINAL_PARIPURNA.csv` (0.13 MB - 234 lokasi, DATABASE UTAMA FINAL)

---

## EVOLUSI DATABASE WISATA (Kronologis)
| Versi | File | Lokasi | Kolom Kunci | Status |
|---|---|---|---|---|
| V1 | `DATABASE_WISATA_FINAL_LENGKAP.csv` | 232 | Koordinat, harga, kategori | USANG |
| V2 | `DATABASE_WISATA_DENGAN_METADATA.csv` | 234 | + jam buka, deskripsi, tags sintetis | CADANGAN |
| V3 | `DATABASE_MUTERBANDUNG_ENGINE.csv` | ~232 | Prototipe engine awal | USANG |
| **V4 (FINAL)** | **`DATABASE_WISATA_FINAL_PARIPURNA.csv`** | **234** | **+ skor sentimen AI + multi-label** | **AKTIF** |

---

## SKRIP DOKUMENTASI & NOTEBOOK UPDATER
Skrip-skrip ini berfungsi menyuntikkan dokumentasi ke dalam Jupyter Notebook secara otomatis:
- `Scripts/update_notebook.py` - Update notebook dengan dokumentasi cleansing
- `Scripts/update_notebook_fase5.py` - Dokumentasi Fase 5
- `Scripts/update_notebook_fase6.py` - Dokumentasi Fase 6
- `Scripts/update_notebook_nlp.py` - Dokumentasi NLP Pipeline
- `Scripts/inject_lineage_to_notebook.py` - Suntikan bab Data Lineage ke awal notebook
- `Scripts/append_cleaning_eda.py` - Dokumentasi EDA & Cleaning
- `Scripts/append_fase4_notebook.py` - Dokumentasi Fase 4
- `Scripts/append_notebook.py` - Appender umum

---

## SKRIP AUDIT & INSPEKSI
Skrip-skrip ini digunakan untuk memeriksa kualitas data di berbagai tahap:
- `Scripts/audit_dataset.py` - Audit komprehensif dataset
- `Scripts/deep_audit.py` - Audit mendalam
- `Scripts/deep_eda.py` - Exploratory Data Analysis
- `Scripts/audit_model_output.py` - Audit hasil prediksi model
- `Scripts/audit_indobert_zip.py` - Audit file model IndoBERT
- `Scripts/cek_anomali_pre_fase5.py` - Pengecekan anomali sebelum Fase 5
- `Scripts/inspect_duplicates.py` - Inspeksi duplikat
- `Scripts/inspect_all_four.py` - Inspeksi 4 file utama
- `Scripts/inspect_raw_details.py` - Detail file mentah
- `Scripts/analyze_project_files.py` - Analisis kedudukan semua file

---

## FILE & FOLDER YANG TIDAK TERKAIT PIPELINE
| File/Folder | Keterangan | Rekomendasi |
|---|---|---|
| `Tugas_Kuliah/` | Tugas kuliah (Critical Thinking & Stress Management) | Pindahkan ke luar proyek |
| `Foto/` | 3 foto WhatsApp (kemungkinan dokumentasi meeting) | Pindahkan ke `Dokumentasi_Sistem/` |
| `Wisata-Extracted/` | Folder eksplorasi awal berisi sub-folder: `Cleaned/`, `Dataset Schema Seragam/`, `Pemisahan lat lang/`, `Pencarian Harga/` | SUDAH USANG, arsipkan |
| `MuterBandung-IndoBERT-Sentiment.zip` | 461 MB. File ZIP dari Colab. Sudah diekstrak ke `Models/` | BISA DIHAPUS |
| `MuterBandung_Colab_Package.zip` | 2.5 MB. Sudah diekstrak | BISA DIHAPUS |
| `Wisata-20260516T*.zip` | 7.9 MB. Data lama | BISA DIHAPUS |
| `GEMINI_WEB_CONTEXT_PROMPT.md` | Prompt untuk AI Gemini | Pindahkan ke `Dokumentasi_Sistem/` |
| `SKILL_CONTEXT_MUTERBANDUNG.md` | Context file untuk AI agent | Pindahkan ke `Dokumentasi_Sistem/` |
| `DATABASE_WISATA_DENGAN_METADATA.xlsx` | Duplikat Excel dari CSV | BISA DIHAPUS |
| `DATABASE_WISATA_VERIFIKASI_INTERNET_BATCH1.xlsx` | Data verifikasi jam buka manual | Arsipkan |
| `dataset_hotel_cimahi_semua_kolom.csv` | Data hotel Cimahi | KANDIDAT FASE 8 |
| `MuterBandung_Colab_Package/MASTER_REVIEWS_NLP.csv` | Salinan lama di folder Colab | BISA DIHAPUS |
| `MuterBandung_Colab_Package/IndoBERT_Colab.ipynb` | Notebook Colab versi lama | SUDAH DIGANTIKAN Train_IndoBERT*.ipynb |
| `Scraping/venv/` | Virtual environment Python | BISA DIHAPUS (bisa di-recreate) |
| `Dataset/71_lokasi_tanpa_jam_buka.csv` | Daftar lokasi tanpa jam buka (temporary) | Arsipkan |
| `Dataset/lokasi_perlu_tambahan_review.csv` | Daftar lokasi yang ulasannya kurang | Arsipkan |
| `Dataset/lokasi_yang_masih_kurang_final.csv` | Versi final daftar lokasi kurang | Arsipkan |
