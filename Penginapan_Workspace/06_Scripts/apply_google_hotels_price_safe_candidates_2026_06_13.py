import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
DATE_TAG = "2026-06-13"

PRIMARY_INPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_REVIEW_COMPLETED_2026-06-13.csv"
SAFE_CANDIDATE_INPUT = CURATED_DIR / "PENGINAPAN_GOOGLE_HOTELS_PRICE_SAFE_FILL_CANDIDATES_2026-06-13.csv"

PRIMARY_OUTPUT = CURATED_DIR / f"PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_PRICE_COMPLETED_{DATE_TAG}.csv"
QUEUE_OUTPUT = CURATED_DIR / f"PENGINAPAN_PRIMARY_DATA_COMPLETION_QUEUE_ORDERED_PRICE_COMPLETED_{DATE_TAG}.csv"
P1_PRICE_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_AFTER_PRICE_APPLY_P1_PRICE_MISSING_{DATE_TAG}.csv"
P1_CORE_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_AFTER_PRICE_APPLY_P1_CORE_RATING_PRICE_MISSING_{DATE_TAG}.csv"
P1_RATING_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_AFTER_PRICE_APPLY_P1_RATING_REVIEWS_MISSING_{DATE_TAG}.csv"
P2_SENTIMENT_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_AFTER_PRICE_APPLY_P2_SENTIMENT_MISSING_{DATE_TAG}.csv"
APPLIED_AUDIT_OUTPUT = CURATED_DIR / f"PENGINAPAN_GOOGLE_HOTELS_PRICE_APPLIED_AUDIT_{DATE_TAG}.csv"
SUMMARY_OUTPUT = CURATED_DIR / f"penginapan_google_hotels_price_apply_summary_{DATE_TAG}.json"


def clean_text(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_text(value):
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def coerce_float(value):
    try:
        if value in ("", None):
            return None
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def is_missing_number(value):
    return coerce_float(value) is None


def is_missing_text(value):
    return normalize_text(value) in {"", "nan", "none", "null"}


def recompute_completion(row):
    missing_rating_reviews = is_missing_number(row.get("overall_rating")) or is_missing_number(row.get("reviews"))
    missing_price = is_missing_number(row.get("price_lowest"))
    missing_sentiment = is_missing_number(row.get("hotel_adjusted_sentiment_score")) or int(
        coerce_float(row.get("hotel_review_count_analyzed")) or 0
    ) <= 0
    missing_source = is_missing_text(row.get("link"))
    missing_amenities = is_missing_text(row.get("amenities"))
    missing_image = is_missing_text(row.get("primary_image_url"))

    flags = []
    if missing_rating_reviews:
        flags.append("missing_rating_reviews")
    if missing_price:
        flags.append("missing_price")
    if missing_sentiment:
        flags.append("missing_sentiment")
    if missing_source:
        flags.append("missing_source_link")
    if missing_amenities:
        flags.append("missing_amenities")
    if missing_image:
        flags.append("missing_image")

    if missing_rating_reviews and missing_price:
        priority = "P1_core_rating_price_missing"
        route = "scrape_place_rating_reviews_and_price"
        order = 2
    elif missing_price:
        priority = "P1_price_missing"
        route = "scrape_or_manual_price"
        order = 1
    elif missing_rating_reviews:
        priority = "P1_rating_reviews_missing"
        route = "scrape_place_rating_reviews"
        order = 3
    elif missing_sentiment:
        priority = "P2_sentiment_missing"
        route = "scrape_reviews_for_sentiment"
        order = 4
    elif missing_amenities or missing_image:
        priority = "P3_content_missing"
        route = "complete_amenities_or_image"
        order = 5
    elif missing_source:
        priority = "P3_source_link_missing"
        route = "fill_source_link_when_available"
        order = 6
    else:
        priority = "OK_complete_enough"
        route = "ready_for_baseline"
        order = 99

    score = 6 - sum(
        [
            missing_rating_reviews,
            missing_price,
            missing_sentiment,
            missing_source,
            missing_amenities,
            missing_image,
        ]
    )
    return pd.Series(
        {
            "completion_priority_order": order,
            "completion_priority_data_focus": priority,
            "completion_flags_data_focus": "|".join(flags),
            "completion_route_data_focus": route,
            "completion_score_data_focus": score,
        }
    )


def count_flags(df):
    flags = df["completion_flags_data_focus"].fillna("").astype(str)
    return {
        "missing_price": int(flags.str.contains("missing_price").sum()),
        "missing_rating_reviews": int(flags.str.contains("missing_rating_reviews").sum()),
        "missing_sentiment": int(flags.str.contains("missing_sentiment").sum()),
        "missing_source_link": int(flags.str.contains("missing_source_link").sum()),
        "missing_amenities": int(flags.str.contains("missing_amenities").sum()),
        "missing_image": int(flags.str.contains("missing_image").sum()),
    }


def export_queues(updated):
    queue = updated[updated["completion_priority_data_focus"].ne("OK_complete_enough")].copy()
    queue = queue.sort_values(
        ["completion_priority_order", "property_type_final_after_p3", "data_quality_score", "reviews", "name"],
        ascending=[True, True, False, False, True],
    )
    queue.to_csv(QUEUE_OUTPUT, index=False, encoding="utf-8-sig")
    queue[queue["completion_priority_data_focus"].eq("P1_price_missing")].to_csv(
        P1_PRICE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    queue[queue["completion_priority_data_focus"].eq("P1_core_rating_price_missing")].to_csv(
        P1_CORE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    queue[queue["completion_priority_data_focus"].eq("P1_rating_reviews_missing")].to_csv(
        P1_RATING_OUTPUT, index=False, encoding="utf-8-sig"
    )
    queue[queue["completion_priority_data_focus"].eq("P2_sentiment_missing")].to_csv(
        P2_SENTIMENT_OUTPUT, index=False, encoding="utf-8-sig"
    )
    return queue


def main():
    primary = pd.read_csv(PRIMARY_INPUT)
    candidates = pd.read_csv(SAFE_CANDIDATE_INPUT)

    before_priority_counts = primary["completion_priority_data_focus"].value_counts(dropna=False).to_dict()
    before_flag_counts = count_flags(primary)

    updated = primary.copy()
    updated["google_hotels_price_apply_status"] = ""
    updated["google_hotels_price_apply_note"] = ""
    updated["google_hotels_price_source_query"] = ""
    updated["google_hotels_price_source_file"] = ""
    updated["google_hotels_price_property_token"] = ""

    applied_rows = []
    candidate_map = candidates.set_index("penginapan_id").to_dict("index")
    for idx, row in updated.iterrows():
        penginapan_id = row["penginapan_id"]
        if penginapan_id not in candidate_map:
            continue
        candidate = candidate_map[penginapan_id]
        notes = []
        price_filled = False
        rating_filled = False

        if is_missing_number(row.get("price_lowest")) and not is_missing_number(candidate.get("scrape_price_lowest")):
            updated.at[idx, "price_lowest"] = candidate.get("scrape_price_lowest")
            updated.at[idx, "price_display"] = candidate.get("scrape_price_display")
            price_filled = True
            notes.append("price_lowest diisi dari Google Hotels safe candidate")

        if is_missing_number(row.get("overall_rating")) and not is_missing_number(candidate.get("scrape_overall_rating")):
            updated.at[idx, "overall_rating"] = candidate.get("scrape_overall_rating")
            rating_filled = True
            notes.append("overall_rating diisi dari Google Hotels safe candidate")

        if is_missing_number(row.get("reviews")) and not is_missing_number(candidate.get("scrape_reviews")):
            updated.at[idx, "reviews"] = candidate.get("scrape_reviews")
            rating_filled = True
            notes.append("reviews diisi dari Google Hotels safe candidate")

        if not price_filled and not rating_filled:
            continue

        updated.at[idx, "google_hotels_price_apply_status"] = (
            "applied_price_and_rating_reviews"
            if price_filled and rating_filled
            else ("applied_price" if price_filled else "applied_rating_reviews")
        )
        updated.at[idx, "google_hotels_price_apply_note"] = "; ".join(notes)
        updated.at[idx, "google_hotels_price_source_query"] = candidate.get("query", "")
        updated.at[idx, "google_hotels_price_source_file"] = candidate.get("source_file", "")
        updated.at[idx, "google_hotels_price_property_token"] = candidate.get("property_token", "")

        applied_rows.append(
            {
                "penginapan_id": penginapan_id,
                "name": row["name"],
                "apply_status": updated.at[idx, "google_hotels_price_apply_status"],
                "price_before": row.get("price_lowest"),
                "price_after": updated.at[idx, "price_lowest"],
                "rating_before": row.get("overall_rating"),
                "rating_after": updated.at[idx, "overall_rating"],
                "reviews_before": row.get("reviews"),
                "reviews_after": updated.at[idx, "reviews"],
                "source_query": candidate.get("query", ""),
                "source_file": candidate.get("source_file", ""),
                "property_token": candidate.get("property_token", ""),
                "distance_km": candidate.get("distance_km"),
                "audit_note": candidate.get("audit_note", ""),
            }
        )

    completion = updated.apply(recompute_completion, axis=1)
    for col in completion.columns:
        updated[col] = completion[col]

    applied = pd.DataFrame(applied_rows)
    updated.to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    applied.to_csv(APPLIED_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    queue = export_queues(updated)

    after_priority_counts = updated["completion_priority_data_focus"].value_counts(dropna=False).to_dict()
    after_flag_counts = count_flags(updated)
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_primary": str(PRIMARY_INPUT.relative_to(ROOT)),
        "safe_candidate_input": str(SAFE_CANDIDATE_INPUT.relative_to(ROOT)),
        "primary_rows": int(len(primary)),
        "safe_candidate_rows": int(len(candidates)),
        "applied_rows": int(len(applied)),
        "applied_status_counts": applied["apply_status"].value_counts().to_dict() if not applied.empty else {},
        "before_priority_counts": before_priority_counts,
        "after_priority_counts": after_priority_counts,
        "before_flag_counts": before_flag_counts,
        "after_flag_counts": after_flag_counts,
        "price_missing_reduced_by": int(before_flag_counts["missing_price"] - after_flag_counts["missing_price"]),
        "rating_reviews_missing_reduced_by": int(
            before_flag_counts["missing_rating_reviews"] - after_flag_counts["missing_rating_reviews"]
        ),
        "remaining_queue_count": int(len(queue)),
        "remaining_p1_p2_queue_count": int(
            updated["completion_priority_data_focus"].isin(
                [
                    "P1_price_missing",
                    "P1_core_rating_price_missing",
                    "P1_rating_reviews_missing",
                    "P2_sentiment_missing",
                ]
            ).sum()
        ),
        "outputs": {
            "primary_price_completed": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "completion_queue_price_completed": str(QUEUE_OUTPUT.relative_to(ROOT)),
            "applied_audit": str(APPLIED_AUDIT_OUTPUT.relative_to(ROOT)),
            "remaining_p1_price": str(P1_PRICE_OUTPUT.relative_to(ROOT)),
            "remaining_p1_core": str(P1_CORE_OUTPUT.relative_to(ROOT)),
            "remaining_p1_rating": str(P1_RATING_OUTPUT.relative_to(ROOT)),
            "remaining_p2_sentiment": str(P2_SENTIMENT_OUTPUT.relative_to(ROOT)),
        },
        "decision_notes": [
            "Hanya safe candidates dari audit Google Hotels yang di-apply.",
            "Field diisi hanya jika field utama masih kosong.",
            "Master lama tidak ditimpa; output dibuat sebagai candidate baru.",
        ],
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
