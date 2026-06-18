# PANDUAN INTEGRASI TIM BACKEND SERVER - MUTERBANDUNG V1.0

Folder ini berisi file-file backend hasil audit, perbaikan, dan optimasi menyeluruh untuk fitur **RAG Chatbot AI (Cepot AI)** dan **Location-Aware Geospasial Recommender**.

## 📁 Struktur File Rilis
```text
BACKEND_DELIVERY_RELEASE_V1/
├── main.py                <- Masuk ke backend/app/main.py
└── services/              <- Masuk ke backend/app/services/
    ├── recommender.py     <- Optimasi Jarak Dinamis Haversine (Fase B & C)
    ├── chatbot_service.py <- Sistem RAG Chatbot, Hard Guardrail & Failover LLM
    ├── llm_evidence_pack.py<- Kompilasi paket data untuk LLM RAG
    └── llm_guard.py       <- Kontrak Output JSON, Validasi Fakta, Prompt Persona Cepot
```

## 🚀 Perubahan Utama & Fitur Baru yang Siap Digunakan:
1. **Location Intent Parsing & Radius Dinamis (`recommender.py`)**:
   - Fungsi ganda lama (`_detect_landmark_location` dan `_extract_location`) dilebur menjadi fungsi tunggal yang kuat: `_parse_location_intent(query)`.
   - Implementasi **Relaksasi Radius Otomatis** (Mulai dari 15km -> mekar ke 25km -> mekar ke 40km -> Region Fallback) jika kuota hasil kurang dari 5 tempat.
   - API kini mengembalikan metadata terstruktur `radius_km` dan `fallback_used` pada objek `location_context`.

2. **RAG Chatbot murni & Anti-Iseng (`chatbot_service.py` & `llm_guard.py`)**:
   - Pengaktifan **Hard Context Guardrail** untuk menapis kueri non-wisata secara instan sebelum menyentuh LLM API token.
   - Penghapusan data kaku `backend_reason` dari data LLM agar Llama 3.1 8B menulis ulasan unik & natural khas Sunda (Cepot).
   - Penambahan fungsi validasi output ketat (`validate_llm_output`) untuk menangkap halusinasi ID lokasi fiktif.

## 🔧 Langkah Integrasi oleh Tim Backend:
1. Cadangkan (Backup) file lama Anda di dalam `backend/app/` dan `backend/app/services/`.
2. Salin seluruh file dari folder rilis ini ke struktur direktori proyek Anda masing-masing.
3. Pastikan konfigurasi `.env` berikut telah terisi jika menggunakan mode Online LLM OpenRouter:
   ```env
   MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM=true
   OPENROUTER_API_KEY=your_key_here
   ```
4. Jalankan pengujian server: `python app/main.py` atau `uvicorn app.main:app`.

Sistem siap diintegrasikan dengan Frontend!
