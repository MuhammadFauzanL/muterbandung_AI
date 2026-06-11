import csv
import json
import math
import os
import re
import sys
import time

import requests


API_URL = os.getenv("MUTERBANDUNG_API_URL", "http://127.0.0.1:5000/api/recommend")
GROUNDTRUTH_PATH = os.getenv(
    "GROUNDTRUTH_PATH",
    os.path.join("Dataset", "3_Curated", "groundtruth_queries.csv"),
)
REPORT_PATH = os.getenv("GROUNDTRUTH_REPORT_PATH", "groundtruth_eval_report.md")
JSON_PATH = os.getenv("GROUNDTRUTH_JSON_PATH", "groundtruth_eval_results.json")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("GROUNDTRUTH_REQUEST_TIMEOUT", "30"))
PREFLIGHT_TIMEOUT_SECONDS = float(os.getenv("GROUNDTRUTH_PREFLIGHT_TIMEOUT", "30"))
DEFAULT_TOP_CHECK = int(os.getenv("GROUNDTRUTH_TOP_CHECK", "3"))


def split_pipe(value):
    return [item.strip() for item in str(value or "").split("|") if item.strip()]


def norm(value):
    return str(value or "").strip().lower()


def is_true(value):
    return norm(value) == "true"


def as_int(value, default=0):
    try:
        return int(str(value or "").strip())
    except ValueError:
        return default


def as_float(value):
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed):
        return None
    return parsed


def contains_term(value, terms):
    text = norm(value)
    return any(norm(term) and norm(term) in text for term in terms)


def label_set(item):
    """Prefer reviewed taxonomy labels over legacy multi_labels when available."""
    labels = set()
    taxonomy = item.get("label_taxonomy") or {}
    for field in ("primary_intent",):
        value = taxonomy.get(field)
        if value:
            labels.add(norm(value))
    for field in ("core_labels", "secondary_labels"):
        for label in taxonomy.get(field) or []:
            labels.add(norm(label))
    if not labels:
        for label in item.get("multi_labels") or []:
            labels.add(norm(label))
    return labels


def item_has_any_label(item, terms):
    labels = label_set(item)
    return any(norm(term) in labels for term in terms)


def item_has_all_labels(item, terms):
    labels = label_set(item)
    return all(norm(term) in labels for term in terms)


def price_is_allowed(item, expectation):
    expectation = norm(expectation)
    if not expectation:
        return True

    harga = str((item.get("info_praktis") or {}).get("harga") or "")
    harga_norm = norm(harga)
    if expectation == "gratis":
        return harga_norm == "gratis"
    if expectation == "max_50000":
        if harga_norm == "gratis":
            return True
        numbers = []
        for raw in re.findall(r"\d[\d.]*", harga):
            try:
                numbers.append(int(raw.replace(".", "")))
            except ValueError:
                pass
        return bool(numbers) and min(numbers) <= 50000
    return expectation in harga_norm


def build_payload(row):
    payload = {}
    query = row.get("query", "").strip()
    if query:
        payload["query"] = query

    categories = split_pipe(row.get("payload_categories"))
    if categories:
        payload["categories"] = categories

    sort_by = row.get("sort_by", "").strip()
    if sort_by:
        payload["sort_by"] = sort_by

    user_lat = as_float(row.get("user_lat"))
    user_lon = as_float(row.get("user_lon"))
    max_distance_km = as_float(row.get("max_distance_km"))
    if user_lat is not None:
        payload["user_lat"] = user_lat
    if user_lon is not None:
        payload["user_lon"] = user_lon
    if max_distance_km is not None:
        payload["max_distance_km"] = max_distance_km

    return payload


def post_recommend(payload, timeout=REQUEST_TIMEOUT_SECONDS):
    response = requests.post(API_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def preflight_api():
    try:
        data = post_recommend({"query": "wisata alam yang sejuk"}, timeout=PREFLIGHT_TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as exc:
        return False, f"API is not reachable at {API_URL}: {exc}"
    except ValueError as exc:
        return False, f"API response is not valid JSON: {exc}"

    if data.get("status") != "success":
        return False, f"API returned non-success status: {data.get('status') or 'missing'}"
    if "recommendations" not in data:
        return False, "API response is missing recommendations."
    if not isinstance(data.get("llm_evidence_pack"), dict):
        return False, "API response is missing llm_evidence_pack."
    if not isinstance(data.get("llm_prompt_guard"), dict):
        return False, "API response is missing llm_prompt_guard."
    return True, "API reachable and response schema looks usable."


def add_check(checks, name, passed, detail):
    checks.append({
        "name": name,
        "passed": bool(passed),
        "detail": detail,
    })


def validate_llm_evidence_pack(checks, data, recommendations):
    pack = data.get("llm_evidence_pack")
    prompt_guard = data.get("llm_prompt_guard")
    add_check(
        checks,
        "llm_evidence_pack_present",
        isinstance(pack, dict),
        "API response should include llm_evidence_pack.",
    )
    add_check(
        checks,
        "llm_prompt_guard_present",
        isinstance(prompt_guard, dict),
        "API response should include llm_prompt_guard.",
    )
    if isinstance(prompt_guard, dict):
        add_check(
            checks,
            "llm_prompt_guard_schema",
            prompt_guard.get("schema_version") == "muterbandung.llm_prompt_guard.v1",
            f"Unexpected prompt guard schema version: {prompt_guard.get('schema_version')}.",
        )
        add_check(
            checks,
            "llm_prompt_guard_output_schema",
            prompt_guard.get("output_schema_version") == "muterbandung.llm_output.v1",
            f"Unexpected LLM output schema version: {prompt_guard.get('output_schema_version')}.",
        )
        guard_text = " ".join(prompt_guard.get("rules") or []) + " " + str(prompt_guard.get("system_prompt") or "")
        add_check(
            checks,
            "llm_prompt_guard_forbids_media_hallucination",
            "image_url" in guard_text and "media.available" in guard_text,
            "Prompt guard should forbid image/link output unless media is available in evidence.",
        )
    if not isinstance(pack, dict):
        return

    ranking_policy = pack.get("ranking_policy") or {}
    candidates = pack.get("candidates") or []
    allowed_ids = ranking_policy.get("allowed_destination_ids") or []
    candidate_ids = [candidate.get("destination_id") for candidate in candidates]

    add_check(
        checks,
        "llm_evidence_pack_schema",
        pack.get("schema_version") == "muterbandung.llm_evidence_pack.v1",
        f"Unexpected evidence schema version: {pack.get('schema_version')}.",
    )
    add_check(
        checks,
        "llm_guard_no_destination_creation",
        ranking_policy.get("llm_may_create_destinations") is False,
        "LLM guardrail must forbid creating destinations.",
    )
    add_check(
        checks,
        "llm_guard_no_reranking",
        ranking_policy.get("llm_may_rerank") is False,
        "Initial LLM layer must not rerank backend recommendations.",
    )
    add_check(
        checks,
        "llm_allowed_ids_match_candidates",
        allowed_ids == candidate_ids,
        "allowed_destination_ids should exactly match evidence candidate ids.",
    )
    add_check(
        checks,
        "llm_candidate_count_matches_recommendations",
        len(candidates) == min(len(recommendations), 5),
        f"Evidence candidate count should match top recommendations; got {len(candidates)} vs {len(recommendations)}.",
    )

    required_candidate_fields = {
        "destination_id",
        "name",
        "category",
        "primary_intent",
        "core_labels",
        "final_score",
        "backend_reason",
        "practical_info",
        "sentiment",
        "media",
        "realworld_flags",
        "limitations",
    }
    add_check(
        checks,
        "llm_candidate_required_fields",
        all(required_candidate_fields.issubset(set(candidate)) for candidate in candidates),
        f"Each evidence candidate should include {sorted(required_candidate_fields)}.",
    )
    add_check(
        checks,
        "llm_sentiment_provenance",
        all((candidate.get("sentiment") or {}).get("model_source") == "tfidf_linearsvc" for candidate in candidates),
        "Evidence candidates should carry active sentiment provenance tfidf_linearsvc.",
    )
    add_check(
        checks,
        "llm_media_contract_present",
        all(isinstance(candidate.get("media"), dict) and "available" in candidate.get("media") for candidate in candidates),
        "Evidence candidates should include media availability contract.",
    )
    add_check(
        checks,
        "llm_media_urls_are_guarded",
        all(
            (
                not (candidate.get("media") or {}).get("available")
                or any(
                    str((candidate.get("media") or {}).get(field) or "").startswith("http")
                    for field in ("image_url", "destination_url", "website")
                )
            )
            for candidate in candidates
        ),
        "Available media should expose at least one audited HTTP URL.",
    )


def evaluate_row(row):
    payload = build_payload(row)
    expected_no_strong = is_true(row.get("expect_no_strong_match"))
    expected_min_results = as_int(row.get("expect_min_results"), default=0)

    started = time.time()
    try:
        data = post_recommend(payload)
    except Exception as exc:
        return {
            "id": row.get("id"),
            "scenario": row.get("scenario"),
            "query": row.get("query"),
            "status": "ERROR",
            "elapsed_seconds": round(time.time() - started, 3),
            "issues": [str(exc)],
            "checks": [],
            "top_results": [],
            "payload": payload,
        }

    elapsed = round(time.time() - started, 3)
    recommendations = data.get("recommendations") or []
    top_check_count = max(1, min(DEFAULT_TOP_CHECK, expected_min_results or DEFAULT_TOP_CHECK, len(recommendations)))
    top_items = recommendations[:top_check_count]
    no_strong = data.get("no_strong_match") or {}
    ai_intents = data.get("ai_intents") or {}
    active_intents = [norm(item) for item in ai_intents.get("active_intents") or []]
    checks = []
    validate_llm_evidence_pack(checks, data, recommendations)

    if expected_no_strong:
        add_check(
            checks,
            "expected_no_strong_match",
            bool(no_strong.get("used")) or not recommendations,
            "Expected no strong match for unsupported or unverified query.",
        )
        add_check(
            checks,
            "expected_min_results",
            len(recommendations) <= expected_min_results,
            f"Expected at most {expected_min_results} recommendations, got {len(recommendations)}.",
        )
    else:
        add_check(
            checks,
            "expected_min_results",
            len(recommendations) >= expected_min_results,
            f"Expected at least {expected_min_results} recommendations, got {len(recommendations)}.",
        )
        add_check(
            checks,
            "no_unexpected_no_strong_match",
            not bool(no_strong.get("used")),
            "Did not expect no_strong_match for this query.",
        )

    expected_intents = [norm(item) for item in split_pipe(row.get("expected_intents"))]
    if expected_intents and not expected_no_strong:
        add_check(
            checks,
            "expected_intents",
            all(intent in active_intents for intent in expected_intents),
            f"Expected intents {expected_intents}, got {active_intents}.",
        )

    required_categories = split_pipe(row.get("required_any_category"))
    if required_categories and not expected_no_strong:
        add_check(
            checks,
            "required_any_category",
            any(contains_term(item.get("category"), required_categories) for item in recommendations[:DEFAULT_TOP_CHECK]),
            f"Top {DEFAULT_TOP_CHECK} should include one category from {required_categories}.",
        )

    required_labels = split_pipe(row.get("required_any_label"))
    if required_labels and not expected_no_strong:
        add_check(
            checks,
            "required_any_label",
            any(item_has_any_label(item, required_labels) for item in recommendations[:DEFAULT_TOP_CHECK]),
            f"Top {DEFAULT_TOP_CHECK} should include one positive label from {required_labels}.",
        )

    required_all_labels = split_pipe(row.get("required_all_labels"))
    if required_all_labels and not expected_no_strong:
        add_check(
            checks,
            "required_all_labels",
            bool(top_items) and all(item_has_all_labels(item, required_all_labels) for item in top_items),
            f"Top {top_check_count} should all include labels {required_all_labels}.",
        )

    forbidden_categories = split_pipe(row.get("forbidden_any_category"))
    if forbidden_categories and not expected_no_strong:
        add_check(
            checks,
            "forbidden_any_category",
            not any(contains_term(item.get("category"), forbidden_categories) for item in recommendations[:DEFAULT_TOP_CHECK]),
            f"Top {DEFAULT_TOP_CHECK} should not include categories {forbidden_categories}.",
        )

    forbidden_labels = split_pipe(row.get("forbidden_any_label"))
    if forbidden_labels and not expected_no_strong:
        add_check(
            checks,
            "forbidden_any_label",
            not any(item_has_any_label(item, forbidden_labels) for item in recommendations[:DEFAULT_TOP_CHECK]),
            f"Top {DEFAULT_TOP_CHECK} should not include positive labels {forbidden_labels}.",
        )

    expected_landmark = row.get("expected_landmark", "").strip()
    if expected_landmark and not expected_no_strong:
        location_context = data.get("location_context") or {}
        add_check(
            checks,
            "expected_landmark",
            location_context.get("landmark_name") == expected_landmark,
            f"Expected landmark {expected_landmark}, got {location_context.get('landmark_name')}.",
        )

    if (row.get("user_lat") and row.get("user_lon") or expected_landmark) and not expected_no_strong:
        add_check(
            checks,
            "distance_present",
            bool(top_items) and all(item.get("distance_km") is not None for item in top_items),
            f"Top {top_check_count} should include distance_km.",
        )
        add_check(
            checks,
            "coordinates_verified",
            bool(top_items) and all((item.get("realworld_flags") or {}).get("coordinate_verified", True) for item in top_items),
            f"Top {top_check_count} should not use unverified coordinates.",
        )

    radius = as_float(row.get("max_distance_km"))
    if radius is not None and not expected_no_strong:
        add_check(
            checks,
            "radius_filter",
            all(item.get("distance_km") is None or float(item.get("distance_km")) <= radius for item in recommendations),
            f"All results with distance should be within {radius} km.",
        )

    requested_subtype = row.get("required_shopping_subtype", "").strip()
    if requested_subtype and not expected_no_strong:
        add_check(
            checks,
            "required_shopping_subtype",
            bool(top_items) and all(
                str((item.get("label_taxonomy") or {}).get("shopping_subtype") or "") == requested_subtype
                for item in top_items
            ),
            f"Top {top_check_count} should all have shopping_subtype {requested_subtype}.",
        )

    required_flags = split_pipe(row.get("required_flags"))
    if required_flags and not expected_no_strong:
        add_check(
            checks,
            "required_flags",
            bool(top_items) and all(
                all((item.get("realworld_flags") or {}).get(flag) is True for flag in required_flags)
                for item in top_items
            ),
            f"Top {top_check_count} should all have realworld flags {required_flags}.",
        )

    required_crowd = row.get("required_crowd_level", "").strip()
    if required_crowd and not expected_no_strong:
        add_check(
            checks,
            "required_crowd_level",
            bool(top_items) and all(str((item.get("realworld_flags") or {}).get("crowd_level") or "") == required_crowd for item in top_items),
            f"Top {top_check_count} should all have crowd_level {required_crowd}.",
        )

    required_price = row.get("required_price_type", "").strip()
    if required_price and not expected_no_strong:
        add_check(
            checks,
            "required_price_type",
            bool(top_items) and all(price_is_allowed(item, required_price) for item in top_items),
            f"Top {top_check_count} should satisfy price expectation {required_price}.",
        )

    issues = [check["detail"] for check in checks if not check["passed"]]
    status = "PASS" if not issues else "FAIL"

    return {
        "id": row.get("id"),
        "scenario": row.get("scenario"),
        "query": row.get("query"),
        "status": status,
        "elapsed_seconds": elapsed,
        "issues": issues,
        "checks": checks,
        "active_intents": ai_intents.get("active_intents") or [],
        "no_strong_match": bool(no_strong.get("used")),
        "fallback_used": bool((data.get("fallback") or {}).get("used")),
        "after_filtering": data.get("after_filtering"),
        "top_results": summarize_top_results(recommendations),
        "payload": payload,
    }


def summarize_top_results(recommendations, limit=3):
    rows = []
    for item in recommendations[:limit]:
        score_breakdown = item.get("score_breakdown") or {}
        rows.append({
            "name": item.get("location_name"),
            "category": item.get("category"),
            "score": item.get("final_score"),
            "sentiment_score": score_breakdown.get("sentiment_score"),
            "sentiment_model_source": score_breakdown.get("sentiment_model_source"),
            "sentiment_available": score_breakdown.get("sentiment_available"),
            "distance_km": item.get("distance_km"),
            "labels": sorted(label_set(item)),
            "shopping_subtype": (item.get("label_taxonomy") or {}).get("shopping_subtype"),
            "flags": item.get("realworld_flags") or {},
            "harga": (item.get("info_praktis") or {}).get("harga"),
        })
    return rows


def load_groundtruth():
    with open(GROUNDTRUTH_PATH, "r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return rows


def validate_groundtruth(rows):
    issues = []
    ids = set()
    for index, row in enumerate(rows, start=2):
        row_id = row.get("id", "").strip()
        if not row_id:
            issues.append(f"line {index}: missing id")
        elif row_id in ids:
            issues.append(f"line {index}: duplicate id {row_id}")
        ids.add(row_id)
        if not row.get("query", "").strip():
            issues.append(f"line {index}: missing query")
        if row.get("expect_no_strong_match") not in {"true", "false"}:
            issues.append(f"line {index}: invalid expect_no_strong_match")
        if not str(row.get("expect_min_results", "")).isdigit():
            issues.append(f"line {index}: invalid expect_min_results")
    return issues


def markdown_escape(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_outputs(results, rows):
    passed = sum(1 for item in results if item["status"] == "PASS")
    failed = sum(1 for item in results if item["status"] == "FAIL")
    errors = sum(1 for item in results if item["status"] == "ERROR")
    total = len(results)

    by_scenario = {}
    for result in results:
        scenario = result["scenario"] or "Uncategorized"
        bucket = by_scenario.setdefault(scenario, {"total": 0, "passed": 0, "failed": 0, "errors": 0})
        bucket["total"] += 1
        if result["status"] == "PASS":
            bucket["passed"] += 1
        elif result["status"] == "FAIL":
            bucket["failed"] += 1
        else:
            bucket["errors"] += 1

    report = [
        "# Ground Truth Evaluation Report",
        "",
        "## Summary",
        f"- Ground truth file: `{GROUNDTRUTH_PATH}`",
        f"- API URL: `{API_URL}`",
        f"- Total cases: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Errors: {errors}",
        f"- Pass rate: {(passed / total * 100.0) if total else 0:.1f}%",
        "",
        "## Scenario Breakdown",
        "| Scenario | Total | Passed | Failed | Errors |",
        "|---|---:|---:|---:|---:|",
    ]

    for scenario, counts in sorted(by_scenario.items()):
        report.append(
            f"| {markdown_escape(scenario)} | {counts['total']} | {counts['passed']} | {counts['failed']} | {counts['errors']} |"
        )

    report.extend([
        "",
        "## Failed / Error Cases",
        "| ID | Scenario | Query | Status | Issue | Top Results |",
        "|---|---|---|---|---|---|",
    ])

    problem_cases = [item for item in results if item["status"] != "PASS"]
    if problem_cases:
        for result in problem_cases:
            top_names = ", ".join(
                f"{item.get('name')} ({item.get('category')})"
                for item in result.get("top_results", [])
            )
            issue = "; ".join(result.get("issues") or ["-"])
            report.append(
                "| {id} | {scenario} | {query} | {status} | {issue} | {top} |".format(
                    id=markdown_escape(result.get("id")),
                    scenario=markdown_escape(result.get("scenario")),
                    query=markdown_escape(result.get("query")),
                    status=result.get("status"),
                    issue=markdown_escape(issue),
                    top=markdown_escape(top_names or "-"),
                )
            )
    else:
        report.append("| - | - | - | - | - | - |")

    report.extend([
        "",
        "## Case Details",
    ])

    for result in results:
        top_names = ", ".join(
            f"{item.get('name')} ({item.get('category')} - {item.get('score')})"
            for item in result.get("top_results", [])
        )
        failed_checks = [check["name"] for check in result.get("checks", []) if not check["passed"]]
        report.extend([
            f"### {result['id']} - {result['query']}",
            f"- Status: {result['status']}",
            f"- Scenario: {result['scenario']}",
            f"- Active intents: {', '.join(result.get('active_intents') or []) or 'None'}",
            f"- No strong match: {'Yes' if result.get('no_strong_match') else 'No'}",
            f"- Fallback: {'Yes' if result.get('fallback_used') else 'No'}",
            f"- Failed checks: {', '.join(failed_checks) if failed_checks else 'None'}",
            f"- Top 3: {top_names or 'No results'}",
            "",
        ])

    status = "PASSED" if failed == 0 and errors == 0 else "NEEDS REVISION"
    report.extend([
        "## Final Status",
        status,
        "",
    ])

    payload = {
        "summary": {
            "groundtruth_path": GROUNDTRUTH_PATH,
            "api_url": API_URL,
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": round((passed / total * 100.0) if total else 0.0, 2),
        },
        "scenario_breakdown": by_scenario,
        "results": results,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(report))
    with open(JSON_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def main():
    print("MuterBandung Ground Truth Evaluator")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Ground truth: {GROUNDTRUTH_PATH}")

    api_ready, api_message = preflight_api()
    if not api_ready:
        print(f"\n[PRECHECK FAILED] {api_message}")
        print("Evaluation report was not written.")
        raise SystemExit(2)
    print(f"Preflight: {api_message}")

    rows = load_groundtruth()
    validation_issues = validate_groundtruth(rows)
    if validation_issues:
        print("\n[GROUNDTRUTH INVALID]")
        for issue in validation_issues:
            print(f"- {issue}")
        raise SystemExit(3)

    results = []
    for row in rows:
        print(f"  -> {row['id']} {row['query']}", end="", flush=True)
        result = evaluate_row(row)
        results.append(result)
        print(f" [{result['status']}] ({result['elapsed_seconds']:.2f}s)")

    write_outputs(results, rows)

    passed = sum(1 for item in results if item["status"] == "PASS")
    failed = sum(1 for item in results if item["status"] == "FAIL")
    errors = sum(1 for item in results if item["status"] == "ERROR")
    print("")
    print(f"Evaluation completed. Passed={passed}, Failed={failed}, Errors={errors}")
    print(f"Markdown report: {REPORT_PATH}")
    print(f"JSON results: {JSON_PATH}")
    raise SystemExit(0 if failed == 0 and errors == 0 else 1)


if __name__ == "__main__":
    main()
