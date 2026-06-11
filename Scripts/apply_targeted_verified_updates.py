import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


CURATED_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
OUTPUT_AUDIT_PATH = Path("Wisata_Workspace/03_Dokumentasi/TARGETED_VERIFIED_UPDATES_2026-05-25.md")

UPDATES = [
    {
        "location_id": "LOC-016",
        "location_name": "Chinatown Bandung",
        "reason": (
            "Multiple public sources mark Chinatown Bandung/Jalan Kelenteng closed or permanently closed; "
            "hide from active recommendations until a reliable reopening source is found."
        ),
        "source_urls": [
            "https://www.exploresunda.com/jalan-Kelenteng-Bandung.html",
            "https://idetrips.com/chinatown-bandung-en/",
            "https://wanderlog.com/place/details/54367",
        ],
        "set": {
            "display_status": "temporarily_hidden",
            "curation_action": "hide_temporarily",
            "is_active_verified": "False",
            "review_status": "needs_review",
        },
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


def apply_updates(dataset_path=CURATED_PATH, audit_path=OUTPUT_AUDIT_PATH):
    dataset_path = Path(dataset_path)
    audit_path = Path(audit_path)
    backup_path = dataset_path.with_name(f"{dataset_path.name}.bak_targeted_{now_stamp()}")
    shutil.copy2(dataset_path, backup_path)

    df = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    applied = []
    skipped = []

    for update in UPDATES:
        location_id = update["location_id"]
        mask = df["location_id"] == location_id
        if int(mask.sum()) != 1:
            skipped.append({
                "location_id": location_id,
                "reason": f"Expected one row, found {int(mask.sum())}.",
            })
            continue

        index = df.index[mask][0]
        before = df.loc[index].to_dict()
        for column, value in update["set"].items():
            if column in df.columns:
                df.at[index, column] = value

        note = (
            f"Targeted verified update 2026-05-25: {update['reason']} "
            f"Sources: {'; '.join(update['source_urls'])}"
        )
        if "curation_note" in df.columns:
            df.at[index, "curation_note"] = append_note(df.at[index, "curation_note"], note)
        if "qa_flag_reason" in df.columns:
            df.at[index, "qa_flag_reason"] = append_note(df.at[index, "qa_flag_reason"], "active_status_hidden_until_reverified")

        after = df.loc[index].to_dict()
        applied.append({
            "location_id": location_id,
            "location_name": update["location_name"],
            "reason": update["reason"],
            "source_urls": update["source_urls"],
            "before": {key: before.get(key) for key in ["display_status", "curation_action", "is_active_verified", "review_status"]},
            "after": {key: after.get(key) for key in ["display_status", "curation_action", "is_active_verified", "review_status"]},
        })

    if applied:
        df.to_csv(dataset_path, index=False)

    write_audit(audit_path, backup_path, applied, skipped)
    return {
        "backup_path": str(backup_path),
        "applied": applied,
        "skipped": skipped,
        "audit_path": str(audit_path),
    }


def write_audit(audit_path, backup_path, applied, skipped):
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Targeted Verified Updates - 2026-05-25",
        "",
        f"Generated at: `{now_iso()}`",
        f"Backup: `{backup_path}`",
        "",
        "## Applied Updates",
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
                f"Reason: {item['reason']}",
                "",
                "Sources:",
            ])
            for source in item["source_urls"]:
                lines.append(f"- {source}")
            lines.extend([
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
        "## Skipped Updates",
        "",
    ])
    if not skipped:
        lines.append("No updates skipped.")
        lines.append("")
    else:
        for item in skipped:
            lines.append(f"- `{item['location_id']}`: {item['reason']}")
        lines.append("")

    audit_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply evidence-backed targeted dataset updates.")
    parser.add_argument("--dataset", default=str(CURATED_PATH))
    parser.add_argument("--audit-output", default=str(OUTPUT_AUDIT_PATH))
    args = parser.parse_args(argv)

    result = apply_updates(Path(args.dataset), Path(args.audit_output))
    print("MuterBandung Targeted Verified Updates")
    print("=" * 42)
    print(f"Applied: {len(result['applied'])}")
    print(f"Skipped: {len(result['skipped'])}")
    print(f"Backup: {result['backup_path']}")
    print(f"Audit: {result['audit_path']}")
    return 0 if not result["skipped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
