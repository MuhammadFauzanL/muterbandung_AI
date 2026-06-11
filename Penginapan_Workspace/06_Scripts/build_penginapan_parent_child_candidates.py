from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
CURATED_DIR = WORKSPACE / "02_Curated"
DOC_DIR = WORKSPACE / "04_Dokumentasi"

DEFAULT_INPUT = CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
DEFAULT_MAPPING = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_MAPPING_CANDIDATE_2026-06-05.csv"
DEFAULT_ROOM_LEVEL = CURATED_DIR / "PENGINAPAN_ROOM_LEVEL_LISTINGS_2026-06-05.csv"
DEFAULT_DUPLICATE_REVIEW = CURATED_DIR / "PENGINAPAN_POSSIBLE_DUPLICATE_REVIEW_2026-06-05.csv"
DEFAULT_SUMMARY = CURATED_DIR / "penginapan_parent_child_candidate_summary_2026-06-05.json"
DEFAULT_REPORT = DOC_DIR / "PENGINAPAN_PARENT_CHILD_CANDIDATE_2026-06-05.md"


ROOM_TYPES = {"room_level_listing"}
PARENT_TYPES = {"hotel", "guest_house", "villa", "apartment", "vacation_rental"}
ROOM_OR_UNIT_PATTERN = re.compile(
    r"\b("
    r"standard|deluxe|superior|double|twin|single|queen|king|family|triple|"
    r"room|kamar|bedroom|1br|2br|3br|studio|unit|cottage"
    r")\b",
    re.IGNORECASE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value).strip()


def parse_float(value) -> float:
    text = clean_text(value)
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    if any(math.isnan(value) for value in [lat1, lon1, lat2, lon2]):
        return math.nan
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def token_set(value: str) -> set[str]:
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = {token for token in text.split() if len(token) >= 3}
    stopwords = {
        "hotel",
        "room",
        "kamar",
        "deluxe",
        "standard",
        "superior",
        "double",
        "twin",
        "queen",
        "king",
        "family",
        "with",
        "near",
        "the",
        "and",
        "view",
    }
    return tokens - stopwords


def looks_room_or_unit_name(value: str) -> bool:
    return bool(ROOM_OR_UNIT_PATTERN.search(clean_text(value)))


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def confidence_label(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.65:
        return "medium"
    if score > 0:
        return "low"
    return "no_candidate"


def possible_duplicate_key(df: pd.DataFrame) -> pd.Series:
    lat_round = pd.to_numeric(df["latitude"], errors="coerce").round(4)
    lon_round = pd.to_numeric(df["longitude"], errors="coerce").round(4)
    return df["normalized_name"].map(clean_text) + "|" + lat_round.astype(str) + "|" + lon_round.astype(str)


def add_match_features(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["_lat_float"] = pd.to_numeric(work["latitude"], errors="coerce")
    work["_lon_float"] = pd.to_numeric(work["longitude"], errors="coerce")
    work["_lat_round_4"] = work["_lat_float"].round(4)
    work["_lon_round_4"] = work["_lon_float"].round(4)
    work["_match_key"] = work["normalized_name"].map(clean_text) + "|" + work["_lat_round_4"].astype(str) + "|" + work["_lon_round_4"].astype(str)
    work["_token_set"] = work.apply(lambda row: token_set(clean_text(row.get("normalized_name")) or clean_text(row.get("name"))), axis=1)
    work["_quality_float"] = pd.to_numeric(work["data_quality_score"], errors="coerce").fillna(0)
    work["_reviews_float"] = pd.to_numeric(work["reviews"], errors="coerce").fillna(0)
    return work


def duplicate_review_type(group: pd.DataFrame) -> tuple[str, str]:
    types = set(group["property_type"].map(clean_text))
    has_room = bool(types & ROOM_TYPES)
    non_room_types = sorted(types - ROOM_TYPES)
    if has_room and non_room_types:
        return "parent_child_candidate", "Review sebagai kandidat parent-child; jangan auto-merge."
    if has_room:
        return "room_variant_group", "Kelompok room/unit; cari parent utama atau tahan sebagai child tanpa parent."
    if len(non_room_types) == 1:
        return "same_type_duplicate_candidate", "Review duplikat semantik; gabungkan hanya jika bukti cukup."
    return "mixed_type_duplicate_candidate", "Review manual karena tipe properti berbeda pada lokasi/nama mirip."


def build_possible_duplicate_review(candidate: pd.DataFrame) -> pd.DataFrame:
    work = candidate.copy()
    work["possible_duplicate_key"] = possible_duplicate_key(work)
    valid_key = (
        work["normalized_name"].map(clean_text).ne("")
        & pd.to_numeric(work["latitude"], errors="coerce").notna()
        & pd.to_numeric(work["longitude"], errors="coerce").notna()
    )
    possible = work[valid_key & work["possible_duplicate_key"].duplicated(keep=False)].copy()

    rows = []
    grouped = possible.groupby("possible_duplicate_key", sort=True)
    for group_index, (key, group) in enumerate(grouped, start=1):
        group_id = f"DUP-20260605-{group_index:04d}"
        review_type, recommendation = duplicate_review_type(group)
        property_types = "; ".join(sorted(set(group["property_type"].map(clean_text))))
        for _, row in group.iterrows():
            rows.append(
                {
                    "possible_duplicate_group_id": group_id,
                    "possible_duplicate_key": key,
                    "group_size": int(len(group)),
                    "group_property_types": property_types,
                    "group_review_type": review_type,
                    "recommended_decision": recommendation,
                    "penginapan_id": clean_text(row.get("penginapan_id")),
                    "name": clean_text(row.get("name")),
                    "normalized_name": clean_text(row.get("normalized_name")),
                    "property_type": clean_text(row.get("property_type")),
                    "latitude": clean_text(row.get("latitude")),
                    "longitude": clean_text(row.get("longitude")),
                    "overall_rating": clean_text(row.get("overall_rating")),
                    "reviews": clean_text(row.get("reviews")),
                    "price_lowest": clean_text(row.get("price_lowest")),
                    "data_quality_score": clean_text(row.get("data_quality_score")),
                    "data_quality_label": clean_text(row.get("data_quality_label")),
                    "link": clean_text(row.get("link")),
                    "primary_image_url": clean_text(row.get("primary_image_url")),
                    "dedupe_group_size": clean_text(row.get("dedupe_group_size")),
                }
            )
    return pd.DataFrame(rows)


def build_room_level_listings(candidate: pd.DataFrame, duplicate_review: pd.DataFrame) -> pd.DataFrame:
    group_lookup = {}
    if not duplicate_review.empty:
        for _, row in duplicate_review.iterrows():
            group_lookup[clean_text(row.get("penginapan_id"))] = clean_text(row.get("possible_duplicate_group_id"))

    room = candidate[candidate["property_type"].map(clean_text).isin(ROOM_TYPES)].copy()
    rows = []
    for _, row in room.iterrows():
        pid = clean_text(row.get("penginapan_id"))
        rows.append(
            {
                "child_penginapan_id": pid,
                "child_name": clean_text(row.get("name")),
                "child_normalized_name": clean_text(row.get("normalized_name")),
                "child_property_type": clean_text(row.get("property_type")),
                "latitude": clean_text(row.get("latitude")),
                "longitude": clean_text(row.get("longitude")),
                "overall_rating": clean_text(row.get("overall_rating")),
                "reviews": clean_text(row.get("reviews")),
                "price_lowest": clean_text(row.get("price_lowest")),
                "data_quality_score": clean_text(row.get("data_quality_score")),
                "data_quality_label": clean_text(row.get("data_quality_label")),
                "possible_duplicate_group_id": group_lookup.get(pid, ""),
                "name_looks_room_or_unit": str(looks_room_or_unit_name(row.get("name"))),
                "suggested_handling": "keep_as_child_candidate_not_main_ranking",
                "parent_search_hint": "Cari parent dari nama dasar + koordinat sama/dekat; jangan hapus otomatis.",
                "link": clean_text(row.get("link")),
                "primary_image_url": clean_text(row.get("primary_image_url")),
            }
        )
    return pd.DataFrame(rows)


def score_parent_candidate(child: pd.Series, parent: pd.Series) -> tuple[float, str, str]:
    child_lat = parse_float(child.get("_lat_float"))
    child_lon = parse_float(child.get("_lon_float"))
    parent_lat = parse_float(parent.get("_lat_float"))
    parent_lon = parse_float(parent.get("_lon_float"))
    distance = haversine_km(child_lat, child_lon, parent_lat, parent_lon)

    child_norm = clean_text(child.get("normalized_name"))
    parent_norm = clean_text(parent.get("normalized_name"))
    child_tokens = child.get("_token_set") if isinstance(child.get("_token_set"), set) else token_set(child_norm or child.get("name"))
    parent_tokens = parent.get("_token_set") if isinstance(parent.get("_token_set"), set) else token_set(parent_norm or parent.get("name"))
    overlap = jaccard(child_tokens, parent_tokens)

    child_key = clean_text(child.get("_match_key"))
    parent_key = clean_text(parent.get("_match_key"))

    if child_key == parent_key:
        return 0.95, "same_normalized_name_and_rounded_coordinate", "Nama dasar dan koordinat rounded sama."
    if not math.isnan(distance) and distance <= 0.03 and overlap >= 0.70:
        return 0.88, "very_close_coordinate_and_strong_name_overlap", "Koordinat sangat dekat dan token nama kuat."
    if not math.isnan(distance) and distance <= 0.05 and (
        (child_norm and parent_norm and (child_norm in parent_norm or parent_norm in child_norm)) or overlap >= 0.65
    ):
        return 0.78, "close_coordinate_and_name_similarity", "Koordinat dekat dan nama masih mirip."
    if not math.isnan(distance) and distance <= 0.10 and overlap >= 0.60:
        return 0.66, "near_coordinate_and_medium_name_overlap", "Koordinat dekat dan overlap nama sedang."
    return 0.0, "no_safe_match", "Tidak ada bukti cukup untuk kandidat parent otomatis."


def relation_type_for_child(child: pd.Series, parent: pd.Series | None) -> str:
    if parent is None:
        return "no_parent_candidate_found"
    child_name = clean_text(child.get("name")).lower()
    if "room" in child_name or "kamar" in child_name:
        return "room_of"
    if any(token in child_name for token in ["unit", "studio", "1br", "2br", "3br", "apartment", "apartemen"]):
        return "unit_of"
    return "listing_variant_of"


def build_parent_child_mapping(candidate: pd.DataFrame) -> pd.DataFrame:
    candidate = add_match_features(candidate)
    children = candidate[candidate["property_type"].map(clean_text).isin(ROOM_TYPES)].copy()
    parent_pool = candidate[
        candidate["property_type"].map(clean_text).isin(PARENT_TYPES)
        & ~candidate["name"].map(looks_room_or_unit_name)
    ].copy()

    rows = []
    for child_index, child in children.iterrows():
        scored = []
        child_lat = parse_float(child.get("_lat_float"))
        child_lon = parse_float(child.get("_lon_float"))
        if math.isnan(child_lat) or math.isnan(child_lon):
            nearby_parent_pool = parent_pool.iloc[0:0]
        else:
            nearby_parent_pool = parent_pool[
                (
                    parent_pool["_lat_round_4"].eq(child.get("_lat_round_4"))
                    & parent_pool["_lon_round_4"].eq(child.get("_lon_round_4"))
                )
                | (
                    (parent_pool["_lat_float"] - child_lat).abs().le(0.001)
                    & (parent_pool["_lon_float"] - child_lon).abs().le(0.001)
                )
            ]

        for parent_index, parent in nearby_parent_pool.iterrows():
            if clean_text(parent.get("penginapan_id")) == clean_text(child.get("penginapan_id")):
                continue
            score, basis, evidence = score_parent_candidate(child, parent)
            if score <= 0:
                continue
            scored.append((score, basis, evidence, parent_index, parent))

        scored.sort(
            key=lambda item: (
                item[0],
                parse_float(item[4].get("_quality_float")),
                parse_float(item[4].get("_reviews_float")),
            ),
            reverse=True,
        )
        top_candidates = scored[:3]

        if not top_candidates:
            rows.append(
                {
                    "mapping_candidate_id": f"PCM-20260605-{len(rows) + 1:04d}",
                    "child_penginapan_id": clean_text(child.get("penginapan_id")),
                    "child_name": clean_text(child.get("name")),
                    "child_property_type": clean_text(child.get("property_type")),
                    "child_normalized_name": clean_text(child.get("normalized_name")),
                    "child_latitude": clean_text(child.get("latitude")),
                    "child_longitude": clean_text(child.get("longitude")),
                    "parent_candidate_id": "",
                    "parent_candidate_name": "",
                    "parent_property_type": "",
                    "parent_name_looks_room_or_unit": "",
                    "parent_latitude": "",
                    "parent_longitude": "",
                    "relation_type": relation_type_for_child(child, None),
                    "confidence_score": 0.0,
                    "confidence_label": "no_candidate",
                    "match_basis": "no_safe_parent_candidate",
                    "evidence": "Tidak ada parent non-room yang cukup dekat dan cukup mirip.",
                    "decision_recommendation": "manual_review_or_keep_child_without_parent",
                    "is_final_relation": "False",
                }
            )
            continue

        for score, basis, evidence, _, parent in top_candidates:
            rows.append(
                {
                    "mapping_candidate_id": f"PCM-20260605-{len(rows) + 1:04d}",
                    "child_penginapan_id": clean_text(child.get("penginapan_id")),
                    "child_name": clean_text(child.get("name")),
                    "child_property_type": clean_text(child.get("property_type")),
                    "child_normalized_name": clean_text(child.get("normalized_name")),
                    "child_latitude": clean_text(child.get("latitude")),
                    "child_longitude": clean_text(child.get("longitude")),
                    "parent_candidate_id": clean_text(parent.get("penginapan_id")),
                    "parent_candidate_name": clean_text(parent.get("name")),
                    "parent_property_type": clean_text(parent.get("property_type")),
                    "parent_name_looks_room_or_unit": str(looks_room_or_unit_name(parent.get("name"))),
                    "parent_latitude": clean_text(parent.get("latitude")),
                    "parent_longitude": clean_text(parent.get("longitude")),
                    "relation_type": relation_type_for_child(child, parent),
                    "confidence_score": round(float(score), 3),
                    "confidence_label": confidence_label(score),
                    "match_basis": basis,
                    "evidence": evidence,
                    "decision_recommendation": "candidate_mapping_review_before_final",
                    "is_final_relation": "False",
                }
            )
    return pd.DataFrame(rows)


def markdown_table(mapping: dict, key_label: str, value_label: str) -> str:
    lines = [f"| {key_label} | {value_label} |", "|---|---:|"]
    for key, value in mapping.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict) -> None:
    text = f"""# Penginapan Parent-Child Candidate Mapping - 2026-06-05

Dokumen ini mencatat tahap awal entity resolution penginapan.

Status output: **candidate mapping**, belum relasi final.

## Output

- Possible duplicate review: `{summary['possible_duplicate_review_path']}`
- Room-level listings: `{summary['room_level_listings_path']}`
- Parent-child mapping candidate: `{summary['parent_child_mapping_candidate_path']}`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Candidate input rows | {summary['candidate_input_rows']} |
| Possible duplicate rows | {summary['possible_duplicate_rows']} |
| Possible duplicate groups | {summary['possible_duplicate_groups']} |
| Room-level listing rows | {summary['room_level_listing_rows']} |
| Parent-child mapping rows | {summary['parent_child_mapping_rows']} |
| Child with parent candidate | {summary['child_with_parent_candidate']} |
| Child without parent candidate | {summary['child_without_parent_candidate']} |

## Confidence Label

{markdown_table(summary['confidence_label_counts'], 'Confidence label', 'Jumlah')}

## Catatan Keputusan

- Mapping ini tidak mengubah canonical candidate.
- Relasi dengan confidence tinggi tetap belum dianggap final.
- Child listing tidak dihapus otomatis.
- Review scraping sebaiknya menunggu parent utama dipilih.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(
    input_path: Path,
    mapping_path: Path,
    room_level_path: Path,
    duplicate_review_path: Path,
    summary_path: Path,
    report_path: Path,
) -> dict:
    candidate = pd.read_csv(input_path, dtype=str, keep_default_na=False)

    duplicate_review = build_possible_duplicate_review(candidate)
    room_level = build_room_level_listings(candidate, duplicate_review)
    mapping = build_parent_child_mapping(candidate)

    duplicate_review_path.parent.mkdir(parents=True, exist_ok=True)
    room_level_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.parent.mkdir(parents=True, exist_ok=True)

    duplicate_review.to_csv(duplicate_review_path, index=False)
    room_level.to_csv(room_level_path, index=False)
    mapping.to_csv(mapping_path, index=False)

    child_with_parent = (
        mapping[mapping["parent_candidate_id"].map(clean_text).ne("")]["child_penginapan_id"].nunique()
        if not mapping.empty
        else 0
    )
    child_total = int(len(room_level))
    confidence_counts = mapping["confidence_label"].value_counts(dropna=False).to_dict() if not mapping.empty else {}

    summary = {
        "generated_at": now_iso(),
        "input_path": str(input_path),
        "possible_duplicate_review_path": str(duplicate_review_path),
        "room_level_listings_path": str(room_level_path),
        "parent_child_mapping_candidate_path": str(mapping_path),
        "candidate_input_rows": int(len(candidate)),
        "possible_duplicate_rows": int(len(duplicate_review)),
        "possible_duplicate_groups": int(duplicate_review["possible_duplicate_group_id"].nunique() if not duplicate_review.empty else 0),
        "possible_duplicate_review_type_counts": duplicate_review["group_review_type"].value_counts(dropna=False).to_dict()
        if not duplicate_review.empty
        else {},
        "room_level_listing_rows": child_total,
        "parent_child_mapping_rows": int(len(mapping)),
        "child_with_parent_candidate": int(child_with_parent),
        "child_without_parent_candidate": int(child_total - child_with_parent),
        "confidence_label_counts": confidence_counts,
        "relation_type_counts": mapping["relation_type"].value_counts(dropna=False).to_dict() if not mapping.empty else {},
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(report_path, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build penginapan parent-child candidate mapping.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--mapping-output", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--room-level-output", type=Path, default=DEFAULT_ROOM_LEVEL)
    parser.add_argument("--duplicate-review-output", type=Path, default=DEFAULT_DUPLICATE_REVIEW)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    summary = build(
        input_path=args.input,
        mapping_path=args.mapping_output,
        room_level_path=args.room_level_output,
        duplicate_review_path=args.duplicate_review_output,
        summary_path=args.summary,
        report_path=args.report,
    )
    print(f"candidate_input_rows={summary['candidate_input_rows']}")
    print(f"possible_duplicate_rows={summary['possible_duplicate_rows']}")
    print(f"possible_duplicate_groups={summary['possible_duplicate_groups']}")
    print(f"room_level_listing_rows={summary['room_level_listing_rows']}")
    print(f"parent_child_mapping_rows={summary['parent_child_mapping_rows']}")
    print(f"child_with_parent_candidate={summary['child_with_parent_candidate']}")
    print(f"child_without_parent_candidate={summary['child_without_parent_candidate']}")
    print(f"mapping_output={summary['parent_child_mapping_candidate_path']}")


if __name__ == "__main__":
    main()
