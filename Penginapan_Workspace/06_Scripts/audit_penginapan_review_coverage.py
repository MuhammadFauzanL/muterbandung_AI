import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
CURATED_DIR = WORKSPACE / "02_Curated"

DATE_TAG = os.getenv("PENGINAPAN_REVIEW_AUDIT_TAG", "2026-06-10_DRIVE_FULL_REVIEW")
REVIEW_PATH = Path(
    os.getenv(
        "PENGINAPAN_REVIEW_NORMALIZED_PATH",
        str(CURATED_DIR / f"PENGINAPAN_REVIEW_{DATE_TAG}_NORMALIZED.csv"),
    )
)
TARGET_PATH = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_READY_2026-06-05.csv"

PER_TARGET_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_REVIEW_{DATE_TAG}_PER_TARGET_AUDIT.csv"
MISSING_TARGET_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_REVIEW_{DATE_TAG}_MISSING_TARGETS.csv"
SUMMARY_OUTPUT_PATH = CURATED_DIR / f"penginapan_review_{DATE_TAG.lower()}_coverage_summary.json"


def non_empty(series):
    return series.fillna("").astype(str).str.strip().ne("")


def main():
    if not REVIEW_PATH.exists():
        raise FileNotFoundError(REVIEW_PATH)
    if not TARGET_PATH.exists():
        raise FileNotFoundError(TARGET_PATH)

    reviews = pd.read_csv(REVIEW_PATH)
    targets = pd.read_csv(TARGET_PATH)

    for col in ["review_target_id", "penginapan_id"]:
        if col not in reviews.columns:
            reviews[col] = ""
        if col not in targets.columns:
            targets[col] = ""

    reviews["has_text_review"] = non_empty(reviews.get("text", pd.Series("", index=reviews.index))) | non_empty(
        reviews.get("textTranslated", pd.Series("", index=reviews.index))
    )
    reviews["has_review_id"] = non_empty(reviews.get("reviewId", pd.Series("", index=reviews.index)))

    grouped = (
        reviews.groupby("review_target_id", dropna=False)
        .agg(
            scraped_rows=("review_target_id", "size"),
            text_review_rows=("has_text_review", "sum"),
            unique_review_ids=("reviewId", lambda s: int(s.fillna("").astype(str).str.strip().replace("", pd.NA).dropna().nunique())),
            unique_place_titles=("title", lambda s: int(s.fillna("").astype(str).str.strip().replace("", pd.NA).dropna().nunique())),
            sample_place_title=("title", lambda s: next((v for v in s.fillna("").astype(str) if v.strip()), "")),
        )
        .reset_index()
    )

    audit = targets.merge(grouped, on="review_target_id", how="left")
    for col in ["scraped_rows", "text_review_rows", "unique_review_ids", "unique_place_titles"]:
        audit[col] = audit[col].fillna(0).astype(int)
    audit["review_batch_status"] = "missing_from_review_batch"
    audit.loc[audit["scraped_rows"] > 0, "review_batch_status"] = "scraped_star_only"
    audit.loc[audit["text_review_rows"] > 0, "review_batch_status"] = "scraped_with_text"

    audit.to_csv(PER_TARGET_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    missing = audit[audit["review_batch_status"] == "missing_from_review_batch"].copy()
    missing.to_csv(MISSING_TARGET_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    status_counts = audit["review_batch_status"].value_counts().to_dict()
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_path": str(REVIEW_PATH),
        "target_path": str(TARGET_PATH),
        "target_total": int(len(targets)),
        "review_rows": int(len(reviews)),
        "target_with_any_scrape": int((audit["scraped_rows"] > 0).sum()),
        "target_with_text_review": int((audit["text_review_rows"] > 0).sum()),
        "target_missing_from_batch": int((audit["review_batch_status"] == "missing_from_review_batch").sum()),
        "review_batch_status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "outputs": {
            "per_target_audit": str(PER_TARGET_OUTPUT_PATH),
            "missing_targets": str(MISSING_TARGET_OUTPUT_PATH),
        },
        "decision": "Batch diterima untuk sentiment baseline hotel. Target yang belum masuk batch disimpan sebagai next scraping queue.",
    }
    SUMMARY_OUTPUT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
