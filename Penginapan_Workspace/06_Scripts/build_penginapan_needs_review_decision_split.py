from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_NEEDS_REVIEW_AUDIT_2026-06-05.csv"
CHILD_PARENT_OUTPUT = CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_20_CHILD_PARENT_CANDIDATE_2026-06-05.csv"
MANUAL_CHECK_OUTPUT = CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_9_MANUAL_CHECK_2026-06-05.csv"
HELD_LOW_PRIORITY_OUTPUT = CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_58_HELD_LOW_PRIORITY_2026-06-05.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_needs_review_decision_split_summary_2026-06-05.json"


DECISION_MAP = {
    "candidate_child_to_parent": {
        "decision_group": "child_parent_candidate",
        "decision_status": "prepare_child_parent_relation",
        "decision_reason": "Kandidat parent cukup kuat dari nama dan koordinat.",
    },
    "needs_manual_check": {
        "decision_group": "manual_check",
        "decision_status": "wait_manual_review",
        "decision_reason": "Ada indikasi kandidat, tetapi belum cukup aman untuk diputuskan otomatis.",
    },
    "candidate_standalone_or_unclear": {
        "decision_group": "held_low_priority",
        "decision_status": "soft_remove_from_main_flow",
        "decision_reason": "Belum ada kandidat parent kuat; ditahan agar tidak memperbesar scraping.",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def apply_decision(row: pd.Series, key: str) -> str:
    return DECISION_MAP.get(row.get("audit_recommendation", ""), {}).get(key, "")


def add_decision_columns(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()
    output["decision_group"] = output.apply(lambda row: apply_decision(row, "decision_group"), axis=1)
    output["decision_status"] = output.apply(lambda row: apply_decision(row, "decision_status"), axis=1)
    output["decision_reason"] = output.apply(lambda row: apply_decision(row, "decision_reason"), axis=1)
    if "manual_decision" not in output.columns:
        output["manual_decision"] = ""
    if "manual_note" not in output.columns:
        output["manual_note"] = ""
    return output


def write_sorted(df: pd.DataFrame, path: Path) -> None:
    sort_columns = [
        column
        for column in [
            "audit_recommendation",
            "parent_candidate_score",
            "property_type",
            "name",
        ]
        if column in df.columns
    ]
    if sort_columns:
        df = df.sort_values(sort_columns, ascending=[True, False, True, True][: len(sort_columns)])
    df.to_csv(path, index=False)


def main() -> None:
    needs_review = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    needs_review = add_decision_columns(needs_review)

    child_parent = needs_review[needs_review["audit_recommendation"].eq("candidate_child_to_parent")].copy()
    manual_check = needs_review[needs_review["audit_recommendation"].eq("needs_manual_check")].copy()
    held_low_priority = needs_review[
        needs_review["audit_recommendation"].eq("candidate_standalone_or_unclear")
    ].copy()

    write_sorted(child_parent, CHILD_PARENT_OUTPUT)
    write_sorted(manual_check, MANUAL_CHECK_OUTPUT)
    write_sorted(held_low_priority, HELD_LOW_PRIORITY_OUTPUT)

    split_ids = {
        "child_parent_candidate": set(child_parent["review_target_id"]),
        "manual_check": set(manual_check["review_target_id"]),
        "held_low_priority": set(held_low_priority["review_target_id"]),
    }
    overlap_count = 0
    keys = list(split_ids)
    for index, left in enumerate(keys):
        for right in keys[index + 1 :]:
            overlap_count += len(split_ids[left] & split_ids[right])

    summary = {
        "generated_at": now_iso(),
        "input_path": str(INPUT),
        "total_needs_review_rows": int(len(needs_review)),
        "child_parent_candidate_rows": int(len(child_parent)),
        "manual_check_rows": int(len(manual_check)),
        "held_low_priority_rows": int(len(held_low_priority)),
        "split_total_rows": int(len(child_parent) + len(manual_check) + len(held_low_priority)),
        "overlap_review_target_id_count": int(overlap_count),
        "outputs": {
            "child_parent_candidate": str(CHILD_PARENT_OUTPUT),
            "manual_check": str(MANUAL_CHECK_OUTPUT),
            "held_low_priority": str(HELD_LOW_PRIORITY_OUTPUT),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"total_needs_review_rows={summary['total_needs_review_rows']}")
    print(f"child_parent_candidate_rows={summary['child_parent_candidate_rows']}")
    print(f"manual_check_rows={summary['manual_check_rows']}")
    print(f"held_low_priority_rows={summary['held_low_priority_rows']}")
    print(f"split_total_rows={summary['split_total_rows']}")
    print(f"overlap_review_target_id_count={summary['overlap_review_target_id_count']}")


if __name__ == "__main__":
    main()
