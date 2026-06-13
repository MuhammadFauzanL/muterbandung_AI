import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_2026-06-12.csv"
DECISIONS_OUTPUT = CURATED_DIR / "PENGINAPAN_P1_MANUAL_VALIDATION_DECISIONS_2026-06-12.csv"
AUDITED_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P1_DECISIONS_2026-06-12.csv"
PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_CANDIDATE_AFTER_P1_DECISIONS_2026-06-12.csv"
SECONDARY_OUTPUT = CURATED_DIR / "PENGINAPAN_SECONDARY_OPTION_AFTER_P1_DECISIONS_2026-06-12.csv"
DROPPED_OUTPUT = CURATED_DIR / "PENGINAPAN_DROPPED_AFTER_P1_DECISIONS_2026-06-12.csv"
REMAINING_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_REMAINING_MANUAL_VALIDATION_QUEUE_AFTER_P1_2026-06-12.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_p1_manual_validation_summary_2026-06-12.json"


DECISIONS = [
    {
        "penginapan_id": "LODGE-00004",
        "manual_decision": "hold_from_primary",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "held_child_room_level",
        "primary_after_p1": False,
        "secondary_after_p1": False,
        "drop_after_p1": False,
        "manual_note": "Harga benar, tetapi ini unit kamar child, bukan properti utama.",
    },
    {
        "penginapan_id": "LODGE-00010",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "primary_high_price_validated",
        "primary_after_p1": True,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga Wildan Guesthouse sudah divalidasi benar.",
    },
    {
        "penginapan_id": "LODGE-00401",
        "manual_decision": "fix_property_type",
        "manual_corrected_property_type": "vacation_rental",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Rumah/villa 5 kamar berkapasitas besar, bukan hotel reguler.",
    },
    {
        "penginapan_id": "LODGE-00562",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga wajar untuk homestay 4 kamar/rumah besar.",
    },
    {
        "penginapan_id": "LODGE-00564",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga benar, akomodasi disewakan sebagai rumah utuh/kapasitas besar.",
    },
    {
        "penginapan_id": "LODGE-00569",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "primary_high_price_validated",
        "primary_after_p1": True,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga benar sesuai scrape OTA, meskipun nama mengandung kata murah.",
    },
    {
        "penginapan_id": "LODGE-00898",
        "manual_decision": "hold_from_primary",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Unit besar 6 kamar; lebih tepat sebagai secondary large unit.",
    },
    {
        "penginapan_id": "LODGE-00919",
        "manual_decision": "drop_if_invalid",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "dropped_duplicate",
        "primary_after_p1": False,
        "secondary_after_p1": False,
        "drop_after_p1": True,
        "manual_note": "Duplikat Guest House Omah Ningrat Bandung; gunakan LODGE-01255.",
    },
    {
        "penginapan_id": "LODGE-01255",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga wajar untuk rumah 3 kamar; gunakan data ini, bukan LODGE-00919.",
    },
    {
        "penginapan_id": "LODGE-01292",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "primary_high_price_validated",
        "primary_after_p1": True,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga Ouma Guest House sudah divalidasi benar.",
    },
    {
        "penginapan_id": "LODGE-01351",
        "manual_decision": "fix_property_type",
        "manual_corrected_property_type": "vacation_rental",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Cottage/house, bukan hotel reguler.",
    },
    {
        "penginapan_id": "LODGE-01396",
        "manual_decision": "fix_property_type",
        "manual_corrected_property_type": "apartment",
        "ranking_tier_after_p1": "secondary_aparthotel",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Aparthotel/apartment; jadikan opsi secondary.",
    },
    {
        "penginapan_id": "LODGE-01443",
        "manual_decision": "accept_high_price",
        "manual_corrected_property_type": "",
        "ranking_tier_after_p1": "secondary_large_unit",
        "primary_after_p1": False,
        "secondary_after_p1": True,
        "drop_after_p1": False,
        "manual_note": "Harga benar; faktanya rumah 3 kamar sehingga masuk akal sebagai large unit.",
    },
]


EXPORT_COLUMNS = [
    "penginapan_id",
    "name",
    "property_type",
    "property_type_final",
    "latitude",
    "longitude",
    "region_bucket",
    "overall_rating",
    "reviews",
    "price_lowest",
    "price_display",
    "data_quality_score",
    "data_quality_label",
    "hotel_review_count_analyzed",
    "hotel_adjusted_sentiment_score",
    "hotel_adjusted_sentiment_label",
    "hotel_review_confidence_label",
    "capacity_min_estimated",
    "capacity_max_estimated",
    "capacity_confidence",
    "listing_policy_status",
    "listing_policy_action",
    "manual_decision",
    "manual_note",
    "ranking_tier_after_p1",
    "primary_ranking_allowed_after_p1",
    "secondary_ranking_allowed_after_p1",
    "drop_from_dataset_after_p1",
    "manual_validation_needed_after_p1",
    "manual_validation_topic_after_p1",
]


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    decisions = pd.DataFrame(DECISIONS)
    decisions.to_csv(DECISIONS_OUTPUT, index=False, encoding="utf-8-sig")

    df["property_type_final"] = df["property_type"]
    df["manual_decision"] = ""
    df["manual_note"] = ""
    df["ranking_tier_after_p1"] = df["listing_policy_status"]
    df["primary_ranking_allowed_after_p1"] = df["primary_ranking_allowed"].astype(bool)
    df["secondary_ranking_allowed_after_p1"] = df["secondary_ranking_allowed"].astype(bool)
    df["drop_from_dataset_after_p1"] = False
    df["manual_validation_needed_after_p1"] = df["manual_validation_needed"].astype(bool)
    df["manual_validation_topic_after_p1"] = df["manual_validation_topic"].fillna("")
    df["p1_validation_applied"] = False

    decision_map = decisions.set_index("penginapan_id").to_dict("index")
    for idx, row in df.iterrows():
        item = decision_map.get(row["penginapan_id"])
        if not item:
            continue

        corrected_type = str(item.get("manual_corrected_property_type", "")).strip()
        if corrected_type:
            df.at[idx, "property_type_final"] = corrected_type
        df.at[idx, "manual_decision"] = item["manual_decision"]
        df.at[idx, "manual_note"] = item["manual_note"]
        df.at[idx, "ranking_tier_after_p1"] = item["ranking_tier_after_p1"]
        df.at[idx, "primary_ranking_allowed_after_p1"] = bool(item["primary_after_p1"])
        df.at[idx, "secondary_ranking_allowed_after_p1"] = bool(item["secondary_after_p1"])
        df.at[idx, "drop_from_dataset_after_p1"] = bool(item["drop_after_p1"])
        df.at[idx, "manual_validation_needed_after_p1"] = False
        df.at[idx, "manual_validation_topic_after_p1"] = ""
        df.at[idx, "p1_validation_applied"] = True

    primary = df[df["primary_ranking_allowed_after_p1"] & ~df["drop_from_dataset_after_p1"]].copy()
    secondary = df[
        (~df["primary_ranking_allowed_after_p1"])
        & df["secondary_ranking_allowed_after_p1"]
        & ~df["drop_from_dataset_after_p1"]
    ].copy()
    dropped = df[df["drop_from_dataset_after_p1"]].copy()
    remaining_queue = df[df["manual_validation_needed_after_p1"] & ~df["drop_from_dataset_after_p1"]].copy()

    export_columns = [col for col in EXPORT_COLUMNS if col in df.columns]
    df.to_csv(AUDITED_OUTPUT, index=False, encoding="utf-8-sig")
    primary[export_columns].to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    secondary[export_columns].to_csv(SECONDARY_OUTPUT, index=False, encoding="utf-8-sig")
    dropped[export_columns].to_csv(DROPPED_OUTPUT, index=False, encoding="utf-8-sig")
    remaining_queue[export_columns].to_csv(REMAINING_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "decision_count": int(len(decisions)),
        "row_count": int(len(df)),
        "p1_validation_applied_count": int(df["p1_validation_applied"].sum()),
        "primary_candidate_after_p1_count": int(len(primary)),
        "secondary_option_after_p1_count": int(len(secondary)),
        "dropped_after_p1_count": int(len(dropped)),
        "remaining_manual_validation_count": int(len(remaining_queue)),
        "remaining_manual_validation_topic_counts": remaining_queue["manual_validation_topic_after_p1"].value_counts().to_dict(),
        "manual_decision_counts": df.loc[df["p1_validation_applied"], "manual_decision"].value_counts().to_dict(),
        "ranking_tier_after_p1_counts_for_decisions": df.loc[df["p1_validation_applied"], "ranking_tier_after_p1"].value_counts().to_dict(),
        "property_type_final_counts_for_decisions": df.loc[df["p1_validation_applied"], "property_type_final"].value_counts().to_dict(),
        "outputs": {
            "decisions": str(DECISIONS_OUTPUT.relative_to(ROOT)),
            "audit_with_p1_decisions": str(AUDITED_OUTPUT.relative_to(ROOT)),
            "primary_after_p1": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "secondary_after_p1": str(SECONDARY_OUTPUT.relative_to(ROOT)),
            "dropped_after_p1": str(DROPPED_OUTPUT.relative_to(ROOT)),
            "remaining_manual_queue": str(REMAINING_QUEUE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
