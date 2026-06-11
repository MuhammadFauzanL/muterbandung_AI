# MuterBandung: Arsitektur Sistem AI Terintegrasi
**Hybrid AI Tourism Recommender — Mobile & Backend Architecture**

---

## 1. Positioning Proyek

**MuterBandung** bukan sekadar aplikasi filter wisata yang memakai sentiment analysis. Ini adalah **Hybrid AI Tourism Recommender** yang menggabungkan:

- **Analisis Sentimen Ulasan** → mengukur kualitas destinasi
- **Klasifikasi Multi-Label Karakter Destinasi** → auto-tagging cerdas
- **Semantic Matching** → mencocokkan preferensi user dengan profil wisata
- **Learning-to-Rank Package Model** → memilih paket terbaik dari kandidat
- **RAG Chatbot + Evidence Re-Ranker** → tanya-jawab berbasis bukti ulasan

> *"Sistem rekomendasi paket wisata berbasis hybrid AI yang menggabungkan analisis sentimen ulasan, klasifikasi multi-label karakter destinasi, pemeringkatan paket menggunakan learning-to-rank, serta chatbot berbasis retrieval-augmented generation dengan evidence re-ranking."*

---

## 2. Arsitektur Tingkat Tinggi

```text
┌─────────────────────────────────────────────────────┐
│                 MOBILE APP / WEB UI                  │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ Layer 1:     │  │ Peta       │  │ Layer 2:     │ │
│  │ Guided Form  │  │ Interaktif │  │ AI Chatbot   │ │
│  └──────┬───────┘  └─────┬──────┘  └──────┬───────┘ │
└─────────┼────────────────┼─────────────────┼─────────┘
          │                │                 │
┌─────────▼────────────────▼─────────────────▼─────────┐
│              API GATEWAY (FastAPI)                     │
│                                                       │
│  ┌───────────────────────────────────────────────┐   │
│  │         AI PIPELINE (9 Komponen)               │   │
│  │                                                │   │
│  │  1. Sentiment Classifier (SVM, 94%)            │   │
│  │  2. Aspect Extractor (5 Aspek)                 │   │
│  │  3. Multi-Label Attribute Classifier ←─[NEW]   │   │
│  │  4. Semantic Matcher (Sentence Embedding)      │   │
│  │  5. Candidate Package Generator                │   │
│  │  6. Feasibility Scoring Model ←────────[NEW]   │   │
│  │  7. Learning-to-Rank Package Model ←───[NEW]   │   │
│  │  8. RAG Retrieval + Evidence Re-Ranker ←[NEW]  │   │
│  │  9. LLM Chatbot (Generative Layer)             │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  ┌───────────────────────────────────────────────┐   │
│  │         BUSINESS LOGIC                         │   │
│  │  - Haversine (Jarak Hotel Terdekat)            │   │
│  │  - Budget Estimator (Kalkulator Total Biaya)   │   │
│  │  - Constraint Filter (Durasi, Pax, Tipe Paket) │   │
│  └───────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────┐
│              DATABASE LAYER                            │
│  ┌─────────────┐ ┌──────────┐ ┌─────────────────────┐│
│  │ Tabel Wisata │ │ Tabel    │ │ Tabel Sentimen &    ││
│  │ 232 Lokasi   │ │ Hotel    │ │ Aspect Mentions     ││
│  │ + Koordinat  │ │ [PENDING]│ │ + Multi-Label Tags  ││
│  └─────────────┘ └──────────┘ └─────────────────────┘│
└───────────────────────────────────────────────────────┘
```

---

## 3. Detail 9 Komponen AI Pipeline

### Komponen 1 & 2: Sentiment Classifier + Aspect Extractor ✅ SELESAI
- **Model:** Linear SVM Binary (Positif/Negatif), Akurasi 94.14%
- **Aspek:** Pemandangan, Harga, Fasilitas, Pelayanan, Keluarga
- **Output:** `skor_sentimen_persen` dan `mentions_*` per lokasi
- **Peran:** Menjadi sinyal kualitas destinasi dalam ranking

### Komponen 3: Multi-Label Tourist Attribute Classifier 🔧 BARU
- **Tujuan:** Auto-tag setiap destinasi dengan label ganda (Alam, Keluarga, Edukasi, Spot Foto, Santai, Cocok Anak, Indoor, Outdoor, dll)
- **Input:** Gabungan teks ulasan + deskripsi per destinasi
- **Model:** IndoBERT Multi-Label / SVM One-vs-Rest / TF-IDF + Logistic Regression
- **Evaluasi:** Micro F1, Macro F1, Hamming Loss
- **Peran:** Memperkaya filtering kategori agar tidak kaku (satu wisata bisa punya banyak label)

### Komponen 4: Semantic Matcher 🔧 BARU
- **Tujuan:** Mencocokkan kalimat preferensi user dengan profil destinasi secara makna
- **Contoh:** User: *"wisata alam santai untuk pasangan"* → cocok dengan Dusun Bambu meskipun kategorinya bukan persis "Alam"
- **Model:** Sentence-BERT / paraphrase-multilingual-MiniLM
- **Peran:** Retrieval kandidat wisata yang relevan sebelum masuk ke filter budget

### Komponen 5: Candidate Package Generator
- **Tujuan:** Membuat 10-20 kandidat paket berdasarkan constraint (budget, durasi, pax, tipe paket)
- **Logika:** Kombinasi wisata + hotel terdekat (Haversine) yang totalnya ≤ budget
- **Output:** Daftar paket kandidat dengan fitur numerik lengkap

### Komponen 6: Feasibility Scoring Model 🔧 BARU
- **Tujuan:** Menilai apakah paket realistis (tidak terlalu padat, lokasi tidak terlalu menyebar, budget masuk akal)
- **Fitur:** Jumlah wisata/hari, total jarak antar wisata, rasio biaya/budget, variasi kategori, kepadatan geografis
- **Model:** XGBoost / Random Forest Classifier/Regressor
- **Label:** Layak (3) / Cukup Layak (2) / Kurang Layak (1) / Tidak Layak (0)
- **Peran:** Membuang paket yang secara logistik tidak masuk akal sebelum di-ranking

### Komponen 7: Package Learning-to-Rank Model 🔧 BARU — PRIORITAS UTAMA
- **Tujuan:** Memilih paket terbaik dari kandidat yang lolos feasibility check
- **Model:** LightGBM Ranker / XGBoost Ranker
- **Fitur Input:**
  - **Fitur User:** budget_total, jumlah_orang, durasi_hari, tipe_paket, jumlah_kategori_dipilih
  - **Fitur Paket:** total_biaya, rasio_biaya/budget, sisa_budget, skor_sentimen_rata2, rating_rata2, kecocokan_kategori, jarak_hotel, kepadatan_geografis, variasi_kategori
- **Data Training:** Skenario user buatan + rubrik pakar untuk labeling (relevance grade 0-3)
- **Evaluasi:** NDCG@K, MAP, MRR, Precision@K
- **Peran:** Inti keputusan AI — mengurutkan paket dari yang paling cocok

### Komponen 8: RAG Retrieval + Review Evidence Re-Ranker 🔧 BARU
- **Tujuan:** Saat user bertanya di chatbot, sistem mengambil 20 review terdekat (embedding), lalu model re-ranker memilih 5 review paling relevan terhadap pertanyaan spesifik user
- **Model Re-Ranker:** Cross-Encoder BERT / IndoBERT sentence-pair classifier
- **Contoh:** User: *"Apakah cocok untuk balita?"* → Re-ranker memilih review yang membahas stroller, anak kecil, jalan curam — bukan review umum "tempatnya bagus"
- **Evaluasi:** MRR, Recall@K
- **Peran:** Membuat chatbot benar-benar *grounded* (menjawab dari bukti, bukan menebak)

### Komponen 9: LLM Chatbot (Generative Layer)
- **Tujuan:** Menjawab pertanyaan lanjutan user secara natural berdasarkan evidence dari Re-Ranker
- **Behavior:** Mengikuti System Prompt di `readme.md` (MIOA Directive)
- **Constraint:** Dilarang menghitung harga/jarak sendiri, hanya membahasakan output Backend

---

## 4. Alur Lengkap Sistem (End-to-End Pipeline)

```text
User Input (Budget, Kategori, Durasi, Pax)
          │
          ▼
[Semantic Matcher] ── Cocokkan preferensi dgn profil wisata
          │
          ▼
[Multi-Label Filter] ── Saring berdasarkan kecocokan kategori (soft match, bukan hard filter)
          │
          ▼
[Candidate Package Generator] ── Buat 10-20 paket (Wisata + Hotel + Budget)
          │
          ▼
[Feasibility Model] ── Buang paket yang tidak realistis
          │
          ▼
[Learning-to-Rank Model] ── Ranking paket terbaik
          │
          ▼
Top 3 Paket ditampilkan ke User (Hemat / Seimbang / Premium)
          │
          ▼
User klik "Tanya AI" pada salah satu paket
          │
          ▼
[RAG Retrieval] ── Ambil 20 review relevan
          │
          ▼
[Evidence Re-Ranker] ── Pilih 5 bukti paling tepat
          │
          ▼
[LLM Chatbot] ── Jawab secara natural berbasis evidence
```

---

## 5. Weighted Scoring Formula (Multi-Label Soft Match)

Sistem TIDAK menggunakan hard filter kategori. Sebaliknya:

```
Skor Akhir Wisata =
    (0.35 × Skor Sentimen Persen)
  + (0.20 × Rating Rata-rata)
  + (0.15 × Popularitas / Total Ulasan)
  + (0.30 × Kecocokan Kategori Multi-Label)
```

**Kecocokan Kategori** dihitung sebagai persentase overlap antara pilihan user dan label destinasi:
- User pilih: [Alam, Keluarga]
- Dusun Bambu punya: [Alam, Keluarga, Kuliner] → Kecocokan = 100%
- Kawah Putih punya: [Alam, Pemandangan] → Kecocokan = 50%
- Museum Geologi punya: [Edukasi, Sejarah] → Kecocokan = 0%

Wisata dengan kecocokan 0% **tidak langsung dibuang**, melainkan mendapat skor rendah dan bisa muncul sebagai fallback jika hasil terlalu sedikit.

---

## 6. Strategi Data Training untuk Model Baru

Karena belum ada histori interaksi user sungguhan, data training dibuat dengan metode **Synthetic Scenario Generation**:

1. Buat 200+ skenario user buatan (variasi budget rendah/sedang/tinggi, 1-4 orang, 1-3 hari, berbagai kategori)
2. Untuk setiap skenario, engine menghasilkan 10-20 paket kandidat
3. Paket diberi label relevansi (0-3) berdasarkan rubrik pakar yang jelas
4. Model belajar meranking dari label tersebut

---

## 7. Teknologi & Dependensi

| Komponen | Teknologi |
|----------|-----------|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL + PostGIS / CSV (Capstone) |
| ML Models | scikit-learn, LightGBM, XGBoost |
| NLP/Embedding | IndoBERT, Sentence-Transformers |
| Geospatial | Haversine (custom Python) |
| Frontend | React Native / Flutter (Mobile), Streamlit (Prototype) |
| Chatbot LLM | Gemini API / OpenAI API |
| Peta | Leaflet.js / Google Maps SDK |

---

## 8. Roadmap Implementasi

| Fase | Deskripsi | Status |
|------|-----------|--------|
| Fase 1-3 | Scraping, Cleaning, EDA | ✅ Selesai |
| Fase 4 | Aspect-Based NLP (5 Aspek) | ✅ Selesai |
| Fase 5 | Binary Sentiment (SVM 94%) | ✅ Selesai |
| Fase 6 | Core Engine Prototype | ✅ Selesai |
| Fase 7 | Multi-Label Attribute Classifier | 🔧 Selanjutnya |
| Fase 8 | Hotel Integration + Haversine | ⏳ Menunggu Data Hotel |
| Fase 9 | Candidate Package Generator | 🔧 Selanjutnya |
| Fase 10 | Feasibility + Learning-to-Rank | 🔧 Selanjutnya |
| Fase 11 | RAG + Evidence Re-Ranker | 🔧 Selanjutnya |
| Fase 12 | Frontend UI (Streamlit → Mobile) | 🔧 Selanjutnya |
