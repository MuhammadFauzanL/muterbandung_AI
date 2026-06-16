# 🗺️ Peta Arsitektur & Alur Kerja AI Backend MuterBandung (PIJAK)

Dokumen ini menjelaskan secara teknis mengenai komponen, lokasi file, dan cara kerja sistem AI Backend untuk digunakan sebagai acuan integrasi tim pengembang.

---

## 🏗️ 1. Lapisan Integrasi Utama (Entry Point)
Pintu masuk utama bagi seluruh permintaan dari aplikasi antarmuka.

*   **File:** `backend/app/main.py`
*   **Tipe:** Flask Web Server / API Router.
*   **Fungsi:** Mengatur *routing* API, validasi JSON payload awal, dan mengorkestrasi pemanggilan layanan AI (*Services*). Semua *request* wajib melalui file ini.

---

## 🎭 2. Komponen Persona & Klasifikasi User
Sistem pertama yang menentukan profil pengguna untuk keperluan personalisasi halaman utama.

*   **Service Logic:** `backend/app/services/persona_service.py`
*   **Model Utama (ML):** `Models/persona_kmeans.pkl` & `Models/persona_scaler.pkl`
*   **Fallback (Rules):** `MUTERBANDUNG_CORE_SYSTEM/1_Dataset_Runtime/Persona_Home/PERSONA_HOME_RULES_2026-06-13.json`
*   **Cara Kerja:**
    1.  Menerima parameter kesukaan pengguna (Label).
    2.  `PersonaService` memuat model K-Means via `joblib`.
    3.  Melakukan prediksi *cluster* id secara matematis.
    4.  Jika model gagal dimuat atau input tidak valid, sistem melakukan *fallback* ke sistem pencocokan aturan (*Rule-based*) di file JSON.

---

## 📝 3. Komponen AI Planner (Core Recommender)
Mesin utama untuk mencari dan memberikan rekomendasi tempat wisata.

*   **Service Logic:** `backend/app/services/recommender.py`
*   **Intent Parser:** `backend/app/services/llm_extractor.py` (Menggunakan OpenRouter Llama-3.1).
*   **Dataset Utama:** `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_CLEANED.csv`
*   **Geospatial Helper:** `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/landmark_aliases.csv`
*   **Cara Kerja:**
    1.  `llm_extractor` membedah kueri natural menjadi parameter kaku (Category, Price, Location).
    2.  `Recommender` melakukan pencarian semantik menggunakan model **IndoBERT lokal** di memori RAM.
    3.  Melakukan filter koordinat berdasarkan *landmark* dan menghitung radius (Haversine).

---

## 🗣️ 4. Komponen Persona Cepot (RAG Layer)
Menghasilkan narasi alasan rekomendasi yang natural dan interaktif.

*   **Service Logic:** `backend/app/services/chatbot_service.py`
*   **Data Preparation:** `backend/app/services/llm_evidence_pack.py`
*   **Guardrails & Prompt:** `backend/app/services/llm_guard.py`
*   **Cara Kerja:**
    1.  Mengambil Top 5 hasil dari AI Planner.
    2.  Membungkusnya menjadi *Evidence Pack* (JSON ketat).
    3.  Mengirimkan ke LLM (OpenRouter) dengan instruksi persona dari `llm_guard`.
    4.  Memvalidasi output LLM agar tidak ada data harga/lokasi yang fiktif (*Anti-Hallucination*).

---

## 👣 5. Komponen Analisis Perilaku (Behaviour Service)
Memberikan prediksi langkah atau kategori selanjutnya bagi pengguna.

*   **Service Logic:** `backend/app/services/behaviour_service.py`
*   **Model Utama (Deep Learning):** `Behaviour_Workspace/lstm_v1_extracted/behaviour_lstm_muterbandung_v1.keras`
*   **Encoder Pendukung:** `Behaviour_Workspace/lstm_v1_extracted/category_encoder_v1.pkl`
*   **Model Baseline:** `Behaviour_Workspace/03_Models/markov_order1_baseline.pkl`
*   **Cara Kerja:**
    1.  Menerima riwayat klik/kategori pengguna.
    2.  `BehaviourService` memuat model LSTM menggunakan `Tensorflow Keras`.
    3.  Jika data riwayat cukup, LSTM memprediksi probabilitas kategori selanjutnya.
    4.  Jika data minim, sistem otomatis menggunakan model *Markov Chain* (.pkl) sebagai *baseline* prediksi.

---

## 🏨 6. Komponen Penginapan (Automatic Distance Search)
Mencari akomodasi terdekat dari destinasi wisata pilihan.

*   **Service Logic:** `backend/app/services/penginapan_service.py`
*   **Dataset Hotel:** `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_PENGINAPAN_ONLY.csv`
*   **Cara Kerja:**
    1.  Menerima koordinat tujuan wisata.
    2.  Menghitung jarak ke seluruh data hotel di CSV secara matematis.
    3.  Menggabungkan skor jarak (70%) dan skor rating/sentimen (30%) untuk memberikan peringkat hotel terbaik di area tersebut.

---

## 💡 Ringkasan Tipe File untuk Developer
1.  **File `.py` (Logic):** Berisi alur kodingan yang bisa dibaca dan diedit manusia.
2.  **File `.pkl` & `.keras` (Binary):** Berisi "Otak" hasil training Machine Learning. **Dilarang edit manual.** Harus dibaca menggunakan `joblib` atau `keras.load_model`.
3.  **File `.csv` (Database):** Sumber data mentah. Bisa diedit menggunakan Excel jika ingin menambah destinasi atau mengubah harga tiket.
4.  **File `.json` (Config):** Berisi aturan baku sistem.
