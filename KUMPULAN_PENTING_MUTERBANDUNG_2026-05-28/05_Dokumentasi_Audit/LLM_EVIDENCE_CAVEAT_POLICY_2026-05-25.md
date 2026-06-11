# LLM Evidence Caveat Policy - 2026-05-25

Scope:

- Strengthen LLM-facing evidence so model output stays conservative when canonical data is incomplete.
- Expose additional real-world verification flags in `/api/recommend`.
- Keep the existing LLM validator as the final gate.

## Implemented

`Scripts/recommender.py` now includes these additional fields inside `recommendations[].realworld_flags`:

- `is_active_verified`
- `price_verified`
- `night_verified`
- `indoor_verified`
- `child_friendly_verified`

`Scripts/llm_evidence_pack.py` now adds candidate-level limitations when evidence is weak:

- destination active status is not verified
- price is not verified
- media/image/link metadata is unavailable
- sentiment is unavailable
- weekday/weekend opening-hour text is incomplete
- coordinate or safety verification is false
- no facility flag is verified
- night, indoor, or child-friendly labels are present but their matching verification flag is not true

Important wording rule:

Facility caveats must not mention specific unverified facilities as if they exist. The caveat uses conservative wording:

```text
Detail fasilitas belum terverifikasi; jangan menyebut fasilitas spesifik kecuali flag terkait bernilai true.
```

This prevents the output validator from treating the caveat itself as a positive facility claim.

## Guardrail Meaning

The LLM may explain backend recommendations, but it must not:

- create destinations outside `allowed_destination_ids`
- rerank candidates
- invent prices, opening hours, distances, ratings, media URLs, or facilities
- ignore candidate limitations when writing user-facing summaries

## Snapshot Update

The golden API schema snapshot was intentionally updated because `realworld_flags` gained additional verification fields.

Updated file:

- `Dataset/4_Evaluation/api_schema_snapshot.json`

## Verification

Executed:

```powershell
python -B -m py_compile Scripts\recommender.py Scripts\llm_evidence_pack.py Scripts\test_llm_evidence_pack.py
python -B -m unittest Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_schema_snapshot
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract Scripts.test_api_schema_snapshot Scripts.test_data_validation Scripts.test_targeted_completion_queue
```

Result:

- compile: PASS
- targeted LLM/schema tests: 20/20 PASS
- full regression: 42/42 PASS after the later sentiment adjustment policy update

## Current Readiness

The system is now safer for a first LLM explanation or itinerary layer because weak fields are explicitly carried into evidence as caveats.

This does not remove the need for manual data completion. It reduces hallucination risk while active status, media, facility, price, and hour verification are still incomplete.
