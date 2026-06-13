import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

FULL_INPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_PRIMARY_DEDUPE_RESOLVED_2026-06-13.csv"

FULL_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_DATA_FOCUS_2026-06-13.csv"
PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_2026-06-13.csv"
DROPPED_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_DROPPED_2026-06-13.csv"
ORDERED_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_COMPLETION_QUEUE_ORDERED_2026-06-13.csv"
PRICE_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_P1_PRICE_MISSING_2026-06-13.csv"
CORE_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_P1_CORE_RATING_PRICE_MISSING_2026-06-13.csv"
RATING_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_P1_RATING_REVIEWS_MISSING_2026-06-13.csv"
SENTIMENT_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_COMPLETION_P2_SENTIMENT_MISSING_2026-06-13.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_data_focus_cleanup_summary_2026-06-13.json"


PAKUHAJI_KEEP_ID = "LODGE-00170"
PAKUHAJI_DROP_ID = "LODGE-00431"

PRIORITY_ORDER = {
    "P1_price_missing": 1,
    "P1_core_rating_price_missing": 2,
    "P1_rating_reviews_missing": 3,
    "P2_sentiment_missing": 4,
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_blank(value):
    return clean_text(value) in {"", "nan", "None", "NaN"}


def to_bool(value):
    if isinstance(value, bool):
        return value
    text = clean_text(value).lower()
    return text in {"true", "1", "yes", "y"}


def append_pipe_value(existing, value):
    existing_text = clean_text(existing)
    value_text = clean_text(value)
    if not value_text:
        return existing_text
    parts = [part for part in existing_text.split("|") if part] if existing_text else []
    if value_text not in parts:
        parts.append(value_text)
    return "|".join(parts)


def fill_if_missing(df, target_idx, source_row, column):
    if column not in df.columns:
        return
    source_value = source_row.get(column)
    if is_blank(source_value):
        return
    if is_blank(df.at[target_idx, column]):
        df.at[target_idx, column] = source_value


def row_completion(row):
    missing_rating_reviews = pd.isna(row.get("overall_rating")) or pd.isna(row.get("reviews"))
    missing_price = pd.isna(row.get("price_lowest"))
    missing_sentiment = pd.isna(row.get("hotel_adjusted_sentiment_score")) or int(row.get("hotel_review_count_analyzed") or 0) <= 0
    missing_amenities = is_blank(row.get("amenities"))
    missing_image = is_blank(row.get("primary_image_url"))
    missing_source = is_blank(row.get("link"))

    flags = []
    if missing_rating_reviews:
        flags.append("missing_rating_reviews")
    if missing_price:
        flags.append("missing_price")
    if missing_sentiment:
        flags.append("missing_sentiment")
    if missing_amenities:
        flags.append("missing_amenities")
    if missing_image:
        flags.append("missing_image")
    if missing_source:
        flags.append("missing_source_link")

    score = 0
    for ok in [
        not missing_rating_reviews,
        not missing_price,
        not missing_sentiment,
        not missing_amenities,
        not missing_image,
        not missing_source,
    ]:
        score += int(ok)

    if missing_rating_reviews and missing_price:
        priority = "P1_core_rating_price_missing"
        route = "scrape_place_rating_reviews_and_price"
    elif missing_price:
        priority = "P1_price_missing"
        route = "scrape_or_manual_price"
    elif missing_rating_reviews:
        priority = "P1_rating_reviews_missing"
        route = "scrape_place_rating_reviews"
    elif missing_sentiment:
        priority = "P2_sentiment_missing"
        route = "scrape_reviews_for_sentiment"
    elif missing_amenities or missing_image:
        priority = "P3_content_missing"
        route = "complete_amenities_or_image"
    elif missing_source:
        priority = "P3_source_link_missing"
        route = "fill_source_link_when_available"
    else:
        priority = "OK_complete_enough"
        route = "ready_for_baseline"

    return pd.Series(
        {
            "completion_score_data_focus": score,
            "completion_priority_data_focus": priority,
            "completion_flags_data_focus": "|".join(flags),
            "completion_route_data_focus": route,
        }
    )


def main():
    df = pd.read_csv(FULL_INPUT)

    for col in [
        "data_focus_manual_decision",
        "data_focus_manual_note",
        "data_focus_merge_target_id",
        "primary_ranking_allowed_data_focus",
        "drop_from_dataset_data_focus",
    ]:
        if col not in df.columns:
            df[col] = ""

    df["primary_ranking_allowed_data_focus"] = df["primary_ranking_allowed_after_far_resolution"].map(to_bool)
    df["drop_from_dataset_data_focus"] = df["drop_from_dataset_after_far_resolution"].map(to_bool)

    keep_idx = df.index[df["penginapan_id"].eq(PAKUHAJI_KEEP_ID)]
    drop_idx = df.index[df["penginapan_id"].eq(PAKUHAJI_DROP_ID)]
    if len(keep_idx) != 1 or len(drop_idx) != 1:
        raise ValueError("Pakuhaji keep/drop rows are not unique.")

    keep_idx = keep_idx[0]
    drop_idx = drop_idx[0]
    drop_row = df.loc[drop_idx]

    for column in [
        "overall_rating",
        "reviews",
        "price_lowest",
        "price_display",
        "amenities",
        "primary_image_url",
        "link",
        "hotel_adjusted_sentiment_score",
        "hotel_review_count_analyzed",
    ]:
        fill_if_missing(df, keep_idx, drop_row, column)

    df.at[keep_idx, "primary_dedupe_merged_from_ids"] = append_pipe_value(
        df.at[keep_idx, "primary_dedupe_merged_from_ids"], PAKUHAJI_DROP_ID
    )
    df.at[keep_idx, "data_focus_manual_decision"] = "keep_primary_merge_duplicate"
    df.at[keep_idx, "data_focus_manual_note"] = (
        "Pakuhaji resolved: gunakan LODGE-00170 karena lengkap dan koordinat sama dengan LODGE-00431."
    )

    df.at[drop_idx, "data_focus_manual_decision"] = "drop_duplicate"
    df.at[drop_idx, "data_focus_manual_note"] = (
        "Duplikat Pakuhaji; koordinat hampir sama, tetapi harga/rating/review kosong."
    )
    df.at[drop_idx, "data_focus_merge_target_id"] = PAKUHAJI_KEEP_ID
    df.at[drop_idx, "primary_ranking_allowed_data_focus"] = False
    df.at[drop_idx, "drop_from_dataset_data_focus"] = True
    df.at[drop_idx, "primary_dedupe_status"] = "manual_resolved_drop_duplicate_data_focus"

    primary = df[
        df["primary_ranking_allowed_data_focus"].map(to_bool)
        & ~df["drop_from_dataset_data_focus"].map(to_bool)
    ].copy()
    completion = primary.apply(row_completion, axis=1)
    primary = pd.concat([primary, completion], axis=1)
    primary["completion_priority_order"] = (
        primary["completion_priority_data_focus"].map(PRIORITY_ORDER).fillna(99).astype(int)
    )

    ordered_queue = primary[
        primary["completion_priority_data_focus"].isin(PRIORITY_ORDER.keys())
    ].copy()
    ordered_queue = ordered_queue.sort_values(
        [
            "completion_priority_order",
            "property_type_final_after_p3",
            "data_quality_score",
            "reviews",
            "name",
        ],
        ascending=[True, True, False, False, True],
    )

    dropped = df[df["drop_from_dataset_data_focus"].map(to_bool)].copy()

    export_columns = [
        col
        for col in [
            "penginapan_id",
            "name",
            "property_type_final_after_p3",
            "latitude",
            "longitude",
            "region_validation_label",
            "price_lowest",
            "price_display",
            "overall_rating",
            "reviews",
            "hotel_review_count_analyzed",
            "hotel_adjusted_sentiment_score",
            "hotel_sentiment_label",
            "amenities",
            "primary_image_url",
            "link",
            "data_quality_score",
            "primary_dedupe_status",
            "primary_dedupe_merged_from_ids",
            "data_focus_manual_decision",
            "data_focus_manual_note",
            "data_focus_merge_target_id",
            "completion_priority_order",
            "completion_priority_data_focus",
            "completion_flags_data_focus",
            "completion_route_data_focus",
            "completion_score_data_focus",
        ]
        if col in primary.columns
    ]

    queue_columns = [col for col in export_columns if col in ordered_queue.columns]

    df.to_csv(FULL_OUTPUT, index=False, encoding="utf-8-sig")
    primary[export_columns].to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    dropped.to_csv(DROPPED_OUTPUT, index=False, encoding="utf-8-sig")
    ordered_queue[queue_columns].to_csv(ORDERED_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")
    ordered_queue[ordered_queue["completion_priority_data_focus"].eq("P1_price_missing")][queue_columns].to_csv(
        PRICE_QUEUE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    ordered_queue[ordered_queue["completion_priority_data_focus"].eq("P1_core_rating_price_missing")][queue_columns].to_csv(
        CORE_QUEUE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    ordered_queue[ordered_queue["completion_priority_data_focus"].eq("P1_rating_reviews_missing")][queue_columns].to_csv(
        RATING_QUEUE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    ordered_queue[ordered_queue["completion_priority_data_focus"].eq("P2_sentiment_missing")][queue_columns].to_csv(
        SENTIMENT_QUEUE_OUTPUT, index=False, encoding="utf-8-sig"
    )

    summary = {
        "input_file": str(FULL_INPUT.relative_to(ROOT)),
        "pakuhaji_decision": {
            "keep_id": PAKUHAJI_KEEP_ID,
            "drop_id": PAKUHAJI_DROP_ID,
            "decision": "drop_duplicate_into_keep_id",
        },
        "primary_count_data_focus": int(len(primary)),
        "dropped_count_data_focus": int(len(dropped)),
        "ordered_completion_queue_count": int(len(ordered_queue)),
        "completion_priority_data_focus_counts": primary[
            "completion_priority_data_focus"
        ].value_counts().to_dict(),
        "missing_counts": {
            "rating_reviews": int(
                (primary["overall_rating"].isna() | primary["reviews"].isna()).sum()
            ),
            "price": int(primary["price_lowest"].isna().sum()),
            "sentiment": int(
                (
                    primary["hotel_adjusted_sentiment_score"].isna()
                    | (primary["hotel_review_count_analyzed"].fillna(0).astype(int).le(0))
                ).sum()
            ),
            "amenities": int(primary["amenities"].map(is_blank).sum()),
            "image": int(primary["primary_image_url"].map(is_blank).sum()),
            "source_link": int(primary["link"].map(is_blank).sum()),
        },
        "outputs": {
            "full": str(FULL_OUTPUT.relative_to(ROOT)),
            "primary": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "dropped": str(DROPPED_OUTPUT.relative_to(ROOT)),
            "ordered_queue": str(ORDERED_QUEUE_OUTPUT.relative_to(ROOT)),
            "p1_price_missing": str(PRICE_QUEUE_OUTPUT.relative_to(ROOT)),
            "p1_core_rating_price_missing": str(CORE_QUEUE_OUTPUT.relative_to(ROOT)),
            "p1_rating_reviews_missing": str(RATING_QUEUE_OUTPUT.relative_to(ROOT)),
            "p2_sentiment_missing": str(SENTIMENT_QUEUE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
