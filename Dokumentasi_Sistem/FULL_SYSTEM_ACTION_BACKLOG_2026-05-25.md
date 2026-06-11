# Full System Action Backlog - 2026-05-25

Backlog ini mengubah hasil audit menjadi urutan kerja teknis. Prioritas disusun untuk memperkuat fondasi sebelum LLM dipasang.

## Progress Update - 2026-05-25

Status setelah engineering awal:

- P0.1 Environment Reproducibility: baseline done via `requirements.txt`, `.env.example`, and local setup document. Needs clean `.venv` install verification.
- P0.2 Repository Hygiene: partial done via expanded `.gitignore`. Root Git strategy and artifact separation still pending.
- P0.3 API Contract Hardening: done for `/api/recommend` input validation and response metadata.
- P0.4 API Contract Tests: done via `Scripts/test_api_contract.py`.
- Dataset validation pipeline: done via `Scripts/validate_curated_dataset.py`, `Scripts/test_data_validation.py`, JSON result, and Markdown report.
- Targeted data completion queue: done via `Scripts/generate_targeted_completion_queue.py`.
- Evidence-backed active-status update: `LOC-016 Chinatown Bandung` temporarily hidden pending reopening verification.
- Clean `.venv` verification: done via `.venv_clean_verify`; `requirements.txt` install passed.
- Golden API/schema snapshot: done via `Dataset/4_Evaluation/api_schema_snapshot.json` and `Scripts/test_api_schema_snapshot.py`.
- LLM evidence caveat policy: done via expanded `realworld_flags`, candidate limitations, and schema snapshot update.
- Sentiment adjustment policy: done via Bayesian `adjusted_sentiment_score`, p95 review confidence, confidence labels, and 42/42 regression pass.

Current next best step:

Start P1.1 LLM provider harness and P1.2 benchmark runner while manual targeted data completion continues in parallel.

## P0 - Must Fix Before LLM Integration

### P0.1 Environment Reproducibility

Problem:
Tidak ada `requirements.txt`, `pyproject.toml`, atau environment spec di root.

Action:

1. Buat `requirements.txt` dari dependency yang benar-benar dipakai.
2. Buat `.env.example` untuk konfigurasi non-rahasia.
3. Dokumentasikan cara setup lokal dan cara menjalankan server.

Acceptance:

- Developer baru bisa membuat environment dari nol.
- Server dan test bisa berjalan tanpa menebak package manual.

### P0.2 Repository Hygiene

Problem:
Root project belum menjadi Git repo yang jelas, sementara ada artifact besar dan backup lokal di workspace.

Action:

1. Perluas `.gitignore` untuk log, backup, cache, venv, model besar, output benchmark, dan file lokal.
2. Putuskan strategi Git root: root PIJAK sebagai repo utama atau sub-repo per modul.
3. Pisahkan artifact besar ke storage/model registry/manual archive.

Acceptance:

- Source code, dataset curated, dan dokumentasi bisa dilacak.
- Artifact besar tidak ikut mengganggu version control.

### P0.3 API Contract Hardening

Problem:
API saat ini fungsional tetapi masih menerima input ambigu dan beberapa edge case bisa salah perilaku.

Action:

1. Tolak malformed JSON dengan `400 Bad Request`.
2. Parse boolean secara eksplisit, terutama `free_only`.
3. Validasi `open_at_hour` hanya format valid.
4. Validasi rentang numeric: price, rating, radius, top_k.
5. Batasi panjang query.
6. Tambahkan metadata response: `api_schema_version`, `data_version`, `request_id`, `generated_at`.

Acceptance:

- Input buruk tidak berubah menjadi rekomendasi diam-diam.
- Tidak ada 500 untuk input user biasa.
- LLM/tool caller mendapat kontrak API yang stabil.

### P0.4 API Contract Tests

Problem:
Groundtruth kuat untuk kualitas rekomendasi, tetapi API edge cases belum menjadi automated test.

Action:

1. Tambah `Scripts/test_api_contract.py`.
2. Test malformed JSON, boolean string, invalid hour, invalid numeric range, query panjang, dan top_k.
3. Test response metadata.

Acceptance:

- Test gagal jika API kembali menerima input ambigu.
- Semua P0.3 punya coverage minimal.

## P1 - Required For Safe LLM Layer

### P1.1 LLM Provider Harness

Action:

1. Buat `Scripts/llm_provider.py`.
2. Sediakan adapter minimal untuk Gemini, OpenRouter, dan Ollama.
3. Gunakan satu interface output JSON.
4. Jangan hubungkan provider langsung ke ranking utama.

Acceptance:

- Provider bisa ditukar tanpa mengubah recommender.
- Semua output masuk ke validator sebelum dikirim ke frontend.

### P1.2 LLM Benchmark Dataset And Runner

Action:

1. Buat `Dataset/3_Curated/llm_benchmark_queries.csv`.
2. Buat `Scripts/benchmark_llm_provider.py`.
3. Ukur latency, JSON validity, validator pass rate, hallucination rejection, token estimate, dan cost estimate.
4. Simpan output ke `llm_benchmark_results.json` dan `llm_benchmark_report.md`.

Acceptance:

- Pemilihan model tidak berdasarkan asumsi.
- Ada angka pembanding antar provider.

### P1.3 Safe LLM Endpoint

Action:

1. Tambah endpoint terpisah, misalnya `POST /api/llm/itinerary`.
2. Input endpoint hanya evidence pack dari hasil rekomendasi.
3. Gunakan low temperature, token limit, strict JSON schema, cache, dan fallback deterministic.

Acceptance:

- Jika LLM gagal, sistem tetap memberi hasil rekomendasi normal.
- Output LLM tidak bisa membawa destinasi di luar `allowed_destination_ids`.

### P1.4 Real-World Verification Queue

Action:

1. Prioritaskan queue HIGH.
2. Isi field `is_active_verified`, ringkasan verifikasi, dan fasilitas verified/unverified.
3. Pastikan LLM selalu menampilkan caveat untuk data belum verified.

Acceptance:

- Klaim operasional tidak terlalu percaya diri.
- Tempat aktif punya status verifikasi yang lebih jelas.

Status:

- Caveat policy is implemented so weak fields are carried into the evidence pack.
- Manual completion still continues to reduce caveats and improve answer confidence.

## P2 - Quality And Scale Improvements

### P2.1 Notebook Canonical Index

Action:

1. Buat `Notebooks/README.md`.
2. Tandai notebook canonical, legacy, dan eksperimen.
3. Jelaskan urutan pipeline data.

Acceptance:

- Tidak ada kebingungan antara `wisata_training.ipynb` dan `wisata_traning.ipynb`.

### P2.2 Data Completeness

Action:

1. Lengkapi weekend hours yang kosong.
2. Audit duplicate reviews.
3. Lengkapi active media unavailable.
4. Dokumentasikan field yang memang unavailable.

Acceptance:

- UI lebih kaya.
- LLM punya lebih sedikit caveat.

### P2.3 Production Architecture

Action:

1. Pindah dari Flask dev server ke WSGI/FastAPI ketika siap deploy.
2. Evaluasi PostgreSQL/PostGIS untuk data spasial dan audit query.
3. Tambahkan structured logging, monitoring, dan cache.

Acceptance:

- Sistem siap untuk traffic dan observability production.

## Recommended Next Sprint

Urutan paling realistis untuk sprint berikutnya setelah update ini:

1. LLM provider benchmark harness using the current evidence pack and validator.
2. Root Git strategy and artifact separation.
3. High-impact data warning reduction: active verification, facility flags, media, missing hours, rating/sentiment unavailable.
4. Safe LLM endpoint only after provider benchmark results are reviewed.

Clean environment verification and warning policy confirmation are complete, so the system is now ready for a guarded P1 benchmark harness.
