# MuterBandung AI — Smart Tourism Recommender for Bandung Raya

**MuterBandung** adalah sistem rekomendasi wisata berbasis AI untuk kawasan Bandung Raya (Bandung, Cimahi, Lembang). Platform ini menggabungkan semantic search, sentiment analysis, dan geospatial filtering untuk memberikan rekomendasi destinasi wisata dan oleh-oleh yang dipersonalisasi.

---

## 📁 Struktur Folder (Monorepo)

```
muterbandung_AI/
│
├── backend/                       # 🔧 Backend API (FastAPI + PostgreSQL)
│   ├── app/
│   │   ├── main.py               # FastAPI entry-point
│   │   ├── database.py           # SQLAlchemy engine & session
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic-settings (.env)
│   │   │   ├── exceptions.py     # Custom exception handlers
│   │   │   └── security.py      # JWT auth (Phase 2)
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── api/
│   │   │   ├── __init__.py      # Router aggregation
│   │   │   └── health.py       # Health check endpoints
│   │   ├── services/            # Business logic layer
│   │   └── utils/
│   │       ├── response.py      # Standard response helpers
│   │       └── pagination.py   # Pagination utility
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # pytest test suite
│   ├── requirements.txt         # Production dependencies
│   ├── requirements-dev.txt     # Dev/test dependencies
│   ├── docker-compose.yml       # PostgreSQL container
│   ├── .env.example             # Environment template
│   └── .python-version         # Python version pin
│
├── frontend/                     # 🎨 Frontend Website (Next.js)
│   ├── app/                     # Next.js app router
│   ├── components/              # React components
│   └── public/                  # Static assets
│
├── ai_workspace/                # 📊 AI Research & Data Pipeline (Jupyter + Datasets)
│   ├── Wisata_Workspace/        # Dataset dan dokumen wisata
│   ├── OlehOleh_Workspace/     # Dataset oleh-oleh
│   └── Penginapan_Workspace/   # Dataset penginapan/hotel
│
├── logs/                         # 📝 Server logs (tidak di-commit ke git)
│
├── .gitignore                   # Git ignore rules
├── .env.example                 # Root environment variables template
│
├── ARCHITECTURE.md              # Arsitektur sistem detail
├── BACKEND_AGENT_HANDOFF.md    # Dokumentasi untuk developer backend
├── SKILLS.md                    # Context & onboarding untuk AI agent
├── README_DEV.md                # File ini (Panduan Monorepo)
└── readme.md                    # LLM System Prompt (MIOA Directive untuk chatbot)
```

---

## 🚀 Cara Menjalankan Lokal

### Prerequisites
- **Python 3.9+** (3.11+ direkomendasikan)
- **Node.js 18+** (untuk frontend)
- **Docker & Docker Compose** (untuk PostgreSQL)
- **pip** (Python package manager)
- Git

### Setup Backend (FastAPI)

1. **Navigate ke backend**:
   ```bash
   cd backend
   ```

2. **Start PostgreSQL**:
   ```bash
   docker compose up -d
   ```

3. **Buat virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # Untuk development/testing:
   pip install -r requirements-dev.txt
   ```

5. **Setup environment variables**:
   ```bash
   cp .env.example .env
   ```
   *Catatan:* Jika Anda mengaktifkan fitur AI Cepot atau AI Planner, pastikan Anda telah memasukkan `OPENROUTER_API_KEY` dan `CLOUDFLARE_API_TOKEN` ke dalam file `.env` tersebut.

6. **Siapkan Model AI (Persona & Behaviour)**:
   Sistem rekomendasi AI membutuhkan model lokal untuk berfungsi. Pastikan Anda telah mengambil (*pull*) folder `Persona_Workspace` dan `Behaviour_Workspace` (yang berisi file `.pkl` dan `.keras`) ke direktori root repository.

7. **Jalankan server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Server akan berjalan di `http://localhost:8000`.

7. **Buka API docs**: http://localhost:8000/docs

### Setup Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend berjalan di `http://localhost:3000`.

---

## ✅ Testing Backend

```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v
```

---

## 📖 API Endpoints

### Phase 1 (Current)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Combined health check |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (checks DB) |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |

---

**Last Updated:** 2026-06-11
**Status:** 🟢 Active Development — Phase 1 Foundation Complete
