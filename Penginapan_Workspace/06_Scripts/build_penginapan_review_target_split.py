from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

TARGETS_INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_SCRAPE_TARGETS_PARENT_MASTER_2026-06-05.csv"
FLAGGED_INPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FLAGGED_DETAIL_NAME_2026-06-05.csv"

READY_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_READY_2026-06-05.csv"
HELD_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_HELD_CHILD_2026-06-05.csv"
NEEDS_REVIEW_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_NEEDS_REVIEW_2026-06-05.csv"
NEEDS_REVIEW_AUDIT_OUTPUT = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_NEEDS_REVIEW_AUDIT_2026-06-05.csv"
SUMMARY_OUTPUT = CURATED_DIR / "penginapan_review_targets_split_summary_2026-06-05.json"


HELD_GROUPS = {"hold_room_label", "hold_unit_or_bedroom_listing"}
NEEDS_REVIEW_GROUPS = {"review_villa_or_house_unit", "review_other_detail_name"}

DETAIL_WORDS = re.compile(
    r"\b("
    r"standard|deluxe|superior|suite|room|kamar|studio|"
    r"double|twin|triple|queen|king|family|with|view|terrace|garden|"
    r"1br|2br|3br|4br|5br|6br|7br|8br|one-bedroom|two-bedroom|three-bedroom|"
    r"four-bedroom|bedroom|bedrooms|private|pool|house|villa"
    r")\b",
    re.IGNORECASE,
)
NON_WORDS = re.compile(r"[^a-z0-9]+", re.IGNORECASE)
PARENT_DETAIL_SUFFIX = re.compile(
    r"\s-\s.*\b("
    r"room|kamar|studio|1br|2br|3br|4br|5br|6br|7br|8br|"
    r"bedroom|bedrooms|double|twin|triple|standard|deluxe|superior|suite|"
    r"family|bungalow|tent|cabin|villa with|villa$"
    r")\b",
    re.IGNORECASE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_name(value: str) -> str:
    text = str(value or "").lower()
    text = text.replace("&", " and ")
    text = NON_WORDS.sub(" ", text)
    return " ".join(text.split())


def base_name(value: str) -> str:
    text = str(value or "")
    first_part = text.split(" - ", 1)[0]
    cleaned = DETAIL_WORDS.sub(" ", first_part)
    cleaned = normalize_name(cleaned)
    return cleaned


def token_set(value: str) -> set[str]:
    return {token for token in normalize_name(value).split() if len(token) >= 3}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def parse_float(value: object) -> float | None:
    try:
        if value in {"", None}:
            return None
        parsed = float(value)
        if math.isnan(parsed):
            return None
        return parsed
    except (TypeError, ValueError):
        return None


def distance_km(lat1: object, lon1: object, lat2: object, lon2: object) -> float | None:
    first_lat = parse_float(lat1)
    first_lon = parse_float(lon1)
    second_lat = parse_float(lat2)
    second_lon = parse_float(lon2)
    if None in {first_lat, first_lon, second_lat, second_lon}:
        return None

    radius = 6371.0
    phi1 = math.radians(first_lat)
    phi2 = math.radians(second_lat)
    d_phi = math.radians(second_lat - first_lat)
    d_lambda = math.radians(second_lon - first_lon)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parent_score(child: pd.Series, parent: pd.Series) -> dict[str, object]:
    child_base = base_name(child.get("name", ""))
    parent_base = base_name(parent.get("name", ""))
    name_ratio = SequenceMatcher(None, child_base, parent_base).ratio() if child_base and parent_base else 0.0
    token_score = jaccard(token_set(child_base), token_set(parent_base))
    dist = distance_km(
        child.get("latitude", ""),
        child.get("longitude", ""),
        parent.get("latitude", ""),
        parent.get("longitude", ""),
    )
    distance_score = 0.0
    if dist is not None:
        if dist <= 0.1:
            distance_score = 1.0
        elif dist <= 0.5:
            distance_score = 0.75
        elif dist <= 1.0:
            distance_score = 0.5
        elif dist <= 2.0:
            distance_score = 0.25

    score = (name_ratio * 0.45) + (token_score * 0.35) + (distance_score * 0.20)
    return {
        "parent_candidate_id": parent.get("penginapan_id", ""),
        "parent_candidate_name": parent.get("name", ""),
        "parent_candidate_property_type": parent.get("property_type", ""),
        "parent_candidate_distance_km": None if dist is None else round(dist, 4),
        "parent_candidate_name_ratio": round(name_ratio, 4),
        "parent_candidate_token_score": round(token_score, 4),
        "parent_candidate_score": round(score, 4),
    }


def find_best_parent_candidates(needs_review: pd.DataFrame, ready: pd.DataFrame) -> pd.DataFrame:
    parent_pool = ready.copy()
    parent_pool = parent_pool[
        ~parent_pool["name"].fillna("").map(lambda value: bool(PARENT_DETAIL_SUFFIX.search(str(value))))
    ].copy()
    parent_pool["_base_name"] = parent_pool["name"].map(base_name)
    parent_pool["_tokens"] = parent_pool["_base_name"].map(token_set)

    rows = []
    for _, child in needs_review.iterrows():
        child_base = base_name(child.get("name", ""))
        child_tokens = token_set(child_base)
        if not child_tokens:
            candidates = parent_pool.head(0)
        else:
            candidates = parent_pool[
                parent_pool["_tokens"].map(lambda tokens: bool(tokens & child_tokens))
            ].copy()

        if len(candidates) > 80:
            candidates = candidates.head(80)

        best = None
        for _, parent in candidates.iterrows():
            score = parent_score(child, parent)
            if best is None or score["parent_candidate_score"] > best["parent_candidate_score"]:
                best = score

        row = child.to_dict()
        if best is None:
            best = {
                "parent_candidate_id": "",
                "parent_candidate_name": "",
                "parent_candidate_property_type": "",
                "parent_candidate_distance_km": "",
                "parent_candidate_name_ratio": 0.0,
                "parent_candidate_token_score": 0.0,
                "parent_candidate_score": 0.0,
            }
        row.update(best)

        score_value = float(row["parent_candidate_score"])
        distance = row.get("parent_candidate_distance_km", "")
        close_distance = isinstance(distance, (int, float)) and distance <= 0.5
        if score_value >= 0.72 and close_distance:
            row["audit_recommendation"] = "candidate_child_to_parent"
            row["audit_reason"] = "Nama mirip dan koordinat dekat dengan kandidat parent."
        elif score_value >= 0.55:
            row["audit_recommendation"] = "needs_manual_check"
            row["audit_reason"] = "Ada kandidat mirip, tetapi bukti belum cukup kuat."
        else:
            row["audit_recommendation"] = "candidate_standalone_or_unclear"
            row["audit_reason"] = "Belum ada kandidat parent yang cukup kuat dari data saat ini."
        rows.append(row)

    audit = pd.DataFrame(rows)
    sort_columns = ["audit_recommendation", "parent_candidate_score", "property_type", "name"]
    return audit.sort_values(sort_columns, ascending=[True, False, True, True])


def add_manual_columns(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()
    if "manual_decision" not in output.columns:
        output["manual_decision"] = ""
    if "manual_note" not in output.columns:
        output["manual_note"] = ""
    return output


def main() -> None:
    targets = pd.read_csv(TARGETS_INPUT, dtype=str, keep_default_na=False)
    flagged = pd.read_csv(FLAGGED_INPUT, dtype=str, keep_default_na=False)

    flagged_lookup = flagged.set_index("review_target_id")[["flag_group", "flag_reason", "suggested_action"]]
    merged = targets.merge(
        flagged_lookup,
        left_on="review_target_id",
        right_index=True,
        how="left",
    )
    merged[["flag_group", "flag_reason", "suggested_action"]] = merged[
        ["flag_group", "flag_reason", "suggested_action"]
    ].fillna("")

    held_mask = merged["flag_group"].isin(HELD_GROUPS)
    needs_review_mask = merged["flag_group"].isin(NEEDS_REVIEW_GROUPS)

    held = merged[held_mask].copy()
    held["split_status"] = "held_child"
    held["split_reason"] = "Nama sudah terlihat sebagai kamar/unit/detail listing, jadi ditahan dari scraping massal."

    needs_review = merged[needs_review_mask].copy()
    needs_review["split_status"] = "needs_review"
    needs_review["split_reason"] = "Nama masih abu-abu; perlu audit parent/child sebelum scraping."

    ready = merged[~held_mask & ~needs_review_mask].copy()
    ready["split_status"] = "ready"
    ready["split_reason"] = "Tidak masuk kelompok detail-name yang perlu ditahan."

    ready = add_manual_columns(ready)
    held = add_manual_columns(held)
    needs_review = add_manual_columns(needs_review)
    needs_review_audit = add_manual_columns(find_best_parent_candidates(needs_review, ready))

    common_sort = ["review_scrape_priority", "property_type", "name"]
    ready.sort_values(common_sort, ascending=[True, True, True]).to_csv(READY_OUTPUT, index=False)
    held.sort_values(["flag_group", *common_sort], ascending=[True, True, True, True]).to_csv(HELD_OUTPUT, index=False)
    needs_review.sort_values(["flag_group", *common_sort], ascending=[True, True, True, True]).to_csv(
        NEEDS_REVIEW_OUTPUT,
        index=False,
    )
    needs_review_audit.to_csv(NEEDS_REVIEW_AUDIT_OUTPUT, index=False)

    summary = {
        "generated_at": now_iso(),
        "input_path": str(TARGETS_INPUT),
        "flagged_input_path": str(FLAGGED_INPUT),
        "total_review_targets": int(len(targets)),
        "flagged_rows": int(len(flagged)),
        "ready_rows": int(len(ready)),
        "held_child_rows": int(len(held)),
        "needs_review_rows": int(len(needs_review)),
        "held_child_flag_group_counts": held["flag_group"].value_counts(dropna=False).to_dict(),
        "needs_review_flag_group_counts": needs_review["flag_group"].value_counts(dropna=False).to_dict(),
        "needs_review_audit_recommendation_counts": needs_review_audit["audit_recommendation"]
        .value_counts(dropna=False)
        .to_dict(),
        "outputs": {
            "ready": str(READY_OUTPUT),
            "held_child": str(HELD_OUTPUT),
            "needs_review": str(NEEDS_REVIEW_OUTPUT),
            "needs_review_audit": str(NEEDS_REVIEW_AUDIT_OUTPUT),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"total_review_targets={summary['total_review_targets']}")
    print(f"ready_rows={summary['ready_rows']}")
    print(f"held_child_rows={summary['held_child_rows']}")
    print(f"needs_review_rows={summary['needs_review_rows']}")
    print(f"held_child_flag_group_counts={summary['held_child_flag_group_counts']}")
    print(f"needs_review_flag_group_counts={summary['needs_review_flag_group_counts']}")
    print(f"needs_review_audit_recommendation_counts={summary['needs_review_audit_recommendation_counts']}")


if __name__ == "__main__":
    main()
