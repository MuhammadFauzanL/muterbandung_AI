# MuterBandung AI — Smart Tourism Recommender for Bandung Raya

**MuterBandung** adalah sistem rekomendasi wisata berbasis AI untuk kawasan Bandung Raya (Bandung, Cimahi, Lembang). Platform ini menggabungkan semantic search, sentiment analysis, dan geospatial filtering untuk memberikan rekomendasi destinasi wisata dan oleh-oleh yang dipersonalisasi.

---

## 📁 Struktur Folder (Monorepo)

```
muterbandung_AI/
│
├── backend/                      # 🔧 Backend API (Flask/FastAPI + ML Runtime)
│   ├── app/
│   │   ├── main.py              # Entry point (Flask app)
│   │   ├── services/            # Business logic & ML services
│   │   │   ├── recommender.py   # Core rekomendasi wisata
│   │   │   ├── oleh_oleh_recommender.py
│   │   │   ├── llm_evidence_pack.py
│   │   │   └── llm_guard.py     # Guardrail validasi LLM
│   │   ├── routers/             # API endpoints (untuk migrasi ke FastAPI)
│   │   ├── schemas/             # Request/response models (Pydantic)
│   │   ├── models/              # Database models (SQLAlchemy)
│   │   └── database/            # Database utilities
│   ├── test_*.py                # Unit tests
│   ├── validate_*.py            # Data validation scripts
│   ├── audit_*.py               # Audit & evaluation scripts
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Container image (untuk produksi)
│
├── frontend/                     # 🎨 Frontend Website (Next.js Prototype / Static Dev)
│   ├── static/                  # CSS, JavaScript, assets
│   │   ├── style.css
│   │   └── script.js
│   └── templates/               # HTML templates
│       └── index.html
│
├── ai_workspace/                # 📊 AI Research & Data Pipeline (Jupyter + Datasets)
│   ├── notebooks/               # Jupyter Notebook untuk riset
│   ├── Wisata_Workspace/        # Dataset dan dokumen wisata
│   │   ├── 01_Dataset/
│   │   │   └── 3_Curated/       # CSV wisata yang sudah di-kurasi
│   │   ├── 02_Notebooks/
│   │   ├── 03_Evaluation/
│   │   └── 05_Evaluation/
│   ├── OlehOleh_Workspace/      # Dataset oleh-oleh
│   └── Penginapan_Workspace/    # Dataset penginapan/hotel
│
├── logs/                         # 📝 Server logs (tidak di-commit ke git)
│
├── .gitignore                   # Git ignore rules (model besar, venv, logs)
├── .env.example                 # Environment variables template
├── requirements.txt             # Root-level deps (untuk development)
├── docker-compose.yml           # Local PostgreSQL + services (opsional)
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
- **Python 3.11+** (pastikan tersedia di sistem)
- **pip** (Python package manager)
- Git

### Setup Backend (Flask API)

1. **Clone atau buka repositori**:
   ```bash
   cd /Users/muhammadrahardianbaihaqi/Projects/muterbandung_AI
   ```

2. **Buat virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # atau pada Windows:
   # .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Setup environment variables** (copy `.env.example` ke `.env`):
   ```bash
   cp .env.example .env
   ```
   Edit `.env` dan pastikan path ke dataset benar (harus menunjuk ke `ai_workspace/`).

5. **Jalankan server Flask**:
   ```bash
   cd backend
   python app/main.py
   ```
   Server akan berjalan di `http://127.0.0.1:5000`.

### Buka Frontend (Sementara)

Buka browser ke `http://127.0.0.1:5000`. Anda akan melihat antarmuka web dev sementara di `frontend/templates/index.html`.

---

## ✅ Testing Backend

### Test API Contract
```bash
cd backend
python -m pytest test_api_contract.py -v
```

### Test Recommender Engine
```bash
cd backend
python -m pytest test_recommender.py -v
```

### Test LLM Guard (Validasi Output AI)
```bash
cd backend
python -m pytest test_llm_guard.py -v
```

---

**Last Updated:** 2026-06-10  
**Status:** 🟢 Active Development
