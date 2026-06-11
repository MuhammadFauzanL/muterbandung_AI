# Notebook Index Wisata - 2026-06-08

Index ini dibuat untuk housekeeping notebook wisata. File ini tidak mengubah dataset dan tidak menggantikan notebook utama.

## Aturan Utama

- Notebook utama wisata adalah `wisata_training.ipynb`.
- Notebook legacy/Colab jangan dijalankan ulang sebelum input dan path diverifikasi.
- Notebook pendukung dipakai sesuai kebutuhan, bukan sebagai pipeline utama.
- Perubahan proses penting sebaiknya dicatat dengan pola: tujuan -> code/output -> keputusan.

## Status Notebook

| Notebook | Status | Fungsi | Aturan Pakai |
|---|---|---|---|
| `Data_Completion_Google_Colab.ipynb` | pendukung_completion | Workflow completion manual/Colab untuk data wisata. | Dipakai saat ada batch completion yang jelas. |
| `IndoBERT_Colab.ipynb` | colab_model_berat | Notebook training/evaluasi model berat di Colab. | Jalankan di Colab/GPU, bukan sebagai pipeline lokal utama. |
| `Media_Fill_Google_Colab.ipynb` | pendukung_enrichment | Workflow pengisian media/gambar dari Colab. | Dipakai saat perlu enrichment media, bukan ranking utama. |
| `NLP_Sentiment_Preparation.ipynb` | pendukung_sentiment | Persiapan/penggabungan data review untuk sentiment. | Jangan dijalankan sebelum path dan input diverifikasi. |
| `Penggabungan_Master_Reviews.ipynb` | pendukung_reviews | Penggabungan review mentah menjadi master review. | Jangan rerun sebelum input review dikunci. |
| `Realworld_Verification_Google_Colab.ipynb` | pendukung_verifikasi | Verifikasi real-world untuk lokasi yang perlu dicek. | Jalankan hanya untuk queue verifikasi, bukan semua data. |
| `Wisata_Training_1_Audit_Master_Data.ipynb` | legacy_ringkas | Audit awal lama untuk master data geospatial. | Referensi historis; bukan notebook utama. |
| `notebook_housekeeping_wisata_2026-06-08.ipynb` | housekeeping | Index dan audit status notebook wisata. | Boleh dijalankan ulang untuk cek struktur notebook. |
| `wisata_training.ipynb` | utama | Decision log utama untuk audit dan kesiapan dataset wisata. | Boleh dilanjutkan bertahap. Jangan loncat langsung ke LLM. |
| `wisata_traning.ipynb` | legacy_arsip | Notebook lama/eksperimen dengan typo nama dan path Colab lama. | Jangan dijalankan sebagai pipeline utama. |

## Audit Struktur

| Notebook | Cells | Markdown | Code | Code Dengan Output | Error Output | Colab Path | Legacy Dataset Path |
|---|---:|---:|---:|---:|---:|---|---|
| `Data_Completion_Google_Colab.ipynb` | 19 | 10 | 9 | 0 | 0 | False | True |
| `IndoBERT_Colab.ipynb` | 6 | 2 | 4 | 0 | 0 | False | False |
| `Media_Fill_Google_Colab.ipynb` | 19 | 10 | 9 | 0 | 0 | False | True |
| `NLP_Sentiment_Preparation.ipynb` | 9 | 5 | 4 | 0 | 0 | False | True |
| `Penggabungan_Master_Reviews.ipynb` | 8 | 2 | 6 | 0 | 0 | False | True |
| `Realworld_Verification_Google_Colab.ipynb` | 19 | 10 | 9 | 0 | 0 | False | True |
| `Wisata_Training_1_Audit_Master_Data.ipynb` | 7 | 3 | 4 | 0 | 0 | False | False |
| `notebook_housekeeping_wisata_2026-06-08.ipynb` | 18 | 13 | 5 | 5 | 0 | False | False |
| `wisata_training.ipynb` | 33 | 23 | 10 | 10 | 0 | False | False |
| `wisata_traning.ipynb` | 60 | 17 | 43 | 25 | 1 | True | True |

## Keputusan Housekeeping

- `wisata_training.ipynb` dipakai sebagai decision log utama.
- `notebook_housekeeping_wisata_2026-06-08.ipynb` dipakai untuk audit status notebook.
- `wisata_traning.ipynb` tetap disimpan sebagai legacy/arsip karena typo nama, path lama, dan riwayat eksperimen.
- Notebook Colab tetap dipertahankan sebagai pendukung proses berat atau enrichment.
- Tidak ada notebook lama yang dihapus pada housekeeping ini.
