import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_FEATURE_ENRICHED_2026-06-12.csv"
AUDITED_OUTPUT = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_FEATURE_ENRICHED_WITH_ATTENTION_2026-06-12.csv"
QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_DATA_ATTENTION_QUEUE_2026-06-12.csv"
DETAIL_OUTPUT = CURATED_DIR / "PENGINAPAN_DETAIL_OR_UNIT_LISTING_ATTENTION_2026-06-12.csv"
MISSING_CORE_OUTPUT = CURATED_DIR / "PENGINAPAN_MISSING_CORE_FIELDS_ATTENTION_2026-06-12.csv"
PRICE_OUTLIER_OUTPUT = CURATED_DIR / "PENGINAPAN_PRICE_OUTLIER_ATTENTION_2026-06-12.csv"
PROPERTY_TYPE_OUTPUT = CURATED_DIR / "PENGINAPAN_PROPERTY_TYPE_ATTENTION_2026-06-12.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_data_attention_summary_2026-06-12.json"


DETAIL_PATTERNS = [
    r"\bstandard\b",
    r"\bdeluxe\b",
    r"\bsuperior\b",
    r"\bfamily room\b",
    r"\bdouble room\b",
    r"\btwin room\b",
    r"\bking room\b",
    r"\bqueen room\b",
    r"\bstudio\b",
    r"\b1br\b",
    r"\b2br\b",
    r"\b3br\b",
    r"\bone-bedroom\b",
    r"\btwo-bedroom\b",
    r"\bthree-bedroom\b",
    r"\bbedroom apartment\b",
    r"\bvilla with private pool\b",
    r"\broom with\b",
]


TYPE_HINTS = {
    "apartment": [r"apartment", r"apartemen", r"studio", r"\b1br\b", r"\b2br\b", r"\b3br\b"],
    "villa": [r"\bvilla\b", r"\bvila\b", r"private pool", r"bedrooms with", r"city view villa", r"hill view villa"],
    "guest_house": [r"guest house", r"guesthouse", r"homestay", r"bed & breakfast", r"\bbnb\b"],
    "vacation_rental": [r"house", r"home", r"cottage", r"resort", r"rental"],
    "hotel": [r"\bhotel\b", r"reddoorz", r"\boyo\b", r"ibis", r"mercure", r"novotel", r"sheraton"],
}


PRICE_REVIEW_LIMITS = {
    "hotel": 1_500_000,
    "guest_house": 1_000_000,
    "apartment": 1_200_000,
    "villa": 10_000_000,
    "vacation_rental": 5_000_000,
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def norm(value):
    return clean_text(value).lower()


def not_blank(series):
    text = series.fillna("").astype(str).str.strip()
    return text.ne("") & ~text.str.lower().isin(["nan", "none", "null"])


def has_pattern(text, patterns):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def detect_type_hint(row):
    text = norm(row.get("name"))
    current = norm(row.get("property_type"))
    hits = []
    for type_name, patterns in TYPE_HINTS.items():
        if has_pattern(text, patterns):
            hits.append(type_name)
    hits = [hit for hit in hits if hit != current]
    if not hits:
        return "", ""
    return "|".join(hits), "name_contains_other_property_type_keyword"


def attention_for_row(row):
    reasons = []
    score = 0

    if row.get("data_quality_label") == "low":
        reasons.append("low_data_quality")
        score += 4

    missing_rating = pd.isna(row.get("overall_rating")) or pd.isna(row.get("reviews"))
    missing_price = pd.isna(row.get("price_lowest"))
    missing_amenities = not clean_text(row.get("amenities"))
    missing_image = not clean_text(row.get("primary_image_url"))
    missing_link = not clean_text(row.get("link"))
    missing_sentiment = pd.isna(row.get("hotel_adjusted_sentiment_score")) and pd.isna(row.get("rating_sentiment_score"))

    if missing_rating and missing_price:
        reasons.append("missing_rating_and_price")
        score += 4
    elif missing_rating:
        reasons.append("missing_rating_or_reviews")
        score += 2
    elif missing_price:
        reasons.append("missing_price")
        score += 2

    if missing_sentiment:
        reasons.append("missing_any_sentiment")
        score += 2
    if missing_amenities:
        reasons.append("missing_amenities")
        score += 2
    if missing_image:
        reasons.append("missing_image")
        score += 2
    if missing_link:
        reasons.append("missing_source_link")
        score += 1

    name_text = norm(row.get("name"))
    detail_by_name = bool(row.get("name_looks_detail_listing")) or has_pattern(name_text, DETAIL_PATTERNS)
    if detail_by_name:
        reasons.append("looks_like_detail_or_unit_listing")
        score += 3

    property_type_hint, property_type_reason = detect_type_hint(row)
    if property_type_hint:
        reasons.append("property_type_maybe_needs_review")
        score += 2

    price = row.get("price_lowest")
    property_type = norm(row.get("property_type"))
    limit = PRICE_REVIEW_LIMITS.get(property_type)
    if limit is not None and not pd.isna(price) and float(price) > limit:
        reasons.append("price_outlier_for_type")
        score += 2

    if row.get("capacity_confidence") == "low_capacity_confidence" and property_type in {"villa", "apartment", "vacation_rental"}:
        reasons.append("capacity_low_confidence_for_unit_property")
        score += 1

    if score >= 7:
        level = "high"
    elif score >= 4:
        level = "medium"
    elif score > 0:
        level = "low"
    else:
        level = "ok"

    if detail_by_name:
        action = "review_parent_child_or_mark_secondary"
    elif missing_rating and missing_price:
        action = "manual_or_source_completion"
    elif "price_outlier_for_type" in reasons:
        action = "verify_price_source"
    elif property_type_hint:
        action = "verify_property_type"
    elif missing_amenities:
        action = "complete_amenities_if_needed"
    else:
        action = "no_action_or_low_priority"

    return pd.Series(
        {
            "attention_score": score,
            "attention_level": level,
            "attention_reasons": "|".join(reasons),
            "recommended_data_action": action,
            "property_type_hint": property_type_hint,
            "property_type_hint_reason": property_type_reason,
        }
    )


def main():
    df = pd.read_csv(INPUT_PATH)
    attention = df.apply(attention_for_row, axis=1)
    audited = pd.concat([df, attention], axis=1)
    audited.to_csv(AUDITED_OUTPUT, index=False, encoding="utf-8-sig")

    base_cols = [
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
        "hotel_adjusted_sentiment_label",
        "hotel_review_confidence_label",
        "rating_sentiment_score",
        "name_looks_detail_listing",
        "capacity_min_estimated",
        "capacity_max_estimated",
        "capacity_confidence",
        "capacity_estimation_reason",
        "attention_score",
        "attention_level",
        "attention_reasons",
        "recommended_data_action",
        "property_type_hint",
        "property_type_hint_reason",
    ]
    base_cols = [col for col in base_cols if col in audited.columns]

    queue = audited[audited["attention_level"].ne("ok")].copy()
    queue = queue.sort_values(["attention_score", "property_type", "name"], ascending=[False, True, True])
    queue[base_cols].to_csv(QUEUE_OUTPUT, index=False, encoding="utf-8-sig")

    detail = queue[queue["attention_reasons"].str.contains("looks_like_detail_or_unit_listing", na=False)].copy()
    detail[base_cols].to_csv(DETAIL_OUTPUT, index=False, encoding="utf-8-sig")

    missing_core = queue[queue["attention_reasons"].str.contains("missing_rating_and_price|missing_rating_or_reviews|missing_price|missing_amenities", na=False)].copy()
    missing_core[base_cols].to_csv(MISSING_CORE_OUTPUT, index=False, encoding="utf-8-sig")

    price_outlier = queue[queue["attention_reasons"].str.contains("price_outlier_for_type", na=False)].copy()
    price_outlier[base_cols].to_csv(PRICE_OUTLIER_OUTPUT, index=False, encoding="utf-8-sig")

    property_type = queue[queue["attention_reasons"].str.contains("property_type_maybe_needs_review", na=False)].copy()
    property_type[base_cols].to_csv(PROPERTY_TYPE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_path": str(INPUT_PATH),
        "rows": int(len(df)),
        "attention_rows": int(len(queue)),
        "attention_level_counts": queue["attention_level"].value_counts(dropna=False).to_dict(),
        "attention_reason_counts": queue["attention_reasons"].str.get_dummies(sep="|").sum().sort_values(ascending=False).astype(int).to_dict(),
        "attention_by_property_type": queue["property_type"].value_counts(dropna=False).to_dict(),
        "outputs": {
            "audited_full_dataset": str(AUDITED_OUTPUT),
            "queue": str(QUEUE_OUTPUT),
            "detail_or_unit_listing": str(DETAIL_OUTPUT),
            "missing_core_fields": str(MISSING_CORE_OUTPUT),
            "price_outlier": str(PRICE_OUTLIER_OUTPUT),
            "property_type_attention": str(PROPERTY_TYPE_OUTPUT),
        },
        "decision": "This is a data-attention queue only. Do not replace runtime data from this file directly.",
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
