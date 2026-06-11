# Final Live Audit Report - 2026-05-24

## Scope

Audit ini dijalankan terhadap server live:

```text
http://127.0.0.1:5000/api/recommend
```

Fokus audit:

- kontrak API rekomendasi live
- metadata sentiment setelah perbaikan lineage
- konsistensi dataset sentiment
- groundtruth evaluator
- QC suite
- unit test backend recommender

## Verdict

```text
PASSED WITH OPERATIONAL NOTE
```

Sistem rekomendasi dan kontrak metadata sentiment sudah valid untuk lanjut ke tahap LLM evidence pack. Catatan operasional tersisa: ada dua proses Python yang masih listening di port 5000, sehingga proses server perlu dirapikan sebelum demo atau presentasi.

## Live API Contract

Probe API live:

```text
api_status: success
recommendation_count: 5
top_location: Glamping Legok Kondang
has_sentiment_score: True
sentiment_model_source: tfidf_linearsvc
sentiment_model_version: run_nlp_pipeline_v2
sentiment_available: True
has_old_sentimen_indobert: False
has_realworld_flags: True
has_explanation: True
```

Probe stabilitas 20 request:

```text
samples: 20
ok_new_contract: 20
missing_sentiment_score: 0
old_field_seen: 0
sources: {'tfidf_linearsvc': 20}
```

## Dataset Audit

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
- rows: 234
- sentiment metadata columns: complete
- sentiment_available: 212
- max sentiment_score vs avg_sentimen_skor delta: 0.0

Dataset/3_Curated/DATABASE_WISATA_LABELED_V2.csv
- rows: 234
- sentiment metadata columns: complete
- sentiment_available: 212
- max sentiment_score vs avg_sentimen_skor delta: 0.0

DATABASE_WISATA_FINAL_PARIPURNA.csv
- rows: 234
- sentiment metadata columns: complete
- sentiment_available: 212
- max sentiment_score vs avg_sentimen_skor delta: 0.0

Dataset/SENTIMENT_SCORES_PER_LOKASI.csv
- rows: 212
- sentiment metadata columns: complete
- sentiment_available: 212
- max sentiment_score vs avg_sentimen_skor delta: 0.0
```

## Groundtruth Evaluation

Command:

```powershell
python -B .\Scripts\evaluate_groundtruth.py
```

Result:

```text
Passed: 62
Failed: 0
Errors: 0
Pass rate: 100.0%
```

Output:

- `groundtruth_eval_report.md`
- `groundtruth_eval_results.json`

## QC Suite

Command:

```powershell
python -B .\scratch_qc.py
```

Result:

```text
Passed: 62
Failed: 0
Errors: 0
Final QA Status: PASSED WITH NOTES
```

Output:

- `qc_report.md`

## Backend Unit Test

Command:

```powershell
python -B -m unittest Scripts.test_recommender
```

Result:

```text
Ran 9 tests
OK
```

## Operational Note

Port 5000 masih menunjukkan dua proses Python listening:

```text
PID 12484 - python
PID 18840 - python
```

Response API sudah konsisten memakai kontrak baru, tetapi sebelum demo/presentasi sebaiknya jalankan hanya satu proses server agar tidak membingungkan audit operasional.

Manual cleanup yang disarankan:

```powershell
netstat -ano | findstr :5000
Stop-Process -Id <PID_YANG_TIDAK_DIPAKAI> -Force
$env:PORT="5000"
$env:FLASK_DEBUG="0"
python -B .\Scripts\app.py
```

## Next Step

Tahap berikutnya yang paling aman adalah membuat **LLM evidence pack** dari response rekomendasi yang sudah tervalidasi. LLM belum perlu mengubah ranking; LLM cukup menjadi explanation layer yang memakai evidence backend.

## Follow-Up Implementation - LLM Evidence Pack

Status 2026-05-24:

```text
IMPLEMENTED AND LIVE-VALIDATED
```

Implementasi:

- `Scripts/llm_evidence_pack.py`
- `Scripts/app.py`
- `Scripts/evaluate_groundtruth.py`
- `scratch_qc.py`
- `Scripts/test_llm_evidence_pack.py`
- `Dokumentasi_Sistem/LLM_EVIDENCE_PACK_SPEC.md`

Catatan:

- Evidence pack sudah valid melalui Flask test client dan server live `http://127.0.0.1:5000/api/recommend`.
- Groundtruth live: 62/62 PASS.
- QC live: 62/62 PASS.
- Unit test: 12/12 OK.
- Saat audit evidence pack dijalankan, port 5000 sudah dirapikan menjadi satu proses LISTENING aktif.

## Follow-Up Implementation - LLM Prompt Guard And Output Validator

Status 2026-05-25:

```text
IMPLEMENTED AND LIVE-VALIDATED
```

Implementasi:

- `Scripts/llm_guard.py`
- `Scripts/llm_evidence_pack.py`
- `Scripts/recommender.py`
- `Scripts/app.py`
- `Scripts/evaluate_groundtruth.py`
- `scratch_qc.py`
- `Scripts/test_llm_guard.py`
- `Dokumentasi_Sistem/LLM_GUARD_VALIDATOR_AUDIT_2026-05-25.md`

Catatan:

- `POST /api/recommend` sekarang mengembalikan `llm_prompt_guard`.
- `POST /api/llm/validate` menolak output LLM yang mengarang destinasi, harga, jarak, URL gambar/link, website, rating, atau fasilitas.
- Evidence pack sekarang membawa `candidate.media`; karena dataset curated aktif belum punya kolom URL/gambar, kandidat tanpa media akan keluar sebagai `media.available=false`.
- Groundtruth live: 62/62 PASS.
- QC live: 62/62 PASS.
- Unit test saat tahap guard: 25/25 OK.
- Server kemudian direstart ulang pada tahap media enrichment.

## Follow-Up Implementation - Media Enrichment Pipeline

Status 2026-05-25:

```text
IMPLEMENTED AND LIVE-VALIDATED
```

Implementasi:

- `Scripts/enrich_media_metadata.py`
- `Scripts/recommender.py`
- `Scripts/llm_evidence_pack.py`
- `Scripts/llm_guard.py`
- `Scripts/static/script.js`
- `Scripts/static/style.css`
- `Scripts/test_recommender.py`
- `Scripts/append_media_enrichment_notebook.py`
- `Dokumentasi_Sistem/MEDIA_ENRICHMENT_AUDIT_2026-05-25.md`
- `Dataset/3_Curated/media_groundtruth_audit.csv`
- `Dataset/3_Curated/media_match_review_queue.csv`

Catatan:

- Dataset curated aktif sekarang memiliki kolom `media_*`.
- Media accepted: 181/234 rows.
- Active candidate rows with media: 169/213.
- Top live result `Glamping Legok Kondang` sudah membawa `media.available=true`, image URL, dan Maps URL pada API recommendation dan LLM evidence pack.
- Frontend sekarang menampilkan gambar dan tombol Maps/Website saat `media.available=true`.
- Groundtruth live: 62/62 PASS.
- QC live: 62/62 PASS.
- Unit test: 26/26 OK.
- Port 5000 sekarang hanya memiliki satu proses LISTENING aktif pada PID 9936.
