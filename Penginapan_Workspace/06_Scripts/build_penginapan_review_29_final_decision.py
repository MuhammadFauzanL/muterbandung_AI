from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
PACK_DIR = ROOT / "Penginapan_Workspace" / "04_Dokumentasi" / "CLAUDE_AGENT_REVIEW_29_2026-06-05"

INPUT = PACK_DIR / "PENGINAPAN_CLAUDE_REVIEW_29_PARENT_CHILD_DECISION_2026-06-05.csv"
OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_29_FINAL_DECISION_2026-06-05.csv"
CHILD_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_29_FINAL_CHILD_PARENT_2026-06-05.csv"
PARENT_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_29_FINAL_PARENT_READY_2026-06-05.csv"
HELD_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_29_FINAL_HELD_DROP_2026-06-05.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_review_29_final_decision_summary_2026-06-05.json"


ACCEPT_AS_CHILD = {
    "PHREV-20260605-1248",
    "PHREV-20260605-0598",
    "PHREV-20260605-1086",
    "PHREV-20260605-1131",
    "PHREV-20260605-0531",
    "PHREV-20260605-1216",
    "PHREV-20260605-1234",
    "PHREV-20260605-1356",
    "PHREV-20260605-1426",
    "PHREV-20260605-1456",
    "PHREV-20260605-1459",
    "PHREV-20260605-0414",
    "PHREV-20260605-1364",
    "PHREV-20260605-1365",
    "PHREV-20260605-1163",
    "PHREV-20260605-0594",
    "PHREV-20260605-0589",
    "PHREV-20260605-0993",
    "PHREV-20260605-1496",
}

ACCEPT_AS_PARENT = {
    "PHREV-20260605-0539",
    "PHREV-20260605-0640",
    "PHREV-20260605-1420",
    "PHREV-20260605-1158",
    "PHREV-20260605-1159",
    "PHREV-20260605-0514",
    "PHREV-20260605-0435",
    "PHREV-20260605-0505",
    "PHREV-20260605-0573",
}

DROP_FROM_MAIN_FLOW = {
    "PHREV-20260605-1361",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def decide(row: pd.Series) -> tuple[str, str, str]:
    review_target_id = row["review_target_id"]
    if review_target_id in ACCEPT_AS_CHILD:
        return (
            "accept_as_child",
            "child_parent_relation",
            "Diterima sebagai child/detail dari parent kandidat.",
        )
    if review_target_id in ACCEPT_AS_PARENT:
        if review_target_id == "PHREV-20260605-0539":
            return (
                "accept_as_parent",
                "parent_ready",
                "Keputusan manual: Clamitan House dan Clamitan Villas 2 adalah tempat berbeda.",
            )
        return (
            "accept_as_parent",
            "parent_ready",
            "Diterima sebagai properti mandiri untuk target scraping review.",
        )
    if review_target_id in DROP_FROM_MAIN_FLOW:
        return (
            "drop_from_main_flow",
            "held_drop",
            "Keputusan manual: dikeluarkan dari jalur utama karena kurang layak dipakai.",
        )
    return (
        "needs_more_check",
        "needs_more_check",
        "Belum ada keputusan final.",
    )


def write_csv(df: pd.DataFrame, path: Path) -> None:
    sort_cols = [column for column in ["final_group", "property_type", "name"] if column in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)
    df.to_csv(path, index=False)


def main() -> None:
    review_29 = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    decisions = review_29.apply(decide, axis=1)
    review_29["final_decision"] = [item[0] for item in decisions]
    review_29["final_group"] = [item[1] for item in decisions]
    review_29["final_reason"] = [item[2] for item in decisions]
    review_29["final_decision_source"] = "claude_review_plus_user_decision"

    child_parent = review_29[review_29["final_group"].eq("child_parent_relation")].copy()
    parent_ready = review_29[review_29["final_group"].eq("parent_ready")].copy()
    held_drop = review_29[review_29["final_group"].eq("held_drop")].copy()
    needs_more_check = review_29[review_29["final_group"].eq("needs_more_check")].copy()

    write_csv(review_29, OUTPUT)
    write_csv(child_parent, CHILD_OUTPUT)
    write_csv(parent_ready, PARENT_OUTPUT)
    write_csv(held_drop, HELD_OUTPUT)

    summary = {
        "generated_at": now_iso(),
        "input_path": str(INPUT),
        "final_decision_path": str(OUTPUT),
        "total_rows": int(len(review_29)),
        "child_parent_rows": int(len(child_parent)),
        "parent_ready_rows": int(len(parent_ready)),
        "held_drop_rows": int(len(held_drop)),
        "needs_more_check_rows": int(len(needs_more_check)),
        "final_group_counts": review_29["final_group"].value_counts(dropna=False).to_dict(),
        "outputs": {
            "final_decision": str(OUTPUT),
            "child_parent": str(CHILD_OUTPUT),
            "parent_ready": str(PARENT_OUTPUT),
            "held_drop": str(HELD_OUTPUT),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"total_rows={summary['total_rows']}")
    print(f"child_parent_rows={summary['child_parent_rows']}")
    print(f"parent_ready_rows={summary['parent_ready_rows']}")
    print(f"held_drop_rows={summary['held_drop_rows']}")
    print(f"needs_more_check_rows={summary['needs_more_check_rows']}")
    print(f"output={OUTPUT}")


if __name__ == "__main__":
    main()
