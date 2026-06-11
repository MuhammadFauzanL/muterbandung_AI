import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DEFAULT_DATASET_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
DEFAULT_AUDIT_OUTPUT = Path("Wisata_Workspace/03_Dokumentasi/MANUAL_REVIEW_DOCX_REVIEWER_OVERRIDES_2026-05-26.md")

OVERRIDES = [
    {
        "location_id": "LOC-123",
        "location_name": "Museum Pendidikan Nasional UPI",
        "reason": "Reviewer states the destination is still active and provided a weekly hours table in the DOCX.",
        "sources": ["manual_reviewer_docx_2026-05-26"],
        "set": {
            "is_active_verified": "True",
            "review_status": "reviewed",
            "jam_buka_weekday": "08:00",
            "jam_tutup_weekday": "15:00",
            "jam_buka_weekend": "Tutup",
            "jam_tutup_weekend": "Tutup",
        },
        "note": (
            "Manual reviewer override 2026-05-26: active; weekday hours summarized as 08:00-15:00. "
            "DOCX table notes Mon-Thu 08:00-11:30, 13:00-15:00; Fri 08:00-11:00, 13:00-15:30; Sat-Sun closed."
        ),
        "qa_marker": "manual_docx_override:active_status:opening_hours",
    },
    {
        "location_id": "LOC-155",
        "location_name": "Curug Panganten",
        "reason": "Reviewer allowed applying the source that says the place opens tomorrow 07:00-16:00, plus location-specific Travelspromo media/facility text.",
        "sources": [
            "https://id.trip.com/travel-guide/attraction/cisarua/curug-panganten-cimahi-137230763/",
            "https://travelspromo.com/htm-wisata/curug-panganten-bandung-barat/",
        ],
        "set": {
            "is_active_verified": "True",
            "review_status": "reviewed",
            "jam_buka_weekday": "07:00",
            "jam_tutup_weekday": "16:00",
            "jam_buka_weekend": "07:00",
            "jam_tutup_weekend": "16:00",
            "parking_verified": "True",
            "media_available": "True",
            "media_image_url": "https://travelspromo.com/wp-content/uploads/2021/09/Air-terjun-yang-diselimuti-mitos-dan-misteri-Asrie-Kuswara-1536x1152.jpg",
            "media_source": "manual_review_docx",
            "media_audit_status": "accepted",
        },
        "note": (
            "Manual reviewer override 2026-05-26: active/opening hours 07:00-16:00 from Trip.com field; "
            "Travelspromo text notes area parkir, gazebo, and warung, but no toilet/mushola/ruang ganti."
        ),
        "qa_marker": "manual_docx_override:active_status:opening_hours:parking:media",
    },
    {
        "location_id": "LOC-158",
        "location_name": "Situ Ninah (Situ Datar)",
        "reason": "Reviewer provided Instagram source with explicit weekday/weekend hours and facility text.",
        "sources": [
            "https://www.instagram.com/situdatarbuana/",
        ],
        "set": {
            "jam_buka_weekday": "09:00",
            "jam_tutup_weekday": "16:00",
            "jam_buka_weekend": "09:00",
            "jam_tutup_weekend": "17:00",
            "parking_verified": "True",
            "toilet_verified": "True",
            "mushola_verified": "True",
        },
        "note": (
            "Manual reviewer override 2026-05-26: tourism hours weekday 09:00-16:00 and weekend 09:00-17:00; "
            "camping appears 24h/reservation-only, so open_24h_verified is not set. Facility text mentions parking, toilet, and musola."
        ),
        "qa_marker": "manual_docx_override:opening_hours:facility",
    },
    {
        "location_id": "LOC-162",
        "location_name": "Rumah Putih Cukul",
        "reason": "Reviewer explicitly confirms Google Maps still shows active and recent reviews.",
        "sources": ["manual_reviewer_google_maps_observation_2026-05-26"],
        "set": {
            "is_active_verified": "True",
            "review_status": "reviewed",
            "jam_buka_weekday": "08:00",
            "jam_tutup_weekday": "18:00",
            "jam_buka_weekend": "08:00",
            "jam_tutup_weekend": "18:00",
        },
        "note": (
            "Manual reviewer override 2026-05-26: reviewer observed Google Maps active status and recent reviews. "
            "DOCX text states operating hours 08:00-18:00 daily."
        ),
        "qa_marker": "manual_docx_override:active_status:opening_hours",
    },
    {
        "location_id": "LOC-134",
        "location_name": "Bukit Bintang Bandung (Patahan Lembang)",
        "reason": "Reviewer notes active status and Google Maps name Puncak Bintang; hours and facility text are clear enough for core fields.",
        "sources": ["manual_reviewer_google_maps_observation_2026-05-26"],
        "set": {
            "is_active_verified": "True",
            "review_status": "reviewed",
            "jam_buka_weekday": "06:00",
            "jam_tutup_weekday": "17:00",
            "jam_buka_weekend": "06:00",
            "jam_tutup_weekend": "17:00",
            "parking_verified": "True",
            "toilet_verified": "True",
            "mushola_verified": "True",
        },
        "note": (
            "Manual reviewer override 2026-05-26: active; Google Maps name observed as Puncak Bintang. "
            "Do not rename primary location_name yet; retain alias in curation_note. Facility text mentions parkir, toilet, and mushola."
        ),
        "qa_marker": "manual_docx_override:active_status:opening_hours:facility:alias",
    },
    {
        "location_id": "LOC-174",
        "location_name": "Lereng Anteng Panoramic Coffee",
        "reason": "Reviewer-provided text confirms active cafe context; existing hours already match the extracted weekday/weekend pattern.",
        "sources": ["manual_reviewer_docx_2026-05-26"],
        "set": {
            "is_active_verified": "True",
            "review_status": "reviewed",
        },
        "note": (
            "Manual reviewer override 2026-05-26: active cafe context confirmed in DOCX. Existing hours retained: weekday 08:00-22:00, weekend 08:00-23:00."
        ),
        "qa_marker": "manual_docx_override:active_status",
    },
    {
        "location_id": "LOC-220",
        "location_name": "Nimo Jungle Hot Spring",
        "reason": "Reviewer-provided ticket/hour text indicates active ticketing and a repeated 08:00-20:00 daily schedule.",
        "sources": [
            "https://nagantour.com/nimo-jungle-hot-spring/",
            "manual_reviewer_docx_2026-05-26",
        ],
        "set": {
            "is_active_verified": "True",
            "review_status": "reviewed",
            "jam_buka_weekday": "08:00",
            "jam_tutup_weekday": "20:00",
            "jam_buka_weekend": "08:00",
            "jam_tutup_weekend": "20:00",
        },
        "note": "Manual reviewer override 2026-05-26: active ticketing context and hours normalized to 08:00-20:00 daily from DOCX text.",
        "qa_marker": "manual_docx_override:active_status:opening_hours",
    },
    {
        "location_id": "LOC-228",
        "location_name": "Tanjung Duriat",
        "reason": "Reviewer explicitly requests removal because it is in Jatigede and outside Bandung Raya scope.",
        "sources": ["manual_reviewer_scope_decision_2026-05-26"],
        "set": {
            "display_status": "exclude_scope",
            "curation_action": "remove",
            "is_active_verified": "False",
            "review_status": "reviewed",
        },
        "note": "Manual reviewer override 2026-05-26: removed from active recommendation scope because located in Jatigede, outside Bandung Raya.",
        "qa_marker": "manual_docx_override:exclude_scope",
    },
]


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


def apply_overrides(dataset_path=DEFAULT_DATASET_PATH, audit_output=DEFAULT_AUDIT_OUTPUT):
    dataset_path = Path(dataset_path)
    audit_output = Path(audit_output)
    backup_path = dataset_path.with_name(f"{dataset_path.name}.bak_manual_docx_override_{now_stamp()}")
    shutil.copy2(dataset_path, backup_path)

    df = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    applied = []
    skipped = []

    for override in OVERRIDES:
        location_id = override["location_id"]
        mask = df["location_id"] == location_id
        if int(mask.sum()) != 1:
            skipped.append({
                "location_id": location_id,
                "location_name": override["location_name"],
                "reason": f"Expected one row, found {int(mask.sum())}.",
            })
            continue

        index = df.index[mask][0]
        before = df.loc[index].to_dict()
        set_values = override["set"]
        for column, value in set_values.items():
            if column in df.columns:
                df.at[index, column] = value

        note = f"{override['note']} Sources: {'; '.join(override['sources'])}"
        if "curation_note" in df.columns:
            df.at[index, "curation_note"] = append_note(df.at[index, "curation_note"], note)
        if "qa_flag_reason" in df.columns:
            df.at[index, "qa_flag_reason"] = append_note(df.at[index, "qa_flag_reason"], override["qa_marker"])
        if "media_audit_note" in df.columns and any(key.startswith("media_") for key in set_values):
            df.at[index, "media_audit_note"] = append_note(df.at[index, "media_audit_note"], note)

        after = df.loc[index].to_dict()
        tracked_keys = sorted(set(set_values) | {"curation_note", "qa_flag_reason"})
        applied.append({
            "location_id": location_id,
            "location_name": override["location_name"],
            "reason": override["reason"],
            "sources": override["sources"],
            "updates": set_values,
            "before": {key: before.get(key) for key in tracked_keys},
            "after": {key: after.get(key) for key in tracked_keys},
        })

    if applied:
        df.to_csv(dataset_path, index=False)

    write_audit(audit_output, dataset_path, backup_path, applied, skipped)
    return {
        "backup_path": str(backup_path),
        "audit_output": str(audit_output),
        "applied": applied,
        "skipped": skipped,
    }


def write_audit(audit_output, dataset_path, backup_path, applied, skipped):
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Manual Review DOCX Reviewer Overrides - 2026-05-26",
        "",
        f"Generated at: `{now_iso()}`",
        f"Dataset: `{dataset_path}`",
        f"Backup: `{backup_path}`",
        "",
        "## Applied Overrides",
        "",
    ]
    if not applied:
        lines.append("No overrides applied.")
        lines.append("")
    else:
        for item in applied:
            lines.extend([
                f"### {item['location_id']} - {item['location_name']}",
                "",
                f"Reason: {item['reason']}",
                "",
                "Sources / basis:",
            ])
            for source in item["sources"]:
                lines.append(f"- {source}")
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

    lines.extend(["## Skipped", ""])
    if not skipped:
        lines.append("No overrides skipped.")
        lines.append("")
    else:
        for item in skipped:
            lines.append(f"- `{item['location_id']}` {item['location_name']}: {item['reason']}")
        lines.append("")

    lines.extend([
        "## Guardrail",
        "",
        "These are explicit reviewer overrides requested after the first strict validation pass. They are marked in `curation_note` and `qa_flag_reason` so future audits can distinguish reviewer-observed facts from URL-verified facts.",
    ])
    audit_output.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply explicit reviewer overrides from the filled manual DOCX.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--audit-output", default=str(DEFAULT_AUDIT_OUTPUT))
    args = parser.parse_args(argv)

    result = apply_overrides(Path(args.dataset), Path(args.audit_output))
    print("MuterBandung Manual Review DOCX Reviewer Overrides")
    print("=" * 56)
    print(f"Applied: {len(result['applied'])}")
    print(f"Skipped: {len(result['skipped'])}")
    print(f"Backup: {result['backup_path']}")
    print(f"Audit: {result['audit_output']}")
    return 0 if not result["skipped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
