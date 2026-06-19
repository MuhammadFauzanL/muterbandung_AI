# AI Planner & Cepot AI Integration (Unstable Branch)

**Branch:** `feature/ai-integration-final`
**Status:** 🚧 *Work in Progress / Unstable*

## ⚠️ Peringatan
Branch ini berisi draf integrasi sistem **AI Planner** dan **Cepot AI Chatbot** ke dalam struktur utama (FastAPI & Next.js). Branch ini **sengaja dipisah dari `main`** karena penambahan dependensi Machine Learning yang berat (PyTorch, SentenceTransformers, dll.) dan sistem masih dalam tahap pengujian (belum stabil sepenuhnya). 

Jangan lakukan *merge* ke `main` sebelum semua route AI lolos *stress-test* dan dioptimasi.

---

## 🎯 Tujuan Branch Ini
Memindahkan "otak" AI (Recommender Core, LLM Inference, Persona, dan Behaviour Model) yang sebelumnya di-develop terpisah (pada *scratch/worktree*) ke dalam satu tubuh aplikasi utama (FastAPI backend), namun dengan rute yang aman dan tidak merusak fungsi aplikasi yang sudah berjalan.

## 🛠️ Apa Saja yang Sudah Berubah dari `main`?

1. **Backend API Routes Baru (`backend/app/api/recommendations.py`)**
   - Menambahkan `/recommendations/ai-planner`
   - Menambahkan `/recommendations/cepot-chat`
   - *Route* lama tidak dihapus agar *backward compatibility* terjaga.

2. **Integrasi Layer AI Core (`backend/app/services/`)**
   - Dimasukkannya `chatbot_service.py` untuk Cepot AI.
   - Tersedianya `llm_evidence_pack.py` dan `llm_guard.py` untuk memastikan LLM tidak berhalusinasi saat menjawab.

3. **Injeksi Sinyal Persona & Behaviour (`backend/app/services/`)**
   - Memasukkan model KMeans (`persona_service.py`) dan LSTM/Markov (`behaviour_service.py`).
   - Sinyal dari model ML ini diinjeksi sebagai *boost score* (direkam dalam `score_breakdown`), **bukan** sebagai filter kaku yang mendikte *ranking* rekomendasi utama.

4. **Frontend API & UI Contract (`frontend/`)**
   - Modifikasi `ChatbotWidget.tsx` agar sekarang bisa mengirim form (POST) ke *endpoint* `/recommendations/cepot-chat` dengan mengelola *state typing/sending*.
   - Pembaruan di layer `api.ts` agar frontend siap menerima objek `score_breakdown` dari AI tanpa memecah kartu/UI *existing* yang hanya memakai struktur camelCase lama.

5. **Aset & Model ML (`MUTERBANDUNG_CORE_SYSTEM/` & `ai_workspace/`)**
   - Model Pickle dan Keras untuk Persona & Behaviour.
   - Dataset referensi penginapan.

## 🚀 Apa yang Sedang/Akan Dilakukan Selanjutnya?

- **End-to-End Testing:** Memastikan RAG pipeline dapat membalas pertanyaan *user* di frontend hingga memanggil LLM OpenRouter tanpa *timeout*.
- **Lazy Loading Optimization:** Mengakali *import* Torch dan SentenceTransformers agar startup FastAPI tidak menjadi lambat.
- **Tuning Bobot Skor:** Menyesuaikan seberapa besar pengaruh *persona_score* dan *behaviour_score* terhadap relevansi *keyword* utama.

---
*Dokumen ini dibuat otomatis sebagai rangkuman konteks *staging* integrasi AI sebelum dilanjutkan ke tahap *deployment*.*
