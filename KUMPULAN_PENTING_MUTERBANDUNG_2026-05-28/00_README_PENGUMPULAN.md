# Kumpulan File Penting MuterBandung - 2026-05-28

Folder ini adalah paket bersih untuk dikumpulkan atau direview. File asli di workspace utama tidak dipindah dan tidak dihapus; isi folder ini adalah salinan file penting saja.

## Struktur Folder

- `00_Setup`: file setup project, requirement, arsitektur, dan konfigurasi contoh.
- `01_Dataset_Final`: dataset curated terbaru, queue data completion, batch manual terbaru, dan master agent terbaru.
- `02_Training_Data`: data review/sentiment yang dipakai untuk workflow training dan NLP.
- `03_Notebooks_Training`: notebook utama, termasuk `wisata_training.ipynb` dan `wisata_traning.ipynb`.
- `04_Scripts_Inti`: script backend, recommender, guardrail LLM, validasi, apply data, dan test inti.
- `05_Dokumentasi_Audit`: dokumentasi setup, audit, validasi, LLM evidence, dan laporan batch terbaru.
- `06_Manual_Review`: file manual review Word/CSV yang relevan.
- `07_Model_Colab_Package`: paket Colab/model ringan. Full model besar tidak disalin agar folder tetap ringkas.
- `08_Evaluasi`: hasil evaluasi, QC, dan gambar audit.

## File Utama Yang Paling Penting

- `01_Dataset_Final/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
- `01_Dataset_Final/manual_review_batch3_remaining_46_after_status_facility_2026-05-27.csv`
- `03_Notebooks_Training/wisata_training.ipynb`
- `04_Scripts_Inti/app.py`
- `04_Scripts_Inti/recommender.py`
- `04_Scripts_Inti/validate_curated_dataset.py`
- `05_Dokumentasi_Audit/LOCAL_SETUP_FROM_ZERO_2026-05-25.md`
- `05_Dokumentasi_Audit/DATA_VALIDATION_REPORT_2026-05-25.md`
- `05_Dokumentasi_Audit/UPDATED_MASTER_STATUS_FACILITY_APPLY_2026-05-27.md`
- `MANIFEST_FILE_PENTING.csv`

## Yang Sengaja Tidak Dimasukkan

- `.venv_clean_verify` dan virtual environment lain.
- `logs`, file `.out.log`, `.err.log`, dan log server.
- `Codex_Backups`.
- Folder scraping/raw besar yang tidak dibutuhkan untuk review final.
- Backup dataset lama seperti `.bak_*`.
- Cache, `__pycache__`, dan file sementara.
- Full model weight besar di `Models/MuterBandung-IndoBERT-Sentiment` agar ukuran paket tetap aman.

## Status Terakhir

- Dataset validation: `PASS_WITH_WARNINGS`.
- Error validasi terakhir: `0`.
- Regression test terakhir: `42/42 PASS`.
- Batch manual lanjutan yang perlu diisi: `manual_review_batch3_remaining_46_after_status_facility_2026-05-27.csv`.

## Catatan

Paket ini bukan pengganti workspace penuh. Paket ini dibuat untuk pengumpulan/review agar file penting mudah ditemukan tanpa tercampur file eksperimen, log, backup, cache, dan raw scraping besar.
