import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P3_DECISIONS_2026-06-12.csv"
AUDIT_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_COMPLETION_AUDIT_2026-06-13.csv"
QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_COMPLETION_QUEUE_PRIORITY_2026-06-13.csv"
RATING_PRICE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_RATING_PRICE_COMPLETION_QUEUE_2026-06-13.csv"
REVIEW_SENTIMENT_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_REVIEW_SENTIMENT_COMPLETION_QUEUE_2026-06-13.csv"
AMENITY_IMAGE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_AMENITY_IMAGE_COMPLETION_QUEUE_2026-06-13.csv"
SOURCE_LINK_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_SOURCE_LINK_COMPLETION_QUEUE_2026-06-13.csv"
PRIMARY_DUPLICATE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DUPLICATE_NAME_AUDIT_2026-06-13.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_primary_completion_summary_2026-06-13.json"


CORE_EXPORT_COLUMNS = [
    "penginapan_id",
    "name",
    "property_type",
    "property_type_final_after_p3",
    "latitude",
    "longitude",
    "region_bucket",
    "overall_rating",
    "reviews",
    "price_lowest",
    "price_display",
    "hotel_review_count_analyzed",
    "hotel_adjusted_sentiment_score",
    "hotel_adjusted_sentiment_label",
    "hotel_review_confidence_label",
    "amenities",
    "primary_image_url",
    "link",
    "data_quality_score",
    "data_quality_label",
    "completion_score",
    "completion_priority",
    "completion_flags",
    "recommended_completion_actions",
    "completion_route",
    "scrape_ready",
    "manual_check_needed",
    "completion_note",
]


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_blank(value):
    text = clean_text(value).lower()
    return text in {"", "nan", "none", "null"}


def has_number(value):
    return not pd.isna(value)


def row_completion(row):
    missing_rating_reviews = pd.isna(row.get("overall_rating")) or pd.isna(row.get("reviews"))
    missing_price = pd.isna(row.get("price_lowest"))
    missing_sentiment = pd.isna(row.get("hotel_adjusted_sentiment_score")) or int(row.get("hotel_review_count_analyzed") or 0) <= 0
    missing_amenities = is_blank(row.get("amenities"))
    missing_image = is_blank(row.get("primary_image_url"))
    missing_source = is_blank(row.get("link"))
    missing_coords = pd.isna(row.get("latitude")) or pd.isna(row.get("longitude"))

    flags = []
    actions = []

    if missing_rating_reviews:
        flags.append("missing_rating_reviews")
        actions.append("scrape_or_verify_place_rating")
    if missing_price:
        flags.append("missing_price")
        actions.append("scrape_google_hotels_or_manual_price")
    if missing_sentiment:
        flags.append("missing_sentiment")
        actions.append("scrape_google_maps_reviews_for_sentiment")
    if missing_amenities:
        flags.append("missing_amenities")
        actions.append("complete_amenities")
    if missing_image:
        flags.append("missing_image")
        actions.append("complete_primary_image")
    if missing_source:
        flags.append("missing_source_link")
        actions.append("add_source_link")
    if missing_coords:
        flags.append("missing_coordinates")
        actions.append("manual_coordinate_check")

    available_core = 0
    total_core = 7
    available_core += 0 if missing_rating_reviews else 1
    available_core += 0 if missing_price else 1
    available_core += 0 if missing_sentiment else 1
    available_core += 0 if missing_amenities else 1
    available_core += 0 if missing_image else 1
    available_core += 0 if missing_source else 1
    available_core += 0 if missing_coords else 1
    completion_score = round(available_core / total_core, 3)

    if missing_coords:
        priority = "P0_coordinate_blocker"
        route = "manual_coordinate_fix"
        note = "Koordinat kosong; jangan scrape/rank sebelum koordinat jelas."
    elif missing_rating_reviews and missing_price:
        priority = "P1_core_rating_price_missing"
        route = "scrape_rating_price_first"
        note = "Rating/review dan harga sama-sama kosong; ini prioritas completion utama."
    elif missing_rating_reviews:
        priority = "P1_rating_reviews_missing"
        route = "scrape_place_profile"
        note = "Rating/review kosong; perlu profile tempat dulu."
    elif missing_price:
        priority = "P1_price_missing"
        route = "scrape_price_or_manual_price"
        note = "Harga kosong; filter budget belum kuat."
    elif missing_sentiment:
        priority = "P2_sentiment_missing"
        route = "scrape_reviews_for_sentiment"
        note = "Rating/harga cukup, tetapi sentiment review belum tersedia."
    elif missing_amenities or missing_image:
        priority = "P3_content_missing"
        route = "manual_content_completion"
        note = "Data ranking cukup, tetapi tampilan/filter fasilitas belum lengkap."
    elif missing_source:
        priority = "P3_source_link_missing"
        route = "source_link_completion"
        note = "Data cukup, tetapi sumber link perlu dirapikan."
    else:
        priority = "OK_complete_enough"
        route = "no_action"
        note = "Data primary cukup lengkap untuk baseline."

    scrape_ready = not missing_coords and not is_blank(row.get("name"))
    manual_check_needed = missing_coords or missing_source or (missing_price and missing_rating_reviews)

    return pd.Series(
        {
            "completion_score": completion_score,
            "completion_priority": priority,
            "completion_flags": "|".join(flags),
            "recommended_completion_actions": "|".join(dict.fromkeys(actions)),
            "completion_route": route,
            "scrape_ready": bool(scrape_ready),
            "manual_check_needed": bool(manual_check_needed),
            "completion_note": note,
        }
    )


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    primary_mask = df["primary_ranking_allowed_after_p3"].fillna(False).astype(bool) & ~df[
        "drop_from_dataset_after_p3"
    ].fillna(False).astype(bool)
    primary = df[primary_mask].copy()

    completion = primary.apply(row_completion, axis=1)
    primary = pd.concat([primary, completion], axis=1)
    primary["_name_norm"] = primary["name"].fillna("").astype(str).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    duplicate_name_counts = primary["_name_norm"].value_counts()
    duplicate_names = duplicate_name_counts[duplicate_name_counts > 1]
    primary["primary_exact_name_duplicate_count"] = primary["_name_norm"].map(duplicate_name_counts).fillna(1).astype(int)
    primary["primary_exact_name_duplicate_flag"] = primary["primary_exact_name_duplicate_count"].gt(1)

    export_columns = [col for col in CORE_EXPORT_COLUMNS if col in primary.columns]
    export_columns = export_columns + [
        "primary_exact_name_duplicate_count",
        "primary_exact_name_duplicate_flag",
    ]

    queue = primary[primary["completion_priority"].ne("OK_complete_enough")].copy()
    priority_order = {
        "P0_coordinate_blocker": 0,
        "P1_core_rating_price_missing": 1,
        "P1_rating_reviews_missing": 2,
        "P1_price_missing": 3,
        "P2_sentiment_missing": 4,
        "P3_content_missing": 5,
        "P3_source_link_missing": 6,
    }
    queue["_priority_order"] = queue["completion_priority"].map(priority_order).fillna(99)
    queue = queue.sort_values(
        ["_priority_order", "property_type_final_after_p3", "data_quality_score", "reviews", "name"],
        ascending=[True, True, False, False, True],
    ).drop(columns=["_priority_order"])

    rating_price = queue[
        queue["completion_flags"].str.contains("missing_rating_reviews|missing_price", na=False)
    ].copy()
    review_sentiment = queue[queue["completion_flags"].str.contains("missing_sentiment", na=False)].copy()
    amenity_image = queue[
        queue["completion_flags"].str.contains("missing_amenities|missing_image", na=False)
    ].copy()
    source_link = queue[queue["completion_flags"].str.contains("missing_source_link", na=False)].copy()
    duplicates = primary[primary["primary_exact_name_duplicate_flag"]].copy()
    duplicates = duplicates.sort_values(["_name_norm", "data_quality_score", "reviews"], ascending=[True, False, False])

    primary[export_columns].to_csv(AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    queue[export_columns].to_csv(QUEUE_OUTPUT, index=False, encoding="utf-8-sig")
    rating_price[export_columns].to_csv(RATING_PRICE_OUTPUT, index=False, encoding="utf-8-sig")
    review_sentiment[export_columns].to_csv(REVIEW_SENTIMENT_OUTPUT, index=False, encoding="utf-8-sig")
    amenity_image[export_columns].to_csv(AMENITY_IMAGE_OUTPUT, index=False, encoding="utf-8-sig")
    source_link[export_columns].to_csv(SOURCE_LINK_OUTPUT, index=False, encoding="utf-8-sig")
    duplicates[export_columns].to_csv(PRIMARY_DUPLICATE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "primary_count": int(len(primary)),
        "completion_queue_count": int(len(queue)),
        "complete_enough_count": int(primary["completion_priority"].eq("OK_complete_enough").sum()),
        "completion_priority_counts": primary["completion_priority"].value_counts().to_dict(),
        "completion_flag_counts": {
            "missing_rating_reviews": int(primary["completion_flags"].str.contains("missing_rating_reviews", na=False).sum()),
            "missing_price": int(primary["completion_flags"].str.contains("missing_price", na=False).sum()),
            "missing_sentiment": int(primary["completion_flags"].str.contains("missing_sentiment", na=False).sum()),
            "missing_amenities": int(primary["completion_flags"].str.contains("missing_amenities", na=False).sum()),
            "missing_image": int(primary["completion_flags"].str.contains("missing_image", na=False).sum()),
            "missing_source_link": int(primary["completion_flags"].str.contains("missing_source_link", na=False).sum()),
            "missing_coordinates": int(primary["completion_flags"].str.contains("missing_coordinates", na=False).sum()),
        },
        "queue_by_property_type": queue["property_type_final_after_p3"].value_counts().to_dict(),
        "rating_price_queue_count": int(len(rating_price)),
        "review_sentiment_queue_count": int(len(review_sentiment)),
        "amenity_image_queue_count": int(len(amenity_image)),
        "source_link_queue_count": int(len(source_link)),
        "primary_duplicate_exact_name_group_count": int(len(duplicate_names)),
        "primary_duplicate_exact_name_row_count": int(len(duplicates)),
        "scrape_ready_count_in_queue": int(queue["scrape_ready"].sum()),
        "manual_check_needed_count_in_queue": int(queue["manual_check_needed"].sum()),
        "outputs": {
            "primary_completion_audit": str(AUDIT_OUTPUT.relative_to(ROOT)),
            "primary_completion_queue": str(QUEUE_OUTPUT.relative_to(ROOT)),
            "rating_price_queue": str(RATING_PRICE_OUTPUT.relative_to(ROOT)),
            "review_sentiment_queue": str(REVIEW_SENTIMENT_OUTPUT.relative_to(ROOT)),
            "amenity_image_queue": str(AMENITY_IMAGE_OUTPUT.relative_to(ROOT)),
            "source_link_queue": str(SOURCE_LINK_OUTPUT.relative_to(ROOT)),
            "primary_duplicate_name_audit": str(PRIMARY_DUPLICATE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
