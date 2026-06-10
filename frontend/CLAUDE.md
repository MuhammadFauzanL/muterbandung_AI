# MuterBandung Frontend Development Rules

File ini memberikan panduan cepat bagi AI Agent dan Developer untuk mengelola dan mengembangkan frontend Next.js 16 di proyek ini.

## 🚀 Perintah Terminal Penting

### 1. Mode Development
Jalankan local server pembangunan:
```bash
npm run dev
```

### 2. Membangun Proyek (Build)
Pastikan kode Anda aman dari kesalahan kompilasi TypeScript dan Next.js Turbopack:
```bash
npm run build
```

### 3. Linting Kode
Periksa kualitas penulisan kode sesuai ESLint rules:
```bash
npm run lint
```

## 📐 Arsitektur & Aturan Kode

- **Framework**: Next.js 16 (App Router), React 19, TypeScript.
- **Styling**: Tailwind CSS v4. Gunakan utility classes langsung.
- **Routing**: Semua route diletakkan di dalam `frontend/app/`.
- **Client vs Server Components**:
  - Gunakan Server Components secara default untuk performa rendering yang cepat dan SEO bersahabat.
  - Tuliskan `"use client"` di bagian atas file hanya jika komponen memerlukan state hook (`useState`, `useEffect`) atau interaksi dinamis di browser (seperti Leaflet Map).
- **Integrasi API**:
  - Semua pemanggilan API ke backend Flask/FastAPI harus dibungkus secara clean di dalam folder `frontend/services/api.ts`.
  - Endpoint utama:
    - `POST /api/recommend` -> Rekomendasi wisata & paket.
    - `POST /api/oleh-oleh/recommend` -> Rekomendasi oleh-oleh Bandung.
    - `POST /api/llm/validate` -> Validasi hasil jawaban LLM Chatbot agar bebas halusinasi.
- **Chatbot & RAG**:
  - Jangan biarkan LLM Chatbot langsung menjawab pertanyaan tanpa memvalidasi outputnya ke `/api/llm/validate`.
  - Simpan dan teruskan `llm_evidence_pack` yang dikembalikan dari API rekomendasi wisata saat menginisialisasi percakapan chatbot.
