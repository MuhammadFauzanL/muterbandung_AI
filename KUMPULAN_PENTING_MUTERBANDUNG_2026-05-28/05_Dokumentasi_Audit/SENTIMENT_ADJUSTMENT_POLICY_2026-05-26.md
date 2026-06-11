# Sentiment Adjustment Policy - 2026-05-26

Scope:

- Add `adjusted_sentiment_score` for recommendation ranking.
- Use Bayesian shrinkage so low-review destinations are not overconfident.
- Use p95 `total_ulasan` for review confidence so one extreme destination does not dominate.
- Expose `low_review_confidence`, `medium_review_confidence`, and `high_review_confidence`.

## Implemented Formula

Raw sentiment remains available as:

```text
sentiment_score
```

Ranking now uses:

```text
adjusted_sentiment_score =
(n * sentiment_score + k * sentiment_prior_score) / (n + k)
```

Where:

- `n` = `total_ulasan`
- `k` = `50.0`
- `sentiment_prior_score` = average active available sentiment
- current active prior = `0.7708`

Review confidence now uses p95:

```text
review_confidence =
min(1.0, log1p(total_ulasan) / log1p(p95_total_ulasan))
```

Current active p95:

```text
p95_total_ulasan = 536.9
```

Labels:

```text
confidence < 0.50  -> low_review_confidence
confidence < 0.75  -> medium_review_confidence
confidence >= 0.75 -> high_review_confidence
```

## Example Impact

Assuming a raw sentiment of `1.0`:

| Review Count | Confidence | Label | Adjusted Sentiment |
|---:|---:|---|---:|
| 5 | 0.2850 | `low_review_confidence` | 0.7916 |
| 30 | 0.5461 | `medium_review_confidence` | 0.8567 |
| 40 | 0.5906 | `medium_review_confidence` | 0.8726 |
| 100 | 0.7340 | `medium_review_confidence` | 0.9236 |
| 500 | 0.9887 | `high_review_confidence` | 0.9792 |

Interpretation:

- 30 vs 40 reviews still matters, but only slightly.
- 5 reviews with perfect sentiment is pulled close to the dataset prior.
- 500 reviews with perfect sentiment is trusted much more.
- Review count is not allowed to dominate linearly.

## API Fields Added

Recommendation item:

- `adjusted_sentiment_score`
- `review_confidence`
- `review_confidence_label`

`score_breakdown`:

- `adjusted_sentiment_score`
- `sentiment_used_for_ranking`
- `review_confidence`
- `review_confidence_label`
- `sentiment_prior_score`
- `sentiment_review_count_p95`

`sentiment_metadata`:

- `adjusted_sentiment_score`
- `review_confidence`
- `review_confidence_label`
- `sentiment_prior_score`
- `sentiment_review_count_p95`

LLM evidence pack:

- `candidate.sentiment.adjusted_score`
- `candidate.sentiment.used_for_ranking`
- `candidate.sentiment.review_confidence`
- `candidate.sentiment.review_confidence_label`

## Verification

Executed:

```powershell
python -B -m py_compile Scripts\recommender.py Scripts\llm_evidence_pack.py Scripts\llm_guard.py Scripts\test_recommender.py Scripts\test_llm_evidence_pack.py
node --check Scripts\static\script.js
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_schema_snapshot
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract Scripts.test_api_schema_snapshot Scripts.test_data_validation Scripts.test_targeted_completion_queue
```

Result:

- Python compile: PASS
- frontend syntax check: PASS
- targeted tests: 31/31 PASS
- full regression: 42/42 PASS

## Notes

This change intentionally affects ranking. It makes destinations with very small review samples less overconfident while still allowing high-quality low-review places to appear when relevance, rating, and filters support them.
