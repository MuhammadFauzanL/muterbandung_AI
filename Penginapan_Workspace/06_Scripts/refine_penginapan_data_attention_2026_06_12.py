import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_FEATURE_ENRICHED_WITH_ATTENTION_2026-06-12.csv"
REFINED_OUTPUT = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_FEATURE_ENRICHED_WITH_REFINED_ATTENTION_2026-06-12.csv"
PRICE_REFINED_OUTPUT = CURATED_DIR / "PENGINAPAN_PRICE_OUTLIER_REFINED_AUDIT_2026-06-12.csv"
LOW_QUALITY_OUTPUT = CURATED_DIR / "PENGINAPAN_LOW_DATA_QUALITY_REFINED_AUDIT_2026-06-12.csv"
DETAIL_REFINED_OUTPUT = CURATED_DIR / "PENGINAPAN_DETAIL_LISTING_REFINED_AUDIT_2026-06-12.csv"
DETAIL_HIGH_PRIORITY_OUTPUT = CURATED_DIR / "PENGINAPAN_DETAIL_LISTING_HIGH_PRIORITY_REVIEW_2026-06-12.csv"
DETAIL_ORIGINAL_HIGH_OUTPUT = CURATED_DIR / "PENGINAPAN_DETAIL_LISTING_ORIGINAL_HIGH_ATTENTION_2026-06-12.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_refined_attention_summary_2026-06-12.json"


ROOM_PATTERNS = [
    r"\bstandard\b",
    r"\bdeluxe\b",
    r"\bsuperior\b",
    r"\beconomy\b",
    r"\bfamily room\b",
    r"\bdouble room\b",
    r"\btwin room\b",
    r"\bking room\b",
    r"\bqueen room\b",
    r"\broom with\b",
]

APARTMENT_UNIT_PATTERNS = [
    r"\bstudio\b",
    r"\b1br\b",
    r"\b2br\b",
    r"\b3br\b",
    r"\bone-bedroom\b",
    r"\btwo-bedroom\b",
    r"\bthree-bedroom\b",
    r"\bbedroom apartment\b",
]

VILLA_OR_HOUSE_PATTERNS = [
    r"\bvilla\b",
    r"\bvila\b",
    r"\bhouse\b",
    r"\bhome\b",
    r"\bcottage\b",
    r"\bprivate pool\b",
]

LARGE_UNIT_PATTERNS = [
    r"\b[4-9]\s*br\b",
    r"\b[4-9]\s*bedroom",
    r"\bfour-bedroom\b",
    r"\bfive-bedroom\b",
    r"\bsix-bedroom\b",
    r"\bseven-bedroom\b",
    r"\beight-bedroom\b",
    r"\bnine-bedroom\b",
    r"\bmax\s*[5-9]\b",
    r"\bmax\s*1[0-9]\b",
]

DETAIL_PATTERNS = ROOM_PATTERNS + APARTMENT_UNIT_PATTERNS + [r"\bvilla with private pool\b"]

REVIEW_COLUMNS = [
    "penginapan_id",
    "name",
    "property_type",
    "overall_rating",
    "reviews",
    "price_lowest",
    "price_display",
    "amenities",
    "primary_image_url",
    "link",
    "data_quality_score",
    "data_quality_label",
    "hotel_review_count_analyzed",
    "hotel_adjusted_sentiment_score",
    "hotel_adjusted_sentiment_label",
    "hotel_review_confidence_label",
    "rating_sentiment_score",
    "name_looks_detail_listing",
    "capacity_min_estimated",
    "capacity_max_estimated",
    "capacity_confidence",
    "attention_score",
    "attention_level",
    "attention_reasons",
    "recommended_data_action",
]


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def norm(value):
    return clean_text(value).lower()


def has_any(text, patterns):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def missing(value):
    if pd.isna(value):
        return True
    return clean_text(value).lower() in {"", "nan", "none", "null"}


def num(value):
    try:
        if pd.isna(value):
            return np.nan
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def boolish(value):
    if isinstance(value, bool):
        return value
    return clean_text(value).lower() in {"true", "1", "yes", "ya"}


def classify_detail_listing(row):
    text = norm(row.get("name"))
    property_type = norm(row.get("property_type"))
    attention_level = norm(row.get("attention_level"))
    attention_reasons = norm(row.get("attention_reasons"))
    detail_seed = boolish(row.get("name_looks_detail_listing")) or "looks_like_detail_or_unit_listing" in attention_reasons

    if not detail_seed:
        return pd.Series(
            {
                "refined_detail_listing_group": "",
                "refined_detail_listing_action": "",
                "refined_detail_listing_priority": "",
            }
        )

    room = has_any(text, ROOM_PATTERNS)
    bedroom_unit = has_any(text, APARTMENT_UNIT_PATTERNS)
    apartment_unit = bedroom_unit and not has_any(text, VILLA_OR_HOUSE_PATTERNS)
    villa_or_house = has_any(text, VILLA_OR_HOUSE_PATTERNS)
    large_unit = has_any(text, LARGE_UNIT_PATTERNS)
    capacity_max = num(row.get("capacity_max_estimated"))

    if room and property_type in {"hotel", "guest_house", "vacation_rental"}:
        group = "room_level_detail"
        action = "hold_as_child_detail"
    elif villa_or_house and (large_unit or (not np.isnan(capacity_max) and capacity_max >= 5)):
        group = "whole_house_or_large_unit"
        action = "keep_secondary_or_review_parent_status"
    elif villa_or_house and bedroom_unit:
        group = "villa_or_house_detail"
        action = "review_parent_child_status"
    elif apartment_unit:
        group = "apartment_unit_detail"
        action = "secondary_option_not_primary_parent"
    elif villa_or_house:
        group = "villa_or_house_detail"
        action = "review_parent_child_status"
    elif boolish(row.get("name_looks_detail_listing")) or has_any(text, DETAIL_PATTERNS):
        group = "other_detail_listing"
        action = "review_parent_child_status"
    else:
        group = ""
        action = ""

    if not group:
        priority = ""
    elif attention_level == "high" or group in {"room_level_detail", "apartment_unit_detail"}:
        priority = "high_attention"
    elif group in {"whole_house_or_large_unit", "villa_or_house_detail"}:
        priority = "medium_attention"
    else:
        priority = "low_attention"

    return pd.Series(
        {
            "refined_detail_listing_group": group,
            "refined_detail_listing_action": action,
            "refined_detail_listing_priority": priority,
        }
    )


def classify_price_outlier(row):
    reasons = norm(row.get("attention_reasons"))
    if "price_outlier_for_type" not in reasons:
        return pd.Series({"refined_price_status": "", "refined_price_action": "", "refined_price_note": ""})

    text = norm(row.get("name"))
    property_type = norm(row.get("property_type"))
    price = num(row.get("price_lowest"))
    capacity_max = num(row.get("capacity_max_estimated"))
    large_unit = has_any(text, LARGE_UNIT_PATTERNS) or (not np.isnan(capacity_max) and capacity_max >= 5)
    villa_or_house = has_any(text, VILLA_OR_HOUSE_PATTERNS)
    apartment_unit = has_any(text, APARTMENT_UNIT_PATTERNS)
    rating_missing = pd.isna(row.get("overall_rating")) or pd.isna(row.get("reviews"))
    source_missing = missing(row.get("link"))

    if property_type in {"villa", "vacation_rental"} and (villa_or_house or large_unit):
        status = "likely_valid_large_unit_price"
        action = "keep_but_mark_high_price"
        note = "harga tinggi masuk akal untuk villa/rumah/unit besar, tetap perlu label harga mahal"
    elif property_type == "apartment" or apartment_unit:
        status = "secondary_high_price_unit"
        action = "keep_secondary_and_verify_if_top_ranked"
        note = "apartemen/unit mahal tidak salah, tapi jangan jadi opsi utama tanpa konteks user"
    elif property_type in {"hotel", "guest_house"} and (villa_or_house or large_unit):
        status = "property_type_or_unit_size_review"
        action = "review_type_or_capacity_before_ranking"
        note = "tipe terlihat seperti rumah/homestay/unit besar, bukan hotel reguler"
    elif rating_missing or source_missing:
        status = "verify_price_source"
        action = "manual_source_check"
        note = "harga tinggi dengan rating/source lemah perlu cek sumber"
    elif not np.isnan(price) and price >= 10_000_000:
        status = "extreme_price_verify"
        action = "manual_source_check"
        note = "harga ekstrem perlu cek sumber walau bisa valid"
    else:
        status = "price_outlier_keep_with_caution"
        action = "keep_but_lower_price_confidence"
        note = "tidak terlihat error jelas, cukup ditandai outlier"

    return pd.Series(
        {
            "refined_price_status": status,
            "refined_price_action": action,
            "refined_price_note": note,
        }
    )


def classify_low_quality(row):
    low = norm(row.get("data_quality_label")) == "low" or "low_data_quality" in norm(row.get("attention_reasons"))
    if not low:
        return pd.Series({"refined_low_quality_status": "", "refined_low_quality_action": "", "refined_low_quality_note": ""})

    missing_rating = pd.isna(row.get("overall_rating")) or pd.isna(row.get("reviews"))
    missing_price = pd.isna(row.get("price_lowest"))
    missing_amenities = missing(row.get("amenities"))
    missing_image = missing(row.get("primary_image_url"))
    missing_source = missing(row.get("link"))
    detail_group = clean_text(row.get("refined_detail_listing_group"))

    if detail_group:
        status = "low_quality_detail_listing"
        action = "hold_as_child_or_secondary"
        note = "data lemah dan nama terlihat sebagai kamar/unit"
    elif missing_rating and missing_price and missing_source:
        status = "hold_until_source_available"
        action = "manual_source_completion"
        note = "rating, harga, dan sumber lemah; jangan jadi prioritas"
    elif missing_rating and missing_price:
        status = "core_fields_missing"
        action = "manual_rating_price_completion"
        note = "rating dan harga belum cukup untuk ranking kuat"
    elif missing_amenities or missing_image:
        status = "content_completion_needed"
        action = "complete_amenities_or_image_if_needed"
        note = "data inti ada sebagian, tapi tampilan/filter masih lemah"
    else:
        status = "low_score_but_usable"
        action = "keep_low_confidence"
        note = "masih bisa disimpan, tetapi ranking harus hati-hati"

    return pd.Series(
        {
            "refined_low_quality_status": status,
            "refined_low_quality_action": action,
            "refined_low_quality_note": note,
        }
    )


def choose_overall_action(row):
    detail_action = clean_text(row.get("refined_detail_listing_action"))
    low_action = clean_text(row.get("refined_low_quality_action"))
    price_action = clean_text(row.get("refined_price_action"))

    if detail_action in {"hold_as_child_detail", "secondary_option_not_primary_parent"}:
        return "hold_or_secondary_detail_listing"
    if low_action in {"manual_source_completion", "manual_rating_price_completion"}:
        return "manual_core_completion_before_primary_ranking"
    if detail_action:
        return detail_action
    if price_action in {"manual_source_check", "review_type_or_capacity_before_ranking"}:
        return "verify_price_or_type"
    if low_action:
        return low_action
    if price_action:
        return price_action
    return ""


def build_summary(df, price_df, low_df, detail_df, high_detail_df):
    return {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "row_count": int(len(df)),
        "outputs": {
            "refined_dataset": str(REFINED_OUTPUT.relative_to(ROOT)),
            "price_outlier_refined": str(PRICE_REFINED_OUTPUT.relative_to(ROOT)),
            "low_quality_refined": str(LOW_QUALITY_OUTPUT.relative_to(ROOT)),
            "detail_listing_refined": str(DETAIL_REFINED_OUTPUT.relative_to(ROOT)),
            "detail_listing_high_priority": str(DETAIL_HIGH_PRIORITY_OUTPUT.relative_to(ROOT)),
            "detail_listing_original_high_attention": str(DETAIL_ORIGINAL_HIGH_OUTPUT.relative_to(ROOT)),
        },
        "price_outlier_count": int(len(price_df)),
        "price_outlier_status_counts": price_df["refined_price_status"].value_counts(dropna=False).to_dict(),
        "low_quality_count": int(len(low_df)),
        "low_quality_status_counts": low_df["refined_low_quality_status"].value_counts(dropna=False).to_dict(),
        "detail_listing_count": int(len(detail_df)),
        "detail_listing_group_counts": detail_df["refined_detail_listing_group"].value_counts(dropna=False).to_dict(),
        "detail_listing_original_attention_counts": detail_df["attention_level"].value_counts(dropna=False).to_dict(),
        "detail_listing_high_priority_count": int(len(high_detail_df)),
        "overall_refined_action_counts": df["refined_overall_data_action"].replace("", np.nan).dropna().value_counts().to_dict(),
    }


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)

    detail_labels = df.apply(classify_detail_listing, axis=1)
    df = pd.concat([df, detail_labels], axis=1)

    price_labels = df.apply(classify_price_outlier, axis=1)
    low_labels = df.apply(classify_low_quality, axis=1)
    df = pd.concat([df, price_labels, low_labels], axis=1)

    df["refined_overall_data_action"] = df.apply(choose_overall_action, axis=1)

    output_cols = [col for col in REVIEW_COLUMNS if col in df.columns] + [
        "refined_detail_listing_group",
        "refined_detail_listing_action",
        "refined_detail_listing_priority",
        "refined_price_status",
        "refined_price_action",
        "refined_price_note",
        "refined_low_quality_status",
        "refined_low_quality_action",
        "refined_low_quality_note",
        "refined_overall_data_action",
    ]

    detail_df = df[df["refined_detail_listing_group"].ne("")].copy()
    high_detail_df = detail_df[detail_df["refined_detail_listing_priority"].eq("high_attention")].copy()
    original_high_detail_df = detail_df[detail_df["attention_level"].eq("high")].copy()
    price_df = df[df["refined_price_status"].ne("")].copy()
    low_df = df[df["refined_low_quality_status"].ne("")].copy()

    df.to_csv(REFINED_OUTPUT, index=False, encoding="utf-8-sig")
    price_df[output_cols].to_csv(PRICE_REFINED_OUTPUT, index=False, encoding="utf-8-sig")
    low_df[output_cols].to_csv(LOW_QUALITY_OUTPUT, index=False, encoding="utf-8-sig")
    detail_df[output_cols].to_csv(DETAIL_REFINED_OUTPUT, index=False, encoding="utf-8-sig")
    high_detail_df[output_cols].to_csv(DETAIL_HIGH_PRIORITY_OUTPUT, index=False, encoding="utf-8-sig")
    original_high_detail_df[output_cols].to_csv(DETAIL_ORIGINAL_HIGH_OUTPUT, index=False, encoding="utf-8-sig")

    summary = build_summary(df, price_df, low_df, detail_df, high_detail_df)
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
