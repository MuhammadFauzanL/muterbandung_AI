import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
OUTPUT_DIR = (
    ROOT
    / "Penginapan_Workspace"
    / "05_Apify_Price_Batches"
    / "Google_Hotels_Jalur2_Price_Missing_No_Link_2026-06-13"
)

INPUT_PATH = CURATED_DIR / "PENGINAPAN_COMPLETION_REMAINING_AFTER_PLACES_RATING_APPLY_P1_PRICE_MISSING_2026-06-13.csv"
INDEX_OUTPUT = OUTPUT_DIR / "JALUR2_PRICE_MISSING_NO_LINK_TARGET_INDEX_2026-06-13.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "jalur2_price_missing_no_link_summary_2026-06-13.json"


BASE_CONFIG = {
    "adults": 2,
    "children": 0,
    "check_in_date": "2026-07-11",
    "check_out_date": "2026-07-13",
    "currency": "IDR",
    "gl": "id",
    "hl": "id",
    "max_pages": 25,
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def is_blank(value):
    text = clean_text(value).lower()
    return text in {"", "nan", "none", "null"}


def area_bucket(row):
    name = clean_text(row.get("name")).lower()
    lat = row.get("latitude")
    lon = row.get("longitude")
    prop_type = clean_text(row.get("property_type_final_after_p3")).lower()

    if "ciwidey" in name or "pangalengan" in name:
        return "ciwidey_pangalengan"
    if pd.notna(lat) and float(lat) < -7.05:
        return "ciwidey_pangalengan"
    if "lembang" in name or "padalarang" in name or "bandung barat" in name:
        return "bandung_barat"
    if pd.notna(lon) and float(lon) < 107.53:
        return "bandung_barat"
    if "cimahi" in name:
        return "cimahi"
    if pd.notna(lon) and 107.50 <= float(lon) <= 107.58 and pd.notna(lat) and -6.95 <= float(lat) <= -6.84:
        return "cimahi"
    if prop_type == "guest_house":
        return "guest_house_bandung"
    return "hotel_bandung"


def payload(query, vacation_rentals=False):
    return {
        **BASE_CONFIG,
        "q": query,
        "vacation_rentals": bool(vacation_rentals),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(INPUT_PATH)
    no_link = data[data["link"].apply(is_blank)].copy()
    no_link["jalur2_area_bucket"] = no_link.apply(area_bucket, axis=1)

    query_plan = [
        {
            "filename": "01_hotel_kota_bandung_price_missing_no_link.json",
            "bucket": "hotel_bandung",
            "query": "hotel in Kota Bandung, Jawa Barat",
            "vacation_rentals": False,
        },
        {
            "filename": "02_guest_house_kota_bandung_price_missing_no_link.json",
            "bucket": "guest_house_bandung",
            "query": "guest house in Kota Bandung, Jawa Barat",
            "vacation_rentals": False,
        },
        {
            "filename": "03_penginapan_cimahi_price_missing_no_link.json",
            "bucket": "cimahi",
            "query": "penginapan in Cimahi, Jawa Barat",
            "vacation_rentals": False,
        },
        {
            "filename": "04_penginapan_bandung_barat_lembang_padalarang_price_missing_no_link.json",
            "bucket": "bandung_barat",
            "query": "penginapan in Kabupaten Bandung Barat Lembang Padalarang, Jawa Barat",
            "vacation_rentals": False,
        },
        {
            "filename": "05_penginapan_ciwidey_pangalengan_price_missing_no_link.json",
            "bucket": "ciwidey_pangalengan",
            "query": "penginapan in Ciwidey Pangalengan Kabupaten Bandung, Jawa Barat",
            "vacation_rentals": False,
        },
    ]

    for item in query_plan:
        output_path = OUTPUT_DIR / item["filename"]
        output_path.write_text(
            json.dumps(payload(item["query"], item["vacation_rentals"]), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    index_columns = [
        "penginapan_id",
        "name",
        "property_type_final_after_p3",
        "overall_rating",
        "reviews",
        "hotel_adjusted_sentiment_score",
        "data_quality_score",
        "latitude",
        "longitude",
        "jalur2_area_bucket",
    ]
    no_link[index_columns].to_csv(INDEX_OUTPUT, index=False, encoding="utf-8-sig")

    bucket_counts = no_link["jalur2_area_bucket"].value_counts().to_dict()
    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "output_folder": str(OUTPUT_DIR.relative_to(ROOT)),
        "target_total_p1_price_missing_no_link": int(len(no_link)),
        "bucket_counts": bucket_counts,
        "json_files": [
            {
                "file": item["filename"],
                "bucket": item["bucket"],
                "query": item["query"],
                "target_count_hint": int(bucket_counts.get(item["bucket"], 0)),
                "vacation_rentals": item["vacation_rentals"],
            }
            for item in query_plan
        ],
        "index_file": str(INDEX_OUTPUT.relative_to(ROOT)),
        "decision_note": "Jalur 2 memakai broad Google Hotels query per wilayah/tipe karena target belum punya source link.",
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
