# 🤖 Implementasi AI Agent Backend (MuterBandung)

Dokumen ini menjelaskan arsitektur "Otak" AI yang tertanam di Backend, mencakup logika *Failover*, *Guardrails*, dan penggunaan model Machine Learning.

---

## 🏗️ Arsitektur "Dual-Brain" (Failover AI)
Sistem menggunakan dua penyedia LLM (Large Language Model) untuk menjamin sistem tidak pernah mati (*High Availability*).

### 1. Intent Parser & Chatbot Layer
*   **Layer 1 (Utama):** **Cloudflare Workers AI**
    *   **Model:** `@cf/meta/llama-3.3-70b-instruct-fp8-fast`
    *   **Keunggulan:** Latensi rendah, pengolahan teks cepat di *Edge*.
*   **Layer 2 (Cadangan):** **OpenRouter**
    *   **Model:** `meta-llama/llama-3.1-8b-instruct`
    *   **Pemicu:** Aktif otomatis jika Cloudflare mengembalikan error (Quota habis/Server down).

---

## 🛡️ Sistem Keamanan & Filter (Guardrails)
Backend menerapkan dua lapis pengamanan untuk mencegah *abuse* dan halusinasi data.

### 1. Hard Context Guardrail (Lokal)
Sebelum menyentuh AI eksternal, kueri user diperiksa oleh mesin lokal:
*   **File:** `backend/app/services/chatbot_service.py`
*   **Logika:** Mencocokkan input dengan `TOURISM_CONTEXT_KEYWORDS`.
*   **Hasil:** Jika user bertanya soal "Hacking", "Politik", atau "Resep Rendang", sistem langsung membalas dengan penolakan sopan (logat Sunda) tanpa memanggil API AI. Ini menghemat token 100% pada kueri sampah.

### 2. Prompt Guardrail (LLM Level)
*   **File:** `backend/app/services/llm_guard.py`
*   **Logika:** Instruksi ketat yang memaksa AI menjawab hanya berdasarkan `llm_evidence_pack` (Fakta dari CSV). AI dilarang mengarang harga atau tempat wisata yang tidak terdaftar.

---

## 🧠 Integrasi Model Machine Learning Asli
Sistem menjalankan model hasil training secara mandiri di server lokal.

1.  **Persona Engine (K-Means):**
    *   Memuat `Models/persona_kmeans.pkl`.
    *   Mengklasifikasikan user ke dalam 5 klaster profil berdasarkan preferensi awal.
2.  **Behaviour Engine (LSTM Deep Learning):**
    *   Memuat `behaviour_lstm_muterbandung_v1.keras` menggunakan **Tensorflow**.
    *   Memprediksi langkah user selanjutnya berdasarkan urutan kategori lokasi yang dikunjungi.
3.  **Search Engine (IndoBERT):**
    *   Menggunakan `SentenceTransformer` lokal untuk mencari makna kata (Semantic Search) di database wisata.

---

## 🛠️ Cara Kerja Pipa Data (Data Flow)
1.  **Request Masuk:** Melalui `main.py`.
2.  **Bypass Check:** Jika kueri <= 2 kata, AI Parser dilewati (Heuristic).
3.  **Security Check:** Jika di luar konteks wisata, kirim penolakan.
4.  **AI Execution:** Panggil Cloudflare -> (Fail) -> Panggil OpenRouter.
5.  **Data Enrichment:** Hasil AI digabung dengan data koordinat (Haversine) dan Rating dari CSV.
6.  **Response:** Balikkan JSON final ke Frontend.
