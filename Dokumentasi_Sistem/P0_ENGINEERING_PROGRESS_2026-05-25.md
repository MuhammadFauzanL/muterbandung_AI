# P0 Engineering Progress - 2026-05-25

Scope:

- Environment reproducibility baseline.
- Repository hygiene baseline.
- API contract hardening.
- API contract tests.
- Canonical dataset validation pipeline.
- Targeted data completion queue and one evidence-backed active-status update.
- Clean `.venv` install verification.
- Golden API/schema snapshot.
- LLM evidence caveat policy for weak real-world fields.
- Bayesian adjusted sentiment scoring with p95 review confidence.

## Completed Files

Created:

- `requirements.txt`
- `.env.example`
- `Dokumentasi_Sistem/LOCAL_SETUP_FROM_ZERO_2026-05-25.md`
- `Scripts/test_api_contract.py`
- `Scripts/validate_curated_dataset.py`
- `Scripts/test_data_validation.py`
- `Dataset/3_Curated/data_validation_results.json`
- `Dokumentasi_Sistem/DATA_VALIDATION_REPORT_2026-05-25.md`
- `Scripts/generate_targeted_completion_queue.py`
- `Scripts/test_targeted_completion_queue.py`
- `Scripts/apply_targeted_verified_updates.py`
- `Dataset/3_Curated/targeted_data_completion_queue.csv`
- `Dataset/3_Curated/targeted_data_completion_top50.csv`
- `Dokumentasi_Sistem/TARGETED_DATA_COMPLETION_PLAN_2026-05-25.md`
- `Dokumentasi_Sistem/TARGETED_VERIFIED_UPDATES_2026-05-25.md`
- `Dataset/4_Evaluation/api_schema_snapshot.json`
- `Scripts/test_api_schema_snapshot.py`
- `Dokumentasi_Sistem/CLEAN_VENV_AND_API_SCHEMA_SNAPSHOT_2026-05-25.md`
- `Dokumentasi_Sistem/LLM_EVIDENCE_CAVEAT_POLICY_2026-05-25.md`
- `Dokumentasi_Sistem/SENTIMENT_ADJUSTMENT_POLICY_2026-05-26.md`

Updated:

- `.gitignore`
- `Scripts/app.py`
- `Scripts/recommender.py`
- `Scripts/llm_evidence_pack.py`
- `Scripts/llm_guard.py`
- `Scripts/test_llm_evidence_pack.py`
- `Scripts/test_recommender.py`
- `Scripts/static/script.js`
- `Dataset/4_Evaluation/api_schema_snapshot.json`
- `Dokumentasi_Sistem/CLEAN_VENV_AND_API_SCHEMA_SNAPSHOT_2026-05-25.md`
- `Dokumentasi_Sistem/FULL_SYSTEM_ACTION_BACKLOG_2026-05-25.md`
- `Dokumentasi_Sistem/LOCAL_SETUP_FROM_ZERO_2026-05-25.md`

## API Contract Hardening

Implemented for `POST /api/recommend`:

- malformed JSON returns `400`
- non-object JSON returns `400`
- `query` length limited to 500 characters
- `free_only` and `open_now` parsed explicitly as booleans
- `open_at_hour` requires `HH:MM` string format
- `max_price`, `min_rating`, `max_distance_km`, latitude, longitude, and `top_k` validated by range
- `sort_by` restricted to `relevance`, `balanced`, `nearest`
- `day_type` restricted to `weekday`, `weekend`
- `top_k` request is honored up to max 20
- response metadata added:
  - `api_schema_version`
  - `data_version`
  - `request_id`
  - `generated_at`

Also hardened malformed JSON handling for `POST /api/llm/validate`.

## LLM Evidence Caveat Policy

Implemented:

- API response now exposes `is_active_verified`, `price_verified`, `night_verified`, `indoor_verified`, and `child_friendly_verified` in `recommendations[].realworld_flags`.
- LLM evidence pack now adds candidate-level limitations when active status, price, media, sentiment, opening hours, facilities, coordinates, safety, night suitability, indoor status, or child-friendly status are not strongly verified.
- Facility caveat wording is intentionally generic so the LLM validator does not treat the caveat itself as a positive facility claim.
- Golden API schema snapshot was updated after reviewing the intended contract change.

## Sentiment Adjustment Policy

Implemented:

- `sentiment_score` remains the raw sentiment signal.
- `adjusted_sentiment_score` is now the sentiment value used for ranking.
- Bayesian shrinkage uses active dataset prior and `k=50.0`.
- Review confidence uses p95 `total_ulasan`, not max `total_ulasan`.
- API, score breakdown, sentiment metadata, evidence pack, validator, and frontend now expose `review_confidence_label` values:
  - `low_review_confidence`
  - `medium_review_confidence`
  - `high_review_confidence`

## Verification

Executed:

```text
python -B -m py_compile .\Scripts\app.py .\Scripts\test_api_contract.py
```

Result: PASS

Executed:

```text
python -B -m unittest Scripts.test_api_contract
```

Result:

- 6 tests
- 6 passed

Executed:

```text
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract
```

Result:

- 32 tests
- 32 passed

Executed:

```text
python -B .\Scripts\validate_curated_dataset.py
```

Result:

- gate: PASS_WITH_WARNINGS
- rows: 234
- active candidates: 212
- blocking errors: 0
- warnings: 492

Executed:

```text
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract Scripts.test_api_schema_snapshot Scripts.test_data_validation Scripts.test_targeted_completion_queue
```

Result:

- 42 tests
- 42 passed

Executed:

```text
python -B .\Scripts\generate_targeted_completion_queue.py
```

Result:

- tasks: 616
- locations: 212
- P0 tasks: 52
- queue files generated

Executed:

```text
python -B .\Scripts\apply_targeted_verified_updates.py
```

Result:

- applied: 1
- skipped: 0
- `LOC-016 Chinatown Bandung` moved from `active_candidate/keep` to `temporarily_hidden/hide_temporarily`
- backup created before dataset write

Executed:

```text
python -m venv .\.venv_clean_verify
.\.venv_clean_verify\Scripts\python.exe -m pip install -r requirements.txt
.\.venv_clean_verify\Scripts\python.exe -m pip check
.\.venv_clean_verify\Scripts\python.exe -B -m unittest Scripts.test_api_schema_snapshot Scripts.test_data_validation
```

Result:

- clean venv install: PASS
- pip check: PASS
- clean venv tests: 4/4 PASS
- network escalation was required for PyPI access

## Runtime Note

The already-running Flask server on port `5000` may still use the older in-memory code until restarted.

To activate the new API contract in the browser/API:

```powershell
python .\Scripts\app.py
```

after stopping the old server process.

## Remaining Before LLM

Recommended next step:

Start the P1 LLM provider benchmark harness while manual targeted data completion continues in parallel.

Why:

The data contract has no blocking errors, clean environment install is proven, and weak fields now flow into LLM evidence as caveats. Manual data completion is still needed, but it no longer blocks a guarded provider benchmark because the validator and caveat policy remain the gate.
