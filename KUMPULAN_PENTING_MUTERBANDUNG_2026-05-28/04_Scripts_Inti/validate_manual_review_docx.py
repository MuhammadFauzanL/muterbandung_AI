import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import pandas as pd


DEFAULT_DOCX_PATH = Path("MANUAL_REVIEW_BATCH_1_TARGETED_DATA_COMPLETION_2026-05-25_FILLED_SAFE_REVIEW.docx")
DEFAULT_DATASET_PATH = Path("Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
DEFAULT_QUEUE_PATH = Path("Dataset/3_Curated/targeted_data_completion_top50.csv")
DEFAULT_JSON_OUTPUT = Path("Dataset/3_Curated/manual_review_docx_validation_results.json")
DEFAULT_MARKDOWN_OUTPUT = Path("Dokumentasi_Sistem/MANUAL_REVIEW_DOCX_VALIDATION_2026-05-26.md")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
URL_RE = re.compile(r"https?://[^\s\]\)\"'<>]+", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\[\s*\]|____|tidak tahu", re.IGNORECASE)


@dataclass
class ManualReviewRecord:
    location_id: str
    location_name: str
    category: str
    task_priority: str
    task_summary: str
    fields_to_complete: str
    status_text: str
    status_source: str
    status_note: str
    weekday_hours: str
    weekend_hours: str
    hours_source: str
    facility_text: str
    facility_source: str
    media_decision: str
    media_url: str
    apply_decision: str
    extra_note: str
    urls: list[str]
    decision: str
    safe_to_apply: bool
    planned_location: bool
    dataset_location_exists: bool
    issues: list[str]
    safe_updates: dict


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def cell_text(cell):
    return clean_text("".join(node.text or "" for node in cell.findall(".//w:t", NS)))


def table_rows(table):
    rows = []
    for row in table.findall("./w:tr", NS):
        rows.append([cell_text(cell) for cell in row.findall("./w:tc", NS)])
    return rows


def rows_to_dict(rows):
    result = {}
    for row in rows:
        if len(row) >= 2:
            result[clean_text(row[0])] = clean_text(row[1])
    return result


def extract_tables(docx_path):
    with ZipFile(docx_path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return [table_rows(table) for table in root.findall(".//w:tbl", NS)]


def is_metadata_table(rows):
    return bool(rows and len(rows[0]) >= 2 and rows[0][0] == "Field" and rows[0][1] == "Value")


def is_answer_table(rows):
    return bool(rows and rows[0] and rows[0][0] == "Status Aktif")


def extract_urls(*values):
    urls = []
    for value in values:
        for match in URL_RE.findall(str(value or "")):
            cleaned = match.rstrip(".,;")
            if cleaned not in urls:
                urls.append(cleaned)
    return urls


def normalize_decision(status_text):
    text = clean_text(status_text).lower()
    if not text or text == "[ ] aktif [ ] tutup sementara [ ] tutup permanen [ ] ragu":
        return "unanswered"
    if "hapus" in text or "remove" in text or "out of scope" in text or "luar scope" in text:
        return "remove_or_exclude_requested"
    if "tutup permanen" in text:
        return "closed_permanent"
    if "tutup sementara" in text:
        return "closed_temporary"
    if "ragu" in text:
        return "uncertain"
    if "aktif" in text or "masih aktif" in text or "open tomorrow" in text:
        return "active"
    return "unclear"


def apply_decision_yes(value):
    text = clean_text(value).lower()
    return text in {"ya", "boleh", "[ya", "yes", "y", "true"} or "boleh" in text


def looks_like_placeholder(value):
    return bool(PLACEHOLDER_RE.search(clean_text(value)))


def derive_safe_updates(meta, answer, dataset_ids, planned_ids):
    location_id = meta.get("Location ID", "")
    location_name = meta.get("Location Name", "")
    status_text = answer.get("Status Aktif", "")
    status_source = answer.get("Sumber URL status aktif", "")
    status_note = answer.get("Catatan bukti status aktif", "")
    weekday_hours = answer.get("Jam weekday", "")
    weekend_hours = answer.get("Jam weekend", "")
    hours_source = answer.get("Sumber URL jam buka", "")
    facility_text = answer.get("Fasilitas terverifikasi", "")
    facility_source = answer.get("Sumber URL fasilitas", "")
    media_decision = answer.get("Media/gambar valid", "")
    media_url = answer.get("URL media/website yang valid", "")
    apply_decision = answer.get("Boleh diterapkan ke dataset?", "")
    extra_note = answer.get("Catatan tambahan", "")

    status_urls = extract_urls(status_source, status_note, weekday_hours, weekend_hours, hours_source)
    media_urls = extract_urls(media_url)
    urls = extract_urls(status_source, status_note, weekday_hours, weekend_hours, hours_source, facility_source, media_url, extra_note)
    decision = normalize_decision(status_text)
    issues = []
    safe_updates = {}

    dataset_location_exists = location_id in dataset_ids
    planned_location = location_id in planned_ids
    if not dataset_location_exists:
        issues.append("location_id_not_found_in_dataset")
    if not planned_location:
        issues.append("location_id_not_found_in_top50_plan")

    if not apply_decision_yes(apply_decision):
        issues.append("apply_decision_not_explicit_yes_or_boleh")

    if decision in {"unanswered", "unclear"}:
        issues.append("active_status_decision_unclear_or_unanswered")

    if decision in {"active", "closed_temporary", "closed_permanent", "remove_or_exclude_requested"} and not status_urls:
        issues.append("missing_evidence_url_for_status_change")

    if decision == "active" and status_urls and dataset_location_exists:
        safe_updates.update({
            "is_active_verified": "True",
            "review_status": "reviewed",
        })
    elif decision == "closed_temporary" and status_urls and dataset_location_exists:
        safe_updates.update({
            "is_active_verified": "False",
            "display_status": "temporarily_hidden",
            "curation_action": "hide_temporarily",
            "review_status": "needs_review",
        })
    elif decision == "closed_permanent" and status_urls and dataset_location_exists:
        safe_updates.update({
            "is_active_verified": "False",
            "display_status": "exclude_scope",
            "curation_action": "remove",
            "review_status": "reviewed",
        })

    if decision == "remove_or_exclude_requested":
        issues.append("remove_or_exclude_requested_requires_manual_confirmation_before_apply")

    if media_urls and clean_text(media_decision).lower() in {"ya", "valid", "yes", "true"}:
        first = media_urls[0]
        if "encrypted-tbn0.gstatic.com" in first or "googleusercontent" in first:
            issues.append("media_url_is_google_thumbnail_or_unstable_cache")
        else:
            safe_updates.update({
                "media_available": "True",
                "media_image_url": first,
                "media_source": "manual_review_docx",
                "media_audit_status": "accepted",
            })

    if weekday_hours and not looks_like_placeholder(weekday_hours):
        if not extract_urls(hours_source, weekday_hours):
            issues.append("weekday_hours_present_without_source_url")
    if weekend_hours and not looks_like_placeholder(weekend_hours):
        if not extract_urls(hours_source, weekend_hours):
            issues.append("weekend_hours_present_without_source_url")

    if facility_text and not looks_like_placeholder(facility_text):
        if not extract_urls(facility_source, facility_text):
            issues.append("facility_text_present_without_source_url")

    safe_to_apply = bool(safe_updates) and dataset_location_exists and planned_location and apply_decision_yes(apply_decision)
    blocking_issue_prefixes = {
        "location_id_not_found_in_dataset",
        "location_id_not_found_in_top50_plan",
    }
    if any(issue in blocking_issue_prefixes for issue in issues):
        safe_to_apply = False

    return {
        "status_text": status_text,
        "status_source": status_source,
        "status_note": status_note,
        "weekday_hours": weekday_hours,
        "weekend_hours": weekend_hours,
        "hours_source": hours_source,
        "facility_text": facility_text,
        "facility_source": facility_source,
        "media_decision": media_decision,
        "media_url": media_url,
        "apply_decision": apply_decision,
        "extra_note": extra_note,
        "urls": urls,
        "decision": decision,
        "safe_to_apply": safe_to_apply,
        "planned_location": planned_location,
        "dataset_location_exists": dataset_location_exists,
        "issues": sorted(set(issues)),
        "safe_updates": safe_updates,
    }


def parse_manual_review_docx(docx_path, dataset_path, queue_path):
    dataset = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    queue = pd.read_csv(queue_path, dtype=str, keep_default_na=False)
    dataset_ids = set(dataset["location_id"])
    planned_ids = set(queue["location_id"])
    tables = extract_tables(docx_path)

    records = []
    table_index = 0
    while table_index < len(tables):
        rows = tables[table_index]
        if not is_metadata_table(rows):
            table_index += 1
            continue

        meta = rows_to_dict(rows[1:])
        answer = None
        search_index = table_index + 1
        while search_index < len(tables):
            if is_metadata_table(tables[search_index]):
                break
            if is_answer_table(tables[search_index]):
                answer = rows_to_dict(tables[search_index])
                break
            search_index += 1

        if answer is None:
            answer = {}

        derived = derive_safe_updates(meta, answer, dataset_ids, planned_ids)
        records.append(ManualReviewRecord(
            location_id=meta.get("Location ID", ""),
            location_name=meta.get("Location Name", ""),
            category=meta.get("Category", ""),
            task_priority=meta.get("Task Priority", ""),
            task_summary=meta.get("Task Summary", ""),
            fields_to_complete=meta.get("Fields To Complete", ""),
            **derived,
        ))
        table_index = max(search_index + 1, table_index + 1)

    return records


def write_outputs(records, json_output, markdown_output, docx_path, dataset_path, queue_path):
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "muterbandung.manual_review_docx_validation.v1",
        "validated_at": now_iso(),
        "docx_path": str(docx_path),
        "dataset_path": str(dataset_path),
        "queue_path": str(queue_path),
        "summary": {
            "records": len(records),
            "safe_to_apply": sum(1 for record in records if record.safe_to_apply),
            "blocked": sum(1 for record in records if not record.safe_to_apply),
        },
        "records": [asdict(record) for record in records],
    }
    json_output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Manual Review DOCX Validation - 2026-05-26",
        "",
        f"Generated at: `{payload['validated_at']}`",
        f"DOCX: `{docx_path}`",
        f"Dataset: `{dataset_path}`",
        f"Plan queue: `{queue_path}`",
        "",
        "## Summary",
        "",
        f"- Records parsed: `{payload['summary']['records']}`",
        f"- Safe to apply automatically: `{payload['summary']['safe_to_apply']}`",
        f"- Blocked / needs review: `{payload['summary']['blocked']}`",
        "",
        "## Per-Location Result",
        "",
        "| Location | Decision | Safe | Issues | Safe Updates |",
        "|---|---|---:|---|---|",
    ]
    for record in records:
        issues = ", ".join(record.issues) if record.issues else "-"
        updates = ", ".join(f"{key}={value}" for key, value in record.safe_updates.items()) if record.safe_updates else "-"
        lines.append(
            f"| `{record.location_id}` {record.location_name} | {record.decision} | "
            f"{'YES' if record.safe_to_apply else 'NO'} | {issues} | {updates} |"
        )

    lines.extend([
        "",
        "## Rule Notes",
        "",
        "- Status changes require explicit decision plus evidence URL.",
        "- `HAPUS` / out-of-scope requests are blocked for manual confirmation before dataset mutation.",
        "- Hours/facility free text is not applied unless it has source URL and parseable structured value.",
        "- Google cached thumbnail media URLs are blocked because they are unstable evidence.",
    ])
    markdown_output.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate filled manual review DOCX before applying dataset updates.")
    parser.add_argument("--docx", default=str(DEFAULT_DOCX_PATH))
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--markdown-output", default=str(DEFAULT_MARKDOWN_OUTPUT))
    args = parser.parse_args(argv)

    records = parse_manual_review_docx(Path(args.docx), Path(args.dataset), Path(args.queue))
    write_outputs(records, Path(args.json_output), Path(args.markdown_output), Path(args.docx), Path(args.dataset), Path(args.queue))

    safe_count = sum(1 for record in records if record.safe_to_apply)
    print("MuterBandung Manual Review DOCX Validation")
    print("=" * 48)
    print(f"Records parsed: {len(records)}")
    print(f"Safe to apply: {safe_count}")
    print(f"Blocked / needs review: {len(records) - safe_count}")
    print(f"JSON: {args.json_output}")
    print(f"Markdown: {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
