# LLM Upgrade Blueprint MuterBandung

## Ringkasan

Dokumen ini menjelaskan cara meningkatkan MuterBandung dengan bantuan LLM tanpa mengorbankan sifat deterministik, data integrity, dan hasil rekomendasi yang realistis. Prinsip utama sistem tetap:

```text
Filter deterministic first, LLM second.
```

LLM tidak boleh menjadi mesin utama untuk menentukan kebenaran data. LLM hanya boleh dipakai setelah backend menghasilkan kandidat destinasi yang sudah valid berdasarkan budget, jarak, kategori, status aktif, harga, label, jam buka, dan cakupan wilayah.

Nama teknis sistem yang disarankan:

```text
Hybrid NLP and LLM-Assisted Tourism Recommendation System
```

atau:

```text
Deterministic Constraint-Based Tourism Recommender with LLM Re-ranking and Itinerary Generation
```

---

## 1. Masalah Yang Ingin Diselesaikan

Sistem rekomendasi wisata tidak cukup jika hanya memakai keyword search atau chatbot biasa. Keyword search sering gagal memahami maksud user, sedangkan chatbot murni rawan halusinasi, tidak konsisten, dan bisa melanggar constraint seperti budget, jarak, atau status destinasi.

MuterBandung perlu berada di tengah:

- deterministic untuk data yang harus pasti,
- NLP semantic untuk memahami maksud query,
- LLM untuk narasi, re-ranking, dan itinerary,
- QA untuk membuktikan hasilnya benar secara real-world.

---

## 2. Prinsip Deterministik

Sistem harus dibuat sebisa mungkin stabil. Query yang sama dengan input yang sama sebaiknya menghasilkan output yang sama, kecuali data memang berubah.

Yang harus deterministik:

- filtering kategori,
- filtering budget,
- filtering harga gratis atau berbayar,
- filtering jarak,
- filtering jam malam,
- filtering scope Bandung Raya,
- validasi koordinat,
- validasi destinasi aktif,
- candidate list sebelum LLM,
- aturan no strong match,
- skor ranking dasar.

Yang boleh lebih fleksibel:

- bahasa penjelasan,
- itinerary naratif,
- urutan itinerary versi LLM,
- alasan rekomendasi yang ditulis secara natural.

Untuk menjaga LLM tetap stabil:

- gunakan `temperature = 0` atau serendah mungkin,
- gunakan JSON schema,
- kirim hanya candidate list yang sudah valid,
- paksa LLM memilih dari `destination_id` yang tersedia,
- validasi ulang output LLM di backend,
- simpan cache hasil LLM untuk input yang sama.

---

## 3. Arsitektur Target

Alur sistem yang disarankan:

```text
User Input
  -> Frontend form + natural language preference
  -> Backend validation
  -> Deterministic filtering
  -> Semantic retrieval
  -> Candidate list
  -> LLM re-ranking / itinerary generation
  -> Backend validation of LLM output
  -> Final recommendation response
```

LLM tidak menerima seluruh dataset. LLM hanya menerima kandidat yang sudah lolos filter.

Contoh kandidat yang dikirim ke LLM:

```json
{
  "destination_id": "wisata_001",
  "name": "Taman Hutan Raya Ir. H. Djuanda",
  "category": "Wisata Alam",
  "primary_intent": "Alam",
  "core_labels": ["Alam", "Edukasi", "Santai/Healing"],
  "ticket_price_min": 15000,
  "distance_km": 8.2,
  "rating": 4.5,
  "sentiment_score": 0.82,
  "sentiment_model_source": "tfidf_linearsvc",
  "sentiment_model_version": "run_nlp_pipeline_v2",
  "sentiment_available": true,
  "verified_flags": {
    "coordinate_verified": true,
    "price_verified": true,
    "night_verified": false
  }
}
```

LLM hanya boleh mengembalikan `destination_id` dari kandidat tersebut.

---

## 4. Peran LLM Yang Aman

LLM boleh digunakan untuk:

- re-ranking dari kandidat valid,
- membuat itinerary 1 sampai beberapa hari,
- menjelaskan alasan rekomendasi,
- membuat narasi yang mudah dipahami user,
- menyusun trade-off seperti murah tapi jauh, dekat tapi ramai,
- merangkum risiko atau catatan data.

LLM tidak boleh digunakan untuk:

- membuat destinasi baru,
- menentukan harga pasti,
- menghitung jarak,
- menganggap tempat buka jika datanya tidak ada,
- mengubah status destinasi closed menjadi aktif,
- memasukkan tempat di luar scope Bandung Raya,
- melanggar constraint budget,
- mengarang fasilitas.

---

## 5. Anti-Halusinasi

Anti-halusinasi harus dibuat sebagai sistem, bukan hanya prompt.

### 5.1 Evidence Pack

Setiap kandidat yang dikirim ke LLM harus membawa evidence ringkas:

```json
{
  "source_fields": {
    "category": "Dataset curated",
    "price": "Curated estimate",
    "coordinate": "Google Maps scraped data",
    "labels": "Rule-based + manual review",
    "sentiment": "Review sentiment model with explicit provenance metadata"
  },
  "limitations": [
    "Harga dapat berubah",
    "Jam buka perlu dicek ulang sebelum berangkat"
  ]
}
```

Status implementasi 2026-05-24:

```text
IMPLEMENTED
```

Evidence pack aktif sudah tersedia pada response `POST /api/recommend` melalui field:

```text
llm_evidence_pack
```

Spesifikasi teknis ada di:

```text
Dokumentasi_Sistem/LLM_EVIDENCE_PACK_SPEC.md
```

### 5.2 Output Contract

LLM harus dipaksa mengeluarkan JSON seperti:

```json
{
  "selected_destination_ids": ["wisata_001", "wisata_008"],
  "reranking_reason": {
    "wisata_001": "Cocok karena alam, dekat, dan harga masuk budget.",
    "wisata_008": "Cocok sebagai alternatif keluarga."
  },
  "warnings": [
    "Harga bersifat estimasi dan dapat berubah."
  ]
}
```

Jika LLM mengembalikan ID yang tidak ada, backend harus menolak output tersebut.

Status implementasi 2026-05-25:

```text
IMPLEMENTED - PROMPT GUARD + OUTPUT VALIDATOR
```

Response `POST /api/recommend` sekarang membawa field:

```text
llm_prompt_guard
```

Validator tersedia di:

```text
POST /api/llm/validate
Scripts/llm_guard.py
```

Validator menolak output LLM jika membuat destinasi baru, mengubah urutan ranking backend, mengarang harga, jarak, URL gambar/link, website, rating, atau fasilitas yang tidak tersedia di evidence pack.

### 5.3 Backend Validator

Setelah LLM menjawab, backend wajib cek:

- semua `destination_id` ada di candidate list,
- tidak ada harga baru yang dibuat LLM,
- tidak ada jarak baru yang dibuat LLM,
- tidak ada URL gambar/link/website baru yang dibuat LLM,
- fasilitas hanya boleh berasal dari `realworld_flags`,
- jumlah hari sesuai input,
- budget tidak dilanggar,
- destinasi closed atau out-of-scope tidak masuk,
- JSON valid dan parseable.

Kalau gagal, backend boleh:

- retry satu kali dengan prompt koreksi,
- fallback ke ranking deterministic,
- tampilkan rekomendasi tanpa itinerary LLM.

---

## 6. Personalisasi

Personalisasi harus bertahap agar tidak membuat sistem liar.

### Tahap 1: Session-Based Personalization

Tanpa login, sistem bisa memakai input saat itu:

- lokasi user,
- budget,
- jumlah orang,
- jumlah hari,
- preferensi query,
- mode ranking,
- radius,
- kategori pilihan.

Ini sudah cukup untuk rekomendasi awal.

### Tahap 2: Explicit Preference Profile

Jika nanti ada profil user, simpan preferensi eksplisit:

```json
{
  "preferred_labels": ["Alam", "Kuliner", "Santai/Healing"],
  "avoid_labels": ["Wahana Ekstrem", "Malam"],
  "max_budget": 100000,
  "preferred_area": "Lembang",
  "travel_style": "relaxed",
  "group_type": "family"
}
```

### Tahap 3: Feedback-Based Personalization

Simpan feedback ringan:

- user klik destinasi,
- user menyukai rekomendasi,
- user menyembunyikan destinasi,
- user memilih itinerary tertentu,
- user menolak alasan tertentu.

Tetapi jangan langsung mengubah sistem utama tanpa evaluasi. Feedback perlu dipakai sebagai fitur tambahan, bukan menggantikan filter deterministik.

---

## 7. Ground Truth Evaluation

Ground truth diperlukan agar sistem bisa dinilai secara ilmiah, bukan hanya berdasarkan perasaan.

### 7.1 Dataset Ground Truth

Buat file:

```text
Dataset/4_Evaluation/groundtruth_queries.csv
```

Kolom yang disarankan:

```csv
query_id,query,expected_primary_intents,expected_core_labels,required_filters,acceptable_destinations,blocked_destinations,min_relevance_score,notes
```

Contoh:

```csv
GT001,"wisata alam yang sejuk","Alam","Alam;Santai/Healing","Outdoor","Tahura Djuanda;Terminal Wisata Grafika Cikole;Orchid Forest Cikole","Paris Van Java",0.70,"Harus dominan alam, bukan mall"
```

### 7.2 Jenis Ground Truth

Ground truth tidak harus satu jawaban benar. Untuk rekomendasi wisata, lebih baik gunakan:

- acceptable destinations,
- blocked destinations,
- required labels,
- forbidden labels,
- required filters,
- expected no strong match.

Ini lebih realistis daripada memaksa satu top result saja.

---

## 8. Similarity dan Error Metrics

Evaluasi similarity harus menghasilkan angka yang bisa dibandingkan dari waktu ke waktu.

Metrik utama:

- `Precision@K`: berapa banyak Top K yang benar.
- `Recall@K`: berapa banyak destinasi acceptable yang muncul.
- `MRR`: apakah hasil benar muncul di posisi atas.
- `nDCG@K`: apakah urutan hasil sudah baik.
- `Intent F1`: apakah intent yang diekstrak sesuai ground truth.
- `Constraint Violation Rate`: apakah budget, jarak, malam, gratis dilanggar.
- `Hallucination Rate`: apakah LLM membuat destinasi/harga/jarak palsu.
- `No Strong Match Accuracy`: apakah query mustahil ditolak dengan benar.

Contoh output evaluasi:

```json
{
  "query_id": "GT001",
  "precision_at_5": 0.8,
  "recall_at_5": 0.67,
  "mrr": 1.0,
  "intent_f1": 0.86,
  "constraint_violations": 0,
  "hallucination_count": 0,
  "status": "PASS"
}
```

### 8.1 Error Taxonomy

Setiap kegagalan harus diklasifikasi:

- `intent_leakage`: intent terlalu melebar.
- `wrong_category`: kategori hasil tidak sesuai.
- `constraint_violation`: budget, jarak, jam, atau gratis dilanggar.
- `hallucinated_entity`: LLM membuat destinasi baru.
- `hallucinated_price`: LLM membuat harga palsu.
- `hallucinated_distance`: LLM membuat jarak palsu.
- `out_of_scope`: destinasi di luar Bandung Raya.
- `stale_data_risk`: data mungkin tidak terbaru.
- `weak_evidence`: hasil benar secara umum tetapi bukti data lemah.

---

## 9. Benchmarking LLM Dengan OpenRouter

OpenRouter cocok untuk pengalaman industrial karena satu endpoint bisa membandingkan banyak model. Tetapi benchmark harus tetap adil dan auditable.

### 9.1 Protokol Benchmark

Gunakan input yang sama untuk semua model:

- candidate list yang sama,
- prompt yang sama,
- JSON schema yang sama,
- temperature yang sama,
- max token yang sama,
- query yang sama.

Catat:

- model name,
- latency,
- input token,
- output token,
- cost jika tersedia,
- JSON validity,
- constraint obedience,
- hallucination count,
- itinerary usefulness,
- reranking quality.

### 9.2 File Hasil Benchmark

Buat:

```text
Dataset/4_Evaluation/llm_benchmark_results.csv
```

Kolom:

```csv
run_id,model,query_id,latency_ms,input_tokens,output_tokens,json_valid,hallucination_count,constraint_violation_count,rerank_score,itinerary_score,total_score,notes
```

### 9.3 Model Yang Dibandingkan

Jangan terpaku satu model. Minimal bandingkan:

- satu model murah dan cepat,
- satu model kuat,
- satu model fallback.

Pemilihan model aktual harus mengikuti ketersediaan dan harga terbaru dari provider. Jangan hardcode klaim harga tanpa verifikasi.

---

## 10. Prompt Template Aman

Contoh prompt re-ranking:

```text
Anda adalah LLM re-ranker untuk sistem rekomendasi wisata Bandung Raya.

Aturan wajib:
1. Pilih hanya destination_id dari candidate list.
2. Jangan membuat destinasi baru.
3. Jangan membuat harga baru.
4. Jangan membuat jarak baru.
5. Jangan mengubah status verifikasi.
6. Jika kandidat tidak cukup, tulis warning.
7. Output wajib JSON valid.

User request:
{user_request}

Structured constraints:
{constraints_json}

Candidate list:
{candidate_list_json}

Return JSON:
{
  "selected_destination_ids": [],
  "ranking_notes": {},
  "itinerary": [],
  "warnings": []
}
```

---

## 11. Implementasi Bertahap

### Fase 1: Evaluation Foundation

- Buat ground truth query dataset.
- Buat evaluator Precision@K, Recall@K, MRR, Intent F1.
- Simpan error taxonomy.
- Jadikan QC berbasis ground truth, bukan hanya pass/fail manual.

### Fase 2: LLM Guarded Re-ranker

- Buat candidate pack dari backend.
- Buat prompt JSON.
- Tambahkan backend output validator.
- Tambahkan fallback ke deterministic ranking.
- Cache hasil LLM.

### Fase 3: OpenRouter Benchmark

- Tambahkan konfigurasi provider LLM.
- Jalankan minimal 2 sampai 3 model.
- Simpan latency, token, JSON validity, hallucination rate.
- Pilih model berdasarkan bukti, bukan asumsi.

### Fase 4: Itinerary Generation

- Gunakan kandidat valid.
- Hitung budget backend.
- Hitung jarak backend.
- LLM hanya menyusun itinerary dan narasi.
- Backend validasi ulang itinerary.

### Fase 5: Personalization

- Tambahkan session preference.
- Tambahkan explicit user profile jika diperlukan.
- Tambahkan feedback ringan.
- Evaluasi apakah personalisasi meningkatkan metrik.

---

## 12. Paper Knowledge Structure

Untuk kebutuhan paper, laporan, atau skripsi, struktur yang disarankan:

```text
Title:
Hybrid NLP and LLM-Assisted Tourism Recommendation System for Bandung Raya

Abstract:
Penelitian ini membangun sistem rekomendasi wisata yang menggabungkan NLP semantic retrieval, analisis sentimen, deterministic constraint filtering, geospatial ranking, dan LLM-assisted itinerary generation. Sistem dirancang untuk mengurangi halusinasi dengan membatasi LLM hanya pada kandidat destinasi valid yang telah difilter oleh backend.

Problem:
Pencarian wisata biasa tidak cukup memahami preferensi natural language, sedangkan chatbot murni berisiko mengarang data dan melanggar constraint.

Method:
1. Data curation
2. Label taxonomy
3. Sentiment analysis
4. Semantic similarity
5. Deterministic filtering
6. Hybrid scoring
7. LLM re-ranking
8. Ground truth evaluation

Evaluation:
Precision@K, Recall@K, MRR, Intent F1, Constraint Violation Rate, Hallucination Rate, Latency, Token Usage.

Contribution:
Sistem menggabungkan deterministic validation dan LLM generation sehingga rekomendasi tetap terkontrol, relevan, personal, dan dapat diaudit.
```

---

## 13. Kesimpulan Teknis

LLM bisa membuat MuterBandung jauh lebih baik, tetapi hanya jika dipasang sebagai lapisan kedua. Kecerdasan utama sistem tetap harus berasal dari data bersih, filter deterministik, label yang benar, koordinat valid, dan evaluasi ground truth.

Prioritas terbaik sekarang:

1. Buat ground truth evaluasi.
2. Buat evaluator similarity dan error taxonomy.
3. Buat LLM guarded re-ranker.
4. Validasi output LLM agar tidak halusinasi.
5. Benchmark model lewat OpenRouter.
6. Baru lanjut itinerary generation dan personalisasi.

Status rekomendasi:

```text
PASSED WITH NOTES
```

Sistem saat ini sudah kuat sebagai MVP hybrid recommender, tetapi belum boleh disebut final industrial LLM recommender sebelum ground truth evaluation, output validator LLM, dan benchmark OpenRouter dijalankan.
