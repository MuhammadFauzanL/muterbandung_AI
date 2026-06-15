# 🧠 MuterBandung AI Backend Context

## 📌 Pendahuluan
Dokumen ini dibuat secara khusus untuk memandu **Backend Developer**, **Frontend Developer**, maupun **AI Agent** yang akan melanjutkan pengembangan sistem MuterBandung (PIJAK). Dokumen ini berisi peta arsitektur *AI Core Engine* yang sudah berstatus **STABIL (Code Freeze)**.

---

## 🏗️ Arsitektur 3-Layer AI Pipeline
Sistem ini menggunakan arsitektur *Hybrid Symbolic-Neural Pipeline* yang menggabungkan kecepatan kalkulasi lokal (TF-IDF/Radius) dengan kecerdasan bahasa LLM eksternal.

### 1️⃣ Layer 1: Intent Extractor (Penerjemah Bahasa)
*   **File:** ackend/app/services/llm_extractor.py
*   **Peran:** Saat *user* mengetik kalimat kompleks (*"wisata alam murah buat keluarga gratis di dago"*), model Llama (OpenRouter) dipanggil untuk mengubah teks tersebut menjadi parameter JSON statis (Kategori, Harga, Lokasi, Fasilitas).
*   **Heuristic Bypass:** Untuk mempercepat respons, Layer 1 akan mati otomatis jika *query* kurang dari 3 kata (misal: *"Kawah Putih"*).

### 2️⃣ Layer 2: Deterministic Recommender (Mesin Pencari Jarak & Teks)
*   **File:** ackend/app/services/recommender.py & ackend/app/services/penginapan_service.py
*   **Peran:** Mesin *offline* yang mencocokkan *query* dengan dataset CSV.
    *   **Wisata:** Menggunakan *TF-IDF* dan **Indo-Sentence-BERT (Model Lokal)** untuk *Semantic Search*. Jika ada kata lokasi, mesin ini akan mengunci pencarian dalam radius jarak tertentu (*Haversine*).
    *   **Penginapan:** Membaca koordinat lintang/bujur destinasi wisata, lalu meranking hotel terdekat (Skor Jarak 70%) dan rating tertinggi (Skor Rating 30%).
*   **Penting:** Sistem ini berjalan di memori lokal (RAM) menggunakan Pandas. Model irqaaa/indo-sentence-bert-base (~450MB) diload langsung ke RAM *server*.

### 3️⃣ Layer 3: RAG & Persona Generator (Cepot AI)
*   **File:** ackend/app/services/chatbot_service.py, llm_evidence_pack.py, llm_guard.py
*   **Peran:** Menerima 5 rekomendasi mentah dari Layer 2 (*Evidence Pack*), lalu memanggil OpenRouter (LLM) untuk mengubahnya menjadi narasi sapaan khas lokal (Sunda) bergaya asisten **Cepot**.
*   **Strict RAG Guard:** LLM dilarang keras mengarang harga, lokasi, atau jam buka baru. Ia hanya mengubah gaya bahasa dari data yang disajikan oleh Layer 2.

---

## 📂 Database yang Digunakan (Data Source)
File-file CSV ini berada di folder i_workspace/Wisata_Workspace/01_Dataset/3_Curated/ dan dimuat saat inisiasi aplikasi:
1.  DATABASE_WISATA_CLEANED.csv: Data utama wisata (~587 baris). Memuat nilai sentiment_score yang sudah di-*generate* sebelumnya secara statis.
2.  DATABASE_PENGINAPAN_ONLY.csv: Data utama hotel/villa (~547 baris).
3.  landmark_aliases.csv: Kamus alias lokasi untuk *fallback*.

---

## 🔌 Panduan Interaksi API (Untuk Frontend / Server Utama)

Sistem AI ini menyediakan 3 *endpoint* yang sudah bersih dan mengembalikan *Standard JSON Response*.

### 1. Pencarian Wisata (Layer 1, 2, 3 Bekerja)
*   **Rute:** POST /api/recommend
*   **Fungsi:** Mengembalikan daftar destinasi wisata dan narasi sapaan Cepot.
*   **Payload (Kirim):** { "query": "teks...", "explain": true } *(Ganti explain ke false jika tidak butuh teks sapaan Cepot untuk mempercepat loading).*
*   **Response (Ambil):** 
    *   Kartu Wisata: data.recommendations (Array)
    *   Sapaan Cepot: data.llm_rag_cached.answer (String)

### 2. Pencarian Penginapan Terdekat (Hanya Radius)
*   **Rute:** GET /api/penginapan?lat={FLOAT}&lon={FLOAT}
*   **Fungsi:** Mengembalikan hotel terdekat berdasarkan titik koordinat wisata yang dikirim.
*   **Response (Ambil):** data.data (Array)

### 3. Chatbot Interaktif (Tanya Jawab Bebas Cepot)
*   **Rute:** POST /api/chat
*   **Fungsi:** Merespons obrolan bebas dari *user* di dalam kotak chat UI, tetap diawasi oleh RAG (tidak halusinasi).
*   **Response (Ambil):** data.answer (String)

---

## ⚠️ Peringatan Deployment (DevOps)
1.  **RAM Server:** Pastikan *server deployment* memiliki RAM yang cukup (disarankan minimal 1.5 - 2 GB) karena model IndoBERT dan dataset di-*load* seluruhnya ke memori.
2.  **Environment Variable:** File .env tidak di-commit demi keamanan. Pastikan *server* memiliki variabel OPENROUTER_API_KEY agar AI tidak *crash*.
3.  **Hanya Fitur Inti:** Fitur "Oleh-Oleh" telah dihapus dari sistem untuk memfokuskan performa pada wisata dan penginapan.
