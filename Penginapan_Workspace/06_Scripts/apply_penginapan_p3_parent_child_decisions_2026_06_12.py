import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P2_DECISIONS_2026-06-12.csv"
DECISIONS_OUTPUT = CURATED_DIR / "PENGINAPAN_P3_PARENT_CHILD_AUTO_DECISIONS_2026-06-12.csv"
AUDITED_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_WITH_P3_DECISIONS_2026-06-12.csv"
PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_CANDIDATE_AFTER_P3_DECISIONS_2026-06-12.csv"
SECONDARY_OUTPUT = CURATED_DIR / "PENGINAPAN_SECONDARY_OPTION_AFTER_P3_DECISIONS_2026-06-12.csv"
HELD_OUTPUT = CURATED_DIR / "PENGINAPAN_HELD_AFTER_P3_DECISIONS_2026-06-12.csv"
DROPPED_OUTPUT = CURATED_DIR / "PENGINAPAN_DROPPED_AFTER_P3_DECISIONS_2026-06-12.csv"
MAPPING_CANDIDATE_OUTPUT = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_MAPPING_CANDIDATE_AFTER_P3_2026-06-12.csv"
REMAINING_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_REMAINING_MANUAL_VALIDATION_QUEUE_AFTER_P3_2026-06-12.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_p3_parent_child_summary_2026-06-12.json"


ROOM_PATTERNS = [
    r"\bfull room\b",
    r"\bsingle room\b",
    r"\bdouble room\b",
    r"\btwin room\b",
    r"\btriple room\b",
    r"\bfamily room\b",
    r"\bexecutive room\b",
    r"\bdeluxe room\b",
    r"\bstandard room\b",
    r"\bstandard single room\b",
    r"\bbudget single room\b",
    r"\bfemale room\b",
    r"\broom only\b",
    r"\broom with\b",
    r"\bprivate bathroom\b",
]

APARTMENT_PATTERNS = [
    r"\bapartment\b",
    r"\bapartemen\b",
    r"\bapartement\b",
    r"\b1\s*br\b",
    r"\b2\s*br\b",
    r"\b3\s*br\b",
    r"\b1-bedroom apartment\b",
    r"\b2-bedroom apartment\b",
    r"\btwo-room apartment\b",
    r"\bwith balcony\b",
]

HOUSE_PATTERNS = [
    r"\bhouse\b",
    r"\bhome\b",
    r"\bhomestay\b",
    r"\bbungalow\b",
    r"\bcabin\b",
    r"\bglamping\b",
    r"\bcottage\b",
    r"\bguest house\b",
]

LARGE_UNIT_PATTERNS = [
    r"\b[4-9]\s*br\b",
    r"\b[4-9]-bedroom\b",
    r"\b[4-9]\s*bedroom\b",
    r"\binfinity pool\b",
    r"\bprivate pool\b",
]

VILLA_UNIT_PATTERNS = [
    r"\bone-bedroom villa\b",
    r"\btwo-bedroom villa\b",
    r"\bthree-bedroom villa\b",
    r"\bstandard villa\b",
    r"\bdeluxe villa\b",
    r"\bvilla one\b",
    r"\bvilla \d",
    r"\bvilla chw\b",
    r"\bvilla n\d",
]

GENERIC_DROP_PATTERNS = [
    r"^villa\s*-\s*two-bedroom house$",
]


EXPORT_COLUMNS = [
    "penginapan_id",
    "name",
    "property_type",
    "property_type_final",
    "property_type_final_after_p3",
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
    "ranking_tier_after_p2",
    "ranking_tier_after_p3",
    "primary_ranking_allowed_after_p3",
    "secondary_ranking_allowed_after_p3",
    "drop_from_dataset_after_p3",
    "manual_validation_needed_after_p3",
    "manual_validation_topic_after_p3",
    "p3_validation_applied",
    "p3_decision",
    "p3_note",
    "candidate_parent_name",
    "same_name_count_p3",
]


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def norm(value):
    return clean_text(value).lower()


def has_any(text, patterns):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def candidate_parent_name(name):
    text = clean_text(name)
    if " - " in text:
        return clean_text(text.split(" - ", 1)[0])
    replacements = [
        r"\b(one|two|three)-bedroom (villa|house|apartment)\b",
        r"\b\d+\s*br\b",
        r"\b\d+bedroom\b",
        r"\bdouble room\b",
        r"\bsingle room\b",
        r"\btwin room\b",
        r"\btriple room\b",
        r"\bfamily room\b",
        r"\bdeluxe room\b",
        r"\bstandard room\b",
    ]
    parent = text
    for pattern in replacements:
        parent = re.sub(pattern, "", parent, flags=re.IGNORECASE)
    return clean_text(parent.strip(" -"))


def quality_score(row):
    score = float(row.get("data_quality_score") or 0)
    for col in ["overall_rating", "reviews", "price_lowest", "hotel_review_count_analyzed"]:
        if not pd.isna(row.get(col)):
            score += 1
    return score


def choose_duplicate_keep_ids(p3):
    p3 = p3.copy()
    p3["_name_norm"] = p3["name"].map(norm)
    keep_ids = set()
    duplicate_names = p3["_name_norm"].value_counts()
    duplicate_names = set(duplicate_names[duplicate_names > 1].index)
    for name_norm, group in p3[p3["_name_norm"].isin(duplicate_names)].groupby("_name_norm"):
        ranked = group.copy()
        ranked["_quality_score"] = ranked.apply(quality_score, axis=1)
        ranked = ranked.sort_values(["_quality_score", "penginapan_id"], ascending=[False, True])
        keep_ids.add(ranked.iloc[0]["penginapan_id"])
    return keep_ids, duplicate_names


def classify_p3(row, duplicate_names, duplicate_keep_ids):
    name = clean_text(row.get("name"))
    text = norm(name)
    property_type_final = clean_text(row.get("property_type_final"))
    property_type_norm = norm(property_type_final)
    name_norm = norm(name)
    same_name_count = int(row.get("same_name_count_p3", 1))
    parent_name = candidate_parent_name(name)

    if name_norm in duplicate_names and row["penginapan_id"] not in duplicate_keep_ids:
        return pd.Series(
            {
                "property_type_final_after_p3": property_type_final,
                "ranking_tier_after_p3": "dropped_duplicate_detail_listing",
                "primary_ranking_allowed_after_p3": False,
                "secondary_ranking_allowed_after_p3": False,
                "drop_from_dataset_after_p3": True,
                "manual_validation_needed_after_p3": False,
                "manual_validation_topic_after_p3": "",
                "p3_validation_applied": True,
                "p3_decision": "drop_duplicate_detail_listing",
                "p3_note": "Nama detail/unit duplikat; satu record terbaik dipertahankan.",
                "candidate_parent_name": parent_name,
            }
        )

    if has_any(text, GENERIC_DROP_PATTERNS):
        decision = "hold_generic_detail_listing"
        tier = "held_generic_detail_listing"
        primary = False
        secondary = False
        drop = False
        final_type = property_type_final
        note = "Nama terlalu generik untuk dijadikan parent atau secondary tanpa sumber tambahan."
    elif has_any(text, ROOM_PATTERNS):
        decision = "hold_room_level_child"
        tier = "held_room_level_child"
        primary = False
        secondary = False
        drop = False
        final_type = property_type_final
        note = "Nama terlihat sebagai kamar/unit kecil, bukan properti utama."
    elif has_any(text, LARGE_UNIT_PATTERNS):
        decision = "secondary_large_unit"
        tier = "secondary_large_unit"
        primary = False
        secondary = True
        drop = False
        final_type = "vacation_rental" if property_type_norm in {"hotel", "apartment"} else property_type_final
        note = "Unit besar/rombongan disimpan sebagai secondary, bukan ranking utama."
    elif has_any(text, HOUSE_PATTERNS):
        decision = "secondary_house_or_cabin_unit"
        tier = "secondary_house_or_cabin_unit"
        primary = False
        secondary = True
        drop = False
        final_type = "vacation_rental" if property_type_norm in {"hotel", "apartment"} else property_type_final
        note = "House/cabin/homestay lebih cocok sebagai secondary unit/properti rombongan."
    elif has_any(text, APARTMENT_PATTERNS) or property_type_norm == "apartment":
        decision = "secondary_apartment_unit"
        tier = "secondary_apartment_unit"
        primary = False
        secondary = True
        drop = False
        final_type = "apartment"
        note = "Unit apartemen disimpan sebagai secondary, bukan ranking utama."
    elif has_any(text, VILLA_UNIT_PATTERNS) or property_type_norm == "villa":
        decision = "secondary_villa_unit"
        tier = "secondary_villa_unit"
        primary = False
        secondary = True
        drop = False
        final_type = "villa"
        note = "Villa/unit spesifik disimpan sebagai secondary, bukan parent utama."
    else:
        decision = "hold_parent_child_unclear"
        tier = "held_parent_child_unclear"
        primary = False
        secondary = False
        drop = False
        final_type = property_type_final
        note = "Belum cukup jelas dari nama; tahan dari ranking utama."

    return pd.Series(
        {
            "property_type_final_after_p3": final_type,
            "ranking_tier_after_p3": tier,
            "primary_ranking_allowed_after_p3": primary,
            "secondary_ranking_allowed_after_p3": secondary,
            "drop_from_dataset_after_p3": drop,
            "manual_validation_needed_after_p3": False,
            "manual_validation_topic_after_p3": "",
            "p3_validation_applied": True,
            "p3_decision": decision,
            "p3_note": note,
            "candidate_parent_name": parent_name,
        }
    )


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    df["property_type_final_after_p3"] = df["property_type_final"]
    df["ranking_tier_after_p3"] = df["ranking_tier_after_p2"]
    df["primary_ranking_allowed_after_p3"] = df["primary_ranking_allowed_after_p2"].astype(bool)
    df["secondary_ranking_allowed_after_p3"] = df["secondary_ranking_allowed_after_p2"].astype(bool)
    df["drop_from_dataset_after_p3"] = df["drop_from_dataset_after_p2"].astype(bool)
    df["manual_validation_needed_after_p3"] = df["manual_validation_needed_after_p2"].astype(bool)
    df["manual_validation_topic_after_p3"] = df["manual_validation_topic_after_p2"].fillna("")
    df["p3_validation_applied"] = False
    df["p3_decision"] = ""
    df["p3_note"] = ""
    df["candidate_parent_name"] = ""

    p3_mask = df["manual_validation_topic_after_p2"].eq("parent_child_validation")
    p3 = df[p3_mask].copy()
    p3_name_norm = p3["name"].map(norm)
    same_name_counts = p3_name_norm.map(p3_name_norm.value_counts()).fillna(1).astype(int)
    df.loc[p3_mask, "same_name_count_p3"] = same_name_counts.values
    df["same_name_count_p3"] = df["same_name_count_p3"].fillna(1).astype(int)

    duplicate_keep_ids, duplicate_names = choose_duplicate_keep_ids(p3)
    decisions = p3.apply(lambda row: classify_p3(row, duplicate_names, duplicate_keep_ids), axis=1)
    for col in decisions.columns:
        df.loc[p3_mask, col] = decisions[col].values

    decision_cols = [
        "penginapan_id",
        "name",
        "property_type",
        "property_type_final",
        "property_type_final_after_p3",
        "price_lowest",
        "overall_rating",
        "reviews",
        "same_name_count_p3",
        "candidate_parent_name",
        "p3_decision",
        "ranking_tier_after_p3",
        "primary_ranking_allowed_after_p3",
        "secondary_ranking_allowed_after_p3",
        "drop_from_dataset_after_p3",
        "p3_note",
    ]
    p3_decision_df = df[df["p3_validation_applied"]].copy()
    p3_decision_df[decision_cols].to_csv(DECISIONS_OUTPUT, index=False, encoding="utf-8-sig")

    primary = df[df["primary_ranking_allowed_after_p3"] & ~df["drop_from_dataset_after_p3"]].copy()
    secondary = df[
        (~df["primary_ranking_allowed_after_p3"])
        & df["secondary_ranking_allowed_after_p3"]
        & ~df["drop_from_dataset_after_p3"]
    ].copy()
    held = df[
        (~df["primary_ranking_allowed_after_p3"])
        & (~df["secondary_ranking_allowed_after_p3"])
        & (~df["drop_from_dataset_after_p3"])
    ].copy()
    dropped = df[df["drop_from_dataset_after_p3"]].copy()
    remaining_queue = df[df["manual_validation_needed_after_p3"] & ~df["drop_from_dataset_after_p3"]].copy()

    mapping_candidates = p3_decision_df[
        p3_decision_df["p3_decision"].isin(
            [
                "hold_room_level_child",
                "secondary_apartment_unit",
                "secondary_house_or_cabin_unit",
                "secondary_large_unit",
                "secondary_villa_unit",
                "hold_generic_detail_listing",
            ]
        )
    ].copy()

    export_columns = [col for col in EXPORT_COLUMNS if col in df.columns]
    df.to_csv(AUDITED_OUTPUT, index=False, encoding="utf-8-sig")
    primary[export_columns].to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    secondary[export_columns].to_csv(SECONDARY_OUTPUT, index=False, encoding="utf-8-sig")
    held[export_columns].to_csv(HELD_OUTPUT, index=False, encoding="utf-8-sig")
    dropped[export_columns].to_csv(DROPPED_OUTPUT, index=False, encoding="utf-8-sig")
    mapping_candidates[decision_cols].to_csv(MAPPING_CANDIDATE_OUTPUT, index=False, encoding="utf-8-sig")
    remaining_queue[export_columns].to_csv(REMAINING_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "row_count": int(len(df)),
        "p3_input_count": int(len(p3)),
        "p3_validation_applied_count": int(df["p3_validation_applied"].sum()),
        "primary_candidate_after_p3_count": int(len(primary)),
        "secondary_option_after_p3_count": int(len(secondary)),
        "held_after_p3_count": int(len(held)),
        "dropped_after_p3_count": int(len(dropped)),
        "remaining_manual_validation_count": int(len(remaining_queue)),
        "p3_decision_counts": p3_decision_df["p3_decision"].value_counts().to_dict(),
        "ranking_tier_after_p3_counts_for_decisions": p3_decision_df["ranking_tier_after_p3"].value_counts().to_dict(),
        "property_type_final_after_p3_counts_for_decisions": p3_decision_df["property_type_final_after_p3"].value_counts().to_dict(),
        "exact_duplicate_detail_rows_dropped": int(
            p3_decision_df["p3_decision"].eq("drop_duplicate_detail_listing").sum()
        ),
        "outputs": {
            "decisions": str(DECISIONS_OUTPUT.relative_to(ROOT)),
            "audit_with_p3_decisions": str(AUDITED_OUTPUT.relative_to(ROOT)),
            "primary_after_p3": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "secondary_after_p3": str(SECONDARY_OUTPUT.relative_to(ROOT)),
            "held_after_p3": str(HELD_OUTPUT.relative_to(ROOT)),
            "dropped_after_p3": str(DROPPED_OUTPUT.relative_to(ROOT)),
            "mapping_candidates": str(MAPPING_CANDIDATE_OUTPUT.relative_to(ROOT)),
            "remaining_manual_queue": str(REMAINING_QUEUE_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
