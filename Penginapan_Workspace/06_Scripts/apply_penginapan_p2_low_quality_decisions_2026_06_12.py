import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P1_DECISIONS_2026-06-12.csv"
DECISIONS_OUTPUT = CURATED_DIR / "PENGINAPAN_P2_LOW_QUALITY_DECISIONS_2026-06-12.csv"
AUDITED_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P2_DECISIONS_2026-06-12.csv"
PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_CANDIDATE_AFTER_P2_DECISIONS_2026-06-12.csv"
SECONDARY_OUTPUT = CURATED_DIR / "PENGINAPAN_SECONDARY_OPTION_AFTER_P2_DECISIONS_2026-06-12.csv"
HELD_OUTPUT = CURATED_DIR / "PENGINAPAN_HELD_AFTER_P2_DECISIONS_2026-06-12.csv"
DROPPED_OUTPUT = CURATED_DIR / "PENGINAPAN_DROPPED_AFTER_P2_DECISIONS_2026-06-12.csv"
REMAINING_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_REMAINING_MANUAL_VALIDATION_QUEUE_AFTER_P2_2026-06-12.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_p2_low_quality_summary_2026-06-12.json"


DECISIONS = [
    {
        "penginapan_id": "LODGE-00456",
        "p2_decision": "hold_low_quality",
        "ranking_tier_after_p2": "held_low_quality_no_core_fields",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": False,
        "p2_note": "Hotel/OYO tanpa rating, review, dan harga; tahan dari ranking.",
    },
    {
        "penginapan_id": "LODGE-00457",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00458",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00459",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00460",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00461",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00462",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00463",
        "p2_decision": "hold_low_quality",
        "ranking_tier_after_p2": "held_low_quality_no_core_fields",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": False,
        "p2_note": "Guest house tanpa rating, review, dan harga; tahan dari ranking.",
    },
    {
        "penginapan_id": "LODGE-00464",
        "p2_decision": "hold_low_quality_generic_name",
        "ranking_tier_after_p2": "held_low_quality_generic_name",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": False,
        "p2_note": "Nama terlalu umum dan core fields kosong; tahan dari ranking.",
    },
    {
        "penginapan_id": "LODGE-00465",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00466",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00467",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00468",
        "p2_decision": "drop_low_quality_generic_name",
        "ranking_tier_after_p2": "dropped_low_quality_generic_name",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": True,
        "p2_note": "Nama terlalu umum: Sewa Apartemen Bandung; core fields kosong.",
    },
    {
        "penginapan_id": "LODGE-00469",
        "p2_decision": "secondary_low_quality_villa",
        "ranking_tier_after_p2": "secondary_low_quality_villa",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Villa tanpa core fields; simpan sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-00470",
        "p2_decision": "drop_low_quality_incomplete_name",
        "ranking_tier_after_p2": "dropped_low_quality_incomplete_name",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": True,
        "p2_note": "Nama tidak lengkap dan core fields kosong.",
    },
    {
        "penginapan_id": "LODGE-01651",
        "p2_decision": "drop_low_quality_generic_name",
        "ranking_tier_after_p2": "dropped_low_quality_generic_name",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": True,
        "p2_note": "Nama terlalu umum: Andy; core fields kosong.",
    },
    {
        "penginapan_id": "LODGE-01652",
        "p2_decision": "secondary_low_quality_apartment",
        "ranking_tier_after_p2": "secondary_low_quality_apartment",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Apartemen/OYO tanpa core fields; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-01654",
        "p2_decision": "hold_low_quality",
        "ranking_tier_after_p2": "held_low_quality_no_core_fields",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": False,
        "p2_note": "Hotel/OYO tanpa rating, review, dan harga; tahan dari ranking.",
    },
    {
        "penginapan_id": "LODGE-01655",
        "p2_decision": "secondary_low_quality_home",
        "ranking_tier_after_p2": "secondary_low_quality_home",
        "primary_after_p2": False,
        "secondary_after_p2": True,
        "drop_after_p2": False,
        "p2_note": "Nama mengarah ke home, tetapi core fields kosong; simpan hanya sebagai secondary low confidence.",
    },
    {
        "penginapan_id": "LODGE-01656",
        "p2_decision": "drop_low_quality_suspicious_name",
        "ranking_tier_after_p2": "dropped_low_quality_suspicious_name",
        "primary_after_p2": False,
        "secondary_after_p2": False,
        "drop_after_p2": True,
        "p2_note": "Nama mencurigakan dan core fields kosong.",
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
    "listing_policy_status",
    "ranking_tier_after_p1",
    "ranking_tier_after_p2",
    "primary_ranking_allowed_after_p2",
    "secondary_ranking_allowed_after_p2",
    "drop_from_dataset_after_p2",
    "manual_validation_needed_after_p2",
    "manual_validation_topic_after_p2",
    "p1_validation_applied",
    "p2_validation_applied",
    "manual_decision",
    "manual_note",
    "p2_decision",
    "p2_note",
]


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    decisions = pd.DataFrame(DECISIONS)
    decisions.to_csv(DECISIONS_OUTPUT, index=False, encoding="utf-8-sig")

    df["ranking_tier_after_p2"] = df["ranking_tier_after_p1"]
    df["primary_ranking_allowed_after_p2"] = df["primary_ranking_allowed_after_p1"].astype(bool)
    df["secondary_ranking_allowed_after_p2"] = df["secondary_ranking_allowed_after_p1"].astype(bool)
    df["drop_from_dataset_after_p2"] = df["drop_from_dataset_after_p1"].astype(bool)
    df["manual_validation_needed_after_p2"] = df["manual_validation_needed_after_p1"].astype(bool)
    df["manual_validation_topic_after_p2"] = df["manual_validation_topic_after_p1"].fillna("")
    df["p2_validation_applied"] = False
    df["p2_decision"] = ""
    df["p2_note"] = ""

    decision_map = decisions.set_index("penginapan_id").to_dict("index")
    for idx, row in df.iterrows():
        item = decision_map.get(row["penginapan_id"])
        if not item:
            continue

        df.at[idx, "ranking_tier_after_p2"] = item["ranking_tier_after_p2"]
        df.at[idx, "primary_ranking_allowed_after_p2"] = bool(item["primary_after_p2"])
        df.at[idx, "secondary_ranking_allowed_after_p2"] = bool(item["secondary_after_p2"])
        df.at[idx, "drop_from_dataset_after_p2"] = bool(item["drop_after_p2"])
        df.at[idx, "manual_validation_needed_after_p2"] = False
        df.at[idx, "manual_validation_topic_after_p2"] = ""
        df.at[idx, "p2_validation_applied"] = True
        df.at[idx, "p2_decision"] = item["p2_decision"]
        df.at[idx, "p2_note"] = item["p2_note"]

    primary = df[df["primary_ranking_allowed_after_p2"] & ~df["drop_from_dataset_after_p2"]].copy()
    secondary = df[
        (~df["primary_ranking_allowed_after_p2"])
        & df["secondary_ranking_allowed_after_p2"]
        & ~df["drop_from_dataset_after_p2"]
    ].copy()
    held = df[
        (~df["primary_ranking_allowed_after_p2"])
        & (~df["secondary_ranking_allowed_after_p2"])
        & (~df["drop_from_dataset_after_p2"])
    ].copy()
    dropped = df[df["drop_from_dataset_after_p2"]].copy()
    remaining_queue = df[df["manual_validation_needed_after_p2"] & ~df["drop_from_dataset_after_p2"]].copy()

    export_columns = [col for col in EXPORT_COLUMNS if col in df.columns]
    df.to_csv(AUDITED_OUTPUT, index=False, encoding="utf-8-sig")
    primary[export_columns].to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    secondary[export_columns].to_csv(SECONDARY_OUTPUT, index=False, encoding="utf-8-sig")
    held[export_columns].to_csv(HELD_OUTPUT, index=False, encoding="utf-8-sig")
    dropped[export_columns].to_csv(DROPPED_OUTPUT, index=False, encoding="utf-8-sig")
    remaining_queue[export_columns].to_csv(REMAINING_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "decision_count": int(len(decisions)),
        "row_count": int(len(df)),
        "p2_validation_applied_count": int(df["p2_validation_applied"].sum()),
        "primary_candidate_after_p2_count": int(len(primary)),
        "secondary_option_after_p2_count": int(len(secondary)),
        "held_after_p2_count": int(len(held)),
        "dropped_after_p2_count": int(len(dropped)),
        "remaining_manual_validation_count": int(len(remaining_queue)),
        "remaining_manual_validation_topic_counts": remaining_queue["manual_validation_topic_after_p2"].value_counts().to_dict(),
        "p2_decision_counts": df.loc[df["p2_validation_applied"], "p2_decision"].value_counts().to_dict(),
        "ranking_tier_after_p2_counts_for_decisions": df.loc[df["p2_validation_applied"], "ranking_tier_after_p2"].value_counts().to_dict(),
        "outputs": {
            "decisions": str(DECISIONS_OUTPUT.relative_to(ROOT)),
            "audit_with_p2_decisions": str(AUDITED_OUTPUT.relative_to(ROOT)),
            "primary_after_p2": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "secondary_after_p2": str(SECONDARY_OUTPUT.relative_to(ROOT)),
            "held_after_p2": str(HELD_OUTPUT.relative_to(ROOT)),
            "dropped_after_p2": str(DROPPED_OUTPUT.relative_to(ROOT)),
            "remaining_manual_queue": str(REMAINING_QUEUE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
