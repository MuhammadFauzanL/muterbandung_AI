# 🏗️ Arsitektur Sistem Backend AI MuterBandung (PIJAK) - Status Saat Ini

Dokumen ini merepresentasikan status arsitektur **Production-Ready** dari *Backend AI* MuterBandung per versi terakhir. Semua rancangan eksperimental (seperti model K-Means/Markov .pkl) telah diarsipkan, dan sistem kini menggunakan arsitektur **Hybrid Symbolic-Neural Pipeline (3-Layer RAG)**.

---

## 1. Alur Kerja (The 3-Layer Pipeline)

### Layer 1: Intent Extractor (Penerjemah Niat)
Berfungsi menjembatani kueri kalimat panjang/rumit manusia menjadi parameter pencarian kaku (JSON).
*   **Engine:** LLM via OpenRouter API (model ringan: meta-llama/llama-3.1-8b-instruct).
*   **Cara Kerja:** Zero-shot *prompting*. Hanya bertugas mengekstrak kategori, batas harga, dan intensi lokasi.
*   **Proteksi (Heuristic Bypass):** Otomatis **dimatikan** jika kueri pendek (< 3 kata) untuk menghindari latensi ganda (*double trip*).

### Layer 2: Deterministic Recommender (Mesin Pencari Jarak & Fakta)
Berfungsi sebagai mesin *core* pencarian yang cepat, 100% faktual, dan *offline*.
*   **Engine:** Python (Pandas) + irqaaa/indo-sentence-bert-base (Model lokal *HuggingFace* di RAM).
*   **Cara Kerja:**
    *   **Semantic Search:** Mengubah kueri teks menjadi *dense vector* untuk mencocokkan makna (misal: "tenang" = "alam").
    *   **Spatial Search (Radius):** Menghitung jarak menggunakan *Haversine Formula* berdasarkan koordinat (Latitude/Longitude).
*   **Keunggulan:** Bebas halusinasi, pencarian berlangsung dalam fraksi detik (~0.1 detik).

### Layer 3: Cepot Persona (RAG - Retrieval-Augmented Generation)
Berfungsi memberikan nyawa/interaksi pada hasil pencarian kaku agar lebih natural (Gaya *Guide* Lokal Sunda).
*   **Engine:** LLM via OpenRouter API.
*   **Cara Kerja:** Menerima **Evidence Pack** (Koper Fakta JSON) dari Layer 2. Cepot HANYA boleh menulis alasan/narasi berdasarkan koper fakta ini.
*   **Proteksi:** Dilengkapi dengan alidate_llm_output. Jika Cepot berhalusinasi mengarang harga atau tujuan baru, jawabannya langsung ditolak dan diganti dengan *fallback* bawaan.

---

## 2. Struktur Data (Data Sources)

Sistem sudah TIDAK LAGI me-load model Machine Learning tradisional (.pkl atau .h5) saat *runtime*. Semua proses *training* sentimen telah dilakukan secara *pre-computed*. Backend saat ini membaca data murni dari memori (RAM):

1.  **DATABASE_WISATA_CLEANED.csv:** Dataset primer wisata. Berisi 587 baris yang memuat koordinat, kategori, harga, dan **nilai sentimen statis** (hasil *pre-computation* dari model sentimen sebelumnya).
2.  DATABASE_PENGINAPAN_ONLY.csv: Dataset sekunder untuk rekomendasi hotel radius terdekat.
3.  landmark_aliases.csv: Kamus alias nama jalan/daerah.

---

## 3. Topologi API (Untuk Frontend)

Tim Frontend menggunakan arsitektur *Decoupled* (terpisah) untuk performa dan UX yang berurutan:

*   **Pencarian Wisata Utama (POST /api/recommend):** Menjalankan Layer 1, 2, dan 3. Mengembalikan Kartu Wisata dan teks sapaan Cepot.
*   **Pencarian Penginapan Otomatis (GET /api/penginapan):** Hanya menjalankan Layer 2 (Haversine). Dipicu (*triggered*) secara otomatis oleh *Frontend* ketika pengguna membuka halaman "Planner", menggunakan parameter lat & lon wisata yang ada di keranjang.
*   **Chatbot Interaktif (POST /api/chat):** Menjalankan Layer 3 khusus untuk meladeni tanya jawab interaktif murni dengan Cepot.

---

## 4. Rencana Pengembangan Lanjutan (Future Phase)
Aset Machine Learning tradisional yang ada di *workspace* saat ini (persona_kmeans.pkl, model *LSTM Behaviour*) sengaja di-*hold*. Aset-aset ini disiapkan untuk Fase 2 (*Sequential AI*), di mana sistem nantinya akan mampu melacak riwayat (Log) perjalanan pengguna secara berurutan (misal: menebak *"setelah ke cafe, enaknya ke mana?"*).
