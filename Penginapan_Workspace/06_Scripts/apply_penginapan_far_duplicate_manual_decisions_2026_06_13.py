import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_PRIMARY_DEDUPE_2026-06-13.csv"
DECISIONS_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_FAR_DUPLICATE_MANUAL_DECISIONS_2026-06-13.csv"
FULL_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_PRIMARY_DEDUPE_RESOLVED_2026-06-13.csv"
PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DEDUPED_RESOLVED_CANDIDATE_2026-06-13.csv"
DROPPED_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_FAR_DUPLICATE_DROPPED_2026-06-13.csv"
COMPLETION_AUDIT_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_COMPLETION_AUDIT_AFTER_FAR_DUPLICATE_RESOLUTION_2026-06-13.csv"
COMPLETION_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_COMPLETION_QUEUE_AFTER_FAR_DUPLICATE_RESOLUTION_2026-06-13.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_far_duplicate_manual_resolution_summary_2026-06-13.json"


DECISIONS = [
    {
        "penginapan_id": "LODGE-00006",
        "manual_decision": "keep_separate",
        "merge_target_id": "",
        "resolution_note": "Kandidat utama area Bayabang/Cianjur dan memiliki harga.",
    },
    {
        "penginapan_id": "LODGE-00566",
        "manual_decision": "keep_separate",
        "merge_target_id": "",
        "resolution_note": "Jarak sekitar 8 km dari LODGE-00006 dan memiliki harga unik; pertahankan terpisah.",
    },
    {
        "penginapan_id": "LODGE-00014",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00006",
        "resolution_note": "Duplikat lemah tanpa harga/rating.",
    },
    {
        "penginapan_id": "LODGE-00689",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00566",
        "resolution_note": "Duplikat lemah tanpa harga/rating.",
    },
    {
        "penginapan_id": "LODGE-00690",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00566",
        "resolution_note": "Duplikat lemah tanpa harga/rating.",
    },
    {
        "penginapan_id": "LODGE-00096",
        "manual_decision": "keep_separate",
        "merge_target_id": "",
        "resolution_note": "Kandidat utama Nabila; koordinat paling akurat dan volume ulasan tertinggi.",
    },
    {
        "penginapan_id": "LODGE-00095",
        "manual_decision": "merge_fix_coordinate",
        "merge_target_id": "LODGE-00096",
        "resolution_note": "Merge ke LODGE-00096; selisih sekitar 1 km adalah anomali pinning dari sumber OTA.",
    },
    {
        "penginapan_id": "LODGE-00369",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00096",
        "resolution_note": "Duplikat LODGE-00096 dengan perbedaan digit koordinat minor dan harga kosong.",
    },
    {
        "penginapan_id": "LODGE-00624",
        "manual_decision": "keep_separate",
        "merge_target_id": "",
        "resolution_note": "Kandidat utama Saung Arjuna di area Ciwidey; rating dan ulasan tervalidasi.",
    },
    {
        "penginapan_id": "LODGE-01482",
        "manual_decision": "merge_fix_coordinate",
        "merge_target_id": "LODGE-00624",
        "resolution_note": "Merge ke LODGE-00624; koordinat sumber salah dan harga dipakai untuk melengkapi target.",
    },
    {
        "penginapan_id": "LODGE-00716",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00624",
        "resolution_note": "Duplikat lemah tanpa kelengkapan data.",
    },
    {
        "penginapan_id": "LODGE-00139",
        "manual_decision": "keep_separate",
        "merge_target_id": "",
        "resolution_note": "Kandidat utama The Cluster Harris di Jl. H. Haris, Baros, Cimahi.",
    },
    {
        "penginapan_id": "LODGE-00176",
        "manual_decision": "merge_fix_coordinate",
        "merge_target_id": "LODGE-00139",
        "resolution_note": "Merge ke LODGE-00139; koordinat bergeser sekitar 1 km dari lokasi faktual.",
    },
    {
        "penginapan_id": "LODGE-00382",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00139",
        "resolution_note": "Duplikat LODGE-00139; lokasi sama namun harga kosong.",
    },
    {
        "penginapan_id": "LODGE-00601",
        "manual_decision": "keep_separate",
        "merge_target_id": "",
        "resolution_note": "Kandidat utama Villa Haposan; parameter harga tervalidasi.",
    },
    {
        "penginapan_id": "LODGE-00742",
        "manual_decision": "drop_duplicate",
        "merge_target_id": "LODGE-00601",
        "resolution_note": "Duplikat LODGE-00601 dengan data pendukung kosong.",
    },
]


EXPORT_COLUMNS = [
    "penginapan_id",
    "name",
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
    "primary_dedupe_status",
    "primary_dedupe_merged_from_ids",
    "far_duplicate_manual_decision",
    "far_duplicate_merge_target_id",
    "far_duplicate_resolution_note",
    "far_duplicate_merged_from_ids",
    "primary_ranking_allowed_after_far_resolution",
    "drop_from_dataset_after_far_resolution",
    "completion_score_after_far_resolution",
    "completion_priority_after_far_resolution",
    "completion_flags_after_far_resolution",
    "completion_route_after_far_resolution",
    "completion_note_after_far_resolution",
]


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_blank(value):
    text = clean_text(value).lower()
    return text in {"", "nan", "none", "null"}


def value_available(row, column):
    if column not in row.index:
        return False
    value = row[column]
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return not is_blank(value)
    return True


def fill_if_missing(df, target_idx, source_row, column):
    if column not in df.columns or column not in source_row.index:
        return
    current = df.at[target_idx, column]
    current_missing = pd.isna(current) or (isinstance(current, str) and is_blank(current))
    if current_missing and value_available(source_row, column):
        df.at[target_idx, column] = source_row[column]


def append_pipe_value(existing, value):
    existing_text = clean_text(existing)
    value_text = clean_text(value)
    if not value_text:
        return existing_text
    parts = [part for part in existing_text.split("|") if part] if existing_text else []
    if value_text not in parts:
        parts.append(value_text)
    return "|".join(parts)


def merge_source_into_target(df, source_id, target_id):
    source_rows = df[df["penginapan_id"].eq(source_id)]
    target_idx = df.index[df["penginapan_id"].eq(target_id)]
    if len(source_rows) == 0 or len(target_idx) == 0:
        return
    source = source_rows.iloc[0]
    target_idx = target_idx[0]

    fill_columns = [
        "overall_rating",
        "reviews",
        "location_rating",
        "price_lowest",
        "price_before_taxes_fees",
        "price_display",
        "check_in_time",
        "check_out_time",
        "amenities",
        "nearby_place_names",
        "primary_image_url",
        "image_count",
        "link",
        "rating_sentiment_score",
        "adjusted_rating_sentiment_score",
        "rating_sentiment_label",
        "adjusted_rating_sentiment_label",
        "review_confidence_label",
        "rating_sentiment_source",
        "hotel_review_count_analyzed",
        "hotel_sentiment_score",
        "hotel_sentiment_confidence_mean",
        "positive_review_count",
        "neutral_review_count",
        "negative_review_count",
        "review_target_count",
        "hotel_adjusted_sentiment_score",
        "hotel_sentiment_label",
        "hotel_adjusted_sentiment_label",
        "hotel_review_confidence",
        "hotel_review_confidence_label",
        "hotel_sentiment_available",
    ]
    for column in fill_columns:
        fill_if_missing(df, target_idx, source, column)

    df.at[target_idx, "far_duplicate_merged_from_ids"] = append_pipe_value(
        df.at[target_idx, "far_duplicate_merged_from_ids"], source_id
    )
    df.at[target_idx, "primary_dedupe_merged_from_ids"] = append_pipe_value(
        df.at[target_idx, "primary_dedupe_merged_from_ids"], source_id
    )
    if clean_text(df.at[target_idx, "primary_dedupe_status"]) == "needs_review_same_name_far_distance":
        df.at[target_idx, "primary_dedupe_status"] = "manual_resolved_keep_with_merge"


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

    available_core = sum(
        [
            not missing_rating_reviews,
            not missing_price,
            not missing_sentiment,
            not missing_amenities,
            not missing_image,
            not missing_source,
            not missing_coords,
        ]
    )
    completion_score = round(available_core / 7, 3)

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

    return pd.Series(
        {
            "completion_score_after_far_resolution": completion_score,
            "completion_priority_after_far_resolution": priority,
            "completion_flags_after_far_resolution": "|".join(flags),
            "recommended_completion_actions_after_far_resolution": "|".join(dict.fromkeys(actions)),
            "completion_route_after_far_resolution": route,
            "completion_note_after_far_resolution": note,
        }
    )


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    decisions = pd.DataFrame(DECISIONS)
    decisions.to_csv(DECISIONS_OUTPUT, index=False, encoding="utf-8-sig")

    df["far_duplicate_manual_decision"] = ""
    df["far_duplicate_merge_target_id"] = ""
    df["far_duplicate_resolution_note"] = ""
    df["far_duplicate_merged_from_ids"] = ""
    df["primary_ranking_allowed_after_far_resolution"] = df[
        "primary_ranking_allowed_after_dedupe"
    ].fillna(False).astype(bool)
    df["drop_from_dataset_after_far_resolution"] = df[
        "drop_from_dataset_after_dedupe"
    ].fillna(False).astype(bool)

    decision_map = decisions.set_index("penginapan_id").to_dict("index")
    merge_decisions = decisions[decisions["manual_decision"].eq("merge_fix_coordinate")]

    for _, decision in merge_decisions.iterrows():
        merge_source_into_target(df, decision["penginapan_id"], decision["merge_target_id"])

    for idx, row in df.iterrows():
        decision = decision_map.get(row["penginapan_id"])
        if not decision:
            continue
        manual_decision = decision["manual_decision"]
        df.at[idx, "far_duplicate_manual_decision"] = manual_decision
        df.at[idx, "far_duplicate_merge_target_id"] = decision["merge_target_id"]
        df.at[idx, "far_duplicate_resolution_note"] = decision["resolution_note"]

        if manual_decision in {"drop_duplicate", "merge_fix_coordinate"}:
            df.at[idx, "primary_ranking_allowed_after_far_resolution"] = False
            df.at[idx, "drop_from_dataset_after_far_resolution"] = True
            df.at[idx, "primary_dedupe_status"] = f"manual_resolved_{manual_decision}"
        elif manual_decision == "keep_separate":
            df.at[idx, "primary_ranking_allowed_after_far_resolution"] = True
            df.at[idx, "drop_from_dataset_after_far_resolution"] = False
            if clean_text(df.at[idx, "primary_dedupe_status"]) == "needs_review_same_name_far_distance":
                df.at[idx, "primary_dedupe_status"] = "manual_resolved_keep_separate"

    primary = df[
        df["primary_ranking_allowed_after_far_resolution"].fillna(False).astype(bool)
        & ~df["drop_from_dataset_after_far_resolution"].fillna(False).astype(bool)
    ].copy()
    completion = primary.apply(row_completion, axis=1)
    primary = pd.concat([primary, completion], axis=1)
    completion_queue = primary[
        primary["completion_priority_after_far_resolution"].ne("OK_complete_enough")
    ].copy()

    dropped = df[df["drop_from_dataset_after_far_resolution"].fillna(False).astype(bool)].copy()

    export_columns = [col for col in EXPORT_COLUMNS if col in primary.columns]
    full_export_columns = [col for col in EXPORT_COLUMNS if col in df.columns]

    df.to_csv(FULL_OUTPUT, index=False, encoding="utf-8-sig")
    primary[export_columns].to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    dropped[full_export_columns].to_csv(DROPPED_OUTPUT, index=False, encoding="utf-8-sig")
    primary[export_columns].to_csv(COMPLETION_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    completion_queue[export_columns].to_csv(COMPLETION_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "decision_count": int(len(decisions)),
        "keep_separate_count": int(decisions["manual_decision"].eq("keep_separate").sum()),
        "drop_duplicate_count": int(decisions["manual_decision"].eq("drop_duplicate").sum()),
        "merge_fix_coordinate_count": int(decisions["manual_decision"].eq("merge_fix_coordinate").sum()),
        "primary_count_after_far_resolution": int(len(primary)),
        "dropped_count_after_far_resolution": int(len(dropped)),
        "completion_queue_after_far_resolution_count": int(len(completion_queue)),
        "complete_enough_after_far_resolution_count": int(
            primary["completion_priority_after_far_resolution"].eq("OK_complete_enough").sum()
        ),
        "completion_priority_after_far_resolution_counts": primary[
            "completion_priority_after_far_resolution"
        ].value_counts().to_dict(),
        "completion_flag_after_far_resolution_counts": {
            "missing_rating_reviews": int(
                primary["completion_flags_after_far_resolution"].str.contains("missing_rating_reviews", na=False).sum()
            ),
            "missing_price": int(
                primary["completion_flags_after_far_resolution"].str.contains("missing_price", na=False).sum()
            ),
            "missing_sentiment": int(
                primary["completion_flags_after_far_resolution"].str.contains("missing_sentiment", na=False).sum()
            ),
            "missing_amenities": int(
                primary["completion_flags_after_far_resolution"].str.contains("missing_amenities", na=False).sum()
            ),
            "missing_image": int(
                primary["completion_flags_after_far_resolution"].str.contains("missing_image", na=False).sum()
            ),
            "missing_source_link": int(
                primary["completion_flags_after_far_resolution"].str.contains("missing_source_link", na=False).sum()
            ),
        },
        "outputs": {
            "decisions": str(DECISIONS_OUTPUT.relative_to(ROOT)),
            "full_with_resolution": str(FULL_OUTPUT.relative_to(ROOT)),
            "primary_resolved": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "dropped_resolved": str(DROPPED_OUTPUT.relative_to(ROOT)),
            "completion_audit_after_resolution": str(COMPLETION_AUDIT_OUTPUT.relative_to(ROOT)),
            "completion_queue_after_resolution": str(COMPLETION_QUEUE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
