import json
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

PRIMARY_INPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_PRICE_COMPLETED_2026-06-13.csv"
QUEUE_INPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_COMPLETION_QUEUE_ORDERED_PRICE_COMPLETED_2026-06-13.csv"
CANDIDATE_INPUT = CURATED_DIR / "PENGINAPAN_GOOGLE_PLACES_RATING_REVIEWS_PRIORITY27_BEST_CANDIDATES_V2_2026-06-13.csv"

PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_PLACES_RATING_COMPLETED_2026-06-13.csv"
QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_COMPLETION_QUEUE_ORDERED_PLACES_RATING_COMPLETED_2026-06-13.csv"
P1_PRICE_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_REMAINING_AFTER_PLACES_RATING_APPLY_P1_PRICE_MISSING_2026-06-13.csv"
P1_CORE_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_REMAINING_AFTER_PLACES_RATING_APPLY_P1_CORE_RATING_PRICE_MISSING_2026-06-13.csv"
P1_RATING_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_REMAINING_AFTER_PLACES_RATING_APPLY_P1_RATING_REVIEWS_MISSING_2026-06-13.csv"
P2_SENTIMENT_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_REMAINING_AFTER_PLACES_RATING_APPLY_P2_SENTIMENT_MISSING_2026-06-13.csv"
APPLY_AUDIT_OUTPUT = CURATED_DIR / "PENGINAPAN_GOOGLE_PLACES_RATING_REVIEWS_SAFE_APPLIED_AUDIT_2026-06-13.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_google_places_rating_reviews_safe_apply_summary_2026-06-13.json"


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


def apply_safe_candidates(df, safe_candidates):
    updated = df.copy()
    audit_rows = []

    for _, candidate in safe_candidates.iterrows():
        penginapan_id = candidate["penginapan_id"]
        mask = updated["penginapan_id"].astype(str).eq(str(penginapan_id))
        if not mask.any():
            audit_rows.append(
                {
                    "penginapan_id": penginapan_id,
                    "target_name": candidate.get("target_name"),
                    "apply_status": "not_found_in_dataset",
                    "rating_filled": False,
                    "reviews_filled": False,
                    "link_filled": False,
                    "note": "ID kandidat tidak ditemukan di dataset input.",
                }
            )
            continue

        idx = updated.index[mask][0]
        rating_filled = False
        reviews_filled = False
        link_filled = False

        if "overall_rating" in updated.columns and is_missing_number(updated.at[idx, "overall_rating"]):
            updated.at[idx, "overall_rating"] = candidate["totalScore"]
            rating_filled = True

        if "reviews" in updated.columns and is_missing_number(updated.at[idx, "reviews"]):
            updated.at[idx, "reviews"] = candidate["reviewsCount"]
            reviews_filled = True

        if "link" in updated.columns and is_missing_text(updated.at[idx, "link"]) and not is_missing_text(candidate.get("url")):
            updated.at[idx, "link"] = candidate["url"]
            link_filled = True

        updated.at[idx, "google_places_rating_apply_status"] = "safe_applied"
        updated.at[idx, "google_places_rating_apply_note"] = (
            "rating/reviews diisi dari Google Places safe candidate; "
            f"result={candidate.get('result_title')}"
        )
        updated.at[idx, "google_places_rating_source_url"] = candidate.get("url")
        updated.at[idx, "google_places_rating_place_id"] = candidate.get("placeId")
        updated.at[idx, "google_places_rating_distance_km"] = candidate.get("distance_km")
        updated.at[idx, "google_places_rating_name_similarity"] = candidate.get("name_similarity")

        audit_rows.append(
            {
                "penginapan_id": penginapan_id,
                "target_name": candidate.get("target_name"),
                "result_title": candidate.get("result_title"),
                "totalScore": candidate.get("totalScore"),
                "reviewsCount": candidate.get("reviewsCount"),
                "categoryName": candidate.get("categoryName"),
                "distance_km": candidate.get("distance_km"),
                "name_similarity": candidate.get("name_similarity"),
                "url": candidate.get("url"),
                "placeId": candidate.get("placeId"),
                "apply_status": "safe_applied",
                "rating_filled": rating_filled,
                "reviews_filled": reviews_filled,
                "link_filled": link_filled,
                "note": "Hanya mengisi field kosong; nilai lama tidak dioverwrite.",
            }
        )

    return updated, pd.DataFrame(audit_rows)


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
    queue_before = pd.read_csv(QUEUE_INPUT)
    candidates = pd.read_csv(CANDIDATE_INPUT)
    safe = candidates[
        candidates["audit_status"].eq("safe_candidate")
        & candidates["totalScore"].notna()
        & candidates["reviewsCount"].notna()
    ].copy()

    before_priority_counts = primary["completion_priority_data_focus"].value_counts(dropna=False).to_dict()
    before_flag_counts = count_flags(primary)
    before_missing_source = int(primary["link"].apply(is_missing_text).sum()) if "link" in primary.columns else None

    primary_after, audit = apply_safe_candidates(primary, safe)
    primary_after[
        [
            "completion_priority_order",
            "completion_priority_data_focus",
            "completion_flags_data_focus",
            "completion_route_data_focus",
            "completion_score_data_focus",
        ]
    ] = primary_after.apply(recompute_completion, axis=1)
    queue_after = export_queues(primary_after)

    after_priority_counts = primary_after["completion_priority_data_focus"].value_counts(dropna=False).to_dict()
    after_flag_counts = count_flags(primary_after)
    after_missing_source = int(primary_after["link"].apply(is_missing_text).sum()) if "link" in primary_after.columns else None

    primary_after.to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    audit.to_csv(APPLY_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "primary_input": str(PRIMARY_INPUT.relative_to(ROOT)),
        "candidate_input": str(CANDIDATE_INPUT.relative_to(ROOT)),
        "safe_candidates_available": int(len(safe)),
        "safe_candidates_applied": int((audit["apply_status"] == "safe_applied").sum()),
        "rating_filled": int(audit["rating_filled"].sum()),
        "reviews_filled": int(audit["reviews_filled"].sum()),
        "link_filled": int(audit["link_filled"].sum()),
        "priority_counts_before": before_priority_counts,
        "priority_counts_after": after_priority_counts,
        "flag_counts_before": before_flag_counts,
        "flag_counts_after": after_flag_counts,
        "missing_source_link_before": before_missing_source,
        "missing_source_link_after": after_missing_source,
        "queue_rows_before": int(len(queue_before)),
        "queue_rows_after": int(len(queue_after)),
        "queue_priority_after": queue_after["completion_priority_data_focus"].value_counts(dropna=False).to_dict(),
        "primary_output": str(PRIMARY_OUTPUT.relative_to(ROOT)),
        "queue_output": str(QUEUE_OUTPUT.relative_to(ROOT)),
        "apply_audit_output": str(APPLY_AUDIT_OUTPUT.relative_to(ROOT)),
        "decision_note": "Hanya safe_candidate dari audit Google Places yang diaplikasikan; noisy dan needs_review belum masuk dataset.",
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
