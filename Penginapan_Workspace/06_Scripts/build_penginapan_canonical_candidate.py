from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_RAW_MASTER = (
    PENGINAPAN_WORKSPACE
    / "01_Raw_Data"
    / "generated_raw_csv"
    / "HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.csv"
)
DEFAULT_EXISTING_CANONICAL = (
    PENGINAPAN_WORKSPACE / "02_Curated" / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv"
)
DEFAULT_DEDUPED = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "PENGINAPAN_DEDUPED_MASTER_BANDUNG_RAYA_2026-06-02.csv"
)
DEFAULT_CANDIDATE = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
)
DEFAULT_SUMMARY = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "penginapan_canonical_candidate_summary_2026-06-02.json"
)
DEFAULT_VALIDATION = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "penginapan_canonical_candidate_validation_2026-06-02.json"
)
DEFAULT_REPORT = (
    PENGINAPAN_WORKSPACE
    / "04_Dokumentasi"
    / "PENGINAPAN_CANONICAL_CANDIDATE_PIPELINE_2026-06-02.md"
)
DEFAULT_NOTEBOOK = PENGINAPAN_WORKSPACE / "03_Notebooks" / "penginapan_training.ipynb"

NOTEBOOK_TAG = "penginapan_dedupe_region_validation_2026_06_02"

BANDUNG_CENTER = (-6.917464, 107.619123)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_float(value):
    text = clean_text(value)
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def parse_int(value):
    number = parse_float(value)
    if math.isnan(number):
        return pd.NA
    return int(round(number))


def bool_text(value) -> str:
    return "True" if bool(value) else "False"


def normalized_name(value: str) -> str:
    text = clean_text(value).lower()
    text = re.sub(
        r"\b(standard|deluxe|superior|double|twin|single|queen|king|room|kamar|"
        r"one|two|three|four|bedroom|studio|basic|family|triple|with|view|"
        r"terrace|garden|private|pool|near|by|at)\b",
        " ",
        text,
    )
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = clean_text(text).lower()
    return any(keyword in lowered for keyword in keywords)


def normalize_property_type(name: str, raw_type: str, existing_segment: str = "") -> str:
    lowered = clean_text(name).lower()
    segment = clean_text(existing_segment).lower()
    raw = clean_text(raw_type).lower()

    if segment in {"hotel", "guest_house", "villa", "apartment", "vacation_rental", "room_level_listing"}:
        return segment
    if contains_any(lowered, ["standard double room", "deluxe room", "superior room", "queen room", "king room", "twin room"]):
        return "room_level_listing"
    if contains_any(lowered, ["villa"]):
        return "villa"
    if contains_any(lowered, ["apartment", "apartemen", "studio", "2br", "1br", "gateway pasteur", "the edge"]):
        return "apartment"
    if contains_any(lowered, ["guest house", "guesthouse", "homestay", "home stay", "kost", "bed & breakfast"]):
        return "guest_house"
    if raw == "vacation rental":
        return "vacation_rental"
    return "hotel"


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    if any(math.isnan(value) for value in [lat1, lon1, lat2, lon2]):
        return math.nan
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return round(2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 3)


def region_bucket(lat, lon) -> tuple[str, str, str]:
    if math.isnan(lat) or math.isnan(lon):
        return "unknown", "needs_review", "missing_coordinate"

    broad_valid = -7.45 <= lat <= -6.55 and 107.05 <= lon <= 108.20
    border = -7.60 <= lat <= -6.40 and 106.85 <= lon <= 108.40
    if not broad_valid:
        if border:
            return "border_area", "border_area", "coordinate_on_bandung_border"
        return "outside_bandung_raya", "outside_bandung_raya", "coordinate_outside_broad_bandung_raya"

    if -6.98 <= lat <= -6.80 and 107.45 <= lon <= 107.58:
        return "cimahi_baros_pasteur", "bandung_raya_valid", "rough_coordinate_bucket"
    if -7.05 <= lat <= -6.82 and 107.54 <= lon <= 107.80:
        return "kota_bandung", "bandung_raya_valid", "rough_coordinate_bucket"
    if -6.92 <= lat <= -6.65 and 107.40 <= lon <= 107.78:
        return "kbb_utara_lembang_parongpong_cisarua", "bandung_raya_valid", "rough_coordinate_bucket"
    if -7.20 <= lat <= -6.75 and 107.10 <= lon <= 107.56:
        return "kbb_tengah_barat", "bandung_raya_valid", "rough_coordinate_bucket"
    if -7.38 <= lat <= -6.88 and 107.10 <= lon <= 107.64:
        return "kbb_selatan_baratdaya", "bandung_raya_valid", "rough_coordinate_bucket"
    if -7.38 <= lat <= -6.86 and 107.45 <= lon <= 108.15:
        return "kabupaten_bandung", "bandung_raya_valid", "rough_coordinate_bucket"
    return "bandung_raya_other", "bandung_raya_valid", "inside_broad_bandung_raya"


def quality_label(score) -> str:
    score = parse_float(score)
    if math.isnan(score):
        return "low"
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def dedupe_key(row: pd.Series) -> str:
    token = clean_text(row.get("property_token"))
    if token:
        return f"token::{token}"

    name = clean_text(row.get("normalized_name"))
    lat = parse_float(row.get("latitude"))
    lon = parse_float(row.get("longitude"))
    if name and not math.isnan(lat) and not math.isnan(lon):
        return f"name_geo::{name}::{round(lat, 4)}::{round(lon, 4)}"
    if name:
        # Conservative fallback. This groups exact normalized names only.
        return f"name_only::{name}"
    return f"row::{clean_text(row.get('raw_master_id')) or clean_text(row.get('source_file'))}"


def source_priority(row: pd.Series) -> tuple:
    property_type = clean_text(row.get("property_type"))
    segment_rank = {
        "hotel": 6,
        "guest_house": 5,
        "villa": 5,
        "vacation_rental": 4,
        "apartment": 3,
        "room_level_listing": 1,
    }.get(property_type, 2)
    source_bucket_rank = {
        "properties": 3,
        "existing_canonical": 3,
        "ads": 2,
    }.get(clean_text(row.get("source_bucket")), 1)
    quality = parse_float(row.get("data_quality_score"))
    reviews = parse_float(row.get("reviews"))
    rating = parse_float(row.get("overall_rating"))
    page = parse_float(row.get("source_page_number"))
    return (
        0 if clean_text(row.get("region_validation_label")) == "outside_bandung_raya" else 1,
        segment_rank,
        0 if property_type == "room_level_listing" else 1,
        source_bucket_rank,
        0 if math.isnan(quality) else quality,
        0 if math.isnan(reviews) else reviews,
        0 if math.isnan(rating) else rating,
        9999 if math.isnan(page) else -page,
    )


def load_raw_master(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["source_system"] = "google_hotels_search_raw_master"
    return df


def load_existing_canonical(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    src = pd.read_csv(path, dtype=str, keep_default_na=False)
    rows = []
    for index, row in src.iterrows():
        rows.append(
            {
                "raw_master_id": f"EXISTING-CANONICAL-{index + 1:04d}",
                "property_token": clean_text(row.get("source_property_token")),
                "source_file": path.name,
                "source_file_sha256": "",
                "source_file_duplicate_status": "existing_canonical_source",
                "source_bucket": "existing_canonical",
                "json_record_index": "",
                "source_query_area": "existing_canonical_cimahi_2026_05_29",
                "source_page_number": clean_text(row.get("source_page_number")),
                "search_timestamp": "",
                "query": "",
                "raw_type": clean_text(row.get("raw_type")),
                "property_segment": clean_text(row.get("property_segment")),
                "name": clean_text(row.get("name")),
                "latitude": clean_text(row.get("latitude")),
                "longitude": clean_text(row.get("longitude")),
                "coordinate_available": clean_text(row.get("coordinate_available")),
                "link": clean_text(row.get("source_link")),
                "check_in_time": clean_text(row.get("check_in_time")),
                "check_out_time": clean_text(row.get("check_out_time")),
                "price_lowest": clean_text(row.get("price_lowest")),
                "price_before_taxes_fees": clean_text(row.get("price_before_taxes_fees")),
                "price_display": clean_text(row.get("price_display")),
                "overall_rating": clean_text(row.get("overall_rating")),
                "reviews": clean_text(row.get("reviews")),
                "location_rating": clean_text(row.get("location_rating")),
                "amenities": clean_text(row.get("amenities")),
                "amenities_count": "",
                "nearby_place_names": "",
                "nearby_places_count": clean_text(row.get("nearby_places_count")),
                "primary_image_url": clean_text(row.get("primary_image_url")),
                "image_count": clean_text(row.get("image_count")),
                "data_quality_score": clean_text(row.get("data_quality_score")),
                "rating_sentiment_score": clean_text(row.get("rating_sentiment_score")),
                "adjusted_rating_sentiment_score": clean_text(row.get("adjusted_rating_sentiment_score")),
                "rating_sentiment_label": clean_text(row.get("rating_sentiment_label")),
                "adjusted_rating_sentiment_label": clean_text(row.get("adjusted_rating_sentiment_label")),
                "review_confidence_label": clean_text(row.get("review_confidence_label")),
                "review_count_p95": clean_text(row.get("review_count_p95")),
                "rating_sentiment_source": clean_text(row.get("rating_sentiment_source")),
                "rating_sentiment_model_version": clean_text(row.get("rating_sentiment_model_version")),
                "source_system": "existing_canonical_cimahi",
            }
        )
    return pd.DataFrame(rows)


def prepare_pool(raw_master: pd.DataFrame, existing_canonical: pd.DataFrame) -> pd.DataFrame:
    pool = pd.concat([raw_master, existing_canonical], ignore_index=True, sort=False).fillna("")
    pool["normalized_name"] = pool["name"].map(normalized_name)
    pool["property_type"] = pool.apply(
        lambda row: normalize_property_type(row.get("name"), row.get("raw_type"), row.get("property_segment")),
        axis=1,
    )
    pool["is_room_level_listing"] = pool["property_type"].eq("room_level_listing").map(bool_text)
    pool["is_apartment_listing"] = pool["property_type"].eq("apartment").map(bool_text)
    pool["is_villa_listing"] = pool["property_type"].eq("villa").map(bool_text)
    pool["is_budget_chain_listing"] = pool["name"].map(
        lambda value: bool_text(contains_any(value, ["oyo", "reddoorz", "collection o", "spot on", "super oyo", "sans"]))
    )

    buckets = pool.apply(lambda row: region_bucket(parse_float(row.get("latitude")), parse_float(row.get("longitude"))), axis=1)
    pool["region_bucket"] = [item[0] for item in buckets]
    pool["region_validation_label"] = [item[1] for item in buckets]
    pool["region_validation_reason"] = [item[2] for item in buckets]
    pool["distance_from_bandung_center_km"] = pool.apply(
        lambda row: haversine_km(
            parse_float(row.get("latitude")),
            parse_float(row.get("longitude")),
            BANDUNG_CENTER[0],
            BANDUNG_CENTER[1],
        ),
        axis=1,
    )
    pool["dedupe_key"] = pool.apply(dedupe_key, axis=1)
    return pool


def deduplicate(pool: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_rows = []
    for _, group in pool.groupby("dedupe_key", dropna=False):
        group = group.copy()
        group["_selection_rank"] = group.apply(source_priority, axis=1)
        group = group.sort_values("_selection_rank", ascending=False)
        selected = group.iloc[0].copy()
        selected["dedupe_group_size"] = len(group)
        selected["dedupe_source_files"] = "; ".join(sorted(set(group["source_file"].map(clean_text))))
        selected["dedupe_source_queries"] = "; ".join(sorted(set(filter(None, group["source_query_area"].map(clean_text)))))
        selected["dedupe_raw_master_ids"] = "; ".join(sorted(set(group["raw_master_id"].map(clean_text))))
        selected_rows.append(selected.drop(labels=["_selection_rank"], errors="ignore"))

    deduped = pd.DataFrame(selected_rows).reset_index(drop=True)
    deduped = deduped.sort_values(
        by=["region_validation_label", "region_bucket", "data_quality_score", "name"],
        ascending=[True, True, False, True],
    ).reset_index(drop=True)
    deduped["penginapan_id"] = [f"LODGE-{index:05d}" for index in range(1, len(deduped) + 1)]
    return deduped, pool


def build_candidate(deduped: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "penginapan_id",
        "name",
        "normalized_name",
        "property_token",
        "property_type",
        "raw_type",
        "is_room_level_listing",
        "is_apartment_listing",
        "is_villa_listing",
        "is_budget_chain_listing",
        "latitude",
        "longitude",
        "region_bucket",
        "region_validation_label",
        "region_validation_reason",
        "distance_from_bandung_center_km",
        "overall_rating",
        "reviews",
        "location_rating",
        "price_lowest",
        "price_before_taxes_fees",
        "price_display",
        "check_in_time",
        "check_out_time",
        "amenities",
        "nearby_place_names",
        "primary_image_url",
        "image_count",
        "link",
        "rating_sentiment_score",
        "adjusted_rating_sentiment_score",
        "rating_sentiment_label",
        "adjusted_rating_sentiment_label",
        "review_confidence_label",
        "rating_sentiment_source",
        "data_quality_score",
        "data_quality_label",
        "dedupe_key",
        "dedupe_group_size",
        "dedupe_source_files",
        "dedupe_source_queries",
        "dedupe_raw_master_ids",
        "source_system",
        "generated_at",
    ]
    candidate = deduped.copy()
    candidate["data_quality_label"] = candidate["data_quality_score"].map(quality_label)
    candidate["generated_at"] = now_iso()
    for column in columns:
        if column not in candidate.columns:
            candidate[column] = ""
    return candidate[columns]


def validate_candidate(candidate: pd.DataFrame) -> dict:
    errors = []
    warnings = []
    required = ["penginapan_id", "name", "property_type", "latitude", "longitude", "region_validation_label"]
    for column in required:
        if column not in candidate.columns:
            errors.append({"code": "MISSING_COLUMN", "field": column, "message": f"Missing required column {column}."})

    if "penginapan_id" in candidate.columns and candidate["penginapan_id"].duplicated().any():
        errors.append({"code": "DUPLICATE_ID", "field": "penginapan_id", "message": "penginapan_id must be unique."})

    lat = pd.to_numeric(candidate.get("latitude"), errors="coerce")
    lon = pd.to_numeric(candidate.get("longitude"), errors="coerce")
    missing_coord = int((lat.isna() | lon.isna()).sum())
    if missing_coord:
        warnings.append({"code": "MISSING_COORDINATE", "count": missing_coord, "message": "Some rows are missing coordinates."})

    rating = pd.to_numeric(candidate.get("overall_rating"), errors="coerce")
    invalid_rating = int(((rating < 0) | (rating > 5)).fillna(False).sum())
    if invalid_rating:
        errors.append({"code": "INVALID_RATING", "field": "overall_rating", "count": invalid_rating, "message": "Rating must be between 0 and 5."})

    outside_count = int(candidate["region_validation_label"].eq("outside_bandung_raya").sum())
    border_count = int(candidate["region_validation_label"].eq("border_area").sum())
    if outside_count:
        warnings.append({"code": "OUTSIDE_BANDUNG_RAYA", "count": outside_count, "message": "Outside rows should be filtered from main recommendations."})
    if border_count:
        warnings.append({"code": "BORDER_AREA", "count": border_count, "message": "Border area rows need caveat or review."})

    room_level_count = int(candidate["is_room_level_listing"].eq("True").sum())
    if room_level_count:
        warnings.append({"code": "ROOM_LEVEL_LISTING", "count": room_level_count, "message": "Room-level listings should not outrank main properties."})

    gate = "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {
        "generated_at": now_iso(),
        "gate": gate,
        "row_count": int(len(candidate)),
        "errors": errors,
        "warnings": warnings,
    }


def markdown_table(mapping: dict, key_label: str, value_label: str) -> str:
    lines = [f"| {key_label} | {value_label} |", "|---|---:|"]
    for key, value in sorted(mapping.items(), key=lambda item: str(item[0])):
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict, validation: dict) -> None:
    text = f"""# Penginapan Canonical Candidate Pipeline - 2026-06-02

Tahap ini melakukan dedupe konservatif dan region validation awal untuk data penginapan.

## Output

- Deduped master: `{summary['deduped_output_path']}`
- Canonical candidate: `{summary['candidate_output_path']}`
- Validation JSON: `{summary['validation_output_path']}`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Raw master rows | {summary['raw_master_rows']} |
| Existing canonical rows included | {summary['existing_canonical_rows']} |
| Pool rows | {summary['pool_rows']} |
| Candidate rows after dedupe | {summary['candidate_rows']} |
| Dedupe removed rows | {summary['dedupe_removed_rows']} |
| Validation gate | {validation['gate']} |

## Property Type

{markdown_table(summary['property_type_counts'], 'Property type', 'Jumlah')}

## Region Validation

{markdown_table(summary['region_validation_counts'], 'Region validation', 'Jumlah')}

## Region Bucket

{markdown_table(summary['region_bucket_counts'], 'Region bucket', 'Jumlah')}

## Catatan Kejujuran

- Dedupe dibuat konservatif agar tidak salah menggabungkan villa/apartment/unit yang mirip namanya.
- Dataset ini bernama `PENGINAPAN`, bukan `HOTEL`, karena isinya mencakup hotel, villa, apartment, guest house, homestay, dan vacation rental.
- Region validation ini masih rough coordinate validation, bukan batas administratif presisi.
- Output ini masih `canonical candidate`, belum final production canonical.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def notebook_cell(cell_type: str, source: str) -> dict:
    cell = {
        "cell_type": cell_type,
        "id": uuid4().hex[:8],
        "metadata": {"tags": [NOTEBOOK_TAG]},
        "source": [f"{line}\n" for line in source.strip("\n").split("\n")],
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell


def update_notebook(path: Path, summary: dict, validation: dict) -> None:
    if path.exists():
        nb = json.loads(path.read_text(encoding="utf-8"))
    else:
        nb = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}

    cells = []
    for cell in nb.get("cells", []):
        tags = cell.get("metadata", {}).get("tags", [])
        if NOTEBOOK_TAG not in tags:
            cells.append(cell)

    cells.extend(
        [
            notebook_cell(
                "markdown",
                f"""
## Fase A - Dedupe dan Region Validation Penginapan

Bagian ini membuat `PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv`.

Keputusan penting:

- Nama output memakai `PENGINAPAN`, bukan `HOTEL`, karena data mencakup hotel, villa, apartment, guest house, homestay, vacation rental, dan room-level listing.
- Dedupe dibuat konservatif agar tidak salah menggabungkan properti berbeda.
- Region validation masih berbasis koordinat rough Bandung Raya, bukan batas administratif presisi.

Hasil terakhir:

- Pool rows: {summary['pool_rows']}
- Candidate rows: {summary['candidate_rows']}
- Dedupe removed rows: {summary['dedupe_removed_rows']}
- Validation gate: {validation['gate']}
- Candidate CSV: `{summary['candidate_output_path']}`
""",
            ),
            notebook_cell(
                "code",
                """
# Rebuild dedupe + region validation penginapan.
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

subprocess.run(
    [
        sys.executable,
        str(PROJECT_ROOT / "Penginapan_Workspace" / "06_Scripts" / "build_penginapan_canonical_candidate.py"),
        "--skip-notebook-update",
    ],
    check=True,
)
""",
            ),
            notebook_cell(
                "code",
                """
# Preview hasil canonical candidate penginapan.
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

candidate_csv = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
summary_json = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "penginapan_canonical_candidate_summary_2026-06-02.json"
validation_json = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "penginapan_canonical_candidate_validation_2026-06-02.json"

candidate_df = pd.read_csv(candidate_csv)
summary = json.loads(summary_json.read_text(encoding="utf-8"))
validation = json.loads(validation_json.read_text(encoding="utf-8"))

summary, validation, candidate_df[[
    "penginapan_id",
    "name",
    "property_type",
    "region_bucket",
    "region_validation_label",
    "overall_rating",
    "reviews",
    "data_quality_score",
    "dedupe_group_size",
]].head(20)
""",
            ),
        ]
    )
    nb["cells"] = cells
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def build(
    raw_master_path: Path,
    existing_canonical_path: Path,
    deduped_output_path: Path,
    candidate_output_path: Path,
    summary_path: Path,
    validation_path: Path,
    report_path: Path,
    notebook_path: Path,
    update_nb: bool,
) -> tuple[dict, dict]:
    raw_master = load_raw_master(raw_master_path)
    existing_canonical = load_existing_canonical(existing_canonical_path)
    pool = prepare_pool(raw_master, existing_canonical)
    deduped, prepared_pool = deduplicate(pool)
    candidate = build_candidate(deduped)
    validation = validate_candidate(candidate)

    deduped_output_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_output_path.parent.mkdir(parents=True, exist_ok=True)
    deduped.to_csv(deduped_output_path, index=False)
    candidate.to_csv(candidate_output_path, index=False)

    summary = {
        "generated_at": now_iso(),
        "raw_master_input_path": str(raw_master_path),
        "existing_canonical_input_path": str(existing_canonical_path),
        "deduped_output_path": str(deduped_output_path),
        "candidate_output_path": str(candidate_output_path),
        "validation_output_path": str(validation_path),
        "raw_master_rows": int(len(raw_master)),
        "existing_canonical_rows": int(len(existing_canonical)),
        "pool_rows": int(len(prepared_pool)),
        "candidate_rows": int(len(candidate)),
        "dedupe_removed_rows": int(len(prepared_pool) - len(candidate)),
        "property_type_counts": candidate["property_type"].value_counts(dropna=False).to_dict(),
        "region_validation_counts": candidate["region_validation_label"].value_counts(dropna=False).to_dict(),
        "region_bucket_counts": candidate["region_bucket"].value_counts(dropna=False).to_dict(),
        "data_quality_label_counts": candidate["data_quality_label"].value_counts(dropna=False).to_dict(),
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(report_path, summary, validation)
    if update_nb:
        update_notebook(notebook_path, summary, validation)
    return summary, validation


def main() -> None:
    parser = argparse.ArgumentParser(description="Build penginapan canonical candidate with conservative dedupe and rough region validation.")
    parser.add_argument("--raw-master", type=Path, default=DEFAULT_RAW_MASTER)
    parser.add_argument("--existing-canonical", type=Path, default=DEFAULT_EXISTING_CANONICAL)
    parser.add_argument("--deduped-output", type=Path, default=DEFAULT_DEDUPED)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--skip-notebook-update", action="store_true")
    args = parser.parse_args()

    summary, validation = build(
        raw_master_path=args.raw_master,
        existing_canonical_path=args.existing_canonical,
        deduped_output_path=args.deduped_output,
        candidate_output_path=args.candidate_output,
        summary_path=args.summary,
        validation_path=args.validation,
        report_path=args.report,
        notebook_path=args.notebook,
        update_nb=not args.skip_notebook_update,
    )
    print(f"pool_rows={summary['pool_rows']}")
    print(f"candidate_rows={summary['candidate_rows']}")
    print(f"dedupe_removed_rows={summary['dedupe_removed_rows']}")
    print(f"validation_gate={validation['gate']}")
    print(f"candidate_output={summary['candidate_output_path']}")


if __name__ == "__main__":
    main()
