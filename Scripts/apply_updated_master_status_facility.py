import argparse
import csv
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DEFAULT_DATASET_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
DEFAULT_MASTER_PATH = Path("updated_master_wisata_bandung.csv")
DEFAULT_AUDIT_OUTPUT = Path("Wisata_Workspace/03_Dokumentasi/UPDATED_MASTER_STATUS_FACILITY_APPLY_2026-05-27.md")


STATUS_DECISIONS = {
    "include_active": {
        "display_status": "active_candidate",
        "curation_action": "keep",
        "is_active_verified": "True",
        "review_status": "reviewed",
    },
    "include_renamed": {
        "display_status": "active_candidate",
        "curation_action": "keep",
        "is_active_verified": "True",
        "review_status": "reviewed",
    },
    "exclude_closed": {
        "display_status": "temporarily_hidden",
        "curation_action": "hide_temporarily",
        "is_active_verified": "False",
        "review_status": "reviewed",
    },
    "exclude_unclear": {
        "display_status": "exclude_scope",
        "curation_action": "remove",
        "is_active_verified": "False",
        "review_status": "reviewed",
    },
}

FACILITY_MAP = {
    "Parkir": "parking_verified",
    "Toilet": "toilet_verified",
    "Mushola": "mushola_verified",
    "Kursi_Roda": "wheelchair_accessible_verified",
    "Pet_Friendly": "pet_friendly_verified",
}


def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_note(existing, addition):
    existing = str(existing or "").strip()
    addition = str(addition or "").strip()
    if not addition:
        return existing
    if not existing:
        return addition
    if addition in existing:
        return existing
    return f"{existing} | {addition}"


def norm(value):
    return str(value or "").strip()


def normalize_symbol(value):
    text = norm(value)
    if text in {"✓", "âœ“", "true", "True", "TRUE", "ya", "Ya", "YES", "yes"}:
        return "True"
    if text in {"✗", "âœ—", "false", "False", "FALSE", "tidak", "Tidak", "NO", "no"}:
        return "False"
    return ""


def build_status_note(row):
    parts = [
        "Updated master status/facility 2026-05-27",
        f"status={norm(row.get('Status_Operasional'))}",
        f"decision={norm(row.get('Final_Decision_Status'))}",
        f"confidence={norm(row.get('Confidence_Status'))}",
    ]
    source = norm(row.get("Sumber_Status"))
    note = norm(row.get("Catatan_Status"))
    revision = norm(row.get("Revision_Note_Status"))
    if source:
        parts.append(f"sources={source}")
    if note:
        parts.append(f"note={note}")
    if revision:
        parts.append(f"revision={revision}")
    return "; ".join(parts)


def build_facility_note(row):
    parts = [
        "Updated master status/facility 2026-05-27",
        f"facility_status={norm(row.get('Status_Fasilitas'))}",
        f"facility_evidence={norm(row.get('Evidence_Status_Fasilitas'))}",
    ]
    facility = norm(row.get("Fasilitas_Utama"))
    action = norm(row.get("Final_Action_Fasilitas"))
    note = norm(row.get("Catatan_Fasilitas"))
    revision = norm(row.get("Revision_Note_Fasilitas"))
    if facility:
        parts.append(f"facilities={facility}")
    if action:
        parts.append(f"action={action}")
    if note:
        parts.append(f"note={note}")
    if revision:
        parts.append(f"revision={revision}")
    return "; ".join(parts)


def apply_updates(dataset_path=DEFAULT_DATASET_PATH, master_path=DEFAULT_MASTER_PATH, audit_output=DEFAULT_AUDIT_OUTPUT):
    dataset_path = Path(dataset_path)
    master_path = Path(master_path)
    audit_output = Path(audit_output)

    backup_path = dataset_path.with_name(f"{dataset_path.name}.bak_updated_master_status_facility_{now_stamp()}")
    shutil.copy2(dataset_path, backup_path)

    df = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    with master_path.open("r", encoding="utf-8-sig", newline="") as handle:
        master_rows = list(csv.DictReader(handle))

    applied_status = []
    skipped_status = []
    applied_facilities = []
    skipped_rows = []

    for row in master_rows:
        location_id = norm(row.get("ID"))
        if not location_id:
            skipped_rows.append({"location_id": "", "reason": "Missing ID in updated master."})
            continue
        matches = df.index[df["location_id"].astype(str).eq(location_id)].tolist()
        if len(matches) != 1:
            skipped_rows.append({"location_id": location_id, "reason": f"Expected one dataset row, found {len(matches)}."})
            continue

        idx = matches[0]
        data_availability = norm(row.get("Data_Availability"))

        if "status_operasional_43" in data_availability:
            decision = norm(row.get("Final_Decision_Status"))
            if decision in STATUS_DECISIONS:
                before = df.loc[idx].to_dict()
                for column, value in STATUS_DECISIONS[decision].items():
                    if column in df.columns:
                        df.at[idx, column] = value
                if "curation_note" in df.columns:
                    df.at[idx, "curation_note"] = append_note(df.at[idx, "curation_note"], build_status_note(row))
                if "qa_flag_reason" in df.columns:
                    df.at[idx, "qa_flag_reason"] = append_note(
                        df.at[idx, "qa_flag_reason"],
                        f"updated_master_status_facility_2026-05-27:status:{decision}",
                    )
                applied_status.append(
                    {
                        "location_id": location_id,
                        "location_name": norm(row.get("Nama_Lokasi")),
                        "decision": decision,
                        "before": {
                            key: before.get(key, "")
                            for key in ["display_status", "curation_action", "is_active_verified", "review_status"]
                        },
                        "after": {
                            key: df.at[idx, key]
                            for key in ["display_status", "curation_action", "is_active_verified", "review_status"]
                            if key in df.columns
                        },
                    }
                )
            else:
                skipped_status.append(
                    {
                        "location_id": location_id,
                        "location_name": norm(row.get("Nama_Lokasi")),
                        "decision": decision,
                        "reason": "Status decision is not safe for automatic apply.",
                    }
                )

        if "fasilitas_54" in data_availability:
            before = df.loc[idx].to_dict()
            changed = {}
            for source_column, target_column in FACILITY_MAP.items():
                if target_column not in df.columns:
                    continue
                mapped = normalize_symbol(row.get(source_column))
                if mapped:
                    df.at[idx, target_column] = mapped
                    changed[target_column] = mapped
            if changed:
                if "curation_note" in df.columns:
                    df.at[idx, "curation_note"] = append_note(df.at[idx, "curation_note"], build_facility_note(row))
                if "qa_flag_reason" in df.columns:
                    df.at[idx, "qa_flag_reason"] = append_note(
                        df.at[idx, "qa_flag_reason"],
                        "updated_master_status_facility_2026-05-27:facility",
                    )
                applied_facilities.append(
                    {
                        "location_id": location_id,
                        "location_name": norm(row.get("Nama_Lokasi")),
                        "changed": changed,
                        "before": {key: before.get(key, "") for key in changed},
                    }
                )

    df.to_csv(dataset_path, index=False)
    write_audit(
        audit_output=audit_output,
        dataset_path=dataset_path,
        master_path=master_path,
        backup_path=backup_path,
        applied_status=applied_status,
        skipped_status=skipped_status,
        applied_facilities=applied_facilities,
        skipped_rows=skipped_rows,
    )
    return {
        "backup_path": str(backup_path),
        "audit_output": str(audit_output),
        "applied_status": applied_status,
        "skipped_status": skipped_status,
        "applied_facilities": applied_facilities,
        "skipped_rows": skipped_rows,
    }


def write_audit(
    audit_output,
    dataset_path,
    master_path,
    backup_path,
    applied_status,
    skipped_status,
    applied_facilities,
    skipped_rows,
):
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(item["decision"] for item in applied_status)
    facility_flag_counts = Counter()
    for item in applied_facilities:
        facility_flag_counts.update(item["changed"].keys())

    lines = [
        "# Updated Master Status + Facility Apply - 2026-05-27",
        "",
        f"Generated at: `{now_iso()}`",
        f"Dataset: `{dataset_path}`",
        f"Source master: `{master_path}`",
        f"Backup: `{backup_path}`",
        "",
        "## Summary",
        "",
        f"- Status rows applied: `{len(applied_status)}`",
        f"- Status rows skipped: `{len(skipped_status)}`",
        f"- Facility rows applied: `{len(applied_facilities)}`",
        f"- Missing/invalid rows skipped: `{len(skipped_rows)}`",
        "",
        "## Applied Status Decisions",
        "",
        "| Decision | Count |",
        "| --- | ---: |",
    ]
    for decision, count in status_counts.most_common():
        lines.append(f"| `{decision}` | {count} |")

    lines.extend(["", "## Applied Facility Flags", "", "| Flag | Count |", "| --- | ---: |"])
    for flag, count in facility_flag_counts.most_common():
        lines.append(f"| `{flag}` | {count} |")

    lines.extend(["", "## Skipped Status Rows", "", "| ID | Name | Decision | Reason |", "| --- | --- | --- | --- |"])
    if skipped_status:
        for item in skipped_status:
            lines.append(
                f"| `{item['location_id']}` | {item['location_name']} | `{item['decision']}` | {item['reason']} |"
            )
    else:
        lines.append("| - | - | - | - |")

    lines.extend(["", "## Applied Status Rows", "", "| ID | Name | Decision |", "| --- | --- | --- |"])
    for item in applied_status:
        lines.append(f"| `{item['location_id']}` | {item['location_name']} | `{item['decision']}` |")

    lines.extend(["", "## Applied Facility Rows", "", "| ID | Name | Updated Flags |", "| --- | --- | --- |"])
    for item in applied_facilities:
        flags = ", ".join(f"`{key}={value}`" for key, value in item["changed"].items())
        lines.append(f"| `{item['location_id']}` | {item['location_name']} | {flags} |")

    if skipped_rows:
        lines.extend(["", "## Skipped Rows", "", "| ID | Reason |", "| --- | --- |"])
        for item in skipped_rows:
            lines.append(f"| `{item['location_id']}` | {item['reason']} |")

    audit_output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--master", default=str(DEFAULT_MASTER_PATH))
    parser.add_argument("--audit-output", default=str(DEFAULT_AUDIT_OUTPUT))
    args = parser.parse_args()
    result = apply_updates(args.dataset, args.master, args.audit_output)
    print(f"backup_path={result['backup_path']}")
    print(f"audit_output={result['audit_output']}")
    print(f"applied_status={len(result['applied_status'])}")
    print(f"skipped_status={len(result['skipped_status'])}")
    print(f"applied_facilities={len(result['applied_facilities'])}")
    print(f"skipped_rows={len(result['skipped_rows'])}")


if __name__ == "__main__":
    main()
