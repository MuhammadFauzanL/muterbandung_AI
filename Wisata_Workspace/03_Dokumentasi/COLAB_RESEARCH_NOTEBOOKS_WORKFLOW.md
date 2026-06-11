# Colab Research Notebooks Workflow

Tanggal: 2026-05-25

Dokumen ini menjelaskan notebook Google Colab yang dipakai untuk mencari dan melengkapi data manual MuterBandung tanpa Apify.

## Notebook yang Dipakai

1. `Notebooks/Media_Fill_Google_Colab.ipynb`
   - Input: `Dataset/3_Curated/manual_media_fill_queue.csv`
   - Fokus: `imageUrl`, link destinasi, website.
   - Output: `manual_media_fill_queue_completed.csv`, `media_manual_apply_ready.csv`

2. `Notebooks/Data_Completion_Google_Colab.ipynb`
   - Input: `Dataset/3_Curated/manual_data_fill_queue.csv`
   - Fokus: jam buka/tutup, rating, coordinate verification, dan metadata non-media lain.
   - Output: `manual_data_fill_queue_completed.csv`, `data_manual_apply_ready.csv`

3. `Notebooks/Realworld_Verification_Google_Colab.ipynb`
   - Input: `Dataset/3_Curated/manual_realworld_verification_queue.csv`
   - Fokus: bukti fasilitas dan konteks real-world, seperti parkir, toilet, mushola, akses kursi roda, child friendly, safety, indoor, night, open 24h.
   - Output: `manual_realworld_verification_completed.csv`, `realworld_manual_apply_ready.csv`

## Aturan Isi Data

- Jangan mengarang data.
- Gunakan Google Search, Google Maps, website resmi, atau sumber tepercaya lain.
- Baris yang siap dipakai wajib memakai `reviewer_status=approved`.
- Isi `source_url` atau `evidence_url` dengan URL sumber.
- Untuk data sentiment, jangan ubah menjadi tersedia kecuali pipeline/model sentiment aktif benar-benar menghasilkan skor valid.
- Notebook Colab tidak boleh langsung menulis dataset utama.

## Alur Aman

1. Buka notebook di Google Colab.
2. Upload queue CSV sesuai notebook.
3. Pakai link bantu pencarian yang dibuat otomatis.
4. Isi kolom hasil manual.
5. Jalankan validasi.
6. Download file `*_completed.csv` dan `*_apply_ready.csv`.
7. Simpan file hasil ke `Dataset/3_Curated/` di project lokal.
8. Lakukan audit lokal sebelum apply ke dataset utama.

## Catatan Audit

Semua notebook riset ini sudah dicatat ke `Notebooks/wisata_training.ipynb` dengan marker:

`MUTERBANDUNG_COLAB_RESEARCH_NOTEBOOKS_2026_05_25`
