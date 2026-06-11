# Foundation Audit Before LLM - 2026-05-25

## Scope

Audit ini membaca catatan `MEET 23-05-2027.docx` dan kondisi sistem MuterBandung saat ini. Fokusnya bukan memilih LLM dulu, melainkan menilai apakah pondasi backend, dataset, evaluasi, environment, dan guardrail sudah cukup kuat agar output LLM nanti tidak menjadi liar.

## Meet Summary

Catatan meet mengarah ke arsitektur hybrid:

- Constraint-based filtering dulu: jarak, budget, kategori, status data.
- LLM setelah kandidat valid: re-ranking, itinerary, dan narasi personal.
- Form murni dianggap terlalu kaku; chatbot murni rawan parsing dan latensi.
- Web lebih disarankan daripada mobile.
- Stack target yang disarankan: Next.js/Tailwind, FastAPI, PostgreSQL/PostGIS, Gemini atau model lain via benchmark OpenRouter/Ollama.
- Scraping boleh dieksplorasi dengan etika: robots.txt, rate limiting, sumber legal, dan integritas data.
- Perlu sequence diagram, objective visual, benchmarking model, dan cold start.

## Current Verification

Perintah yang dijalankan:

```powershell
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard
python -B .\Scripts\evaluate_groundtruth.py
python -B .\scratch_qc.py
```

Hasil:

- Unit test: 26/26 OK.
- Groundtruth evaluator: 62/62 PASS.
- QC suite: 62/62 PASS.
- Live API `POST /api/recommend`: status 200, membawa `llm_evidence_pack` dan `llm_prompt_guard`.
- Dataset aktif: 234 baris curated, 213 destinasi aktif, 234 `location_id` unik, koordinat lengkap, 212 sentiment tersedia, 181 media tersedia.

## Strengths

Pondasi sistem sudah kuat pada sisi berikut:

- Backend sudah memakai prinsip deterministik dulu, terlihat dari `llm_evidence_pack` yang menandai `llm_may_rerank=false` dan `llm_may_create_destinations=false`.
- Output LLM sudah punya validator yang menolak destinasi, harga, jarak, rating, media URL, dan fasilitas yang tidak ada di evidence.
- Sentiment lineage sudah jujur: sumber aktif `tfidf_linearsvc`, bukan IndoBERT.
- Dataset curated sudah punya `location_id` unik, koordinat lengkap, metadata sentiment, dan metadata media konservatif.
- Groundtruth query sudah mencakup intent utama, negative query, lokasi dekat, radius, budget, malam, gratis, dan fasilitas.
- QC sudah punya preflight sehingga laporan valid tidak ditimpa ketika API mati.

## Key Vulnerabilities

### 1. Environment belum reproducible

Tidak ditemukan `requirements.txt`, `pyproject.toml`, atau environment spec di root project. Saat audit, environment berjalan di Python 3.13.2 dengan paket lokal seperti Flask 3.1.1, pandas 2.3.3, torch 2.9.1, transformers 4.57.3, dan sentence-transformers 5.2.0.

Risiko: sistem bisa gagal di laptop lain, saat demo, atau saat deploy karena versi dependency tidak terkunci.

Prioritas: sangat tinggi sebelum integrasi LLM eksternal.

### 2. Backend masih dev-server style

`Scripts/app.py` memuat model saat import dan menjalankan Flask development server via `app.run(...)`. Ini cukup untuk prototipe, tapi belum ideal untuk layanan yang memanggil LLM API.

Risiko: startup lambat, server sulit diskalakan, error model membuat seluruh API tidak siap, dan observability terbatas.

Prioritas: tinggi.

### 3. API belum punya input governance yang cukup

`/api/recommend` menerima query bebas, tetapi belum ada batas panjang input, request id, schema validation eksplisit, atau rate limiting. `top_k` juga dikunci di backend menjadi 5.

Risiko: prompt LLM bisa terlalu panjang, sulit debug, dan mudah terjadi variasi output tanpa jejak input yang rapi.

Prioritas: tinggi sebelum LLM benar-benar aktif.

### 4. LLM layer belum punya provider abstraction dan benchmark harness

Dokumen blueprint sudah membahas OpenRouter/Gemini/Ollama, tetapi sistem belum punya modul eksekusi LLM provider, cache, retry policy, cost logging, latency logging, atau benchmark dua model.

Risiko: ketika LLM ditambahkan, keputusan provider bisa menjadi subjektif dan sulit diaudit.

Prioritas: tinggi.

### 5. Storage masih CSV-first

Dataset curated sudah rapi, tetapi masih berbasis CSV. Meet menyarankan PostgreSQL + PostGIS untuk query geospasial.

Risiko: radius query, versi data, concurrent update, dan audit perubahan makin sulit saat sistem membesar.

Prioritas: menengah-tinggi; tidak wajib sebelum LLM explanation layer, tapi penting sebelum produk serius.

### 6. Backup Codex berada di workspace

Backup `.codex` sudah dibuat otomatis, tetapi folder `Codex_Backups` berada di root workspace. Walaupun `auth.json` dikecualikan, backup tetap berisi histori chat, log, dan state lokal.

Risiko: data pribadi/proyek bisa ikut tersalin atau terunggah bila workspace dipindah.

Prioritas: menengah. Aman untuk lokal, tetapi sebaiknya dipindah ke folder backup di luar project atau storage pribadi.

### 7. Evaluasi belum mencakup LLM real output

Evaluator saat ini sangat bagus untuk backend deterministic recommendation, evidence pack, dan validator. Namun belum ada evaluasi end-to-end terhadap output Gemini/OpenRouter/Ollama nyata.

Risiko: saat LLM aktif, kualitas narasi, itinerary, token cost, JSON adherence, dan latency belum terbukti.

Prioritas: tinggi setelah provider abstraction dibuat.

## LLM Readiness Verdict

```text
FOUNDATION: STRONG FOR PROTOTYPE
LLM READINESS: NOT YET READY FOR FULL AUTONOMOUS LLM OUTPUT
SAFE NEXT MODE: LLM explanation/itinerary layer only, behind backend evidence + validator
```

Sistem boleh lanjut ke LLM, tetapi bukan dengan cara chatbot bebas. LLM harus tetap menerima kandidat dari backend, output JSON, lalu divalidasi ulang.

## Recommended Next Steps

1. Buat environment lock: `requirements.txt` atau `pyproject.toml`.
2. Buat konfigurasi `.env.example`: port, model path, API URL, LLM provider, timeout, temperature, token limit.
3. Tambahkan request schema validation untuk `/api/recommend` dan `/api/llm/validate`.
4. Buat modul `llm_provider.py` dengan adapter Gemini, OpenRouter, dan optional Ollama.
5. Tambahkan LLM benchmark harness: query sama, evidence sama, ukur latency, token, JSON validity, hallucination, constraint violation.
6. Tambahkan LLM cache berbasis hash input evidence pack agar demo hemat biaya dan stabil.
7. Tambahkan structured logging: request id, query id, model, latency, validator result.
8. Baru setelah itu aktifkan endpoint itinerary LLM, misalnya `POST /api/llm/itinerary`.

## Engineering Recommendation

Jangan langsung mengganti ranking backend dengan LLM. Tahap paling aman adalah:

```text
Backend recommendation -> Evidence pack -> LLM itinerary/narrative -> Validator -> Final response
```

Jika nanti ingin re-ranking, lakukan sebagai eksperimen terukur dengan flag terpisah dan benchmark, bukan default production behavior.
