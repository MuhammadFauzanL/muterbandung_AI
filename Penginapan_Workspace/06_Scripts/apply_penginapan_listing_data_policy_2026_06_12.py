import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

INPUT_PATH = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_FEATURE_ENRICHED_WITH_REFINED_ATTENTION_2026-06-12.csv"
POLICY_OUTPUT = CURATED_DIR / "PENGINAPAN_LISTING_POLICY_AUDIT_2026-06-12.csv"
PRIMARY_OUTPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_CANDIDATE_AFTER_LISTING_POLICY_2026-06-12.csv"
SECONDARY_OUTPUT = CURATED_DIR / "PENGINAPAN_SECONDARY_OPTION_AFTER_LISTING_POLICY_2026-06-12.csv"
HELD_DETAIL_OUTPUT = CURATED_DIR / "PENGINAPAN_HELD_DETAIL_LISTING_AFTER_POLICY_2026-06-12.csv"
MANUAL_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_MANUAL_VALIDATION_QUEUE_AFTER_POLICY_2026-06-12.csv"
PRICE_TYPE_QUEUE_OUTPUT = CURATED_DIR / "PENGINAPAN_PRICE_TYPE_VALIDATION_QUEUE_2026-06-12.csv"
VALIDATOR_TASKS_OUTPUT = CURATED_DIR / "PENGINAPAN_VALIDATOR_TASKS_PRIORITY_2026-06-12.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_listing_policy_summary_2026-06-12.json"


BASE_COLUMNS = [
    "penginapan_id",
    "name",
    "property_type",
    "latitude",
    "longitude",
    "region_bucket",
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
    "capacity_min_estimated",
    "capacity_max_estimated",
    "capacity_confidence",
    "refined_detail_listing_group",
    "refined_detail_listing_action",
    "refined_price_status",
    "refined_price_action",
    "refined_low_quality_status",
    "refined_low_quality_action",
    "attention_level",
    "attention_reasons",
]


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def norm(value):
    return clean_text(value).lower()


def make_decision(row):
    property_type = norm(row.get("property_type"))
    detail_group = clean_text(row.get("refined_detail_listing_group"))
    price_action = clean_text(row.get("refined_price_action"))
    low_action = clean_text(row.get("refined_low_quality_action"))

    status = "primary_candidate"
    action = "allow_primary_ranking"
    reason = "data tidak terkena kebijakan hold/secondary"
    primary_allowed = True
    secondary_allowed = True
    manual_needed = False
    manual_topic = ""

    if price_action in {"manual_source_check", "review_type_or_capacity_before_ranking"}:
        status = "needs_price_type_validation"
        action = "hold_from_primary_until_checked"
        reason = "harga atau tipe properti perlu validasi sebelum masuk ranking utama"
        primary_allowed = False
        secondary_allowed = False
        manual_needed = True
        manual_topic = "price_type_validation"
    elif low_action in {"manual_source_completion", "manual_rating_price_completion"}:
        status = "hold_low_quality_manual_completion"
        action = "hold_from_primary_until_core_fields_completed"
        reason = "field inti atau sumber masih lemah"
        primary_allowed = False
        secondary_allowed = False
        manual_needed = True
        manual_topic = "low_quality_core_completion"
    elif detail_group == "room_level_detail":
        status = "held_child_room_level"
        action = "do_not_rank_as_parent"
        reason = "nama terlihat sebagai kamar, bukan properti utama"
        primary_allowed = False
        secondary_allowed = False
        manual_needed = False
        manual_topic = ""
    elif detail_group == "apartment_unit_detail":
        status = "secondary_apartment_unit"
        action = "secondary_only"
        reason = "unit apartemen boleh disimpan, tapi bukan kandidat utama"
        primary_allowed = False
        secondary_allowed = True
        manual_needed = False
        manual_topic = ""
    elif detail_group == "whole_house_or_large_unit":
        status = "secondary_large_unit"
        action = "secondary_for_group_or_villa_query"
        reason = "rumah/villa besar relevan untuk rombongan, bukan default utama"
        primary_allowed = False
        secondary_allowed = True
        manual_needed = False
        manual_topic = ""
    elif detail_group in {"villa_or_house_detail", "other_detail_listing"}:
        status = "needs_parent_child_validation"
        action = "hold_from_primary_until_parent_child_checked"
        reason = "nama terlihat detail/unit, perlu cek apakah punya parent"
        primary_allowed = False
        secondary_allowed = False
        manual_needed = True
        manual_topic = "parent_child_validation"
    elif property_type == "apartment":
        status = "secondary_apartment_property"
        action = "secondary_only"
        reason = "apartemen diposisikan sebagai opsi pendukung, bukan pilihan utama"
        primary_allowed = False
        secondary_allowed = True
        manual_needed = False
        manual_topic = ""
    elif low_action == "complete_amenities_or_image_if_needed":
        status = "primary_low_content_confidence"
        action = "allow_primary_with_low_content_confidence"
        reason = "boleh dipakai, tapi konten fasilitas/gambar belum kuat"
        primary_allowed = True
        secondary_allowed = True
        manual_needed = False
        manual_topic = ""

    if manual_topic == "price_type_validation":
        validator_priority = "P1"
        validator_question = "Apakah harga dan tipe properti ini benar dari sumber asli?"
        allowed_manual_decisions = "accept_high_price|fix_property_type|hold_from_primary|drop_if_invalid"
        suggested_default_decision = "hold_from_primary"
    elif manual_topic == "low_quality_core_completion":
        validator_priority = "P2"
        validator_question = "Apakah rating/harga/source bisa dilengkapi dari sumber tepercaya?"
        allowed_manual_decisions = "complete_fields|hold_low_quality|drop_if_invalid"
        suggested_default_decision = "hold_low_quality"
    elif manual_topic == "parent_child_validation":
        validator_priority = "P3"
        validator_question = "Apakah listing ini properti utama, child/unit, atau duplikat parent?"
        allowed_manual_decisions = "accept_as_parent|hold_as_child|map_to_parent|drop_if_invalid"
        suggested_default_decision = "hold_as_child"
    else:
        validator_priority = ""
        validator_question = ""
        allowed_manual_decisions = ""
        suggested_default_decision = ""

    return pd.Series(
        {
            "listing_policy_status": status,
            "listing_policy_action": action,
            "listing_policy_reason": reason,
            "primary_ranking_allowed": primary_allowed,
            "secondary_ranking_allowed": secondary_allowed,
            "manual_validation_needed": manual_needed,
            "manual_validation_topic": manual_topic,
            "validator_priority": validator_priority,
            "validator_question": validator_question,
            "allowed_manual_decisions": allowed_manual_decisions,
            "suggested_default_decision": suggested_default_decision,
        }
    )


def main():
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    policy = df.apply(make_decision, axis=1)
    audited = pd.concat([df, policy], axis=1)

    normalized_name = audited["name"].fillna("").astype(str).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    audited["same_name_count_in_dataset"] = normalized_name.map(normalized_name.value_counts()).fillna(0).astype(int)
    audited["manual_decision"] = ""
    audited["manual_note"] = ""

    output_cols = [col for col in BASE_COLUMNS if col in audited.columns] + [
        "same_name_count_in_dataset",
        "listing_policy_status",
        "listing_policy_action",
        "listing_policy_reason",
        "primary_ranking_allowed",
        "secondary_ranking_allowed",
        "manual_validation_needed",
        "manual_validation_topic",
        "validator_priority",
        "validator_question",
        "allowed_manual_decisions",
        "suggested_default_decision",
        "manual_decision",
        "manual_note",
    ]

    primary = audited[audited["primary_ranking_allowed"]].copy()
    secondary = audited[(~audited["primary_ranking_allowed"]) & audited["secondary_ranking_allowed"]].copy()
    held = audited[audited["listing_policy_status"].str.contains("held_child|secondary_|needs_parent_child", regex=True)].copy()
    manual_queue = audited[audited["manual_validation_needed"]].copy()
    price_type_queue = manual_queue[manual_queue["manual_validation_topic"].eq("price_type_validation")].copy()
    validator_tasks = manual_queue.sort_values(
        ["validator_priority", "same_name_count_in_dataset", "property_type", "name"],
        ascending=[True, False, True, True],
    ).copy()

    audited.to_csv(POLICY_OUTPUT, index=False, encoding="utf-8-sig")
    primary[output_cols].to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    secondary[output_cols].to_csv(SECONDARY_OUTPUT, index=False, encoding="utf-8-sig")
    held[output_cols].to_csv(HELD_DETAIL_OUTPUT, index=False, encoding="utf-8-sig")
    manual_queue[output_cols].to_csv(MANUAL_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")
    price_type_queue[output_cols].to_csv(PRICE_TYPE_QUEUE_OUTPUT, index=False, encoding="utf-8-sig")
    validator_tasks[output_cols].to_csv(VALIDATOR_TASKS_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "input_file": str(INPUT_PATH.relative_to(ROOT)),
        "row_count": int(len(audited)),
        "policy_status_counts": audited["listing_policy_status"].value_counts().to_dict(),
        "primary_candidate_count": int(len(primary)),
        "secondary_option_count": int(len(secondary)),
        "manual_validation_count": int(len(manual_queue)),
        "price_type_validation_count": int(len(price_type_queue)),
        "manual_validation_topic_counts": manual_queue["manual_validation_topic"].value_counts().to_dict(),
        "validator_priority_counts": manual_queue["validator_priority"].value_counts().to_dict(),
        "outputs": {
            "policy_audit": str(POLICY_OUTPUT.relative_to(ROOT)),
            "primary_candidate": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "secondary_option": str(SECONDARY_OUTPUT.relative_to(ROOT)),
            "held_detail_listing": str(HELD_DETAIL_OUTPUT.relative_to(ROOT)),
            "manual_validation_queue": str(MANUAL_QUEUE_OUTPUT.relative_to(ROOT)),
            "price_type_validation_queue": str(PRICE_TYPE_QUEUE_OUTPUT.relative_to(ROOT)),
            "validator_tasks_priority": str(VALIDATOR_TASKS_OUTPUT.relative_to(ROOT)),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
