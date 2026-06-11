from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

READY_INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_READY_2026-06-05.csv"
HELD_CHILD_INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_HELD_CHILD_2026-06-05.csv"
HELD_LOW_PRIORITY_INPUT = CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_58_HELD_LOW_PRIORITY_2026-06-05.csv"
FINAL_29_INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_29_FINAL_DECISION_2026-06-05.csv"

FINAL_READY_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_READY_2026-06-05.csv"
FINAL_EXCLUDED_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_EXCLUDED_2026-06-05.csv"
TEST_BATCH_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_TEST_BATCH_30_2026-06-05.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_review_targets_final_summary_2026-06-05.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def add_exclusion(df: pd.DataFrame, group: str, reason: str) -> pd.DataFrame:
    output = df.copy()
    output["final_target_status"] = "excluded"
    output["final_exclusion_group"] = group
    output["final_exclusion_reason"] = reason
    return output


def add_ready(df: pd.DataFrame, source: str, reason: str) -> pd.DataFrame:
    output = df.copy()
    output["final_target_status"] = "ready"
    output["final_ready_source"] = source
    output["final_ready_reason"] = reason
    return output


def main() -> None:
    ready = pd.read_csv(READY_INPUT, dtype=str, keep_default_na=False)
    held_child = pd.read_csv(HELD_CHILD_INPUT, dtype=str, keep_default_na=False)
    held_low_priority = pd.read_csv(HELD_LOW_PRIORITY_INPUT, dtype=str, keep_default_na=False)
    final_29 = pd.read_csv(FINAL_29_INPUT, dtype=str, keep_default_na=False)

    final_child_parent = final_29[final_29["final_group"].eq("child_parent_relation")].copy()
    final_parent_ready = final_29[final_29["final_group"].eq("parent_ready")].copy()
    final_held_drop = final_29[final_29["final_group"].eq("held_drop")].copy()

    ready_ids = set(ready["review_target_id"])
    parent_ready_ids = set(final_parent_ready["review_target_id"])
    remove_ids = set(final_child_parent["review_target_id"]) | set(final_held_drop["review_target_id"])

    base_ready = ready[~ready["review_target_id"].isin(remove_ids)].copy()
    parent_ready_to_add = final_parent_ready[~final_parent_ready["review_target_id"].isin(set(base_ready["review_target_id"]))].copy()
    final_ready = pd.concat(
        [
            add_ready(base_ready, "initial_ready", "Lolos split awal dan tidak masuk keputusan exclude final."),
            add_ready(parent_ready_to_add, "final_29_parent_ready", "Diterima sebagai parent-ready dari keputusan final 29 data."),
        ],
        ignore_index=True,
    )
    final_ready = final_ready.drop_duplicates(subset=["review_target_id"], keep="first")

    excluded_parts = [
        add_exclusion(held_child, "held_child_detail", "Nama terlihat sebagai kamar/unit/detail listing."),
        add_exclusion(held_low_priority, "held_low_priority", "Data abu-abu tanpa kandidat parent kuat; ditahan dari jalur utama."),
        add_exclusion(final_child_parent, "final_29_child_parent", "Keputusan final 29 data: masuk child-parent, bukan target parent."),
        add_exclusion(final_held_drop, "final_29_held_drop", "Keputusan final 29 data: dikeluarkan dari jalur utama."),
    ]
    final_excluded = pd.concat(excluded_parts, ignore_index=True)
    final_excluded = final_excluded.drop_duplicates(subset=["review_target_id"], keep="last")

    excluded_ids = set(final_excluded["review_target_id"])
    final_ready = final_ready[~final_ready["review_target_id"].isin(excluded_ids)].copy()

    sort_cols = [column for column in ["review_scrape_priority", "property_type", "name"] if column in final_ready.columns]
    if sort_cols:
        final_ready = final_ready.sort_values(sort_cols)
    final_excluded = final_excluded.sort_values(["final_exclusion_group", "property_type", "name"])

    batch_sort_cols = [
        column
        for column in ["review_scrape_priority", "review_confidence_label", "property_type", "name"]
        if column in final_ready.columns
    ]
    test_batch = final_ready.copy()
    if batch_sort_cols:
        test_batch = test_batch.sort_values(batch_sort_cols)
    test_batch = test_batch.head(30).copy()
    test_batch["test_batch_name"] = "prescraping_test_batch_30"

    final_ready.to_csv(FINAL_READY_OUTPUT, index=False)
    final_excluded.to_csv(FINAL_EXCLUDED_OUTPUT, index=False)
    test_batch.to_csv(TEST_BATCH_OUTPUT, index=False)

    ready_id_set = set(final_ready["review_target_id"])
    excluded_id_set = set(final_excluded["review_target_id"])
    overlap_count = len(ready_id_set & excluded_id_set)

    summary = {
        "generated_at": now_iso(),
        "input_rows": {
            "initial_ready": int(len(ready)),
            "held_child": int(len(held_child)),
            "held_low_priority": int(len(held_low_priority)),
            "final_29": int(len(final_29)),
        },
        "decision_rows": {
            "final_29_child_parent": int(len(final_child_parent)),
            "final_29_parent_ready": int(len(final_parent_ready)),
            "final_29_held_drop": int(len(final_held_drop)),
        },
        "final_ready_rows": int(len(final_ready)),
        "final_excluded_rows": int(len(final_excluded)),
        "test_batch_rows": int(len(test_batch)),
        "ready_excluded_overlap_review_target_id_count": int(overlap_count),
        "excluded_group_counts": final_excluded["final_exclusion_group"].value_counts(dropna=False).to_dict(),
        "ready_source_counts": final_ready["final_ready_source"].value_counts(dropna=False).to_dict(),
        "outputs": {
            "final_ready": str(FINAL_READY_OUTPUT),
            "final_excluded": str(FINAL_EXCLUDED_OUTPUT),
            "test_batch": str(TEST_BATCH_OUTPUT),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"initial_ready_rows={summary['input_rows']['initial_ready']}")
    print(f"final_ready_rows={summary['final_ready_rows']}")
    print(f"final_excluded_rows={summary['final_excluded_rows']}")
    print(f"test_batch_rows={summary['test_batch_rows']}")
    print(f"ready_excluded_overlap_review_target_id_count={summary['ready_excluded_overlap_review_target_id_count']}")
    print(f"excluded_group_counts={summary['excluded_group_counts']}")
    print(f"ready_source_counts={summary['ready_source_counts']}")


if __name__ == "__main__":
    main()
