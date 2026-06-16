# 📖 PIJAK AI Backend: Panduan Integrasi Lengkap (Frontend & Backend)

**Status:** Production-Ready (Stable)  
**Branch:** `feature/backend-ai-core-stable`  
**Tujuan Dokumen:** Memberikan panduan teknis yang sangat komprehensif bagi tim Frontend (UI/UX) dan tim Server/Backend untuk mengonsumsi 5 endpoint AI MuterBandung.

---

## 1. Arsitektur AI MuterBandung (Untuk Pengetahuan Tim)

Sistem ini tidak hanya menggunakan API sederhana, melainkan **Multi-Tier AI Pipeline** yang memadukan Machine Learning lokal dan LLM Generatif. Anda tidak perlu memahami cara latih modelnya, cukup pahami fungsinya:

*   **Pencarian Wisata (Core):** Menggunakan `Indo-Sentence-BERT` (Lokal) untuk pencarian makna kalimat (Semantic Search) + TF-IDF + Filter Radius (*Haversine*).
*   **Persona (Home):** Menggunakan model **K-Means Clustering** (.pkl) untuk menebak profil *user*. Jika *input* tidak sesuai, sistem otomatis turun (*fallback*) ke *Rules JSON*.
*   **Behaviour (Next Step):** Menggunakan model **Deep Learning LSTM** (.keras) untuk memprediksi kategori tempat wisata/kegiatan selanjutnya. Jika *input* kurang, otomatis turun ke model *Markov Baseline*.
*   **Chatbot & Narasi (Cepot):** Menggunakan LLM Generatif via OpenRouter API (Llama-3.1). LLM ini diawasi ketat (*Guardrails*) agar tidak berhalusinasi mengarang harga/lokasi.

---

## 2. Prasyarat Deployment (Untuk Tim Server/DevOps)

Jika aplikasi Flask ini di-*deploy* ke VPS/Cloud, pastikan:
1.  **RAM Minimal:** 1.5 GB hingga 2 GB. (Model `IndoBERT` dan `LSTM` akan dimuat ke RAM agar respons API secepat kilat).
2.  **Variabel Lingkungan (.env):** Wajib membuat file `.env` di root folder aplikasi dengan isi:
    ```env
    OPENROUTER_API_KEY="sk-or-v1-..."
    MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM=true
    ```
3.  **Dependencies:** Jalankan `pip install -r requirements.txt`. Pastikan `tensorflow`, `scikit-learn`, `joblib`, dan `sentence-transformers` terinstal.

---

## 3. Daftar Endpoint API (Untuk Tim Frontend)

Semua komunikasi menggunakan format JSON (Kirim JSON, Terima JSON).

### 📍 A. Pencarian Wisata & Narasi Cepot
**Tujuan:** Halaman *Explore* / *Search*.
*   **Endpoint:** `POST /api/recommend`
*   **Payload (Kirim):**
    ```json
    {
      "query": "wisata alam murah buat keluarga gratis di dago", // (Opsional) Ketikan user
      "categories": [],                 // (Opsional) Jika user mencentang filter UI
      "max_distance_km": 15.0,          // (Opsional) Radius batasan
      "top_k": 5,                       // (Opsional) Jumlah hasil
      "explain": true                   // WAJIB TRUE jika ingin narasi sapaan Cepot. False jika hanya butuh data kartu.
    }
    ```
*   **Response (Terima):**
    ```json
    {
      "status": "success",
      "recommendations": [              // LOOPING ARRAY INI UNTUK MEMBUAT UI CARD WISATA
         {
             "location_id": "LOC-050",
             "location_name": "Kawah Putih",
             "price_max": 31000,
             "distance_km": 12.5,
             "alasan": "Kawah Putih pas banget buat kamu..." // Hasil tulisan Cepot AI
         }
      ],
      "llm_rag_cached": {
          "answer": "Halo A'! Ini rekomendasi dari Cepot..." // Render ini di dalam balon chat UI
      }
    }
    ```

### 🏨 B. Pencarian Penginapan Terdekat (Otomatis)
**Tujuan:** Halaman *Planner* (Tab Penginapan). Tidak butuh Search Bar!
*   **Endpoint:** `GET /api/penginapan`
*   **Cara Kerja:** Frontend mengambil koordinat wisata yang baru saja dipilih user, lalu menembaknya ke API ini.
*   **Parameter URL:**
    `GET /api/penginapan?lat=-7.1662&lon=107.4021&limit=5&category=hotel`
*   **Response:**
    Mengembalikan daftar hotel terdekat, diurutkan berdasarkan skor AI (70% Jarak, 30% Rating/Sentimen).

### 🎭 C. Penentuan Persona Beranda (K-Means AI)
**Tujuan:** Halaman *Home* ("Untuk Kamu"). Mengubah tema beranda.
*   **Endpoint:** `POST /api/persona/home`
*   **Payload:**
    ```json
    {
      "favorite_place_labels": ["Alam"],
      "activity_labels": ["Petualangan"],
      "mood_labels": ["Outdoor"],
      "free_only": false
    }
    ```
*   **Response:**
    ```json
    {
      "status": "success",
      "persona": {
        "persona_id": "nature_seeker",
        "home_boost_labels": ["Alam", "Pemandangan"] // Gunakan label ini untuk memfilter data statis di homepage
      },
      "metadata": {
        "model_used": true,  // Jika true berarti K-Means sukses, jika false berarti Fallback ke Rules
        "fallback_used": false
      }
    }
    ```

### 👣 D. Prediksi Perilaku / Next Action (LSTM AI)
**Tujuan:** Memberikan saran teks kecil di UI (misal: *"Setelah ke Cafe, enaknya lanjut ke mana?"*).
*   **Endpoint:** `POST /api/behaviour/next`
*   **Payload:**
    ```json
    {
      "session_categories": ["Alam", "Kuliner"], // Riwayat kategori yang dikunjungi user hari ini
      "current_category": "Kuliner"              // Lokasi terakhir
    }
    ```
*   **Response:**
    ```json
    {
      "status": "success",
      "next_category_predictions": [
        { "category": "Belanja", "score": 0.43 },
        { "category": "Religi", "score": 0.18 }
      ],
      "metadata": {
        "model_source": "deep_learning_lstm_v1" // Jika error, otomatis berubah jadi 'markov_order1_baseline'
      }
    }
    ```

### 💬 E. Chatbot Interaktif Cepot (Tanya Jawab)
**Tujuan:** Halaman obrolan bebas dengan Asisten AI.
*   **Endpoint:** `POST /api/chat`
*   **Payload:**
    ```json
    {
      "message": "Cepot, daerah dago dingin ga sekarang?"
    }
    ```
*   **Response:**
    Mengembalikan `data.answer` yang berisi teks murni hasil pemikiran LLM Llama-3.

---

## 🛑 Do and Don'ts untuk Tim Frontend
1.  **DO:** Lakukan *Loading State* (*skeleton/spinner*) yang komunikatif. Proses AI yang memanggil OpenRouter (Explain, Chat) bisa memakan waktu 2-4 detik. Tuliskan *"Cepot sedang berpikir..."*.
2.  **DON'T:** Jangan biarkan AI Planner (Endpoint A) tercampur/tergantikan secara diam-diam oleh hasil dari Persona (Endpoint C) atau Behaviour (Endpoint D). Biarkan pencarian utama tetap objektif, gunakan Persona hanya untuk *styling* Beranda.
