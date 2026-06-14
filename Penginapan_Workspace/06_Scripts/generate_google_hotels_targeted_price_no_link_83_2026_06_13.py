import json
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
OUTPUT_DIR = (
    ROOT
    / "Penginapan_Workspace"
    / "05_Apify_Price_Batches"
    / "Google_Hotels_Targeted_Price_No_Link_83_2026-06-13"
)

INPUT_PATH = CURATED_DIR / "PENGINAPAN_COMPLETION_REMAINING_AFTER_PLACES_RATING_APPLY_P1_PRICE_MISSING_2026-06-13.csv"
INDEX_OUTPUT = OUTPUT_DIR / "TARGETED_PRICE_NO_LINK_83_INDEX_2026-06-13.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "targeted_price_no_link_83_summary_2026-06-13.json"
JSON_DIR = OUTPUT_DIR / "json_one_by_one"
PACKET_DIR = OUTPUT_DIR / "work_packets_5_groups"


BASE_CONFIG = {
    "adults": 2,
    "children": 0,
    "check_in_date": "2026-07-11",
    "check_out_date": "2026-07-13",
    "currency": "IDR",
    "gl": "id",
    "hl": "id",
    "max_pages": 3,
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def is_blank(value):
    text = clean_text(value).lower()
    return text in {"", "nan", "none", "null"}


def slug(value):
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:64] or "target"


def area_hint(row):
    name = clean_text(row.get("name")).lower()
    lat = row.get("latitude")
    lon = row.get("longitude")
    if "ciwidey" in name or "pangalengan" in name:
        return "Ciwidey Pangalengan Kabupaten Bandung Jawa Barat Indonesia"
    if pd.notna(lat) and float(lat) < -7.05:
        return "Ciwidey Pangalengan Kabupaten Bandung Jawa Barat Indonesia"
    if "lembang" in name:
        return "Lembang Kabupaten Bandung Barat Jawa Barat Indonesia"
    if "padalarang" in name:
        return "Padalarang Kabupaten Bandung Barat Jawa Barat Indonesia"
    if pd.notna(lon) and float(lon) < 107.53:
        return "Cimahi Padalarang Kabupaten Bandung Barat Jawa Barat Indonesia"
    if "cimahi" in name:
        return "Cimahi Jawa Barat Indonesia"
    if pd.notna(lon) and 107.50 <= float(lon) <= 107.58 and pd.notna(lat) and -6.95 <= float(lat) <= -6.84:
        return "Cimahi Jawa Barat Indonesia"
    return "Kota Bandung Jawa Barat Indonesia"


def build_query(row):
    return f"{clean_text(row.get('name'))} {area_hint(row)}"


def is_vacation_rental_type(row):
    prop_type = clean_text(row.get("property_type_final_after_p3")).lower()
    return prop_type in {"villa", "vacation_rental", "apartment"}


def build_payload(row):
    return {
        **BASE_CONFIG,
        "q": build_query(row),
        "vacation_rentals": is_vacation_rental_type(row),
    }


def main():
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    PACKET_DIR.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(INPUT_PATH)
    target = data[data["link"].apply(is_blank)].copy()
    target["_type_order"] = target["property_type_final_after_p3"].map(
        {"hotel": 0, "guest_house": 1, "villa": 2, "vacation_rental": 3}
    ).fillna(9)
    target = target.sort_values(
        ["_type_order", "data_quality_score", "reviews", "name"],
        ascending=[True, False, False, True],
    ).reset_index(drop=True)

    index_rows = []
    for number, (_, row) in enumerate(target.iterrows(), start=1):
        payload = build_payload(row)
        filename = f"{number:03d}_{row['penginapan_id']}_{slug(row['name'])}.json"
        (JSON_DIR / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        index_rows.append(
            {
                "target_no": number,
                "json_file": filename,
                "penginapan_id": row["penginapan_id"],
                "name": row["name"],
                "property_type_final_after_p3": row["property_type_final_after_p3"],
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "overall_rating": row.get("overall_rating"),
                "reviews": row.get("reviews"),
                "data_quality_score": row.get("data_quality_score"),
                "q": payload["q"],
                "vacation_rentals": payload["vacation_rentals"],
                "max_pages": payload["max_pages"],
                "note": "Targeted one-by-one Google Hotels query; validate name and coordinate before apply.",
            }
        )

    index = pd.DataFrame(index_rows)
    index.to_csv(INDEX_OUTPUT, index=False, encoding="utf-8-sig")

    # Work packets are not actor input. They are a compact checklist so the user can split work.
    packet_count = 5
    packet_size = math.ceil(len(index) / packet_count)
    packet_files = []
    for idx in range(packet_count):
        part = index.iloc[idx * packet_size : (idx + 1) * packet_size].copy()
        packet_path = PACKET_DIR / f"TARGETED_PRICE_NO_LINK_83_PACKET_{idx+1:02d}_OF_05.json"
        packet_path.write_text(
            json.dumps(part.to_dict(orient="records"), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        packet_files.append({"file": packet_path.name, "target_count": int(len(part))})

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "output_folder": str(OUTPUT_DIR.relative_to(ROOT)),
        "actor": "johnvc/google-hotels-search-scraper",
        "target_count": int(len(index)),
        "json_one_by_one_folder": str(JSON_DIR.relative_to(ROOT)),
        "index_file": str(INDEX_OUTPUT.relative_to(ROOT)),
        "work_packet_folder": str(PACKET_DIR.relative_to(ROOT)),
        "work_packets": packet_files,
        "type_counts": index["property_type_final_after_p3"].value_counts(dropna=False).to_dict(),
        "decision_note": "Presisi dibuat satu target satu q karena actor Google Hotels memakai satu q per run.",
        "usage_note": "Upload/paste file dari json_one_by_one satu per satu ke actor Google Hotels Search Scraper.",
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
