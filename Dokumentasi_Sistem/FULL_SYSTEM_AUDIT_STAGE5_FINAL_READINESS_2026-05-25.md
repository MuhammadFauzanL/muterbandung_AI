# Full System Audit Stage 5 - Final Readiness, Risk Register, and Roadmap

## Scope

Tahap 5 menggabungkan hasil audit tahap 1-4:

- environment dan project inventory;
- dataset, lineage, dan integrity;
- backend/API/scoring/frontend;
- testing, QC, groundtruth, evidence pack, dan LLM guard.

Tujuannya adalah menentukan apakah MuterBandung sudah siap diberi LLM, dalam bentuk apa, dan apa yang harus diperbaiki lebih dulu.

## Executive Verdict

```text
CORE RECOMMENDER READINESS: STRONG PROTOTYPE
DATA READINESS FOR DETERMINISTIC RECOMMENDATION: STRONG
LLM READINESS FOR EXPLANATION/ITINERARY LAYER: CONDITIONAL YES
LLM READINESS FOR AUTONOMOUS CHATBOT/RERANKING: NO
PRODUCTION READINESS: NOT YET
```

Keputusan utama:

```text
MuterBandung boleh lanjut ke LLM hanya sebagai explanation/itinerary layer yang menerima evidence pack dari backend dan wajib divalidasi ulang.
```

Jangan jadikan LLM sebagai sumber kebenaran data, pencipta destinasi, penghitung harga/jarak, atau pengganti ranking default.

## Current Strengths

### 1. Hybrid architecture sudah berada di jalur yang benar

Sistem sudah memakai pola:

```text
Backend deterministic recommendation
-> LLM evidence pack
-> LLM prompt guard
-> LLM output validator
```

Ini sesuai dengan arahan meet: filtering tradisional dulu, LLM untuk narasi/re-ranking/itinerary setelah kandidat valid.

### 2. Dataset aktif sudah curated dan cukup kaya

Dataset aktif:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Kondisi:

```text
234 rows
213 active candidates
234 unique location_id
0 duplicate location_id
coordinate complete
price complete
taxonomy labels complete
sentiment provenance explicit
media availability explicit
```

### 3. Guardrail LLM sudah bukan sekadar prompt

Validator menolak:

- destinasi palsu;
- reranking;
- harga palsu;
- jarak palsu;
- URL gambar/link palsu;
- field fasilitas bebas;
- klaim fasilitas positif tanpa flag terverifikasi.

### 4. Evaluation foundation sudah kuat

Hasil terakhir:

```text
Unit test: 26/26 OK
Groundtruth: 62/62 PASS
QC: 62/62 PASS
```

Groundtruth sudah mencakup:

- intent utama;
- query negatif;
- no-strong-match;
- lokasi/landmark;
- radius;
- budget;
- malam;
- gratis;
- fasilitas;
- shopping subtype.

### 5. Sentiment lineage sudah diperbaiki

Sistem tidak lagi mengklaim sentiment aktif sebagai IndoBERT.

Sumber aktif:

```text
tfidf_linearsvc
run_nlp_pipeline_v2
```

Ini penting untuk integritas akademik dan evidence pack LLM.

## Critical Risks

### Risk 1 - Environment belum reproducible

Severity: **Critical before serious LLM integration**

Tidak ada:

```text
requirements.txt
pyproject.toml
environment.yml
lockfile
```

Risiko:

- sulit dipindahkan ke laptop lain;
- sulit deploy;
- versi dependency bisa berubah;
- demo bisa gagal karena environment tidak sama.

Required fix:

```text
Buat requirements.txt + .env.example.
```

### Risk 2 - Root project belum version controlled

Severity: **Critical before larger changes**

Root `PIJAK` bukan Git repo.

Risiko:

- sulit rollback;
- sulit audit perubahan;
- eksperimen LLM bisa merusak file tanpa jejak;
- laporan sulit dipertanggungjawabkan secara profesional.

Required fix:

```text
Rapikan .gitignore, pisahkan artefak besar, lalu inisialisasi Git root atau struktur repo bersih.
```

### Risk 3 - API contract belum punya schema validation formal

Severity: **High**

Temuan:

```text
malformed JSON -> tetap menghasilkan rekomendasi
free_only: "false" -> terbaca true
open_at_hour: 20 -> bisa 500
max_price: -1 -> diterima
min_rating: 99 -> diterima
long query -> diterima tanpa batas
```

Ini harus diperbaiki sebelum LLM provider atau API dipakai oleh client eksternal.

### Risk 4 - Real-world verification belum selesai

Severity: **High for LLM narrative**

Status:

```text
manual_realworld_verification_queue: 213 rows
HIGH priority: 144
is_active_verified missing: 198/234
```

Risiko:

- LLM bisa terdorong memberi klaim terlalu yakin;
- fasilitas/status aktif belum cukup kuat;
- itinerary bisa terdengar lebih pasti daripada data sebenarnya.

Mitigasi wajib:

```text
LLM harus memakai caveat dan validator harus tetap ketat.
```

### Risk 5 - Real LLM belum dibenchmark

Severity: **High before choosing provider**

Belum ada pengujian nyata untuk:

- Gemini;
- OpenRouter;
- Ollama.

Belum ada metrik:

- JSON validity;
- validator pass rate;
- hallucination count;
- latency;
- token/cost;
- retry/error handling.

Required fix:

```text
Buat benchmark harness sebelum memilih model final.
```

## LLM Integration Policy

### Allowed Now

LLM boleh digunakan untuk:

- menyusun narasi rekomendasi dari evidence;
- itinerary sederhana dari kandidat backend;
- menjelaskan trade-off;
- membuat ringkasan alasan;
- menyampaikan warning/caveat.

Mode aman:

```text
Backend rank preserved.
LLM selects only allowed_destination_ids.
LLM output validated.
No new destinations.
No invented price/distance/media/facilities.
```

### Not Allowed Yet

LLM belum boleh:

- menjadi chatbot bebas;
- mencari data baru sendiri lalu dicampur ke ranking;
- membuat destinasi baru;
- mengganti ranking default;
- mengklaim fasilitas yang belum terverifikasi;
- menghitung jarak/harga/jam buka;
- membuat itinerary dengan lokasi di luar candidate list.

### Conditional Later

LLM re-ranking boleh dipertimbangkan hanya setelah:

- schema validation API selesai;
- provider benchmark selesai;
- output validator diperluas untuk mode rerank;
- ada A/B evaluation terhadap groundtruth;
- ada cache dan logging.

## Priority Roadmap

### Phase 0 - Stabilize Foundation

Wajib sebelum integrasi LLM provider.

1. Buat `requirements.txt`.
2. Buat `.env.example`.
3. Perluas `.gitignore`.
4. Tentukan strategi Git/root repo.
5. Pisahkan artefak besar dari source code.
6. Buat `Notebooks/README.md` untuk canonical notebook.

Deliverable:

```text
Environment reproducible and project structure auditable.
```

### Phase 1 - API Contract Hardening

Wajib sebelum API dipakai LLM/client eksternal.

1. Tambah request schema validation untuk `/api/recommend`.
2. Tolak malformed JSON dengan 400.
3. Parser boolean eksplisit.
4. Validasi `open_at_hour` format `HH:MM`.
5. Validasi range `max_price`, `min_rating`, `max_distance_km`.
6. Batasi panjang query.
7. Tambah response metadata:

```json
{
  "api_schema_version": "muterbandung.recommend.v1",
  "data_version": "DATABASE_WISATA_LABELED_V2_REVIEWED.csv",
  "request_id": "...",
  "generated_at": "..."
}
```

8. Tambah `Scripts/test_api_contract.py`.

Deliverable:

```text
API safe for structured callers.
```

### Phase 2 - LLM Provider Harness

Belum mengubah UI utama dulu.

1. Buat `Scripts/llm_provider.py`.
2. Adapter minimal:
   - Gemini;
   - OpenRouter;
   - optional Ollama.
3. Buat `Dataset/3_Curated/llm_benchmark_queries.csv`.
4. Buat `Scripts/benchmark_llm_provider.py`.
5. Ukur:
   - latency;
   - JSON validity;
   - validator pass/fail;
   - hallucination;
   - token/cost.
6. Simpan hasil:

```text
llm_benchmark_results.json
llm_benchmark_report.md
```

Deliverable:

```text
Provider chosen by evidence, not guesswork.
```

### Phase 3 - Safe LLM Itinerary Endpoint

Baru setelah Phase 0-2.

Endpoint target:

```text
POST /api/llm/itinerary
```

Rules:

- input wajib `llm_evidence_pack`;
- output JSON schema;
- validator wajib;
- cache by evidence hash;
- temperature rendah;
- max token dibatasi;
- fallback ke backend explanation jika LLM gagal.

Deliverable:

```text
LLM adds narrative value without weakening data integrity.
```

### Phase 4 - Real-World Data Strengthening

Parallel dengan LLM, tetapi jangan diabaikan.

1. Selesaikan `manual_realworld_verification_queue.csv` HIGH priority.
2. Selesaikan `manual_media_fill_queue.csv` active HIGH priority.
3. Tambahkan `verification_summary` ke evidence pack.
4. Audit duplicate review residual.
5. Lengkapi jam weekend untuk:
   - Chinatown Bandung;
   - Museum Pendidikan Nasional UPI.

Deliverable:

```text
LLM can speak with more confidence because evidence is stronger.
```

### Phase 5 - Production Architecture

Bukan prioritas langsung, tapi target jangka menengah.

1. Migrasi API dari Flask dev server ke FastAPI atau WSGI/ASGI server proper.
2. Migrasi CSV aktif ke PostgreSQL/PostGIS.
3. Tambahkan structured logging.
4. Tambahkan monitoring latency/error.
5. Tambahkan caching layer.
6. Tambahkan deployment docs.

Deliverable:

```text
System ready for demo robust / pilot production.
```

## Final Risk Register

| Priority | Risk | Impact | Fix |
|---:|---|---|---|
| P0 | No environment lock | Setup/deploy fragile | `requirements.txt`, `.env.example` |
| P0 | No root Git/version control | No rollback/audit | `.gitignore`, Git init/clean repo |
| P0 | API input validation weak | 500/wrong filters/unsafe LLM tool use | schema validation + tests |
| P1 | Real-world verification incomplete | LLM claims too confident | queue completion + caveats |
| P1 | No real LLM benchmark | model choice subjective | benchmark harness |
| P1 | Large artifacts mixed with code | repo/deploy heavy | artifact strategy |
| P2 | Notebook canonical unclear | documentation confusion | `Notebooks/README.md` |
| P2 | CSV-first storage | harder scale/query audit | PostgreSQL/PostGIS later |
| P2 | Flask dev server | not production ready | FastAPI/WSGI later |

## Recommended Immediate Next Work

Urutan paling tepat setelah audit ini:

```text
1. Fix environment reproducibility.
2. Harden API contract.
3. Add API contract tests.
4. Create LLM benchmark harness.
5. Only then connect Gemini/OpenRouter/Ollama.
```

Jangan langsung membuat endpoint LLM final sebelum tiga hal ini selesai:

```text
requirements/environment
schema validation
benchmark harness
```

## Final Conclusion

MuterBandung sudah punya pondasi rekomendasi yang jauh lebih kuat daripada chatbot wisata biasa karena:

- data curated;
- filtering deterministik;
- semantic matching;
- no-strong-match;
- evidence pack;
- validator;
- groundtruth/QC.

Namun kekuatan itu bisa rusak jika LLM dipasang terlalu cepat sebagai "otak utama". LLM harus dipasang sebagai lapisan terkendali.

Final architecture yang direkomendasikan:

```text
User Query/Form
-> API schema validation
-> Deterministic filters
-> Semantic recommender
-> Evidence pack
-> LLM provider
-> Output validator
-> Final response with caveats
```

Dengan pola ini, LLM akan meningkatkan kualitas pengalaman pengguna tanpa mengorbankan integritas data.
