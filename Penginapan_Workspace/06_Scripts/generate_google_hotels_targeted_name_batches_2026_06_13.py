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
    / "Google_Hotels_Targeted_By_Name_Batch01_80_2026-06-13"
)
QUEUE_PATH = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_COMPLETION_QUEUE_ORDERED_PRICE_COMPLETED_2026-06-13.csv"
INDEX_OUTPUT = OUTPUT_DIR / "TARGETED_BY_NAME_BATCH01_80_INDEX.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "targeted_by_name_batch01_80_summary.json"

DATE_CONFIG = {
    "adults": 2,
    "children": 0,
    "check_in_date": "2026-07-11",
    "check_out_date": "2026-07-13",
    "currency": "IDR",
    "gl": "id",
    "hl": "id",
    "max_pages": 3,
}

TARGET_PRIORITIES = [
    "P1_core_rating_price_missing",
    "P1_rating_reviews_missing",
    "P1_price_missing",
]
TARGET_TYPES = ["hotel", "guest_house"]
BATCH_LIMIT = 80


def safe_slug(value):
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60] or "target"


def build_query(row):
    name = str(row["name"]).strip()
    lat = row.get("latitude")
    lon = row.get("longitude")
    # Google Hotels Search lebih stabil dengan exact name + wilayah.
    # Koordinat tetap disimpan di index untuk validasi setelah scrape.
    return f"{name}, Jawa Barat, Indonesia"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    queue = pd.read_csv(QUEUE_PATH)
    target = queue[
        queue["completion_priority_data_focus"].isin(TARGET_PRIORITIES)
        & queue["property_type_final_after_p3"].isin(TARGET_TYPES)
    ].copy()
    priority_order = {name: idx for idx, name in enumerate(TARGET_PRIORITIES)}
    type_order = {"hotel": 0, "guest_house": 1}
    target["_priority_order"] = target["completion_priority_data_focus"].map(priority_order)
    target["_type_order"] = target["property_type_final_after_p3"].map(type_order)
    target = target.sort_values(
        ["_priority_order", "_type_order", "data_quality_score", "reviews", "name"],
        ascending=[True, True, False, False, True],
    ).head(BATCH_LIMIT)

    index_rows = []
    for number, (_, row) in enumerate(target.iterrows(), start=1):
        query = build_query(row)
        payload = {
            **DATE_CONFIG,
            "q": query,
            "vacation_rentals": False,
        }
        filename = f"{number:03d}_{row['penginapan_id']}_{safe_slug(row['name'])}.json"
        output_path = OUTPUT_DIR / filename
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        index_rows.append(
            {
                "batch_no": number,
                "json_file": filename,
                "penginapan_id": row["penginapan_id"],
                "name": row["name"],
                "property_type_final_after_p3": row["property_type_final_after_p3"],
                "completion_priority_data_focus": row["completion_priority_data_focus"],
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "current_price_lowest": row.get("price_lowest"),
                "current_overall_rating": row.get("overall_rating"),
                "current_reviews": row.get("reviews"),
                "q": query,
                "max_pages": DATE_CONFIG["max_pages"],
                "vacation_rentals": False,
                "note": "Targeted exact-name Google Hotels scrape; validate by name and coordinate before apply.",
            }
        )

    index = pd.DataFrame(index_rows)
    index.to_csv(INDEX_OUTPUT, index=False, encoding="utf-8-sig")
    summary = {
        "queue_input": str(QUEUE_PATH.relative_to(ROOT)),
        "output_dir": str(OUTPUT_DIR.relative_to(ROOT)),
        "target_count": int(len(index)),
        "batch_limit": BATCH_LIMIT,
        "target_priorities": TARGET_PRIORITIES,
        "target_types": TARGET_TYPES,
        "config": DATE_CONFIG,
        "vacation_rentals": False,
        "index_file": str(INDEX_OUTPUT.relative_to(ROOT)),
        "decision_notes": [
            "Batch pertama hanya hotel dan guest_house P1 agar biaya dan noise terkendali.",
            "Satu JSON berisi satu q karena actor Google Hotels Search memakai satu query per run.",
            "max_pages dibuat 3 karena query sudah exact name; jika hasil sering kosong, naikkan ke 5.",
            "Villa/vacation_rental ditunda batch berikutnya karena harga lebih variatif.",
        ],
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
