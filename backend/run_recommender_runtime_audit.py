import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_DATASET = ROOT / (
    "Wisata_Workspace/01_Dataset/3_Curated/"
    "DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv"
)
DEFAULT_EVAL_SET = ROOT / (
    "Wisata_Workspace/01_Dataset/4_Evaluation/"
    "wisata_recommender_eval_queries_2026-06-09.json"
)
DEFAULT_JSON_REPORT = ROOT / (
    "Wisata_Workspace/03_Dokumentasi/"
    "RECOMMENDER_RUNTIME_API_AUDIT_2026-06-09.json"
)
DEFAULT_MD_REPORT = ROOT / (
    "Wisata_Workspace/03_Dokumentasi/"
    "RECOMMENDER_RUNTIME_API_AUDIT_2026-06-09.md"
)


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_max_price(price_text):
    if not price_text:
        return None
    if "gratis" in str(price_text).lower():
        return 0
    values = []
    for match in re.findall(r"Rp\s*([0-9.]+)", str(price_text)):
        digits = re.sub(r"[^0-9]", "", match)
        if digits:
            values.append(int(digits))
    return max(values) if values else None


def is_free(price_text):
    price = parse_max_price(price_text)
    return price == 0


def recommendation_summary(item):
    flags = item.get("realworld_flags", {}) or {}
    breakdown = item.get("score_breakdown", {}) or {}
    practical = item.get("info_praktis", {}) or {}
    return {
        "rank": item.get("rank"),
        "location_id": item.get("location_id"),
        "location_name": item.get("location_name"),
        "category": item.get("category"),
        "final_score": item.get("final_score"),
        "price": practical.get("harga"),
        "distance_km": breakdown.get("distance_km"),
        "similarity": breakdown.get("similarity"),
        "adjusted_sentiment_score": breakdown.get("adjusted_sentiment_score"),
        "google_rating": breakdown.get("google_rating"),
        "review_confidence_label": breakdown.get("review_confidence_label"),
        "sentiment_model_source": breakdown.get("sentiment_model_source"),
        "mushola_verified": flags.get("mushola_verified"),
        "parking_verified": flags.get("parking_verified"),
        "night_verified": flags.get("night_verified"),
        "child_friendly_verified": flags.get("child_friendly_verified"),
        "coordinate_verified": flags.get("coordinate_verified"),
    }


def evaluate_case(case, response_json):
    expect = case.get("expect", {}) or {}
    recs = response_json.get("recommendations", []) or []
    issues = []

    if response_json.get("status") != "success":
        issues.append(f"status is {response_json.get('status')}")

    min_recommendations = expect.get("min_recommendations")
    if min_recommendations is not None and len(recs) < int(min_recommendations):
        issues.append(f"recommendations below minimum: {len(recs)} < {min_recommendations}")

    expected_no_match = expect.get("no_strong_match")
    if expected_no_match is not None:
        actual = bool((response_json.get("no_strong_match") or {}).get("used"))
        if actual != bool(expected_no_match):
            issues.append(f"no_strong_match expected {expected_no_match}, got {actual}")

    expected_fallback = expect.get("fallback_used")
    if expected_fallback is not None:
        actual = bool((response_json.get("fallback") or {}).get("used"))
        if actual != bool(expected_fallback):
            issues.append(f"fallback_used expected {expected_fallback}, got {actual}")

    required_flags = expect.get("required_true_flags") or []
    for flag in required_flags:
        failing = [
            item.get("location_id")
            for item in recs
            if not bool((item.get("realworld_flags") or {}).get(flag))
        ]
        if failing:
            issues.append(f"{flag} not true for: {', '.join(failing)}")

    if expect.get("all_free"):
        failing = [
            item.get("location_id")
            for item in recs
            if not is_free((item.get("info_praktis") or {}).get("harga"))
        ]
        if failing:
            issues.append(f"not free for: {', '.join(failing)}")

    max_price = expect.get("max_price")
    if max_price is not None:
        failing = []
        for item in recs:
            price = parse_max_price((item.get("info_praktis") or {}).get("harga"))
            if price is None or price > int(max_price):
                failing.append(item.get("location_id"))
        if failing:
            issues.append(f"max_price {max_price} failed for: {', '.join(failing)}")

    if expect.get("distance_required"):
        failing = [
            item.get("location_id")
            for item in recs
            if (item.get("score_breakdown") or {}).get("distance_km") is None
        ]
        if failing:
            issues.append(f"distance missing for: {', '.join(failing)}")

    return issues


def render_markdown(report):
    lines = [
        "# Recommender Runtime API Audit 2026-06-09",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Dataset: `{report['dataset_path']}`",
        f"Data version: `{report.get('data_version', 'unknown')}`",
        f"Gate: `{report['gate_status']}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total queries | {report['summary']['total_queries']} |",
        f"| Passed | {report['summary']['passed']} |",
        f"| Warnings | {report['summary']['warnings']} |",
        f"| Failed | {report['summary']['failed']} |",
        "",
        "## Query Results",
        "",
    ]
    for result in report["results"]:
        lines.extend([
            f"### {result['id']}",
            "",
            f"Query: `{result['query']}`",
            "",
            f"Status: `{result['status']}`",
            "",
        ])
        if result["issues"]:
            lines.append("Issues:")
            for issue in result["issues"]:
                lines.append(f"- {issue}")
            lines.append("")
        lines.extend([
            "| Rank | ID | Nama | Score | Harga | Sentiment | Flags |",
            "|---:|---|---|---:|---|---|---|",
        ])
        for rec in result["recommendations"][:5]:
            flags = []
            for key, label in [
                ("mushola_verified", "mushola"),
                ("parking_verified", "parkir"),
                ("night_verified", "malam"),
                ("child_friendly_verified", "anak"),
            ]:
                if rec.get(key):
                    flags.append(label)
            lines.append(
                f"| {rec.get('rank')} | `{rec.get('location_id')}` | "
                f"{rec.get('location_name')} | {rec.get('final_score')} | "
                f"{rec.get('price')} | {rec.get('sentiment_model_source')} / "
                f"{rec.get('review_confidence_label')} | {', '.join(flags) or '-'} |"
            )
        lines.append("")
    lines.extend([
        "## Decision",
        "",
        report["decision"],
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run MuterBandung runtime API recommendation audit.")
    parser.add_argument("--eval-set", default=str(DEFAULT_EVAL_SET))
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_REPORT))
    parser.add_argument("--markdown-output", default=str(DEFAULT_MD_REPORT))
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    os.environ["MUTERBANDUNG_DATASET_PATH"] = str(dataset_path)
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

    from Scripts.app import app

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    expected_dataset_marker = eval_set.get("dataset_expected_contains")
    app.config["TESTING"] = True
    client = app.test_client()

    results = []
    data_version = "unknown"
    for case in eval_set["queries"]:
        response = client.post("/api/recommend", json=case["payload"])
        payload = response.get_json() or {}
        data_version = payload.get("data_version") or data_version
        recommendations = [
            recommendation_summary(item)
            for item in payload.get("recommendations", []) or []
        ]
        issues = []
        if response.status_code != 200:
            issues.append(f"HTTP status {response.status_code}")
        issues.extend(evaluate_case(case, payload))
        if expected_dataset_marker and expected_dataset_marker not in data_version:
            issues.append("runtime data_version does not include expected dataset marker")
        status = "PASS" if not issues else "WARNING"
        results.append({
            "id": case["id"],
            "query": case["payload"].get("query"),
            "status": status,
            "http_status": response.status_code,
            "after_filtering": payload.get("after_filtering"),
            "fallback_used": bool((payload.get("fallback") or {}).get("used")),
            "no_strong_match": bool((payload.get("no_strong_match") or {}).get("used")),
            "issues": issues,
            "recommendations": recommendations,
        })

    passed = sum(1 for item in results if item["status"] == "PASS")
    warnings = sum(1 for item in results if item["status"] == "WARNING")
    failed = sum(1 for item in results if item["status"] == "FAIL")
    gate_status = "PASS" if warnings == 0 and failed == 0 else "PASS_WITH_WARNINGS"
    decision = (
        "Runtime API sudah memakai dataset candidate terbaru. Query dasar berjalan, "
        "tetapi item WARNING perlu dibaca sebagai bahan tuning, bukan blocker langsung."
        if gate_status == "PASS_WITH_WARNINGS"
        else "Runtime API siap untuk baseline rekomendasi awal."
    )

    report = {
        "generated_at": utc_now_iso(),
        "dataset_path": str(dataset_path),
        "data_version": data_version,
        "eval_set": str(Path(args.eval_set)),
        "gate_status": gate_status,
        "summary": {
            "total_queries": len(results),
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
        },
        "results": results,
        "decision": decision,
    }

    json_output = Path(args.json_output)
    markdown_output = Path(args.markdown_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")

    print("MuterBandung Runtime API Audit")
    print("=" * 40)
    print(f"Gate: {gate_status}")
    print(f"Passed: {passed}")
    print(f"Warnings: {warnings}")
    print(f"Failed: {failed}")
    print(f"Data version: {data_version}")
    print(f"JSON: {json_output}")
    print(f"Markdown: {markdown_output}")

    if failed > 0:
        return 1
    if args.fail_on_warning and warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
