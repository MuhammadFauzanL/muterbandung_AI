# PANDUAN INTEGRASI TIM BACKEND SERVER - MUTERBANDUNG V1.0

Folder ini berisi file-file backend hasil audit, perbaikan, dan optimasi menyeluruh untuk fitur **RAG Chatbot AI (Cepot AI)** dan **AI Planner (Arsitektur 3-Layer)** beserta **Location-Aware Geospasial Recommender**.

## 📁 Struktur File Rilis
```text
BACKEND_DELIVERY_RELEASE_V1/
├── README_INTEGRATION.md      <- Panduan ini
├── main.py                    <- Masuk ke backend/app/main.py (Route Gateway)
└── services/                  <- Masuk ke backend/app/services/
    ├── llm_extractor.py       <- [BARU] Layer 1 AI Planner: Parser Intent Bahasa Natural ke JSON
    ├── penginapan_service.py  <- [BARU] Layanan integrasi Hotel/Penginapan
    ├── recommender.py         <- Mesin Geospasial Haversine & Radius Dinamis
    ├── chatbot_service.py     <- Sistem RAG Chatbot, Hard Guardrail & Failover LLM
    ├── llm_evidence_pack.py   <- Kompilasi paket data untuk LLM RAG
    └── llm_guard.py           <- Kontrak Output JSON, Validasi Fakta, Prompt Persona
```

## 🚀 Perubahan Utama & Fitur Baru yang Siap Digunakan:

### A. Sistem AI Planner (3-Layer Architecture)
1. **Layer 1: Intent Parsing (`llm_extractor.py`)**: Fitur baru untuk membedah kueri bebas dari user ("cari tempat wisata alam di lembang yang ramah anak") menjadi parameter terstruktur (JSON).
2. **Geospasial Core (`recommender.py`)**: Implementasi Relaksasi Radius Otomatis (Mulai dari 15km -> mekar ke 25km -> mekar ke 40km -> Region Fallback) jika kuota hasil sedikit.
3. **Fase Akomodasi (`penginapan_service.py`)**: Pencarian hotel terdekat dari titik wisata yang dipilih.

### B. RAG Chatbot Murni & Anti-Iseng
1. **Penjaga Konteks (`chatbot_service.py` & `llm_guard.py`)**: Pemblokiran instan untuk kueri non-wisata sebelum memanggil API OpenRouter.
2. **Anti-Halusinasi (`llm_evidence_pack.py`)**: Chatbot dipaksa hanya membaca data dari Recommender (Evidence Pack), mencegah jawaban fiktif.

## 🔧 Langkah Integrasi oleh Tim Backend:
1. Cadangkan (Backup) file lama Anda di dalam `backend/app/` dan `backend/app/services/`.
2. Salin seluruh file dari folder rilis ini ke struktur direktori proyek Anda masing-masing.
3. Pastikan konfigurasi `.env` berikut telah terisi jika menggunakan mode Online LLM:
   ```env
   MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM=true
   OPENROUTER_API_KEY=your_key_here
   ```
4. **[PENTING] Penanganan Model Lokal (.pkl & Embeddings)**: 
   - Sistem ini menggunakan model lokal yang berat (misal: `model_sentimen_muterbandung.pkl`).
   - **JANGAN PERNAH** melakukan *push* file `.pkl` atau folder model berukuran besar ke dalam Git/GitHub.
   - Pindahkan file model tersebut secara manual langsung ke server *production* (via FTP, SFTP, atau SCP) dan letakkan di struktur *path* yang sesuai dengan yang dibaca oleh kode.
5. Jalankan pengujian server: `python app/main.py` atau `uvicorn app.main:app`.

Sistem siap diintegrasikan dengan Frontend!
