# MuterBandung — AI Travel Recommendation Backend

Backend API untuk sistem rekomendasi wisata Bandung berbasis AI. Dibangun dengan **FastAPI**, **PostgreSQL**, **SQLAlchemy**, dan **Alembic**.

---

## 📋 Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.9+ (3.11+ recommended) |
| Docker & Docker Compose | Latest |
| pip | Latest |

---

## 🚀 Getting Started

### 1. Clone & Navigate

```bash
cd muterbandung_AI/backend
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env jika diperlukan (misalnya mengubah password database)
```

### 3. Start PostgreSQL (Docker)

```bash
docker compose up -d
```

Verifikasi database berjalan:

```bash
docker compose ps
```

### 4. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt

# Untuk development/testing:
pip install -r requirements-dev.txt
```

### 6. Run Database Migrations

```bash
# Buat migration awal (setelah ada model di Phase 2)
alembic revision --autogenerate -m "initial migration"

# Jalankan migration
alembic upgrade head
```

### 7. Start Backend Server

```bash
uvicorn app.main:app --reload
```

Server berjalan di: **http://localhost:8000**

---

## 📖 API Documentation

| Docs | URL |
|------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 🔗 Available Endpoints

### Phase 1

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Combined health check (backward-compatible) |
| `GET` | `/health/live` | Liveness probe – process is running |
| `GET` | `/health/ready` | Readiness probe – checks DB connectivity (returns 503 if unavailable) |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry-point
│   ├── database.py           # SQLAlchemy engine & session
│   ├── core/
│   │   ├── config.py         # Pydantic settings (.env)
│   │   ├── exceptions.py     # Custom exceptions & handlers
│   │   └── security.py       # JWT auth (Phase 2)
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── api/
│   │   ├── __init__.py       # Router aggregation
│   │   └── health.py         # Health check endpoint
│   ├── services/             # Business logic layer
│   └── utils/
│       ├── response.py       # Standard response helpers
│       └── pagination.py     # Pagination utility
├── alembic/
│   ├── env.py                # Migration environment
│   ├── script.py.mako        # Migration template
│   └── versions/             # Migration files
├── tests/
│   ├── conftest.py           # Shared test fixtures
│   ├── test_health.py        # Health endpoint contract tests
│   ├── test_exceptions.py    # Exception handler tests
│   └── test_response.py      # Response helper tests
├── .env.example              # Environment template
├── .python-version           # Python version pin
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # PostgreSQL container
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Dev/test dependencies
└── README.md                 # This file
```

---

## 🐳 Docker Commands

```bash
# Start database
docker compose up -d

# Stop database
docker compose down

# Stop & remove volumes (⚠️ deletes data)
docker compose down -v

# View logs
docker compose logs -f postgres
```

---

## 🔄 Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View current revision
alembic current

# View migration history
alembic history
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v

# Run with coverage (after installing pytest-cov)
pytest tests/ -v --tb=short
```

---

## 📝 API Response Format

### Success

```json
{
  "statusCode": 200,
  "message": "Success",
  "data": {}
}
```

### Error

```json
{
  "statusCode": 400,
  "message": "Invalid request",
  "errors": []
}
```

### Paginated

```json
{
  "statusCode": 200,
  "message": "Success",
  "data": [],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10
  }
}
```

---

## 🗺️ Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Backend Foundation | ✅ Done |
| Phase 2 | Authentication (JWT) | ⏳ Next |
| Phase 3 | Destinations CRUD | 🔜 Planned |
| Phase 4 | User Preferences & Interactions | 🔜 Planned |
| Phase 5 | AI Recommendation Engine | 🔜 Planned |
| Phase 6 | RAG Chatbot Integration | 🔜 Planned |

---

## 🛠️ Development Notes

- Semua credential dibaca dari `.env`, tidak ada yang di-hardcode.
- CORS dikonfigurasi untuk `FRONTEND_URL` (default: `http://localhost:3000`). Methods dan headers dibatasi secara eksplisit (bukan wildcard).
- SQLAlchemy menggunakan **declarative base** yang kompatibel dengan Alembic autogenerate.
- Exception handler global memastikan semua error mengikuti format response standar.
- Logging menggunakan `logging` standar Python (bukan `print`).
- Health check dipisah menjadi liveness (`/health/live`) dan readiness (`/health/ready`).
- `.python-version` file tersedia untuk konsistensi environment.
