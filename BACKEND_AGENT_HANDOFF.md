# MuterBandung AI Backend Handoff

Tanggal: 2026-06-11

Dokumen ini untuk agent/backend developer yang akan melanjutkan integrasi AI recommender MuterBandung.

## Tujuan Repo

Repo ini berisi runtime AI recommender untuk:

| Entitas | Status | Catatan |
|---|---|---|
| Wisata | Siap dikembangkan | Dataset runtime sudah dipakai oleh recommender |
| Oleh-oleh | Baseline siap | Sudah punya scoring, harga manual, produk utama, dan query audit |
| Penginapan | Candidate | Data parent/child sudah rapi, sentiment masih dikerjakan terpisah |

Fokus backend saat ini: expose API, jaga ranking tetap di backend, dan jangan membuat klaim di luar data.

## Stack Backend Saat Ini

| Komponen | Teknologi |
|---|---|
| Framework | **FastAPI** (Python) |
| Database | **PostgreSQL 16** via Docker Compose |
| ORM | **SQLAlchemy 2.0** |
| Migration | **Alembic** |
| Configuration | **pydantic-settings** + `.env` |
| Auth (Phase 2) | JWT via python-jose + passlib |

## File Utama

| File | Fungsi |
|---|---|
| `backend/app/main.py` | FastAPI entry-point |
| `backend/app/database.py` | SQLAlchemy engine & session |
| `backend/app/core/config.py` | Konfigurasi dari environment variables |
| `backend/app/core/exceptions.py` | Custom exception handlers |
| `backend/app/core/security.py` | JWT auth (Phase 2 placeholder) |
| `backend/app/api/health.py` | Health check endpoints |
| `backend/app/utils/response.py` | Standard response helpers |
| `backend/app/utils/pagination.py` | Pagination utility |

## Dataset Runtime

| Entitas | File |
|---|---|
| Wisata | `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv` |
| Wisata validation | `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/data_validation_runtime_candidate_2026-06-09.json` |
| Alias lokasi | `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/landmark_aliases.csv` |
| Oleh-oleh | `ai_workspace/OlehOleh_Workspace/03_Curated/OLEH_OLEH_BASELINE_UI_ENRICHED_WITH_MANUAL_PRODUCT_PRICE_2026-06-10.csv` |
| Penginapan parent | `ai_workspace/Penginapan_Workspace/02_Curated/PENGINAPAN_PARENT_MASTER_2026-06-05.csv` |
| Penginapan child | `ai_workspace/Penginapan_Workspace/02_Curated/PENGINAPAN_CHILD_LISTINGS_FINAL_2026-06-05.csv` |

## Endpoint Saat Ini (Phase 1)

| Endpoint | Method | Fungsi |
|---|---|---|
| `/health` | GET | Combined health check |
| `/health/live` | GET | Liveness probe (process up?) |
| `/health/ready` | GET | Readiness probe (DB reachable?) |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc docs |

## Cara Jalan Lokal

```bash
cd backend

# Start PostgreSQL
docker compose up -d

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy env
cp .env.example .env

# Run server
uvicorn app.main:app --reload
```

Lalu buka: http://localhost:8000/docs

## Validasi Cepat

```bash
cd backend
source venv/bin/activate

# Run tests
pip install -r requirements-dev.txt
pytest tests/ -v

# Quick health check
curl http://localhost:8000/health
```

## Aturan Penting

- Ranking jangan dihitung di frontend.
- Frontend hanya mengirim query dan menampilkan hasil dari API.
- LLM belum menjadi penentu ranking.
- Jika LLM dipasang, gunakan evidence pack dari backend.
- Jangan klaim fasilitas, harga, sentiment, atau status aktif kalau field datanya kosong.
- Penginapan belum final untuk ranking user-facing sampai sentiment hotel selesai.
- Raw scraper, log, venv, dan file besar tidak perlu masuk repo.

## Catatan Untuk Pengembangan Berikutnya

| Prioritas | Pekerjaan |
|---|---|
| 1 | Implementasi Authentication (JWT) — Phase 2 |
| 2 | Buat endpoint destinations CRUD — Phase 3 |
| 3 | Buat endpoint penginapan sebagai candidate/stub |
| 4 | Tambahkan user preferences & interactions — Phase 4 |
| 5 | Integrasi AI recommendation engine — Phase 5 |
| 6 | RAG Chatbot integration — Phase 6 |

## Status Singkat

Backend foundation sudah berjalan dengan FastAPI. Health check, error handling, CORS, dan database connection sudah dikonfigurasi. Test suite sudah ada untuk contract validation. Siap untuk Phase 2 (Authentication).
