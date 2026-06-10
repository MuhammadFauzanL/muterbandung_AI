# Backend Push Guide - MuterBandung

Tanggal: 2026-06-10

## Keputusan LLM

LLM penuh jangan dipasang dulu di frontend. Untuk sekarang cukup disiapkan di backend sebagai layer penjelasan.

Status saat ini:

| Bagian | Status | Catatan |
|---|---|---|
| Ranking wisata | Siap | Tetap dikontrol `recommender.py` |
| Ranking oleh-oleh | Siap baseline | Tetap dikontrol `oleh_oleh_recommender.py` |
| Evidence pack LLM | Siap | Sudah ada di response API |
| Guard LLM | Siap baseline | Dipakai untuk validasi agar LLM tidak mengarang |
| Panggilan LLM provider | Nanti | Pasang setelah backend stabil dan API key tersedia |

Jadi untuk teman backend: jangan ubah ranking memakai LLM dulu. LLM nanti hanya menjelaskan hasil dari backend.

## File Wajib Push

### Runtime Backend

| File/Folder | Fungsi |
|---|---|
| `Scripts/app.py` | API Flask utama |
| `Scripts/recommender.py` | Recommender wisata |
| `Scripts/oleh_oleh_recommender.py` | Recommender oleh-oleh |
| `Scripts/llm_evidence_pack.py` | Evidence pack untuk LLM |
| `Scripts/llm_guard.py` | Guard/validator output LLM |
| `Scripts/templates/index.html` | UI Flask sementara |
| `Scripts/static/script.js` | Logic frontend sementara |
| `Scripts/static/style.css` | Style frontend sementara |

### Config dan Dokumentasi

| File | Fungsi |
|---|---|
| `requirements.txt` | Dependency install |
| `.env.example` | Contoh konfigurasi |
| `.gitignore` | Proteksi file lokal/raw |
| `readme.md` | Ringkasan project |
| `ARCHITECTURE.md` | Gambaran arsitektur |
| `SKILLS.md` | Konteks agent/project |

### Dataset Runtime

| File | Fungsi |
|---|---|
| `Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv` | Dataset wisata runtime |
| `Wisata_Workspace/01_Dataset/3_Curated/data_validation_runtime_candidate_2026-06-09.json` | Audit validasi dataset wisata |
| `Wisata_Workspace/01_Dataset/3_Curated/landmark_aliases.csv` | Alias landmark untuk query dekat lokasi |
| `OlehOleh_Workspace/03_Curated/OLEH_OLEH_BASELINE_UI_ENRICHED_WITH_MANUAL_PRODUCT_PRICE_2026-06-10.csv` | Dataset oleh-oleh runtime |
| `OlehOleh_Workspace/03_Curated/OLEH_OLEH_BASELINE_UI_ENRICHED_WITH_MANUAL_PRODUCT_PRICE_SUMMARY_2026-06-10.json` | Summary dataset oleh-oleh |

### Test dan Audit

| File/Folder | Fungsi |
|---|---|
| `Scripts/test_api_contract.py` | Test kontrak API |
| `Scripts/test_api_schema_snapshot.py` | Test snapshot schema API |
| `Scripts/test_recommender.py` | Test recommender |
| `Scripts/test_llm_evidence_pack.py` | Test evidence pack |
| `Scripts/test_llm_guard.py` | Test guard LLM |
| `Scripts/audit_oleh_oleh_recommender_queries.py` | Audit query oleh-oleh |
| `Scripts/run_recommender_runtime_audit.py` | Audit runtime wisata |
| `Scripts/validate_curated_dataset.py` | Validasi dataset wisata |
| `Wisata_Workspace/05_Evaluation/` | Hasil audit query wisata |
| `OlehOleh_Workspace/04_Evaluation/` | Hasil audit query oleh-oleh |

## Jangan Push

| File/Folder | Alasan |
|---|---|
| `.env` | Secret/API key |
| `.venv/`, `.venv_clean_verify/` | Environment lokal |
| `logs/`, `*.log`, `*.out.log`, `*.err.log` | Output runtime lokal |
| `__pycache__/`, `.pytest_cache/`, `.ipynb_checkpoints/` | Cache |
| `dataset_Google-Maps-Reviews-Scraper_*.json` | Raw review, bisa besar dan mengandung personal data |
| `dataset_google-hotels-search-scraper_*.json` | Raw hotel scraper |
| `dataset_crawler-google-places_*.csv` | Raw place discovery |
| `Penginapan_Workspace/01_Raw_Data/` | Raw penginapan |
| `OlehOleh_Workspace/01_Raw_Data/` | Raw oleh-oleh |
| `OlehOleh_Workspace/05_Review_Scraping/raw_outputs/` | Raw review oleh-oleh |
| Model/cache HuggingFace | Terlalu besar, download ulang via dependency/cache |

## Validasi Setelah Clone

Jalankan dari root project:

```powershell
python -m py_compile .\Scripts\app.py .\Scripts\recommender.py .\Scripts\oleh_oleh_recommender.py .\Scripts\llm_evidence_pack.py .\Scripts\llm_guard.py
python .\Scripts\audit_oleh_oleh_recommender_queries.py
python .\Scripts\run_recommender_runtime_audit.py
```

Untuk jalan lokal:

```powershell
$env:HOST="127.0.0.1"
$env:PORT="5000"
python .\Scripts\app.py
```

Endpoint utama:

| Endpoint | Fungsi |
|---|---|
| `POST /api/recommend` | Rekomendasi wisata |
| `POST /api/oleh-oleh/recommend` | Rekomendasi oleh-oleh |
| `POST /api/llm/validate` | Validasi output LLM |

## Catatan Untuk Backend Developer

- Jangan hitung ulang ranking di frontend.
- Jangan membuat klaim baru dari field kosong.
- Gunakan `llm_evidence_pack` kalau nanti memasang LLM.
- API key LLM hanya boleh ada di backend atau environment server.
- Penginapan belum masuk endpoint final sampai sentiment review selesai.
