import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DEFAULT_DATASET_PATH = Path("Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
DEFAULT_VALIDATION_PATH = Path("Dataset/3_Curated/manual_review_docx_validation_results.json")
DEFAULT_AUDIT_OUTPUT = Path("Dokumentasi_Sistem/MANUAL_REVIEW_DOCX_SAFE_UPDATES_2026-05-26.md")
URL_RE = re.compile(r"https?://[^\s\]\)\"'<>]+", re.IGNORECASE)


def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_note(existing, addition):
    existing = str(existing or "").strip()
    if not existing:
        return addition
    if addition in existing:
        return existing
    return f"{existing} | {addition}"


def load_safe_records(validation_path):
    data = json.loads(Path(validation_path).read_text(encoding="utf-8"))
    return [record for record in data.get("records", []) if record.get("safe_to_apply") and record.get("safe_updates")]


def extract_urls(*values):
    urls = []
    for value in values:
        for match in URL_RE.findall(str(value or "")):
            cleaned = match.rstrip(".,;")
            if cleaned not in urls:
                urls.append(cleaned)
    return urls


def safe_update_sources(record, safe_updates):
    sources = []
    if "is_active_verified" in safe_updates or "display_status" in safe_updates or "curation_action" in safe_updates:
        sources.extend(extract_urls(
            record.get("status_source"),
            record.get("status_note"),
            record.get("weekday_hours"),
            record.get("weekend_hours"),
            record.get("hours_source"),
        ))
    if any(key.startswith("media_") for key in safe_updates):
        sources.extend(extract_urls(record.get("media_url")))
    return list(dict.fromkeys(sources))


def apply_safe_updates(dataset_path=DEFAULT_DATASET_PATH, validation_path=DEFAULT_VALIDATION_PATH, audit_output=DEFAULT_AUDIT_OUTPUT):
    dataset_path = Path(dataset_path)
    validation_path = Path(validation_path)
    audit_output = Path(audit_output)
    records = load_safe_records(validation_path)

    backup_path = dataset_path.with_name(f"{dataset_path.name}.bak_manual_docx_{now_stamp()}")
    shutil.copy2(dataset_path, backup_path)

    df = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    applied = []
    skipped = []

    for record in records:
        location_id = record["location_id"]
        mask = df["location_id"] == location_id
        if int(mask.sum()) != 1:
            skipped.append({
                "location_id": location_id,
                "location_name": record.get("location_name", ""),
                "reason": f"Expected one row, found {int(mask.sum())}.",
            })
            continue

        index = df.index[mask][0]
        before = df.loc[index].to_dict()
        safe_updates = record.get("safe_updates") or {}
        for column, value in safe_updates.items():
            if column in df.columns:
                df.at[index, column] = value

        evidence_urls = safe_update_sources(record, safe_updates)
        note = (
            "Manual DOCX safe update 2026-05-26: "
            f"applied {', '.join(sorted(safe_updates))}. "
            f"Decision={record.get('decision')}. "
            f"Sources: {'; '.join(evidence_urls) if evidence_urls else 'none'}"
        )
        if "curation_note" in df.columns:
            df.at[index, "curation_note"] = append_note(df.at[index, "curation_note"], note)
        if "media_audit_note" in df.columns and any(key.startswith("media_") for key in safe_updates):
            df.at[index, "media_audit_note"] = append_note(df.at[index, "media_audit_note"], note)
        if "qa_flag_reason" in df.columns:
            marker = "manual_docx_safe_update"
            if "is_active_verified" in safe_updates:
                marker += ":active_status"
            if any(key.startswith("media_") for key in safe_updates):
                marker += ":media"
            df.at[index, "qa_flag_reason"] = append_note(df.at[index, "qa_flag_reason"], marker)

        after = df.loc[index].to_dict()
        applied.append({
            "location_id": location_id,
            "location_name": record.get("location_name", ""),
            "decision": record.get("decision"),
            "issues": record.get("issues", []),
            "urls": evidence_urls,
            "updates": safe_updates,
            "before": {key: before.get(key) for key in safe_updates},
            "after": {key: after.get(key) for key in safe_updates},
        })

    if applied:
        df.to_csv(dataset_path, index=False)

    write_audit(audit_output, dataset_path, validation_path, backup_path, applied, skipped)
    return {
        "backup_path": str(backup_path),
        "applied": applied,
        "skipped": skipped,
        "audit_output": str(audit_output),
    }


def write_audit(audit_output, dataset_path, validation_path, backup_path, applied, skipped):
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Manual Review DOCX Safe Updates - 2026-05-26",
        "",
        f"Generated at: `{now_iso()}`",
        f"Dataset: `{dataset_path}`",
        f"Validation source: `{validation_path}`",
        f"Backup: `{backup_path}`",
        "",
        "## Applied",
        "",
    ]
    if not applied:
        lines.append("No updates applied.")
        lines.append("")
    else:
        for item in applied:
            lines.extend([
                f"### {item['location_id']} - {item['location_name']}",
                "",
                f"Decision: `{item['decision']}`",
                f"Issues not applied as data fields: `{', '.join(item['issues']) if item['issues'] else '-'}`",
                "",
                "Sources:",
            ])
            if item["urls"]:
                for url in item["urls"]:
                    lines.append(f"- {url}")
            else:
                lines.append("- none")
            lines.extend([
                "",
                "Updates:",
                "",
                "```json",
                json.dumps(item["updates"], indent=2, ensure_ascii=False),
                "```",
                "",
                "Before:",
                "",
                "```json",
                json.dumps(item["before"], indent=2, ensure_ascii=False),
                "```",
                "",
                "After:",
                "",
                "```json",
                json.dumps(item["after"], indent=2, ensure_ascii=False),
                "```",
                "",
            ])

    lines.extend([
        "## Skipped",
        "",
    ])
    if not skipped:
        lines.append("No updates skipped.")
        lines.append("")
    else:
        for item in skipped:
            lines.append(f"- `{item['location_id']}` {item['location_name']}: {item['reason']}")
        lines.append("")

    lines.extend([
        "## Important Guardrail",
        "",
        "Only fields marked safe by `validate_manual_review_docx.py` were applied. Ambiguous status, unstructured hours, facility text without source URL, and out-of-scope/remove requests remain blocked for manual confirmation.",
    ])
    audit_output.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply only safe updates from manual review DOCX validation results.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--validation", default=str(DEFAULT_VALIDATION_PATH))
    parser.add_argument("--audit-output", default=str(DEFAULT_AUDIT_OUTPUT))
    args = parser.parse_args(argv)

    result = apply_safe_updates(Path(args.dataset), Path(args.validation), Path(args.audit_output))
    print("MuterBandung Manual Review DOCX Safe Updates")
    print("=" * 48)
    print(f"Applied: {len(result['applied'])}")
    print(f"Skipped: {len(result['skipped'])}")
    print(f"Backup: {result['backup_path']}")
    print(f"Audit: {result['audit_output']}")
    return 0 if not result["skipped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
