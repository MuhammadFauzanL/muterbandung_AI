from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_SCRAPE_TARGETS_PARENT_MASTER_2026-06-05.csv"
OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FLAGGED_DETAIL_NAME_2026-06-05.csv"
SUMMARY = CURATED_DIR / "penginapan_review_targets_flagged_detail_name_summary_2026-06-05.json"


PATTERNS = {
    "room_label": re.compile(r"\b(room|kamar)\b", re.IGNORECASE),
    "apartment_unit": re.compile(
        r"\b(apartment|apartemen|studio|apt|1br|2br|3br|4br|one-bedroom|two-bedroom|three-bedroom|four-bedroom)\b",
        re.IGNORECASE,
    ),
    "villa_house_unit": re.compile(r"\b(villa|house|bedroom|private pool|bedrooms)\b", re.IGNORECASE),
    "ota_brand_or_operator": re.compile(
        r"\b(travelio|reddoorz|reddoorz|oyo|airy|collection o|super oyo|sans|zuzu|nemui)\b",
        re.IGNORECASE,
    ),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def classify_name(name: str, property_type: str) -> tuple[str, str]:
    hits = [label for label, pattern in PATTERNS.items() if pattern.search(name or "")]
    hit_set = set(hits)

    if "room_label" in hit_set and property_type in {"hotel", "guest_house"}:
        return "hold_room_label", "Nama terlihat seperti tipe kamar hotel/guest house."
    if "apartment_unit" in hit_set:
        return "hold_unit_or_bedroom_listing", "Nama terlihat seperti unit apartment/studio/BR/bedroom."
    if "villa_house_unit" in hit_set and property_type in {"villa", "vacation_rental", "guest_house"}:
        return "review_villa_or_house_unit", "Bisa properti sewa utuh, tapi perlu cek match Google Maps."
    if "ota_brand_or_operator" in hit_set:
        return "review_ota_name", "Nama membawa brand/operator OTA, perlu cek hasil pencarian."
    return "review_other_detail_name", "Kena flag detail-name, tetapi polanya tidak masuk kelompok utama."


def main() -> None:
    targets = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    flagged = targets[targets["name_looks_detail_listing"].eq("True")].copy()

    classifications = flagged.apply(
        lambda row: classify_name(row.get("name", ""), row.get("property_type", "")),
        axis=1,
    )
    flagged["flag_group"] = [item[0] for item in classifications]
    flagged["flag_reason"] = [item[1] for item in classifications]
    flagged["suggested_action"] = flagged["flag_group"].map(
        {
            "hold_room_label": "tahan_dulu_jangan_scrape_massal",
            "hold_unit_or_bedroom_listing": "tahan_dulu_jangan_scrape_massal",
            "review_villa_or_house_unit": "cek_manual_atau_batch_test",
            "review_ota_name": "cek_manual_atau_batch_test",
            "review_other_detail_name": "cek_manual_ringan",
        }
    )

    columns = [
        "review_target_id",
        "penginapan_id",
        "name",
        "property_type",
        "review_scrape_priority",
        "overall_rating",
        "reviews_existing",
        "review_confidence_label",
        "data_quality_score",
        "has_final_child_listing",
        "final_child_count",
        "name_looks_detail_listing",
        "flag_group",
        "flag_reason",
        "suggested_action",
        "google_maps_search_query",
        "google_maps_search_url",
    ]
    flagged = flagged[columns].sort_values(
        ["flag_group", "review_scrape_priority", "property_type", "name"],
        ascending=[True, True, True, True],
    )
    flagged.to_csv(OUTPUT, index=False)

    summary = {
        "generated_at": now_iso(),
        "input_path": str(INPUT),
        "output_path": str(OUTPUT),
        "total_review_targets": int(len(targets)),
        "flagged_detail_name_rows": int(len(flagged)),
        "property_type_counts": flagged["property_type"].value_counts(dropna=False).to_dict(),
        "review_priority_counts": flagged["review_scrape_priority"].value_counts(dropna=False).to_dict(),
        "flag_group_counts": flagged["flag_group"].value_counts(dropna=False).to_dict(),
        "suggested_action_counts": flagged["suggested_action"].value_counts(dropna=False).to_dict(),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"flagged_rows={summary['flagged_detail_name_rows']}")
    print(f"output={OUTPUT}")
    print(f"flag_group_counts={summary['flag_group_counts']}")
    print(f"suggested_action_counts={summary['suggested_action_counts']}")


if __name__ == "__main__":
    main()
