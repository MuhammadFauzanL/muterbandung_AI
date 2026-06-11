# Full System Audit Stage 4 - Testing, QC, Groundtruth, LLM Evidence, Validator, and Notebook Documentation

## Scope

Tahap 4 mengaudit kekuatan testing dan guardrail:

- unit tests;
- groundtruth evaluator;
- QC suite;
- LLM evidence pack;
- LLM prompt guard;
- LLM output validator;
- notebook/documentation coverage.

## Verification Run

Perintah yang dijalankan:

```powershell
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard
python -B .\Scripts\evaluate_groundtruth.py
python -B .\scratch_qc.py
node --check Scripts\static\script.js
python -B -m py_compile Scripts\app.py Scripts\recommender.py Scripts\llm_evidence_pack.py Scripts\llm_guard.py
```

Hasil:

```text
Unit test: 26/26 OK
Groundtruth: 62/62 PASS
QC: 62/62 PASS
JS syntax: PASS
Python compile: PASS
```

## Test Coverage Summary

### Unit Test - `Scripts/test_recommender.py`

Coverage yang sudah ada:

- initialization;
- parsing `multi_labels`;
- time parsing;
- open/closed logic including overnight;
- hard filtering category;
- hard filtering price and free-only;
- hard filtering rating;
- score range and sorting;
- sentiment metadata contract;
- explanation presence;
- media metadata contract.

Verdict:

```text
Good coverage for recommender core behavior.
```

### Unit Test - `Scripts/test_llm_evidence_pack.py`

Coverage yang sudah ada:

- evidence schema version;
- `llm_may_create_destinations=false`;
- `llm_may_rerank=false`;
- allowed destination IDs;
- sentiment provenance;
- media availability;
- strict JSON serialization;
- empty recommendation evidence still contains guardrails.

Verdict:

```text
Good coverage for anti-hallucination evidence structure.
```

### Unit Test - `Scripts/test_llm_guard.py`

Coverage yang sudah ada:

- prompt guard has schema and core rules;
- valid LLM output passes;
- hallucinated destination rejected;
- reranking rejected;
- fake price rejected;
- fake distance rejected;
- unavailable media URL rejected;
- valid media URL accepted when evidence contains it;
- unsupported facility field rejected;
- positive facility claim rejected without verified flag.

Verdict:

```text
Strong LLM output guard for current explanation-layer mode.
```

## Groundtruth Evaluator

File:

```text
Dataset/3_Curated/groundtruth_queries.csv
```

Summary:

```text
rows: 62
duplicate_id: 0
expect_no_strong_match true: 12
expect_no_strong_match false: 50
```

Scenario coverage:

```text
Attribute Filters: 11
Location / Distance: 9
Specific Guard Tests: 6
Negative Tests: 6
Culinary / Cafe / Hangout: 6
Night / Budget: 6
Family / Children: 5
Nature / Healing: 5
Culture / History / Education: 5
Shopping: 3
```

Evaluator also checks:

- API preflight;
- `llm_evidence_pack` exists;
- `llm_prompt_guard` exists;
- guard schema versions;
- LLM cannot create destinations;
- LLM cannot rerank;
- allowed IDs match candidates;
- candidate required fields;
- sentiment provenance;
- media contract;
- expected intents;
- required/forbidden categories and labels;
- no-strong-match;
- landmark resolution;
- distance presence;
- coordinate verification in top results;
- radius filter;
- shopping subtype;
- required real-world flags;
- price expectations.

Verdict:

```text
Groundtruth suite is strong for backend recommendation and LLM evidence contract.
```

## QC Suite

File:

```text
scratch_qc.py
```

Strengths:

- preflight prevents overwriting valid report when API is down;
- checks API schema includes `llm_evidence_pack` and `llm_prompt_guard`;
- checks LLM evidence ranking authority;
- checks media availability contract;
- covers broad query categories;
- covers location/distance;
- covers attribute filters;
- writes detailed report to `qc_report.md`.

Current result:

```text
Passed: 62
Failed: 0
Errors: 0
```

Verdict:

```text
QC suite is useful and operationally safer than before.
```

## Notebook Documentation

Notebook scan:

```text
Notebooks/wisata_training.ipynb
- cells: 33
- LLM mentions: 53
- evidence mentions: 18
- guard mentions: 16
- validator mentions: 4
- media mentions: 59
- groundtruth mentions: 25
- lineage mentions: 8

Notebooks/wisata_traning.ipynb
- cells: 59
- LLM/evidence/guard mostly absent

Notebooks/Wisata_Training_1_Audit_Master_Data.ipynb
- cells: 6
- LLM/evidence/guard absent
```

Verdict:

```text
Main current documentation notebook appears to be Notebooks/wisata_training.ipynb.
Older typo notebook wisata_traning.ipynb should be treated as historical unless intentionally maintained.
```

## Key Strengths

### 1. Testing is no longer only happy-path

Negative and no-strong-match scenarios are included:

- aurora;
- pantai;
- gurun pasir;
- ski/salju;
- curug malam;
- glamping gratis;
- location-needed query;
- facility-specific filters.

### 2. LLM guardrail is tested as a contract

The system does not merely rely on prompt text. It validates output structurally and rejects unsupported claims.

### 3. Evidence pack is part of live API evaluation

Groundtruth and QC both fail if evidence/guard disappears from `POST /api/recommend`.

### 4. Reports are generated and auditable

Current reports:

- `groundtruth_eval_report.md`
- `groundtruth_eval_results.json`
- `qc_report.md`

## Gaps and Risks

### Finding 1 - API input edge cases from Stage 3 are not covered by automated tests

Severity: **High before public API / LLM tool use**

Known untested/failing edge cases:

```text
malformed JSON -> currently returns recommendations instead of 400
free_only: "false" -> currently treated as true
open_at_hour: 20 -> currently can produce 500
max_price: -1 -> accepted, returns 0 results
min_rating: 99 -> accepted, returns 0 results
long query -> accepted without length limit
```

Recommendation:

Add `Scripts/test_api_contract.py` with Flask test client or live API tests for request validation.

### Finding 2 - No real LLM provider output is tested

Severity: **High for next LLM stage**

Current tests validate evidence and validator logic, but no test calls Gemini/OpenRouter/Ollama. This is correct before provider integration, but means the system has not yet proven:

- JSON adherence from a real model;
- latency;
- token usage;
- cost;
- retry behavior;
- hallucination rate under real prompts.

Recommendation:

Create a benchmark harness before enabling LLM output in the app.

### Finding 3 - No snapshot/golden test for API response schema

Severity: **Medium**

The evaluator checks many fields, but there is no compact schema/golden contract test that fails when field names change unexpectedly.

Recommendation:

Add schema assertions for:

```text
recommend response v1
recommendation item v1
llm_evidence_pack v1
llm_prompt_guard v1
llm_output v1
```

### Finding 4 - Notebook split can confuse documentation lineage

Severity: **Medium**

There are multiple notebooks:

```text
Notebooks/wisata_training.ipynb
Notebooks/wisata_traning.ipynb
Notebooks/Wisata_Training_1_Audit_Master_Data.ipynb
```

Only `wisata_training.ipynb` appears current for LLM/guard/media. The typo notebook is older and may confuse readers.

Recommendation:

Add a short `Notebooks/README.md` defining which notebook is canonical.

### Finding 5 - QC report direct write by default

Severity: **Low-Medium**

`scratch_qc.py` supports atomic report writing with `QC_ATOMIC_REPORT=true`, but default run uses direct write.

Recommendation:

Set default to atomic or document recommended command:

```powershell
$env:QC_ATOMIC_REPORT="true"
python -B .\scratch_qc.py
```

## Stage 4 Verdict

```text
TESTING FOUNDATION: STRONG FOR CURRENT BACKEND
LLM GUARD TESTING: STRONG FOR NON-PROVIDER MODE
LIVE GROUNDTRUTH: STRONG
API CONTRACT EDGE TESTING: NEEDS ADDITION
REAL LLM E2E TESTING: NOT STARTED
NOTEBOOK DOCUMENTATION: GOOD BUT NEEDS CANONICAL INDEX
```

## Recommended Next Test Additions

1. `Scripts/test_api_contract.py`
   - malformed JSON returns 400;
   - string booleans are parsed safely or rejected;
   - invalid `open_at_hour` returns 400, not 500;
   - invalid numeric ranges return 400;
   - long query returns 400 or truncation warning.

2. `Scripts/benchmark_llm_provider.py`
   - input: fixed evidence packs from groundtruth cases;
   - output: JSON validity, validator pass/fail, latency, token estimate, cost estimate.

3. `Dataset/3_Curated/llm_benchmark_queries.csv`
   - subset of 10-20 cases from groundtruth;
   - include expected narrative constraints.

4. `Notebooks/README.md`
   - define canonical notebook;
   - mark historical notebooks.

## Next Stage

Tahap 5 should consolidate:

- readiness verdict;
- top vulnerabilities;
- priority roadmap;
- what must be fixed before LLM provider integration;
- what can wait until production/deploy.
