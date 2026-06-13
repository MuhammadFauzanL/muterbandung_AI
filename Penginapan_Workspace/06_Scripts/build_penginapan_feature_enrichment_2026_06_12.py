import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_2026-06-10_DRIVE_FULL_REVIEW.csv"
OUTPUT_PATH = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_FEATURE_ENRICHED_2026-06-12.csv"
SUMMARY_PATH = CURATED_DIR / "penginapan_feature_enrichment_summary_2026-06-12.json"
AMENITY_AUDIT_PATH = CURATED_DIR / "PENGINAPAN_AMENITY_BOOLEAN_COVERAGE_2026-06-12.csv"
PRICE_AUDIT_PATH = CURATED_DIR / "PENGINAPAN_PRICE_BUCKET_COVERAGE_2026-06-12.csv"
CAPACITY_AUDIT_PATH = CURATED_DIR / "PENGINAPAN_CAPACITY_ESTIMATION_COVERAGE_2026-06-12.csv"


AMENITY_RULES = {
    "has_wifi": [r"\bwi[- ]?fi\b", r"\bwifi\b", r"internet"],
    "has_parking": [r"parkir", r"\bparking\b", r"free parking"],
    "has_ac": [r"ber-?ac", r"\bac\b", r"air conditioning"],
    "has_pool": [r"kolam renang", r"\bpool\b", r"swimming pool"],
    "has_kitchen": [r"dapur", r"kitchen", r"kompor", r"stove"],
    "has_breakfast": [r"breakfast", r"sarapan"],
    "has_laundry": [r"laundry", r"mesin cuci", r"washer"],
    "kid_friendly": [r"cocok untuk anak", r"kid[- ]?friendly", r"children"],
    "pet_friendly": [r"boleh bawa hewan", r"pet[- ]?friendly", r"pets allowed"],
    "wheelchair_accessible": [r"kursi roda", r"accessible", r"dapat diakses"],
    "smoke_free": [r"bebas asap rokok", r"smoke[- ]?free", r"non[- ]?smoking"],
    "has_gym": [r"\bgym\b", r"fitness"],
    "has_hot_tub": [r"bak air panas", r"hot tub", r"jacuzzi"],
    "has_balcony_or_terrace": [r"balkon", r"balcony", r"teras", r"terrace"],
    "has_elevator": [r"elevator", r"\blift\b"],
    "has_airport_shuttle": [r"jemputan bandara", r"airport shuttle"],
    "has_cable_tv": [r"tv kabel", r"cable tv"],
    "has_iron": [r"papan setrika", r"\biron\b"],
    "has_heater_or_fireplace": [r"penghangat", r"heater", r"perapian", r"fireplace"],
}


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "satu": 1,
    "dua": 2,
    "tiga": 3,
    "empat": 4,
    "lima": 5,
    "enam": 6,
    "tujuh": 7,
    "delapan": 8,
    "sembilan": 9,
    "sepuluh": 10,
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def norm_text(value):
    return clean_text(value).lower()


def not_blank(series):
    text = series.fillna("").astype(str).str.strip()
    return text.ne("") & ~text.str.lower().isin(["nan", "none", "null"])


def contains_any(text, patterns):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def add_amenity_flags(df):
    amenities = df["amenities"].fillna("").astype(str)
    norm_amenities = amenities.str.lower()
    df["amenities_text_available"] = not_blank(df["amenities"])
    flag_cols = []
    for column, patterns in AMENITY_RULES.items():
        df[column] = norm_amenities.map(lambda text: contains_any(text, patterns))
        flag_cols.append(column)
    df["amenity_boolean_count"] = df[flag_cols].sum(axis=1).astype(int)
    df["amenity_boolean_source"] = np.where(
        df["amenities_text_available"],
        "amenities_text_rule_v1",
        "missing_amenities_text",
    )
    return df, flag_cols


def price_bucket_global(price):
    if pd.isna(price):
        return "unknown"
    price = float(price)
    if price <= 200_000:
        return "budget_under_200k"
    if price <= 500_000:
        return "standard_200k_500k"
    if price <= 1_000_000:
        return "comfort_500k_1m"
    if price <= 3_000_000:
        return "premium_1m_3m"
    return "luxury_above_3m"


def add_price_features(df):
    df["price_available"] = df["price_lowest"].notna()
    df["price_bucket_global"] = df["price_lowest"].map(price_bucket_global)
    df["price_bucket_by_type"] = "unknown"
    df["price_bucket_by_type_q33"] = np.nan
    df["price_bucket_by_type_q66"] = np.nan

    quantiles = {}
    for property_type, sub in df.groupby("property_type", dropna=False):
        prices = sub["price_lowest"].dropna()
        if len(prices) < 3:
            continue
        q33 = float(prices.quantile(0.33))
        q66 = float(prices.quantile(0.66))
        quantiles[str(property_type)] = {"q33": round(q33, 2), "q66": round(q66, 2), "count": int(len(prices))}
        idx = sub.index
        df.loc[idx, "price_bucket_by_type_q33"] = q33
        df.loc[idx, "price_bucket_by_type_q66"] = q66
        df.loc[idx, "price_bucket_by_type"] = df.loc[idx, "price_lowest"].map(
            lambda price: "unknown"
            if pd.isna(price)
            else ("budget_by_type" if float(price) <= q33 else ("mid_range_by_type" if float(price) <= q66 else "premium_by_type"))
        )

    price_display_available = not_blank(df["price_display"]) if "price_display" in df.columns else pd.Series(False, index=df.index)
    before_tax_available = df["price_before_taxes_fees"].notna() if "price_before_taxes_fees" in df.columns else pd.Series(False, index=df.index)
    high_quality = df["data_quality_score"].fillna(0) >= 0.75
    medium_quality = df["data_quality_score"].fillna(0) >= 0.55

    df["price_confidence"] = "missing_price"
    df.loc[df["price_available"] & (price_display_available | before_tax_available) & high_quality, "price_confidence"] = "high_price_confidence"
    df.loc[df["price_available"] & (df["price_confidence"] == "missing_price") & medium_quality, "price_confidence"] = "medium_price_confidence"
    df.loc[df["price_available"] & (df["price_confidence"] == "missing_price"), "price_confidence"] = "low_price_confidence"
    df["price_is_estimated"] = df["price_available"]
    df["price_bucket_method"] = np.where(
        df["price_available"],
        "global_idr_threshold_v1_and_property_type_quantile_v1",
        "missing_price",
    )
    return df, quantiles


def extract_bedroom_count(text):
    text = norm_text(text)
    patterns = [
        r"(\d+)\s*(?:br|bedroom|bedrooms|kamar tidur|kamar)",
        r"(\d+)[- ]?(?:bedroom|bedrooms)",
        r"(\d+)\s*bed\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = int(match.group(1))
            if 0 < value <= 20:
                return value
    for word, value in NUMBER_WORDS.items():
        if re.search(rf"\b{word}\s*[- ]?(?:bedroom|bedrooms|kamar tidur|kamar)\b", text):
            return value
    return np.nan


def extract_guest_capacity(text):
    text = norm_text(text)
    patterns = [
        r"(?:max|maximal|maksimal|up to|hingga|sampai)\s*(\d+)\s*(?:guest|guests)(?!\s*house)",
        r"(?:max|maximal|maksimal|up to|hingga|sampai)\s*(\d+)\s*(?:orang|pax|tamu)",
        r"(\d+)\s*(?:guest|guests)(?!\s*house)",
        r"(\d+)\s*(?:orang|pax|tamu)",
        r"muat\s*(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = int(match.group(1))
            if 0 < value <= 50:
                return value
    return np.nan


def estimate_capacity(row):
    name = norm_text(row.get("name"))
    property_type = norm_text(row.get("property_type"))
    bedrooms = extract_bedroom_count(name)
    guest_capacity = extract_guest_capacity(name)

    if not pd.isna(guest_capacity):
        guest_capacity = int(guest_capacity)
        min_capacity = max(1, guest_capacity - 1)
        return bedrooms, min_capacity, guest_capacity, "high_capacity_confidence", "guest_count_name_pattern"

    if "studio" in name:
        return 0, 1, 2, "medium_capacity_confidence", "studio_name_pattern"

    if not pd.isna(bedrooms):
        bedrooms = int(bedrooms)
        if property_type in {"villa", "vacation_rental"}:
            min_capacity = max(2, bedrooms * 2 - 2)
            max_capacity = max(2, bedrooms * 2)
            return bedrooms, min_capacity, max_capacity, "high_capacity_confidence", "bedroom_count_name_pattern"
        if property_type == "apartment":
            max_capacity = max(2, bedrooms * 2)
            min_capacity = max(1, max_capacity - 1)
            return bedrooms, min_capacity, max_capacity, "high_capacity_confidence", "bedroom_count_name_pattern"
        max_capacity = max(1, bedrooms * 2)
        min_capacity = max(1, max_capacity - 1)
        return bedrooms, min_capacity, max_capacity, "medium_capacity_confidence", "room_bedroom_name_pattern"

    room_patterns = [
        (r"\bsingle\b", 1, 1, "medium_capacity_confidence", "single_room_name_pattern"),
        (r"\btriple\b", 3, 3, "medium_capacity_confidence", "triple_room_name_pattern"),
        (r"\bfamily\b", 3, 4, "medium_capacity_confidence", "family_room_name_pattern"),
        (r"\bdouble\b|\btwin\b|\bqueen\b|\bking\b|\bdeluxe\b|\bsuperior\b|\bstandard\b", 1, 2, "medium_capacity_confidence", "double_or_standard_room_name_pattern"),
    ]
    for pattern, min_cap, max_cap, confidence, reason in room_patterns:
        if re.search(pattern, name):
            return np.nan, min_cap, max_cap, confidence, reason

    if property_type == "apartment":
        return np.nan, 2, 4, "low_capacity_confidence", "apartment_default_no_capacity_source"
    if property_type in {"villa", "vacation_rental"}:
        return np.nan, 4, 8, "low_capacity_confidence", "villa_or_rental_default_no_capacity_source"
    if property_type == "guest_house":
        return np.nan, 1, 2, "low_capacity_confidence", "guest_house_default_per_room"
    return np.nan, 1, 2, "low_capacity_confidence", "hotel_default_per_room"


def add_capacity_features(df):
    values = df.apply(estimate_capacity, axis=1, result_type="expand")
    values.columns = [
        "bedroom_count_estimated",
        "capacity_min_estimated",
        "capacity_max_estimated",
        "capacity_confidence",
        "capacity_estimation_reason",
    ]
    df = pd.concat([df, values], axis=1)
    df["capacity_is_estimated"] = True
    df["capacity_source"] = "name_and_property_type_rule_v1"
    return df


def build_audits(df, flag_cols, quantiles):
    amenity_rows = []
    for col in flag_cols:
        amenity_rows.append({"amenity_flag": col, "true_count": int(df[col].sum()), "true_pct": round(float(df[col].mean() * 100), 2)})
    amenity_audit = pd.DataFrame(amenity_rows).sort_values("true_count", ascending=False)

    price_audit = (
        df.groupby(["property_type", "price_bucket_global"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["property_type", "rows"], ascending=[True, False])
    )

    capacity_audit = (
        df.groupby(["property_type", "capacity_confidence", "capacity_estimation_reason"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["property_type", "capacity_confidence", "rows"], ascending=[True, True, False])
    )

    summary = {
        "input_path": str(INPUT_PATH),
        "output_path": str(OUTPUT_PATH),
        "rows": int(len(df)),
        "amenity_flags": flag_cols,
        "amenities_text_available": int(df["amenities_text_available"].sum()),
        "amenity_boolean_nonzero": int((df["amenity_boolean_count"] > 0).sum()),
        "price_available": int(df["price_available"].sum()),
        "price_missing": int((~df["price_available"]).sum()),
        "price_confidence_counts": df["price_confidence"].value_counts(dropna=False).to_dict(),
        "price_quantiles_by_type": quantiles,
        "capacity_confidence_counts": df["capacity_confidence"].value_counts(dropna=False).to_dict(),
        "capacity_reason_counts": df["capacity_estimation_reason"].value_counts(dropna=False).to_dict(),
        "capacity_note": "Capacity is estimated from name/property_type because raw Google Hotels CSV/JSON does not provide explicit capacity fields.",
        "decision": "Output is an enriched candidate dataset. It should be reviewed before replacing the runtime penginapan dataset.",
    }
    return amenity_audit, price_audit, capacity_audit, summary


def main():
    df = pd.read_csv(INPUT_PATH)
    df, flag_cols = add_amenity_flags(df)
    df, quantiles = add_price_features(df)
    df = add_capacity_features(df)

    amenity_audit, price_audit, capacity_audit, summary = build_audits(df, flag_cols, quantiles)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    amenity_audit.to_csv(AMENITY_AUDIT_PATH, index=False, encoding="utf-8-sig")
    price_audit.to_csv(PRICE_AUDIT_PATH, index=False, encoding="utf-8-sig")
    capacity_audit.to_csv(CAPACITY_AUDIT_PATH, index=False, encoding="utf-8-sig")
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
