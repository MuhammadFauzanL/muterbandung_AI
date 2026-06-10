# Product Requirements Document (PRD) - MuterBandung Frontend

## 1. Pendahuluan
**MuterBandung** adalah *Hybrid AI Tourism Recommender* untuk Kota Bandung. Frontend ini dibangun menggunakan **Next.js 16 (App Router)**, **TypeScript**, dan **Tailwind CSS v4** sebagai Web UI client yang dinamis dan interaktif untuk merekomendasikan paket wisata, hotel, oleh-oleh, dan menyediakan asisten AI Chatbot.

---

## 2. Arsitektur Frontend & Struktur Direktori
Kami menerapkan struktur folder Next.js modern yang clean dan modular untuk mendukung skalabilitas.

```text
frontend/
├── app/                         # App Router (Next.js Routing)
│   ├── layout.tsx               # Root Layout
│   ├── page.tsx                 # Landing Page & Guided Form (Pencarian Wisata)
│   ├── packages/                # Route: Halaman hasil rekomendasi paket
│   │   └── page.tsx
│   ├── chat/                    # Route: AI Chatbot Assistant terintegrasi
│   │   └── page.tsx
│   └── globals.css              # Global styles (Tailwind v4 imports)
├── components/                  # UI Components (Reusable & Stateless)
│   ├── ui/                      # Base UI Elements (button, input, card, dialog)
│   ├── maps/                    # Map Components (React-Leaflet / Mapbox)
│   ├── forms/                   # Guided Search Form Components
│   └── chat/                    # Chat Bubble & Chat Input Components
├── hooks/                       # Custom React Hooks (State logic & API Fetching)
│   ├── use-recommendation.ts    # Fetching & processing packages
│   └── use-chatbot.ts           # Chat & RAG state management
├── services/                    # API client services
│   └── api.ts                   # Fetching abstraction & schemas
├── types/                       # TypeScript Type Definitions
│   └── index.ts                 # API Request & Response interfaces
├── public/                      # Static assets (images, icons)
└── package.json
```

### Aturan Penulisan Kode (Coding Standards)
- **Komponen React**: Gunakan Functional Components dengan TypeScript typing yang ketat.
- **Client vs Server Components**:
  - Gunakan Server Components (`page.tsx` default) untuk inisialisasi awal.
  - Tambahkan `"use client"` di bagian paling atas file komponen hanya untuk file yang membutuhkan interaksi user, state (`useState`, `useEffect`), atau Web API client (seperti Maps).
- **Styling**: Gunakan utility classes dari **Tailwind CSS v4** secara murni. Hindari CSS inline atau CSS modules kecuali sangat terpaksa.
- **State Management**: Gunakan native React `useState`/`useContext` atau lightweight state library seperti **Zustand** jika diperlukan state global. Hindari Redux karena terlalu overkill.

---

## 3. Alur Fitur Utama & Kebutuhan UI

### A. Guided Form (Halaman Utama)
Input form terpandu yang fleksibel untuk merumuskan preferensi pengguna sebelum merekomendasikan paket.
- **Form Fields**:
  1. **Query Bebas (NLP Input)**: Teks deskriptif preferensi user (misal: "wisata alam yang cocok untuk keluarga dengan anak kecil").
  2. **Kategori Multi-Label**: Pilihan kategori (Alam, Edukasi, Sejarah, Kuliner, Spot Foto, Religi, dll).
  3. **Durasi Kunjungan**: Integer (1, 2, atau 3 hari).
  4. **Jumlah Orang (Pax)**: Angka jumlah wisatawan.
  5. **Max Price (Budget)**: Input slider atau range nominal budget total.
  6. **Preferensi Lokasi (Opsional)**: Menggunakan GPS koordinat (`user_lat`, `user_lon`) untuk pencarian terdekat (`sort_by: "nearest"`).
- **Behavior**: Input-input ini akan divalidasi secara lokal sebelum dikirim ke backend API.

### B. Paket Rekomendasi (Packages Page)
Menampilkan 3 jenis paket hasil kompilasi backend:
1. **Paket Hemat**: Mengoptimalkan budget minimal.
2. **Paket Seimbang (Balanced)**: Kombinasi terbaik antara rating, sentimen, dan sisa budget.
3. **Paket Premium**: Memaksimalkan destinasi dengan rating tertinggi sesuai budget maksimal.

Setiap paket harus menampilkan:
- Rute perjalanan per hari (Itinerary timeline).
- Destinasi wisata pilihan dengan review summary (skor sentimen positif).
- Estimasi Hotel terdekat.
- Total biaya riil vs sisa budget.
- Tombol **"Tanya AI tentang Paket Ini"** yang langsung mengarahkan user ke Chatbot.

### C. Chatbot RAG Assistant (Chat Page)
UI Chatbot interaktif untuk menjawab pertanyaan seputar paket rekomendasi secara terarah dan terbukti (*evidence-backed*).
- **Flow Chat & Validasi**:
  1. Ketika user bertanya tentang paket ("Apakah paket ini cocok untuk lansia?"), frontend mengirimkan payload ke API Chatbot LLM.
  2. Frontend mengambil data `llm_evidence_pack` (kumpulan ulasan/bukti riil dari backend untuk paket tersebut).
  3. LLM menghasilkan jawaban.
  4. Jawaban LLM tersebut **wajib divalidasi** dengan mengirimkannya beserta `llm_evidence_pack` ke API `/api/llm/validate`.
  5. Jika API validasi menghasilkan status `valid: false`, frontend harus menampilkan fallback response yang aman atau menyaring output LLM (`sanitized_output`). Ini adalah mekanisme pertahanan utama terhadap halusinasi AI.

---

## 4. Integrasi Backend API

Semua request frontend akan ditujukan ke Backend API Gateway (Flask/FastAPI) yang berjalan di port `5000` (development) dengan skema payload berikut:

### 1. Rekomendasi Wisata (`POST /api/recommend`)
**Request Body Schema:**
```json
{
  "query": "wisata alam sejuk",
  "categories": ["Alam", "Keluarga"],
  "max_price": 500000,
  "min_rating": 4.0,
  "user_lat": -6.9174,
  "user_lon": 107.6191,
  "max_distance_km": 50.0,
  "sort_by": "balanced",
  "free_only": false,
  "open_now": false,
  "day_type": "weekend",
  "top_k": 5
}
```
**Response Key Output Penting:**
- `itinerary`: Susunan rute perjalanan.
- `llm_evidence_pack`: Data bukti untuk RAG Chatbot.
- `llm_prompt_guard`: Context ruleset untuk LLM.

### 2. Rekomendasi Oleh-Oleh (`POST /api/oleh-oleh/recommend`)
**Request Body Schema:**
```json
{
  "query": "keripik tempe",
  "categories": ["Makanan"],
  "max_price": 100000,
  "user_lat": -6.9174,
  "user_lon": 107.6191,
  "max_distance_km": 10.0,
  "top_k": 3
}
```

### 3. Validasi LLM (`POST /api/llm/validate`)
Frontend harus memanggil endpoint ini setiap kali menerima respons dari model LLM sebelum menampilkannya ke user.
**Request Body Schema:**
```json
{
  "llm_output": "Pernyataan hasil respons AI Chatbot...",
  "llm_evidence_pack": { ... } 
}
```

---

## 5. Non-Functional Requirements & Best Practices
- **Keamanan**: Sensitifitas API Key (OpenAI / Gemini) tidak boleh bocor ke client-side. Panggilan LLM harus ditarik melalui server-side route handler Next.js (`/app/api/chat/route.ts`) atau langsung didelegasikan ke backend Flask/FastAPI.
- **Peta (Interactive Maps)**: Peta menggunakan library open-source `react-leaflet` atau Google Maps dengan pembatasan bundle size yang ketat (lazy loading map components).
- **Responsive Web Design**: Mobile-first approach. UI harus sangat nyaman diakses dari smartphone, karena MuterBandung diposisikan sebagai asisten turis saat di perjalanan.
