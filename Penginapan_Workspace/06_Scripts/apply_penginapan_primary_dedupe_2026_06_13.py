import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P3_DECISIONS_2026-06-12.csv"
FULL_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_PRIMARY_DEDUPE_2026-06-13.csv"
PRIMARY_DEDUPED_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DEDUPED_CANDIDATE_2026-06-13.csv"
PRIMARY_DEDUPE_AUDIT_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DEDUPE_AUDIT_2026-06-13.csv"
PRIMARY_DROPPED_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DEDUP_DROPPED_2026-06-13.csv"
FAR_REVIEW_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_SAME_NAME_FAR_DISTANCE_REVIEW_2026-06-13.csv"
COMPLETION_AUDIT_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_COMPLETION_AUDIT_AFTER_DEDUPE_2026-06-13.csv"
COMPLETION_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_COMPLETION_QUEUE_AFTER_DEDUPE_2026-06-13.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_primary_dedupe_summary_2026-06-13.json"

AUTO_DEDUPE_DISTANCE_KM = 0.2


BASE_EXPORT_COLUMNS = [
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
    "primary_dedupe_status",
    "primary_dedupe_group_size",
    "primary_dedupe_group_max_distance_km",
    "primary_dedupe_keep_id",
    "primary_dedupe_merged_from_ids",
    "primary_dedupe_note",
]

COMPLETION_COLUMNS = BASE_EXPORT_COLUMNS + [
    "completion_score_after_dedupe",
    "completion_priority_after_dedupe",
    "completion_flags_after_dedupe",
    "recommended_completion_actions_after_dedupe",
    "completion_route_after_dedupe",
    "completion_note_after_dedupe",
]


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_blank(value):
    text = clean_text(value).lower()
    return text in {"", "nan", "none", "null"}


def normalize_name(value):
    return " ".join(clean_text(value).lower().split())


def haversine_km(lat1, lon1, lat2, lon2):
    if any(pd.isna(v) for v in [lat1, lon1, lat2, lon2]):
        return np.nan
    radius = 6371
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    d_phi = math.radians(float(lat2) - float(lat1))
    d_lambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def group_max_distance(group):
    max_distance = 0.0
    rows = list(group.itertuples(index=False))
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            distance = haversine_km(rows[i].latitude, rows[i].longitude, rows[j].latitude, rows[j].longitude)
            if not pd.isna(distance):
                max_distance = max(max_distance, float(distance))
    return round(max_distance, 4)


def value_available(row, column):
    value = row.get(column)
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return not is_blank(value)
    return True


def keep_score(row):
    score = float(row.get("data_quality_score") or 0) * 100
    for column, weight in [
        ("overall_rating", 15),
        ("reviews", 10),
        ("price_lowest", 15),
        ("hotel_adjusted_sentiment_score", 10),
        ("amenities", 8),
        ("primary_image_url", 8),
        ("link", 6),
    ]:
        if value_available(row, column):
            score += weight
    score += min(float(row.get("reviews") or 0), 10000) / 10000
    score += min(float(row.get("hotel_review_count_analyzed") or 0), 200) / 200
    return score


def best_row_for_group(group):
    ranked = group.copy()
    ranked["_keep_score"] = ranked.apply(keep_score, axis=1)
    ranked = ranked.sort_values(["_keep_score", "data_quality_score", "penginapan_id"], ascending=[False, False, True])
    return ranked.iloc[0]


def fill_if_missing(target, source, column):
    if column not in target.index or column not in source.index:
        return target
    if not value_available(target, column) and value_available(source, column):
        target[column] = source[column]
    return target


def merge_group_into_keep(group, keep_id):
    keep = group[group["penginapan_id"].eq(keep_id)].iloc[0].copy()

    # Prefer rich review sentiment from the row with the largest analyzed review count.
    sentiment_sources = group[group["hotel_review_count_analyzed"].fillna(0).gt(0)].copy()
    if len(sentiment_sources):
        sentiment_sources = sentiment_sources.sort_values("hotel_review_count_analyzed", ascending=False)
        source = sentiment_sources.iloc[0]
        for column in [
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
        ]:
            keep = fill_if_missing(keep, source, column)

    # Fill simple missing profile fields from any duplicate row.
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
    ]
    for _, source in group.iterrows():
        for column in fill_columns:
            keep = fill_if_missing(keep, source, column)

    merged_from = [item for item in group["penginapan_id"].tolist() if item != keep_id]
    keep["primary_dedupe_merged_from_ids"] = "|".join(merged_from)
    return keep


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
            "completion_score_after_dedupe": completion_score,
            "completion_priority_after_dedupe": priority,
            "completion_flags_after_dedupe": "|".join(flags),
            "recommended_completion_actions_after_dedupe": "|".join(dict.fromkeys(actions)),
            "completion_route_after_dedupe": route,
            "completion_note_after_dedupe": note,
        }
    )


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    primary_mask = df["primary_ranking_allowed_after_p3"].fillna(False).astype(bool) & ~df[
        "drop_from_dataset_after_p3"
    ].fillna(False).astype(bool)
    df["primary_dedupe_status"] = ""
    df["primary_dedupe_group_size"] = 1
    df["primary_dedupe_group_max_distance_km"] = 0.0
    df["primary_dedupe_keep_id"] = ""
    df["primary_dedupe_merged_from_ids"] = ""
    df["primary_dedupe_note"] = ""
    df["primary_ranking_allowed_after_dedupe"] = df["primary_ranking_allowed_after_p3"].fillna(False).astype(bool)
    df["drop_from_dataset_after_dedupe"] = df["drop_from_dataset_after_p3"].fillna(False).astype(bool)

    primary = df[primary_mask].copy()
    primary["_name_norm"] = primary["name"].map(normalize_name)
    duplicate_counts = primary["_name_norm"].value_counts()
    duplicate_names = duplicate_counts[duplicate_counts > 1].index

    audit_rows = []
    keep_replacement_rows = {}
    auto_group_count = 0
    far_group_count = 0

    for name_norm in duplicate_names:
        group = primary[primary["_name_norm"].eq(name_norm)].copy()
        max_distance = group_max_distance(group)
        auto_dedupe = max_distance <= AUTO_DEDUPE_DISTANCE_KM
        keep_row = best_row_for_group(group)
        keep_id = keep_row["penginapan_id"]
        group_size = len(group)

        if auto_dedupe:
            auto_group_count += 1
            merged_keep = merge_group_into_keep(group, keep_id)
            keep_replacement_rows[keep_id] = merged_keep
            group_status = "auto_dedupe_close_exact_name"
        else:
            far_group_count += 1
            group_status = "needs_review_same_name_far_distance"

        for _, row in group.iterrows():
            is_keep = row["penginapan_id"] == keep_id
            if auto_dedupe and is_keep:
                status = "keep_primary_deduped"
                drop = False
                note = "Record terbaik dipertahankan; field kosong diisi dari duplikat dekat jika tersedia."
            elif auto_dedupe:
                status = "drop_primary_exact_duplicate"
                drop = True
                note = "Nama sama dan koordinat dekat; dikeluarkan dari primary agar tidak dobel."
            else:
                status = "needs_review_same_name_far_distance"
                drop = False
                note = "Nama sama tetapi koordinat cukup jauh; tidak dihapus otomatis."

            audit_row = row.to_dict()
            audit_row.update(
                {
                    "primary_dedupe_group_status": group_status,
                    "primary_dedupe_status": status,
                    "primary_dedupe_group_size": group_size,
                    "primary_dedupe_group_max_distance_km": max_distance,
                    "primary_dedupe_keep_id": keep_id,
                    "primary_dedupe_drop": drop,
                    "primary_dedupe_note": note,
                }
            )
            audit_rows.append(audit_row)

            idx = df.index[df["penginapan_id"].eq(row["penginapan_id"])]
            if len(idx):
                idx = idx[0]
                df.at[idx, "primary_dedupe_status"] = status
                df.at[idx, "primary_dedupe_group_size"] = group_size
                df.at[idx, "primary_dedupe_group_max_distance_km"] = max_distance
                df.at[idx, "primary_dedupe_keep_id"] = keep_id
                df.at[idx, "primary_dedupe_note"] = note
                if drop:
                    df.at[idx, "primary_ranking_allowed_after_dedupe"] = False
                    df.at[idx, "drop_from_dataset_after_dedupe"] = True

    for keep_id, merged_keep in keep_replacement_rows.items():
        idx = df.index[df["penginapan_id"].eq(keep_id)]
        if not len(idx):
            continue
        idx = idx[0]
        for column, value in merged_keep.items():
            if column in df.columns:
                df.at[idx, column] = value
        df.at[idx, "primary_dedupe_merged_from_ids"] = merged_keep.get("primary_dedupe_merged_from_ids", "")

    for audit_row in audit_rows:
        if audit_row["primary_dedupe_status"] != "keep_primary_deduped":
            continue
        idx = df.index[df["penginapan_id"].eq(audit_row["penginapan_id"])]
        if not len(idx):
            continue
        idx = idx[0]
        df.at[idx, "primary_dedupe_status"] = "keep_primary_deduped"
        df.at[idx, "primary_dedupe_group_size"] = audit_row["primary_dedupe_group_size"]
        df.at[idx, "primary_dedupe_group_max_distance_km"] = audit_row["primary_dedupe_group_max_distance_km"]
        df.at[idx, "primary_dedupe_keep_id"] = audit_row["primary_dedupe_keep_id"]
        df.at[idx, "primary_dedupe_note"] = audit_row["primary_dedupe_note"]

    df.loc[
        primary_mask & df["primary_dedupe_status"].eq(""),
        ["primary_dedupe_status", "primary_dedupe_note"],
    ] = ["unique_primary", "Tidak termasuk duplicate exact-name primary."]

    deduped_primary = df[
        df["primary_ranking_allowed_after_dedupe"].fillna(False).astype(bool)
        & ~df["drop_from_dataset_after_dedupe"].fillna(False).astype(bool)
    ].copy()
    completion = deduped_primary.apply(row_completion, axis=1)
    deduped_primary = pd.concat([deduped_primary, completion], axis=1)
    queue = deduped_primary[deduped_primary["completion_priority_after_dedupe"].ne("OK_complete_enough")].copy()

    audit_df = pd.DataFrame(audit_rows)
    dropped_df = audit_df[audit_df["primary_dedupe_drop"].fillna(False).astype(bool)].copy()
    far_review_df = audit_df[audit_df["primary_dedupe_status"].eq("needs_review_same_name_far_distance")].copy()

    base_cols = [col for col in BASE_EXPORT_COLUMNS if col in df.columns]
    completion_cols = [col for col in COMPLETION_COLUMNS if col in deduped_primary.columns]
    audit_cols = base_cols + [
        "primary_dedupe_group_status",
        "primary_dedupe_drop",
    ]
    audit_cols = [col for col in audit_cols if col in audit_df.columns]

    df.to_csv(FULL_OUTPUT, index=False, encoding="utf-8-sig")
    deduped_primary[completion_cols].to_csv(PRIMARY_DEDUPED_OUTPUT, index=False, encoding="utf-8-sig")
    audit_df[audit_cols].to_csv(PRIMARY_DEDUPE_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    dropped_df[audit_cols].to_csv(PRIMARY_DROPPED_OUTPUT, index=False, encoding="utf-8-sig")
    far_review_df[audit_cols].to_csv(FAR_REVIEW_OUTPUT, index=False, encoding="utf-8-sig")
    deduped_primary[completion_cols].to_csv(COMPLETION_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    queue[completion_cols].to_csv(COMPLETION_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "original_primary_count": int(len(primary)),
        "duplicate_exact_name_group_count": int(len(duplicate_names)),
        "duplicate_exact_name_row_count": int(len(audit_df)),
        "auto_dedupe_close_group_count": int(auto_group_count),
        "needs_review_far_group_count": int(far_group_count),
        "auto_dropped_duplicate_count": int(len(dropped_df)),
        "far_distance_review_row_count": int(len(far_review_df)),
        "deduped_primary_count": int(len(deduped_primary)),
        "completion_queue_after_dedupe_count": int(len(queue)),
        "complete_enough_after_dedupe_count": int(
            deduped_primary["completion_priority_after_dedupe"].eq("OK_complete_enough").sum()
        ),
        "completion_priority_after_dedupe_counts": deduped_primary[
            "completion_priority_after_dedupe"
        ].value_counts().to_dict(),
        "completion_flag_after_dedupe_counts": {
            "missing_rating_reviews": int(
                deduped_primary["completion_flags_after_dedupe"].str.contains("missing_rating_reviews", na=False).sum()
            ),
            "missing_price": int(
                deduped_primary["completion_flags_after_dedupe"].str.contains("missing_price", na=False).sum()
            ),
            "missing_sentiment": int(
                deduped_primary["completion_flags_after_dedupe"].str.contains("missing_sentiment", na=False).sum()
            ),
            "missing_amenities": int(
                deduped_primary["completion_flags_after_dedupe"].str.contains("missing_amenities", na=False).sum()
            ),
            "missing_image": int(
                deduped_primary["completion_flags_after_dedupe"].str.contains("missing_image", na=False).sum()
            ),
            "missing_source_link": int(
                deduped_primary["completion_flags_after_dedupe"].str.contains("missing_source_link", na=False).sum()
            ),
        },
        "outputs": {
            "full_with_primary_dedupe": str(FULL_OUTPUT.relative_to(ROOT)),
            "primary_deduped_candidate": str(PRIMARY_DEDUPED_OUTPUT.relative_to(ROOT)),
            "primary_dedupe_audit": str(PRIMARY_DEDUPE_AUDIT_OUTPUT.relative_to(ROOT)),
            "primary_dedup_dropped": str(PRIMARY_DROPPED_OUTPUT.relative_to(ROOT)),
            "same_name_far_distance_review": str(FAR_REVIEW_OUTPUT.relative_to(ROOT)),
            "completion_audit_after_dedupe": str(COMPLETION_AUDIT_OUTPUT.relative_to(ROOT)),
            "completion_queue_after_dedupe": str(COMPLETION_QUEUE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
