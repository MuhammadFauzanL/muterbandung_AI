# SKILL FILE — MUTERBANDUNG AI TOURISM RECOMMENDER

> **INSTRUKSI UNTUK AI AGENT:**  
> Baca file ini SEBELUM mengerjakan apapun.  
> File ini adalah sumber kebenaran tunggal tentang status, aturan, dan arah proyek.  
> JANGAN keluar dari konteks yang dijelaskan di sini.

---

## 1. IDENTITAS PROYEK

- **Nama:** MuterBandung
- **Jenis:** Hybrid AI Tourism Recommender System (Capstone Project)
- **Cakupan Wilayah:** Bandung Raya (Kota Bandung, Kabupaten Bandung, Bandung Barat, Cimahi, Sumedang)
- **Arsitektur Lengkap:** Lihat `ARCHITECTURE.md` di root proyek
- **Workspace:** `d:/File/file/Fauzan Lubada/PIJAK/`

---

## 2. APA YANG BOLEH DAN TIDAK BOLEH DILAKUKAN

### ✅ BOLEH
- Mengerjakan tugas data engineering (cleaning, enrichment, normalisasi, labeling)
- Mengerjakan tugas NLP (sentiment analysis, aspect extraction, multi-label classification)
- Mengerjakan tugas ML modeling (recommendation engine, learning-to-rank, feasibility scoring)
- Membuat/menjalankan script Python untuk manipulasi dataset
- Melakukan riset internet untuk verifikasi data wisata (deskripsi, jam buka)
- Membangun prototype UI (Streamlit)

### 🚫 DILARANG
- Mendesain ulang arsitektur proyek tanpa diminta
- Menghapus baris data dari dataset manapun
- Mengarang/menebak data (deskripsi, jam operasional, harga) tanpa sumber
- Membahas topik di luar lingkup proyek MuterBandung
- Membuat model ML tanpa dataset yang sudah bersih
- Mengubah struktur kolom dataset tanpa persetujuan user
- Mengerjakan langkah yang belum diminta oleh user — tanya dulu

---

## 3. STATUS PROYEK (Update: 21 Mei 2026)

### Fase yang Sudah Selesai ✅

| Fase | Deskripsi | File Output Utama |
|------|-----------|-------------------|
| Fase 1 | Scraping ulasan Google Maps (~28.576 review) | `MASTER_REVIEWS_ENRICHED.csv` |
| Fase 2 | Cleaning & deduplikasi review | `MASTER_REVIEWS_ENRICHED.csv` |
| Fase 3 | EDA (Exploratory Data Analysis) | Notebooks di `Notebooks/` |
| Fase 4 | Aspect-Based NLP (5 Aspek) | Kolom `mentions_*` di master review |
| Fase 5 | Binary Sentiment SVM (94% akurasi) | Model di `Scripts/` |
| Fase 6 | Core Engine Prototype | `DATABASE_MUTERBANDUNG_ENGINE.csv` |
| Enrichment | Metadata 232 lokasi (deskripsi + jam buka/tutup + traceability) | `DATABASE_WISATA_DENGAN_METADATA.csv` + `.xlsx` |

### Fase yang Belum Dikerjakan ❌

| Fase | Deskripsi | Prioritas | Prasyarat |
|------|-----------|-----------|-----------|
| **KRITIS-A** | Normalisasi nama lokasi (review ↔ database) | 🔴 KRITIS | Tidak ada |
| **KRITIS-B** | Label sentimen NLP ~13.061 review baru | 🔴 Tinggi | Normalisasi nama |
| Fase 7 | Multi-Label Attribute Classifier | 🟡 Sedang | Sentimen selesai |
| Fase 8 | Integrasi Hotel + Haversine | 🟡 Sedang | Data hotel |
| Fase 9 | Candidate Package Generator | 🔧 | Fase 7 + 8 |
| Fase 10 | Feasibility + Learning-to-Rank | 🔧 | Fase 9 |
| Fase 11 | RAG + Evidence Re-Ranker | 🔧 | Embedding review |
| Fase 12 | Frontend UI (Streamlit → Mobile) | 🔧 | Semua fase AI |

---

## 4. FILE-FILE PENTING

### Dataset Utama
| File | Deskripsi | Baris |
|------|-----------|-------|
| `DATABASE_WISATA_DENGAN_METADATA.csv` | Master lokasi wisata + metadata enriched | 232 |
| `DATABASE_WISATA_DENGAN_METADATA.xlsx` | Versi Excel dari file di atas | 232 |
| `DATABASE_MUTERBANDUNG_ENGINE.csv` | Engine prototype (skor sentimen, rating, aspek) | 232 |
| `DATABASE_WISATA_FINAL_LENGKAP.csv` | Master lokasi lama (sebelum enrichment) | 232 |
| `MuterBandung_Colab_Package/MASTER_REVIEWS_NLP.csv` | Review yang sudah dilabeli sentimen (lama) | ~15.515 |
| `dataset_hotel_cimahi_semua_kolom.csv` | Data hotel (belum diintegrasikan) | ? |

### Dokumentasi
| File | Deskripsi |
|------|-----------|
| `ARCHITECTURE.md` | Arsitektur lengkap 9 komponen AI pipeline |
| `audit_progress_pijak.md` | Audit dataset per 19 Mei 2026 |
| `SKILL_CONTEXT_MUTERBANDUNG.md` | **FILE INI** — context anchor untuk AI agent |
| `readme.md` | README proyek + MIOA directive chatbot |

### Direktori
| Direktori | Isi |
|-----------|-----|
| `Scripts/` | Script Python (batch applier, sentiment, checking) |
| `Notebooks/` | Jupyter notebooks (training, EDA, NLP prep) |
| `Apify_Workspace/` | Config dan script untuk Apify scraper |
| `Scraping/` | File terkait scraping |
| `Dataset/` | Dataset mentah |

---

## 5. KOLOM DATABASE WISATA (DATABASE_WISATA_DENGAN_METADATA.csv)

```
location_id, location_name, latitude, longitude,
price_min, price_max, price_type,
category, subcategory,
jam_buka, jam_tutup,                    ← jam legacy (umum)
estimasi_durasi_menit, tags_sintetis,
deskripsi_google,                       ← deskripsi faktual singkat
jam_buka_weekday, jam_tutup_weekday,    ← format HH:MM
jam_buka_weekend, jam_tutup_weekend,    ← format HH:MM
sumber_deskripsi, sumber_jam,           ← traceability
status_deskripsi, status_jam,           ← traceability
catatan_jam                             ← traceability
```

### Aturan Kolom Jam
- Format: `HH:MM` (24-jam). Contoh: `08:00`, `17:00`, `23:59`
- Jika tempat tutup permanen: semua jam dikosongkan + `status_jam = temporarily_closed_or_unclear`
- Jika weekend = reservasi saja: jam weekend dikosongkan + `status_jam = seasonal_or_uncertain`
- Nilai `Tutup` pada beberapa baris menandakan hari tertentu tempat tidak buka

### Status Label yang Digunakan
- `status_deskripsi`: `verified`, `filled_from_reliable_source`, `needs_review`, `not_found`
- `status_jam`: `verified`, `general_schedule_used_for_both`, `weekday_copied_from_weekend`, `weekend_copied_from_weekday`, `seasonal_or_uncertain`, `temporarily_closed_or_unclear`, `not_found`

---

## 6. MASALAH KRITIS YANG HARUS DISELESAIKAN

### Masalah #1: Normalisasi Nama Lokasi (🔴 KRITIS)
- **Apa:** ~86 lokasi di dataset review memiliki nama berbeda dari database wisata
- **Dampak:** ~40% review tidak terhubung ke lokasi wisata saat modeling
- **Contoh:** `23 PASKAL Shopping Center` vs `23 Paskal Shopping Center`
- **Solusi:** Buat mapping dictionary + script normalisasi
- **File terkait:** `audit_progress_pijak.md` bagian 4

### Masalah #2: Review Baru Belum Dilabeli Sentimen (🔴 Tinggi)
- **Apa:** ~13.061 review dari batch scraping baru belum punya label sentimen
- **Dampak:** Model sentimen hanya bekerja pada data lama
- **Solusi:** Jalankan pipeline SVM yang sudah ada pada review baru
- **Prasyarat:** Normalisasi nama harus selesai dulu

### Masalah #3: Nilai "Tutup" di Kolom Jam
- **Apa:** 8 baris memiliki nilai `Tutup` (bukan format HH:MM) di kolom jam weekday/weekend
- **Dampak:** Format tidak konsisten
- **Solusi:** Ganti dengan NaN + tandai `catatan_jam` bahwa hari tertentu tutup

---

## 7. ATURAN INTERAKSI DENGAN USER

1. **Selalu tanya sebelum mengerjakan** — jangan langsung eksekusi tanpa konfirmasi
2. **Jelaskan dulu, kerjakan kemudian** — user lebih suka memahami rencana sebelum eksekusi
3. **Satu langkah per waktu** — jangan lompat fase
4. **Jika ragu, kosongkan** — lebih baik data kosong daripada data salah
5. **Selalu validasi** — cek row count sebelum dan sesudah setiap operasi
6. **Backup sebelum modifikasi besar** — salin file asli sebelum mengubah

---

## 8. CARA MENGGUNAKAN FILE INI

### Untuk Memulai Sesi Baru
1. Baca file ini terlebih dahulu
2. Periksa bagian "Status Proyek" untuk tahu posisi terkini
3. Periksa bagian "Masalah Kritis" untuk tahu apa yang mendesak
4. Tanyakan ke user: "Mau lanjutkan dari langkah mana?"

### Untuk Mengupdate File Ini
- Setiap kali ada fase yang selesai, update tabel di bagian 3
- Setiap kali ada masalah baru ditemukan, tambahkan di bagian 6
- Setiap kali ada file baru yang penting, tambahkan di bagian 4

---

## 9. REFERENSI ARSITEKTUR (RINGKASAN)

Sistem MuterBandung memiliki **9 komponen AI pipeline**:

```
User Input → Semantic Matcher → Multi-Label Filter
  → Candidate Package Generator → Feasibility Model
  → Learning-to-Rank → Top 3 Paket
  → RAG Retrieval → Evidence Re-Ranker → LLM Chatbot
```

Detail lengkap ada di `ARCHITECTURE.md`.

---

> **PERINGATAN AKHIR:**  
> Jangan pernah mengerjakan hal di luar scope proyek ini.  
> Jangan pernah mengarang data.  
> Jangan pernah memodifikasi dataset tanpa konfirmasi user.  
> Selalu rujuk file ini sebagai panduan utama.
