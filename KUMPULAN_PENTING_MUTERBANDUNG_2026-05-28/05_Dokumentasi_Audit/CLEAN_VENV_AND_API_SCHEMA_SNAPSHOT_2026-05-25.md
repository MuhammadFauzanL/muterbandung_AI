# Clean Venv And API Schema Snapshot - 2026-05-25

Scope:

- Verify `requirements.txt` from a clean virtual environment.
- Add golden API/schema snapshot protection.

## Clean Venv Verification

Environment created:

```text
.venv_clean_verify
```

Commands executed:

```powershell
python -m venv .\.venv_clean_verify
.\.venv_clean_verify\Scripts\python.exe -m pip install --upgrade pip
.\.venv_clean_verify\Scripts\python.exe -m pip install -r requirements.txt
```

Result:

- venv creation: PASS
- `requirements.txt` install: PASS
- network escalation was required because sandbox blocked PyPI access

Follow-up checks:

```powershell
.\.venv_clean_verify\Scripts\python.exe -m pip check
```

Result:

```text
No broken requirements found.
```

Import smoke test:

- Flask
- pandas
- numpy
- torch
- sentence-transformers
- scikit-learn
- requests
- transformers
- tensorflow
- tf-keras
- BeautifulSoup
- nbformat
- Sastrawi

Result: PASS

Observed runtime versions:

```text
Python 3.13.2
torch 2.9.1+cpu
tensorflow 2.20.0
```

Clean-venv tests:

```powershell
.\.venv_clean_verify\Scripts\python.exe -B -m unittest Scripts.test_api_schema_snapshot Scripts.test_data_validation
.\.venv_clean_verify\Scripts\python.exe -B .\Scripts\validate_curated_dataset.py
```

Result:

- schema snapshot + data validation tests: 4/4 PASS
- data validation gate: PASS_WITH_WARNINGS
- active candidates: 212
- blocking errors: 0
- warnings: 492

## Golden API Schema Snapshot

Created:

- `Dataset/4_Evaluation/api_schema_snapshot.json`
- `Scripts/test_api_schema_snapshot.py`

Purpose:

The snapshot fails when the API response structure changes unexpectedly. This protects:

- top-level `/api/recommend` response keys
- error response keys
- recommendation item keys
- nested recommendation schema
- `llm_evidence_pack` schema
- `llm_prompt_guard` schema
- expected schema version strings

Global regression:

```powershell
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract Scripts.test_api_schema_snapshot Scripts.test_data_validation Scripts.test_targeted_completion_queue
```

Result:

- 42 tests
- 42 passed

## Notes

- `.venv_clean_verify` is ignored by `.gitignore`.
- The existing Flask server on port `5000` still needs restart after code changes.
- Clean environment install is now proven, but first install is large because `torch`, `tensorflow`, and notebook dependencies are included.
- The API schema snapshot was later expanded intentionally to include additional `realworld_flags` required by the LLM evidence caveat policy.
- The API schema snapshot was later expanded again intentionally to include adjusted sentiment and p95 review-confidence fields.
