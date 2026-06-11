# MuterBandung - Transfer Context dari Chat "Pahami skill.md"

File ini dibuat untuk melanjutkan pekerjaan dari chat Codex lama yang sulit reload di VSCode.

Gunakan di chat Codex baru dengan prompt:

```text
Baca file ini dulu:
C:\Users\M Fauzan Lubada\MUTERBANDUNG_PAHAMI_SKILL_CHAT_CONTEXT.md

Lalu lanjutkan pekerjaan MuterBandung di folder:
D:\File\file\Fauzan Lubada\PIJAK
```

## Sumber Chat Lama

- Thread: `Pahami skill.md`
- Session ID: `019e4b6a-25e8-7bf0-9b2c-baf0a9003376`
- File sesi lokal:
  `C:\Users\M Fauzan Lubada\.codex\sessions\2026\05\21\rollout-2026-05-21T23-41-48-019e4b6a-25e8-7bf0-9b2c-baf0a9003376.jsonl`
- Project path saat itu:
  `D:\File\file\Fauzan Lubada\PIJAK`

## Inti skill.md

Project ini adalah **MuterBandung**, sistem rekomendasi wisata Bandung Raya.

Karakter sistem:

- Backend: Flask.
- Frontend: Vanilla JS.
- AI/NLP: SentenceTransformer.
- Recommender: hybrid recommender, bukan keyword search biasa.
- Ranking menggabungkan semantic similarity, sentiment, rating, review confidence, label wisata, constraint, dan jarak.
- Sistem harus menjaga real-world fit: rekomendasi harus masuk akal secara wisata, lokasi, kategori, harga, waktu, dan fasilitas.

Aturan penting yang pernah dibaca dari `skill.md`:

- `torch` dan `SentenceTransformer` harus di-import paling atas di file Python ML.
- Jangan hapus stop words sebelum embedding.
- Corpus destinasi harus berupa narasi lengkap.
- Intent extraction memakai phrase-level maximum similarity.
- Threshold intent: absolute `0.45`, relative margin `0.22`.
- Bobot scoring utama:
  - semantic `35%`
  - sentiment `35%`
  - rating `20%`
  - review confidence `10%`
- Fallback wajib jika intent filter terlalu ketat.
- Frontend tetap dark glassmorphism.
- AI badge harus dari response backend, bukan hardcode.

## Status Implementasi Dari Chat Lama

Audit besar sudah dilakukan pada project MuterBandung.

File yang pernah disentuh/diperbaiki:

- `Scripts/recommender.py`
- `Scripts/app.py`
- `Scripts/static/script.js`
- `scratch_qc.py`
- `qc_report.md`
- `audit_peluang_peningkatan.md`
- `Scripts/audit_coordinate_sanity.py`
- `Dataset/3_Curated/coordinate_audit.csv`
- `Dataset/3_Curated/landmark_aliases.csv`
- `Dokumentasi_Sistem/LLM_UPGRADE_BLUEPRINT.md`

Peningkatan utama yang sudah dilakukan:

- Lexical intent injection untuk intent seperti `Kuliner`, `Belanja`, `Budaya`, `Sejarah`, `Edukasi`, `Keluarga`.
- Dynamic boost/penalty untuk ranking.
- Guard untuk query mustahil seperti `aurora`, `pantai Bandung kota`, `ski salju`, `gurun pasir`.
- Guard untuk query `dekat saya/terdekat` tanpa koordinat.
- Guard agar query fasilitas tidak menghasilkan rekomendasi palsu jika data belum verified.
- Landmark-aware query untuk tempat seperti Gedung Sate, Alun-Alun Bandung, Stasiun Bandung, Braga, Lembang.
- Audit koordinat dengan `coordinate_verified`.
- Shopping subtype seperti `Mall`, `Factory Outlet`, `Oleh-Oleh`, `Pasar Wisata`.
- Facility flags seperti `parking_verified`, `wheelchair_accessible_verified`, `toilet_verified`, `mushola_verified`, `pet_friendly_verified`, `open_24h_verified`, `safety_verified`.
- Frontend di-hardening untuk escape dynamic HTML dan membaca schema AI badge baru.

## Status QC Terakhir

Status terakhir dari chat lama:

- `qc_report.md`: `62/62 PASS`
- Failed: `0`
- Needs review: `0`
- Final status: `PASSED WITH NOTES`

Catatan penting:

- Sistem logic/recommender sudah lebih sehat.
- Risiko utama yang tersisa bukan logic utama, tapi kekosongan data verified.

## Data Penting Terakhir

Ringkasan data yang pernah muncul:

- Destinasi aktif: `213`
- Koordinat aktif meragukan: `10`
- `night_verified`: `33`
- `parking_verified`: `1`
- `wheelchair_accessible_verified`: `0`
- `toilet_verified`: `0`
- `mushola_verified`: `5`
- `pet_friendly_verified`: `0`
- `Mall`: `8`
- `Pasar Wisata`: `1`
- `Factory Outlet`: `0`
- `Oleh-Oleh`: `0`

Kesimpulan audit:

```text
Masalah terbesar berikutnya adalah data verified:
- fasilitas
- factory outlet
- oleh-oleh
- toilet
- akses disabilitas
- pet-friendly
- koordinat bermasalah
```

## Pondasi Data Sentiment

Data sentiment MuterBandung berasal dari ulasan Google Maps yang dibersihkan.

File terkait:

- `Dataset/MASTER_REVIEWS_ENRICHED.csv`
- `Dataset/MASTER_REVIEWS_LABELED.csv`
- `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv`
- `DATABASE_WISATA_FINAL_PARIPURNA.csv`
- `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`

Ringkasan yang pernah ditemukan:

- `MASTER_REVIEWS_ENRICHED.csv`: sekitar `34.150` ulasan bersih.
- `MASTER_REVIEWS_LABELED.csv`: sekitar `34.003` ulasan berlabel.
- Distribusi sentiment yang pernah dicek:
  - positif: `29.326`
  - netral: `2.360`
  - negatif: `2.317`
- `SENTIMENT_SCORES_PER_LOKASI.csv`: sekitar `212` lokasi dengan skor sentiment agregat.

Catatan penting:

- Dokumentasi menyebut model IndoBERT ada di `Models/MuterBandung-IndoBERT-Sentiment`.
- Audit 2026-05-24 memastikan pipeline sentiment aktif memakai TF-IDF + LinearSVC, bukan IndoBERT runtime.
- Backend dan dataset sekarang memakai metadata netral:
  - `sentiment_score`
  - `sentiment_model_source`
  - `sentiment_model_version`
  - `sentiment_available`
- Klaim IndoBERT aktif tidak boleh dipakai sampai pipeline IndoBERT benar-benar tersambung dan tervalidasi.

Catatan lanjutan:

```text
Active sentiment source = tfidf_linearsvc
Active sentiment version = run_nlp_pipeline_v2
IndoBERT status = artifact/training asset, belum source aktif
```

## Ide Lanjutan Yang Pernah Dibahas

### 1. Label Taxonomy Lebih Matang

Struktur label yang disarankan:

```text
primary_category
primary_intent
core_labels
secondary_labels
avoid_labels
```

Makna:

- `primary_category`: jenis tempat secara objektif.
- `primary_intent`: alasan utama user datang.
- `core_labels`: label utama untuk filter keras.
- `secondary_labels`: boost ringan.
- `avoid_labels`: penalty untuk mencegah rekomendasi salah.

### 2. Auto-Label Semi-Otomatis

Pipeline yang disarankan:

```text
Dataset lama
-> rule-based labeling + semantic score
-> confidence score
-> review queue untuk data ragu
-> manual review hanya data bermasalah
-> generate dataset final
```

Output ideal:

- `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2.csv`
- `Dataset/3_Curated/label_review_queue.csv`

### 3. Facility Review Queue

Script yang pernah disarankan:

```text
Scripts/generate_facility_review_queue.py
```

Output:

```text
Dataset/3_Curated/facility_review_queue.csv
```

Tujuan:

- mencari kekosongan fasilitas
- mengumpulkan evidence
- memberi confidence
- membuat review manual lebih terarah

### 4. LLM Upgrade

Dokumen blueprint sudah dibuat:

```text
Dokumentasi_Sistem/LLM_UPGRADE_BLUEPRINT.md
```

Prinsip utama:

- Jangan jadikan LLM sebagai otak utama.
- Backend deterministik memilih kandidat dulu.
- LLM hanya menerima kandidat valid.
- LLM boleh membantu re-ranking, alasan rekomendasi, itinerary, dan ringkasan trade-off.
- Output LLM harus divalidasi backend.
- Kalau LLM mengarang destinasi/harga/jarak, output ditolak.

Tahap sebelum OpenRouter:

```text
1. Buat ground truth query.
2. Buat evaluator otomatis.
3. Ukur baseline engine deterministic.
4. Baru benchmark model OpenRouter.
5. Bandingkan deterministic vs deterministic + LLM.
```

## Command Penting

Masuk project:

```powershell
cd "D:\File\file\Fauzan Lubada\PIJAK"
```

Jalankan Flask:

```powershell
python .\Scripts\app.py
```

Buka UI:

```text
http://127.0.0.1:5000/
```

Jalankan QC:

```powershell
python .\scratch_qc.py
```

Catatan:

- Pada chat lama, API pernah aktif di `http://127.0.0.1:5003`.
- Port bisa berbeda jika `5000` sedang dipakai.
- Model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` bisa lambat saat pertama load.

## Prioritas Lanjutan Yang Masuk Akal

Jika melanjutkan dari chat baru, urutan kerja yang paling masuk akal:

1. Cek repo dan status file terbaru di `D:\File\file\Fauzan Lubada\PIJAK`.
2. Baca `skill.md`.
3. Baca `qc_report.md` dan `audit_peluang_peningkatan.md`.
4. Jalankan `python .\scratch_qc.py` untuk memastikan baseline masih `62/62 PASS`.
5. Pilih salah satu fokus:
   - buat `groundtruth_queries.csv` + evaluator,
   - buat `generate_facility_review_queue.py`,
   - audit ulang sumber sentiment SVM vs IndoBERT,
   - benchmark embedding model,
   - eksperimen OpenRouter guarded re-ranker.

## Prompt Lanjutan Yang Disarankan

Untuk chat baru, pakai prompt seperti ini:

```text
Baca dulu file:
C:\Users\M Fauzan Lubada\MUTERBANDUNG_PAHAMI_SKILL_CHAT_CONTEXT.md

Lalu masuk ke project:
D:\File\file\Fauzan Lubada\PIJAK

Saya ingin melanjutkan pekerjaan dari chat "Pahami skill.md".
Mulai dengan membaca skill.md, qc_report.md, audit_peluang_peningkatan.md, dan cek status sistem terbaru.
Jangan ubah file dulu sebelum memberi ringkasan kondisi saat ini.
```
