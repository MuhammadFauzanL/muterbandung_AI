# Full System Current State Audit - 2026-05-26

Audit ini dilakukan sambil menunggu hasil manual review/scrape Excel. Fokusnya adalah pekerjaan yang tidak membutuhkan fakta baru: environment, data contract, backend, LLM guard, scoring, queue manual, dan readiness menuju benchmark LLM.

## Executive Summary

Status sistem saat ini:

```text
ENGINEERING STATUS: STABLE
DATA CONTRACT STATUS: PASS_WITH_WARNINGS
LLM EXPLANATION READINESS: CONDITIONAL YES
FULL AUTONOMOUS LLM/RERANKING: NO
```

Sistem sudah cukup kuat untuk lanjut ke benchmark provider LLM secara guarded, karena:

- API contract sudah dilindungi golden snapshot.
- LLM evidence pack dan validator sudah aktif.
- Sentiment ranking sudah memakai Bayesian `adjusted_sentiment_score`.
- Data validator tidak menemukan blocking error.
- Full regression terakhir: 42/42 PASS.

Sistem belum boleh menjadi autonomous LLM chatbot/reranker karena:

- 197 active candidates belum punya `is_active_verified=True`.
- 206 active candidates belum punya verified facility flag.
- 43 active candidates belum punya media.
- 17 active candidates belum punya sentiment/rating kuat.
- 142 active candidates belum punya website/reference.

## Verification Run

Executed:

```powershell
python -B Scripts\validate_curated_dataset.py
python -B -m py_compile Scripts\app.py Scripts\recommender.py Scripts\llm_evidence_pack.py Scripts\llm_guard.py Scripts\validate_curated_dataset.py Scripts\generate_targeted_completion_queue.py Scripts\apply_targeted_verified_updates.py
node --check Scripts\static\script.js
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract Scripts.test_api_schema_snapshot Scripts.test_data_validation Scripts.test_targeted_completion_queue
```

Result:

- data validation gate: `PASS_WITH_WARNINGS`
- compile: PASS
- frontend syntax check: PASS
- full regression: 42/42 PASS

## Dataset State

Canonical dataset:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Current validation summary:

```text
rows: 234
columns: 87
active candidates: 212
blocking errors: 0
warnings: 492
validation timestamp: 2026-05-26T04:33:26Z
```

Warning breakdown:

| Code | Count | Meaning |
|---|---:|---|
| `W_ACTIVE_VERIFICATION_MISSING` | 197 | Active status not fully verified |
| `W_ACTIVE_FACILITY_VERIFICATION_SPARSE` | 206 | Facility flags mostly unverified |
| `I_ACTIVE_WEBSITE_MISSING` | 142 | Website/reference missing |
| `W_ACTIVE_MEDIA_UNAVAILABLE` | 43 | Media not available |
| `W_ACTIVE_RATING_MISSING` | 17 | Runtime median rating fallback used |
| `W_ACTIVE_SENTIMENT_UNAVAILABLE` | 17 | Sentiment unavailable |
| `W_ACTIVE_COORDINATE_UNVERIFIED` | 10 | Coordinates need caution |
| `W_ACTIVE_WEEKEND_HOURS_MISSING` | 1 | Weekend hours incomplete |
| `W_ZERO_PRICE_NOT_MARKED_FREE` | 1 | Price label mismatch |

## Manual Queue State

Current queue files:

| Queue | Rows | Main Risk |
|---|---:|---|
| `targeted_data_completion_queue.csv` | 616 | broad prioritized completion tasks |
| `targeted_data_completion_top50.csv` | 50 | P0 active status/opening-hour tasks |
| `manual_realworld_verification_queue.csv` | 213 | real-world active/facility verification |
| `manual_media_fill_queue.csv` | 53 | image/link completion |
| `manual_data_fill_queue.csv` | 60 | missing factual fields |
| `local_scrape_unresolved_queue.csv` | 78 | unresolved scrape candidates |

Interpretation:

Manual review should prioritize `targeted_data_completion_top50.csv` first, especially active status verification. Do not batch-apply factual fields without evidence URL or reviewer note.

## Backend/API State

Healthy:

- `/api/recommend` has input validation.
- `top_k` is honored up to configured max.
- API response includes `api_schema_version`, `data_version`, `request_id`, and `generated_at`.
- Golden snapshot protects API structure.
- `llm_evidence_pack` and `llm_prompt_guard` are included in recommendation responses.

Current API snapshot:

```text
recommendation_keys: 22
score_breakdown_keys: 24
candidate_sentiment_keys:
- score
- adjusted_score
- used_for_ranking
- review_confidence
- review_confidence_label
- review_count
- model_source
- model_version
- label
- available
```

## Scoring State

Implemented:

- raw `sentiment_score` remains visible
- ranking uses `adjusted_sentiment_score`
- Bayesian shrinkage uses `k=50.0`
- review confidence uses p95 `total_ulasan`
- confidence labels are exposed:
  - `low_review_confidence`
  - `medium_review_confidence`
  - `high_review_confidence`

Runtime check:

```text
active candidates: 212
sentiment prior: 0.7708
p95 review count: 536.9
sample top result for "wisata alam sejuk": Wayang Windu Panenjoan
raw sentiment: 0.96
adjusted sentiment: 0.9222
review confidence: 0.8434
review confidence label: high_review_confidence
```

## Runtime/Environment State

Environment:

- Python global detected: Python 3.13.2
- `.venv_clean_verify` exists and was previously verified.
- Root `.venv` does not currently exist.
- Root folder is not currently a Git repository.
- Latest Codex backup observed: `Codex_Backups/codex_backup_20260526_113056.zip`

Server/process state:

- Port `5000` was not listening during this audit.
- Some `python.exe` processes are alive, but command-line inspection was blocked by Windows permission.
- No current evidence that Flask is serving on port `5000`.

## Main Risks

### R1 - No Git Root Yet

Root project is still not a Git repo. This is the biggest engineering governance gap now that API/scoring changes are accumulating.

Recommended action:

```text
Initialize Git or decide exact repo root before more major engineering.
```

### R2 - Manual Data Still Dominates Real-World Quality

The system is guarded, but many real-world fields remain unverified. LLM can explain safely, but it will need caveats often.

Recommended action:

```text
Continue manual review, then apply only evidence-backed updates.
```

### R3 - Live Groundtruth API Eval Not Re-run After Sentiment Scoring

Unit/API schema tests pass, but `evaluate_groundtruth.py` is live-server based and should be re-run after starting the server with the latest code.

Recommended action:

```powershell
python .\Scripts\app.py
python -B .\Scripts\evaluate_groundtruth.py
python -B .\scratch_qc.py
```

### R4 - Artifact Sprawl

There are many logs, backups, models, notebooks, and local venv artifacts. `.gitignore` covers them, but without a Git repo this is only a plan, not actual governance.

Recommended action:

```text
Create repo boundary and separate source/data/artifact ownership.
```

## Safe Work While Waiting For Manual Excel

These can be done now without needing new factual data:

1. Build LLM provider benchmark harness.
2. Add benchmark query CSV for deterministic + LLM output validation.
3. Add local live API smoke runner that starts/stops server or uses Flask test client.
4. Create Git repo strategy and artifact separation plan.
5. Add an import validator for the manual Excel results before applying them to canonical CSV.

## Recommended Next Step

Best next engineering move:

```text
Build manual Excel import validator first, then LLM provider benchmark harness.
```

Reason:

The manual Excel result will soon become the highest-risk input. Before applying it, the system should have a validator that checks schema, allowed values, evidence URL/reviewer note, location_id existence, duplicate rows, and dangerous status changes.

After that, the LLM benchmark harness can run safely on the current evidence pack and validator without waiting for all data completion to finish.
