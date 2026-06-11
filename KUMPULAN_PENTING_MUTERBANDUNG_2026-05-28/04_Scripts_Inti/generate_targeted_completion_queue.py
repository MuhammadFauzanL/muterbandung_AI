import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


CURATED_PATH = Path("Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
VALIDATION_JSON_PATH = Path("Dataset/3_Curated/data_validation_results.json")
LOCAL_DATA_CANDIDATES_PATH = Path("Dataset/3_Curated/local_scrape_data_candidates.csv")
LOCAL_MEDIA_CANDIDATES_PATH = Path("Dataset/3_Curated/local_scrape_media_candidates.csv")
MANUAL_DATA_QUEUE_PATH = Path("Dataset/3_Curated/manual_data_fill_queue.csv")
MANUAL_MEDIA_QUEUE_PATH = Path("Dataset/3_Curated/manual_media_fill_queue.csv")
MANUAL_REALWORLD_QUEUE_PATH = Path("Dataset/3_Curated/manual_realworld_verification_queue.csv")

OUTPUT_QUEUE_PATH = Path("Dataset/3_Curated/targeted_data_completion_queue.csv")
OUTPUT_TOP_QUEUE_PATH = Path("Dataset/3_Curated/targeted_data_completion_top50.csv")
OUTPUT_REPORT_PATH = Path("Dokumentasi_Sistem/TARGETED_DATA_COMPLETION_PLAN_2026-05-25.md")

FACILITY_COLUMNS = [
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
]

HOUR_COLUMNS = [
    "jam_buka_weekday",
    "jam_tutup_weekday",
    "jam_buka_weekend",
    "jam_tutup_weekend",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_csv_if_exists(path):
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def norm(value):
    return str(value or "").strip()


def is_true(value):
    return norm(value).lower() == "true"


def is_false(value):
    return norm(value).lower() == "false"


def bool_text(value):
    text = norm(value)
    return text if text else ""


def has_text(value):
    return bool(norm(value))


def priority_from_score(score):
    if score >= 100:
        return "P0"
    if score >= 80:
        return "P1"
    if score >= 55:
        return "P2"
    return "P3"


def first_value(df, location_id, field, default=""):
    if df.empty or field not in df.columns or "location_id" not in df.columns:
        return default
    match = df[df["location_id"] == location_id]
    if match.empty:
        return default
    return norm(match.iloc[0].get(field, default))


def count_matches(df, location_id):
    if df.empty or "location_id" not in df.columns:
        return 0
    return int((df["location_id"] == location_id).sum())


def candidate_status_summary(df, location_id):
    if df.empty or "location_id" not in df.columns:
        return ""
    match = df[df["location_id"] == location_id]
    if match.empty:
        return ""
    if "reviewer_status" not in match.columns:
        return f"{len(match)} candidate(s)"
    counts = match["reviewer_status"].value_counts().to_dict()
    return "; ".join(f"{status}:{count}" for status, count in counts.items())


def best_local_data_candidate(local_data, location_id, field_name):
    if local_data.empty:
        return {}
    match = local_data[
        (local_data.get("location_id", "") == location_id)
        & (local_data.get("field_name", "") == field_name)
    ]
    if match.empty:
        return {}
    approved = match[match.get("reviewer_status", "") == "approved_candidate"]
    row = (approved if not approved.empty else match).iloc[0]
    return {
        "candidate_value": norm(row.get("new_value", "")),
        "candidate_source_url": norm(row.get("source_url", "")),
        "candidate_status": norm(row.get("reviewer_status", "")),
        "candidate_match_title": norm(row.get("matched_raw_title", "")),
        "candidate_match_score": norm(row.get("match_score", "")),
    }


def best_local_media_candidate(local_media, location_id):
    if local_media.empty:
        return {}
    match = local_media[local_media.get("location_id", "") == location_id]
    if match.empty:
        return {}
    approved = match[match.get("reviewer_status", "") == "approved_candidate"]
    row = (approved if not approved.empty else match).iloc[0]
    return {
        "candidate_value": norm(row.get("new_media_image_url", "")) or norm(row.get("new_media_destination_url", "")),
        "candidate_source_url": norm(row.get("new_media_destination_url", "")),
        "candidate_status": norm(row.get("reviewer_status", "")),
        "candidate_match_title": norm(row.get("matched_raw_title", "")),
        "candidate_match_score": norm(row.get("match_score", "")),
    }


def task_row(row, task_type, issue_codes, fields, score, recommended_action, candidate=None, evidence_sources=None):
    candidate = candidate or {}
    evidence_sources = evidence_sources or []
    location_id = norm(row.get("location_id", ""))
    location_name = norm(row.get("location_name", ""))
    return {
        "priority": priority_from_score(score),
        "impact_score": int(score),
        "task_type": task_type,
        "location_id": location_id,
        "location_name": location_name,
        "category": norm(row.get("category", "")),
        "display_status": norm(row.get("display_status", "")),
        "issue_codes": "|".join(issue_codes),
        "fields_to_complete": "|".join(fields),
        "current_is_active_verified": bool_text(row.get("is_active_verified", "")),
        "current_media_available": bool_text(row.get("media_available", "")),
        "current_sentiment_available": bool_text(row.get("sentiment_available", "")),
        "current_avg_rating": norm(row.get("avg_rating", "")),
        "current_coordinate_verified": bool_text(row.get("coordinate_verified", "")),
        "candidate_value": candidate.get("candidate_value", ""),
        "candidate_source_url": candidate.get("candidate_source_url", ""),
        "candidate_status": candidate.get("candidate_status", ""),
        "candidate_match_title": candidate.get("candidate_match_title", ""),
        "candidate_match_score": candidate.get("candidate_match_score", ""),
        "evidence_sources": "|".join(source for source in evidence_sources if source),
        "recommended_action": recommended_action,
        "auto_apply_allowed": "False",
        "reviewer_status": "todo",
        "reviewer_note": "",
    }


def load_validation_summary(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("summary", {})
    except json.JSONDecodeError:
        return {}


def generate_queue(
    curated_path=CURATED_PATH,
    validation_json_path=VALIDATION_JSON_PATH,
    local_data_candidates_path=LOCAL_DATA_CANDIDATES_PATH,
    local_media_candidates_path=LOCAL_MEDIA_CANDIDATES_PATH,
    manual_data_queue_path=MANUAL_DATA_QUEUE_PATH,
    manual_media_queue_path=MANUAL_MEDIA_QUEUE_PATH,
    manual_realworld_queue_path=MANUAL_REALWORLD_QUEUE_PATH,
):
    df = pd.read_csv(curated_path, dtype=str, keep_default_na=False)
    active = df[df["display_status"] == "active_candidate"].copy()
    local_data = read_csv_if_exists(local_data_candidates_path)
    local_media = read_csv_if_exists(local_media_candidates_path)
    manual_data = read_csv_if_exists(manual_data_queue_path)
    manual_media = read_csv_if_exists(manual_media_queue_path)
    manual_realworld = read_csv_if_exists(manual_realworld_queue_path)

    tasks = []
    for _, row in active.iterrows():
        location_id = norm(row.get("location_id", ""))
        evidence_sources = []
        if count_matches(manual_realworld, location_id):
            evidence_sources.append("manual_realworld_verification_queue")

        missing_hours = [field for field in HOUR_COLUMNS if not has_text(row.get(field, ""))]
        if missing_hours:
            tasks.append(task_row(
                row,
                task_type="opening_hours_completion",
                issue_codes=["W_ACTIVE_WEEKDAY_HOURS_MISSING", "W_ACTIVE_WEEKEND_HOURS_MISSING"],
                fields=missing_hours,
                score=115,
                recommended_action="Find official/Maps source, fill open/close pairs, then rerun validator.",
                evidence_sources=evidence_sources + ["manual_data_fill_queue"],
            ))

        if not has_text(row.get("is_active_verified", "")):
            score = 95
            if is_false(row.get("coordinate_verified", "")):
                score += 10
            if is_false(row.get("media_available", "")):
                score += 8
            if is_false(row.get("sentiment_available", "")) or not has_text(row.get("avg_rating", "")):
                score += 8
            if missing_hours:
                score += 15
            tasks.append(task_row(
                row,
                task_type="active_status_verification",
                issue_codes=["W_ACTIVE_VERIFICATION_MISSING"],
                fields=["is_active_verified"],
                score=score,
                recommended_action="Verify whether place is active/open from reliable source; set True/False with evidence URL.",
                evidence_sources=evidence_sources,
            ))

        facility_true_count = sum(is_true(row.get(column, "")) for column in FACILITY_COLUMNS)
        if facility_true_count == 0:
            score = 70
            category = norm(row.get("category", "")).lower()
            if any(term in category for term in ["keluarga", "belanja", "kuliner", "museum", "wahana"]):
                score += 10
            if not has_text(row.get("is_active_verified", "")):
                score += 5
            tasks.append(task_row(
                row,
                task_type="facility_verification",
                issue_codes=["W_ACTIVE_FACILITY_VERIFICATION_SPARSE"],
                fields=FACILITY_COLUMNS,
                score=score,
                recommended_action="Verify only facilities explicitly supported by source; keep unknown facilities False.",
                evidence_sources=evidence_sources,
            ))

        if is_false(row.get("media_available", "")):
            candidate = best_local_media_candidate(local_media, location_id)
            score = 75
            if candidate.get("candidate_status") == "approved_candidate":
                score += 15
            if count_matches(manual_media, location_id):
                evidence_sources.append("manual_media_fill_queue")
            tasks.append(task_row(
                row,
                task_type="media_completion",
                issue_codes=["W_ACTIVE_MEDIA_UNAVAILABLE"],
                fields=["media_available", "media_image_url", "media_destination_url", "media_website", "media_source"],
                score=score,
                recommended_action="Review candidate media; accept only destination-level, non-misleading URL.",
                candidate=candidate,
                evidence_sources=evidence_sources + (["local_scrape_media_candidates"] if candidate else []),
            ))

        rating_missing = not has_text(row.get("avg_rating", ""))
        sentiment_unavailable = is_false(row.get("sentiment_available", ""))
        if rating_missing or sentiment_unavailable:
            candidate = best_local_data_candidate(local_data, location_id, "avg_rating")
            fields = []
            issue_codes = []
            if rating_missing:
                fields.append("avg_rating")
                issue_codes.append("W_ACTIVE_RATING_MISSING")
            if sentiment_unavailable:
                fields.extend(["sentiment_available", "sentiment_model_source", "sentiment_model_version"])
                issue_codes.append("W_ACTIVE_SENTIMENT_UNAVAILABLE")
            score = 72
            if rating_missing and sentiment_unavailable:
                score += 8
            if candidate.get("candidate_status") == "approved_candidate":
                score += 8
            tasks.append(task_row(
                row,
                task_type="rating_sentiment_completion",
                issue_codes=issue_codes,
                fields=fields,
                score=score,
                recommended_action="Apply rating only after source review; sentiment requires review corpus or keep unavailable with caveat.",
                candidate=candidate,
                evidence_sources=evidence_sources + (["local_scrape_data_candidates"] if candidate else ["manual_data_fill_queue"]),
            ))

        if is_false(row.get("coordinate_verified", "")):
            tasks.append(task_row(
                row,
                task_type="coordinate_verification",
                issue_codes=["W_ACTIVE_COORDINATE_UNVERIFIED"],
                fields=["coordinate_verified", "latitude", "longitude"],
                score=92,
                recommended_action="Verify coordinates against Maps/source before using for distance-sensitive claims.",
                evidence_sources=evidence_sources + ["manual_data_fill_queue"],
            ))

        if not has_text(row.get("media_website", "")):
            tasks.append(task_row(
                row,
                task_type="website_reference_completion",
                issue_codes=["I_ACTIVE_WEBSITE_MISSING"],
                fields=["media_website"],
                score=35,
                recommended_action="Optional: add official/reference website only when reliable.",
                evidence_sources=evidence_sources,
            ))

    queue = pd.DataFrame(tasks)
    if queue.empty:
        return queue, {
            "generated_at": now_iso(),
            "task_count": 0,
            "validation_summary": load_validation_summary(validation_json_path),
        }

    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    queue["_priority_order"] = queue["priority"].map(priority_order)
    queue = queue.sort_values(
        by=["_priority_order", "impact_score", "task_type", "location_name"],
        ascending=[True, False, True, True],
    ).drop(columns=["_priority_order"]).reset_index(drop=True)

    summary = {
        "generated_at": now_iso(),
        "task_count": int(len(queue)),
        "location_count": int(queue["location_id"].nunique()),
        "priority_counts": queue["priority"].value_counts().to_dict(),
        "task_type_counts": queue["task_type"].value_counts().to_dict(),
        "candidate_task_count": int(queue["candidate_status"].ne("").sum()),
        "validation_summary": load_validation_summary(validation_json_path),
        "manual_queue_status": {
            "manual_realworld_rows": int(len(manual_realworld)),
            "manual_media_rows": int(len(manual_media)),
            "manual_data_rows": int(len(manual_data)),
            "local_media_candidates": int(len(local_media)),
            "local_data_candidates": int(len(local_data)),
        },
    }
    return queue, summary


def render_markdown(queue, summary):
    validation = summary.get("validation_summary") or {}
    lines = [
        "# Targeted Data Completion Plan - 2026-05-25",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "## Gate Context",
        "",
        f"- Data validation gate: `{validation.get('gate_status', 'unknown')}`",
        f"- Blocking errors: `{validation.get('error_count', 'unknown')}`",
        f"- Warnings: `{validation.get('warning_count', 'unknown')}`",
        f"- Active candidates: `{validation.get('active_candidate_count', 'unknown')}`",
        "",
        "## Queue Summary",
        "",
        f"- Tasks: `{summary['task_count']}`",
        f"- Locations: `{summary['location_count']}`",
        f"- Tasks with local candidate evidence: `{summary['candidate_task_count']}`",
        "",
        "### By Priority",
        "",
        "| Priority | Count |",
        "| --- | ---: |",
    ]
    for priority in ["P0", "P1", "P2", "P3"]:
        lines.append(f"| {priority} | {summary.get('priority_counts', {}).get(priority, 0)} |")

    lines.extend([
        "",
        "### By Task Type",
        "",
        "| Task Type | Count |",
        "| --- | ---: |",
    ])
    for task_type, count in sorted(summary.get("task_type_counts", {}).items()):
        lines.append(f"| `{task_type}` | {count} |")

    lines.extend([
        "",
        "## Top 50 Work Queue",
        "",
        "| Priority | Score | Task | location_id | location_name | Candidate | Recommended Action |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ])
    for _, row in queue.head(50).iterrows():
        candidate = row.get("candidate_status") or "-"
        name = str(row.get("location_name", "")).replace("|", "\\|")
        action = str(row.get("recommended_action", "")).replace("|", "\\|")
        lines.append(
            f"| {row['priority']} | {row['impact_score']} | `{row['task_type']}` | `{row['location_id']}` | {name} | {candidate} | {action} |"
        )

    lines.extend([
        "",
        "## Operating Rules",
        "",
        "- Do not auto-apply `approved_candidate` rows without human/source review; they are candidates, not accepted facts.",
        "- For LLM, unknown facility flags must stay conservative. False here often means not verified, not necessarily absent.",
        "- `is_active_verified` must only become True/False with an evidence URL or reviewer note.",
        "- Media URLs must be destination-level and not road, route, unrelated business, or generic search pages.",
        "- Opening hours should be filled in pairs: open and close for weekday/weekend.",
        "",
        "## Recommended Execution Order",
        "",
        "1. Finish P0 opening-hours and active-status tasks.",
        "2. Review local media candidates with `approved_candidate` status.",
        "3. Review local avg_rating candidates with `approved_candidate` status.",
        "4. Work facility verification for high-traffic categories: family, shopping, culinary, museum, and theme/water parks.",
        "5. Rerun `python -B .\\Scripts\\validate_curated_dataset.py` after every accepted batch.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(queue, summary, output_queue, output_top_queue, output_report):
    output_queue.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(output_queue, index=False)
    queue.head(50).to_csv(output_top_queue, index=False)
    output_report.write_text(render_markdown(queue, summary), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate targeted data completion queue from validation warnings.")
    parser.add_argument("--dataset", default=str(CURATED_PATH))
    parser.add_argument("--validation-json", default=str(VALIDATION_JSON_PATH))
    parser.add_argument("--output-queue", default=str(OUTPUT_QUEUE_PATH))
    parser.add_argument("--output-top-queue", default=str(OUTPUT_TOP_QUEUE_PATH))
    parser.add_argument("--output-report", default=str(OUTPUT_REPORT_PATH))
    args = parser.parse_args(argv)

    queue, summary = generate_queue(
        curated_path=Path(args.dataset),
        validation_json_path=Path(args.validation_json),
    )
    write_outputs(
        queue,
        summary,
        Path(args.output_queue),
        Path(args.output_top_queue),
        Path(args.output_report),
    )
    print("MuterBandung Targeted Data Completion Queue")
    print("=" * 48)
    print(f"Tasks: {summary['task_count']}")
    print(f"Locations: {summary['location_count']}")
    print(f"Priorities: {summary['priority_counts']}")
    print(f"Task types: {summary['task_type_counts']}")
    print(f"Queue: {args.output_queue}")
    print(f"Top queue: {args.output_top_queue}")
    print(f"Report: {args.output_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
