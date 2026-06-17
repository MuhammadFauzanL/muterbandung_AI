#!/usr/bin/env python3
"""
CSV Import Script for Destination Data
=======================================

Reads the curated CSV dataset and populates the destination tables:
  - destinations
  - destination_media
  - destination_labels
  - destination_facilities

Usage:
    # Dry run (validate only, no DB writes)
    python scripts/import_destinations.py --file data/wisata_populer.csv --dry-run

    # Import active destinations
    python scripts/import_destinations.py --file data/wisata_populer.csv

    # Import limited rows for testing
    python scripts/import_destinations.py --file data/wisata_populer.csv --limit 10

    # Import all rows including inactive
    python scripts/import_destinations.py --file data/wisata_populer.csv --include-inactive

    # Clear existing data before import
    python scripts/import_destinations.py --file data/wisata_populer.csv --clear-existing
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Ensure the backend package is importable when running from backend/
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.destination import Destination  # noqa: E402
from app.models.destination_facility import DestinationFacility  # noqa: E402
from app.models.destination_label import DestinationLabel  # noqa: E402
from app.models.destination_media import DestinationMedia  # noqa: E402

# =========================================================================
# Required CSV columns
# =========================================================================
REQUIRED_COLUMNS: list[str] = [
    # Destination main
    "location_id",
    "location_name",
    "category",
    "subcategory",
    "deskripsi_google",
    "estimasi_durasi_menit",
    "crowd_level",
    "tags_sintetis",
    # Location
    "latitude",
    "longitude",
    "coordinate_verified",
    "distance_from_alun_alun_km",
    # Price
    "price_min",
    "price_max",
    "price_type",
    # Opening hours
    "jam_buka",
    "jam_tutup",
    "jam_buka_weekday",
    "jam_tutup_weekday",
    "jam_buka_weekend",
    "jam_tutup_weekend",
    # Rating & sentiment
    "avg_rating",
    "total_ulasan",
    "ulasan_positif",
    "ulasan_negatif",
    "sentimen_label_lokasi",
    "sentiment_score",
    "avg_sentimen_skor",
    "sentiment_available",
    # AI labels
    "final_primary_intent",
    "final_core_labels",
    "final_secondary_labels",
    "final_avoid_labels",
    "label_confidence",
    "final_label_source",
    "label_scores_json",
    # Media
    "media_available",
    "media_image_url",
    "media_destination_url",
    "media_website",
    "media_source",
    "media_place_id",
    "media_audit_status",
    # Facilities
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
    "open_24h_verified",
    "child_friendly_verified",
    "night_verified",
    "indoor_verified",
    "safety_verified",
    # Display status
    "curation_action",
    "display_status",
    "is_active_verified",
]

# Optional columns (may not exist in every CSV version)
OPTIONAL_COLUMNS: list[str] = [
    "zona_wisata",
]

FACILITY_SOURCE_COLUMNS: list[str] = [
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
    "open_24h_verified",
    "child_friendly_verified",
    "night_verified",
    "indoor_verified",
    "safety_verified",
]


@dataclass(frozen=True)
class ImportScoringContext:
    """Reusable calibration values for recommendation-oriented scoring."""

    avg_rating_baseline: float
    bayesian_min_reviews: int = 200
    review_log_cap: int = 1000

# =========================================================================
# Transform helpers
# =========================================================================


def safe_str(value: Any) -> str | None:
    """Return stripped string or None if empty."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def safe_int(value: Any) -> int | None:
    """Convert '200.0' → 200, '' → None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def safe_float(value: Any) -> float | None:
    """Convert string float → float, '' → None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def safe_bool(value: Any) -> bool | None:
    """'True' → True, 'False' → False, '' → None."""
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None


def parse_semicolon_list(value: Any) -> list[str]:
    """'Alam;Spot Foto;Santai' → ['Alam', 'Spot Foto', 'Santai']."""
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    return [item.strip() for item in s.split(";") if item.strip()]


def parse_comma_list(value: Any) -> list[str]:
    """'Belanja, Indoor, Kuliner' → ['Belanja', 'Indoor', 'Kuliner']."""
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    return [item.strip() for item in s.split(",") if item.strip()]


def parse_json(value: Any, row_id: str = "?") -> dict:
    """Parse JSON string → dict; return {} on failure."""
    if value is None:
        return {}
    s = str(value).strip()
    if not s:
        return {}
    try:
        result = json.loads(s)
        if isinstance(result, dict):
            return result
        return {}
    except (json.JSONDecodeError, TypeError):
        print(f"  ⚠ Row {row_id}: invalid JSON in label_scores_json, using {{}}")
        return {}


def generate_slug(name: str, external_id: str, existing_slugs: set[str]) -> str:
    """
    Generate a URL-safe slug from the destination name.
    If duplicate, append the external_id.
    """
    # Normalize unicode, lowercase
    slug = unicodedata.normalize("NFKD", name)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower()
    # Replace non-alphanumeric with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)

    if not slug:
        slug = external_id.lower().replace("_", "-")

    # Handle duplicates
    if slug in existing_slugs:
        slug = f"{slug}-{external_id.lower().replace('_', '-')}"

    existing_slugs.add(slug)
    return slug


def calculate_popular_score(
    total_reviews: int | None,
    avg_rating: float | None,
    sentiment_score: float | None,
    avg_sentiment_score: float | None,
    media_available: bool | None,
    image_url: str | None,
) -> float:
    """
    MVP popularity formula:
        0.45 * review_score
      + 0.30 * rating_score
      + 0.15 * sentiment_value
      + 0.10 * media_score
    """
    review_score = min((total_reviews or 0) / 1000, 1.0)
    rating_score = (avg_rating or 0) / 5.0
    sentiment_value = sentiment_score if sentiment_score is not None else (
        avg_sentiment_score if avg_sentiment_score is not None else 0.0
    )
    media_score = 1.0 if (media_available and image_url) else 0.0

    return round(
        0.45 * review_score
        + 0.30 * rating_score
        + 0.15 * sentiment_value
        + 0.10 * media_score,
        6,
    )


def build_scoring_context(rows: list[dict]) -> ImportScoringContext:
    """
    Build calibration values from the latest curated CSV snapshot.

    The recommendation score uses a Bayesian rating baseline so that
    destinations with a smaller review count are not punished too harshly.
    """
    ratings = [
        rating
        for row in rows
        if (rating := safe_float(row.get("avg_rating"))) is not None
    ]
    avg_rating_baseline = sum(ratings) / len(ratings) if ratings else 4.0
    return ImportScoringContext(avg_rating_baseline=avg_rating_baseline)


def calculate_quality_score(
    row: dict,
    *,
    total_reviews: int | None,
    avg_rating: float | None,
    sentiment_score: float | None,
    avg_sentiment_score: float | None,
    scoring_context: ImportScoringContext,
) -> float:
    """
    Calculate a quality-oriented score for recommendation surfaces.

    We intentionally separate this from popular_score:
      - popular_score answers "what is currently popular?"
      - quality_score answers "what is broadly strong for users?"
    """
    rating_value = avg_rating or 0.0
    review_count = total_reviews or 0
    sentiment_value = sentiment_score if sentiment_score is not None else (
        avg_sentiment_score if avg_sentiment_score is not None else 0.0
    )

    bayes_m = scoring_context.bayesian_min_reviews
    baseline = scoring_context.avg_rating_baseline
    bayesian_rating = (
        (review_count / (review_count + bayes_m)) * rating_value
        + (bayes_m / (review_count + bayes_m)) * baseline
        if (review_count + bayes_m) > 0
        else baseline
    )
    bayesian_rating_norm = bayesian_rating / 5.0

    review_confidence = min(
        math.log1p(review_count) / math.log1p(scoring_context.review_log_cap),
        1.0,
    )

    opening_hours_available = any(
        [
            safe_str(row.get("jam_buka")) and safe_str(row.get("jam_tutup")),
            safe_str(row.get("jam_buka_weekday"))
            and safe_str(row.get("jam_tutup_weekday")),
            safe_str(row.get("jam_buka_weekend"))
            and safe_str(row.get("jam_tutup_weekend")),
        ],
    )
    completeness_checks = [
        safe_str(row.get("deskripsi_google")) is not None,
        safe_str(row.get("price_type")) is not None,
        safe_int(row.get("estimasi_durasi_menit")) is not None,
        safe_str(row.get("media_image_url")) is not None,
        safe_str(row.get("media_destination_url")) is not None,
        safe_str(row.get("final_primary_intent")) is not None,
        safe_str(row.get("final_core_labels")) is not None,
        opening_hours_available,
    ]
    data_completeness = sum(1 for ok in completeness_checks if ok) / len(
        completeness_checks,
    )

    facility_values = [safe_bool(row.get(col)) for col in FACILITY_SOURCE_COLUMNS]
    known_facility_values = [value for value in facility_values if value is not None]
    facility_coverage = len(known_facility_values) / len(FACILITY_SOURCE_COLUMNS)
    facility_positive_ratio = (
        sum(1 for value in known_facility_values if value is True)
        / len(known_facility_values)
        if known_facility_values
        else 0.0
    )
    facility_confidence = (
        0.6 * facility_coverage + 0.4 * facility_positive_ratio
    )

    return round(
        0.45 * bayesian_rating_norm
        + 0.20 * sentiment_value
        + 0.20 * review_confidence
        + 0.10 * data_completeness
        + 0.05 * facility_confidence,
        6,
    )


def is_active_candidate(row: dict) -> bool:
    """
    MVP active data filter:
        curation_action == 'keep'
        display_status == 'active_candidate'
        media_available == True
        coordinate_verified == True
    """
    return (
        safe_str(row.get("curation_action")) == "keep"
        and safe_str(row.get("display_status")) == "active_candidate"
        and safe_bool(row.get("media_available")) is True
        and safe_bool(row.get("coordinate_verified")) is True
    )


# =========================================================================
# Row → model data transformers
# =========================================================================


def build_destination_data(
    row: dict,
    slug: str,
    scoring_context: ImportScoringContext,
) -> dict:
    """Transform a CSV row into Destination column values."""
    total_reviews = safe_int(row.get("total_ulasan"))
    avg_rating = safe_float(row.get("avg_rating"))
    sentiment_sc = safe_float(row.get("sentiment_score"))
    avg_sentiment = safe_float(row.get("avg_sentimen_skor"))
    media_avail = safe_bool(row.get("media_available"))
    image_url = safe_str(row.get("media_image_url"))

    return {
        "external_id": safe_str(row["location_id"]),
        "slug": slug,
        "name": safe_str(row["location_name"]),
        "category": safe_str(row.get("category")),
        "subcategory": safe_str(row.get("subcategory")),
        "description": safe_str(row.get("deskripsi_google")),
        "tourism_zone": safe_str(row.get("zona_wisata")),
        "synthetic_tags": parse_comma_list(row.get("tags_sintetis")),
        "crowd_level": safe_str(row.get("crowd_level")),
        "latitude": safe_float(row.get("latitude")),
        "longitude": safe_float(row.get("longitude")),
        "distance_from_center_km": safe_float(
            row.get("distance_from_alun_alun_km")
        ),
        "coordinate_verified": safe_bool(row.get("coordinate_verified")),
        "price_min": safe_int(row.get("price_min")),
        "price_max": safe_int(row.get("price_max")),
        "price_type": safe_str(row.get("price_type")),
        "opening_time": safe_str(row.get("jam_buka")),
        "closing_time": safe_str(row.get("jam_tutup")),
        "weekday_opening_time": safe_str(row.get("jam_buka_weekday")),
        "weekday_closing_time": safe_str(row.get("jam_tutup_weekday")),
        "weekend_opening_time": safe_str(row.get("jam_buka_weekend")),
        "weekend_closing_time": safe_str(row.get("jam_tutup_weekend")),
        "estimated_duration_minutes": safe_int(
            row.get("estimasi_durasi_menit")
        ),
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "positive_reviews": safe_int(row.get("ulasan_positif")),
        "negative_reviews": safe_int(row.get("ulasan_negatif")),
        "sentiment_score": sentiment_sc,
        "avg_sentiment_score": avg_sentiment,
        "sentiment_label": safe_str(row.get("sentimen_label_lokasi")),
        "sentiment_available": safe_bool(row.get("sentiment_available")),
        "curation_action": safe_str(row.get("curation_action")),
        "display_status": safe_str(row.get("display_status")),
        "is_active": safe_bool(row.get("is_active_verified")),
        "popular_score": calculate_popular_score(
            total_reviews,
            avg_rating,
            sentiment_sc,
            avg_sentiment,
            media_avail,
            image_url,
        ),
        "quality_score": calculate_quality_score(
            row,
            total_reviews=total_reviews,
            avg_rating=avg_rating,
            sentiment_score=sentiment_sc,
            avg_sentiment_score=avg_sentiment,
            scoring_context=scoring_context,
        ),
    }


def build_media_data(row: dict) -> dict:
    """Transform a CSV row into DestinationMedia column values."""
    return {
        "media_available": safe_bool(row.get("media_available")),
        "image_url": safe_str(row.get("media_image_url")),
        "maps_url": safe_str(row.get("media_destination_url")),
        "website_url": safe_str(row.get("media_website")),
        "media_source": safe_str(row.get("media_source")),
        "place_id": safe_str(row.get("media_place_id")),
        "media_audit_status": safe_str(row.get("media_audit_status")),
    }


def build_label_data(row: dict) -> dict:
    """Transform a CSV row into DestinationLabel column values."""
    ext_id = safe_str(row.get("location_id", "?"))
    return {
        "primary_intent": safe_str(row.get("final_primary_intent")),
        "core_labels": parse_semicolon_list(row.get("final_core_labels")),
        "secondary_labels": parse_semicolon_list(
            row.get("final_secondary_labels")
        ),
        "avoid_labels": parse_semicolon_list(row.get("final_avoid_labels")),
        "label_confidence": safe_float(row.get("label_confidence")),
        "label_source": safe_str(row.get("final_label_source")),
        "label_scores": parse_json(row.get("label_scores_json"), ext_id),
    }


def build_facility_data(row: dict) -> dict:
    """Transform a CSV row into DestinationFacility column values."""
    return {
        "parking_available": safe_bool(row.get("parking_verified")),
        "wheelchair_accessible": safe_bool(
            row.get("wheelchair_accessible_verified")
        ),
        "toilet_available": safe_bool(row.get("toilet_verified")),
        "mushola_available": safe_bool(row.get("mushola_verified")),
        "pet_friendly": safe_bool(row.get("pet_friendly_verified")),
        "open_24h": safe_bool(row.get("open_24h_verified")),
        "child_friendly": safe_bool(row.get("child_friendly_verified")),
        "night_available": safe_bool(row.get("night_verified")),
        "indoor_available": safe_bool(row.get("indoor_verified")),
        "safety_verified": safe_bool(row.get("safety_verified")),
    }


# =========================================================================
# Upsert logic
# =========================================================================


def upsert_destination(
    db,
    row: dict,
    existing_slugs: set[str],
    scoring_context: ImportScoringContext,
) -> tuple[str, str]:
    """
    Insert or update a single destination and its child records.
    Returns (external_id, 'inserted' | 'updated').
    """
    ext_id = safe_str(row["location_id"])
    name = safe_str(row["location_name"])

    # Check if destination already exists
    dest = db.query(Destination).filter(
        Destination.external_id == ext_id
    ).first()

    action = "updated" if dest else "inserted"

    if dest:
        # Regenerate slug keeping existing if unchanged name
        slug = dest.slug
        if dest.name != name:
            # Name changed — regenerate slug
            existing_slugs.discard(dest.slug)
            slug = generate_slug(name, ext_id, existing_slugs)

        dest_data = build_destination_data(row, slug, scoring_context)
        for key, value in dest_data.items():
            setattr(dest, key, value)
    else:
        slug = generate_slug(name, ext_id, existing_slugs)
        dest_data = build_destination_data(row, slug, scoring_context)
        dest = Destination(**dest_data)
        db.add(dest)

    # Flush to get dest.id for child tables
    db.flush()

    # --- Media ---
    media_data = build_media_data(row)
    if dest.media:
        for key, value in media_data.items():
            setattr(dest.media, key, value)
    else:
        dest.media = DestinationMedia(**media_data)

    # --- Labels ---
    label_data = build_label_data(row)
    if dest.labels:
        for key, value in label_data.items():
            setattr(dest.labels, key, value)
    else:
        dest.labels = DestinationLabel(**label_data)

    # --- Facilities ---
    facility_data = build_facility_data(row)
    if dest.facilities:
        for key, value in facility_data.items():
            setattr(dest.facilities, key, value)
    else:
        dest.facilities = DestinationFacility(**facility_data)

    return ext_id, action


# =========================================================================
# Main import logic
# =========================================================================


def validate_columns(headers: list[str]) -> list[str]:
    """Return list of missing required columns."""
    header_set = set(headers)
    return [col for col in REQUIRED_COLUMNS if col not in header_set]


def run_import(
    csv_path: str,
    dry_run: bool = False,
    limit: int | None = None,
    include_inactive: bool = False,
    clear_existing: bool = False,
) -> None:
    """Execute the CSV import pipeline."""

    # ── 1. Read CSV ──────────────────────────────────────
    path = Path(csv_path)
    if not path.exists():
        print(f"❌ CSV file not found: {path}")
        sys.exit(1)

    print(f"📂 Reading CSV: {path}")

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # ── 2. Validate columns ──────────────────────────
        missing = validate_columns(headers)
        if missing:
            print("❌ Missing required columns:")
            for col in missing:
                print(f"   • {col}")
            sys.exit(1)

        # Check optional columns
        optional_present = {
            col: col in headers for col in OPTIONAL_COLUMNS
        }
        for col, present in optional_present.items():
            if not present:
                print(f"  ℹ Optional column '{col}' not in CSV — will use None")

        rows = list(reader)

    total_rows = len(rows)
    print(f"📊 Total rows in CSV: {total_rows}")

    scoring_rows = [r for r in rows if is_active_candidate(r)] or rows
    scoring_context = build_scoring_context(scoring_rows)
    print(
        "🧮 Scoring baseline:"
        f" avg_rating={scoring_context.avg_rating_baseline:.4f},"
        f" bayes_m={scoring_context.bayesian_min_reviews}",
    )

    # ── 3. Apply active filter ───────────────────────────
    if include_inactive:
        filtered_rows = rows
        skipped_inactive = 0
    else:
        filtered_rows = [r for r in rows if is_active_candidate(r)]
        skipped_inactive = total_rows - len(filtered_rows)

    # ── 4. Apply limit ───────────────────────────────────
    if limit is not None:
        filtered_rows = filtered_rows[:limit]
        print(f"🔢 Limiting to {limit} rows")

    active_rows = len(filtered_rows)
    print(f"✅ Rows to process: {active_rows}")
    print(f"⏭  Skipped (inactive): {skipped_inactive}")

    if active_rows == 0:
        print("⚠ No rows to import. Exiting.")
        return

    # ── 5. Dry-run preview ───────────────────────────────
    if dry_run:
        print("\n🔍 DRY RUN — previewing first 3 rows:\n")
        existing_slugs: set[str] = set()
        for i, row in enumerate(filtered_rows[:3]):
            ext_id = safe_str(row["location_id"])
            name = safe_str(row["location_name"])
            slug = generate_slug(name or "", ext_id or "", existing_slugs)
            dest_data = build_destination_data(row, slug, scoring_context)
            print(f"  [{i + 1}] {ext_id}: {name}")
            print(f"      slug: {slug}")
            print(f"      category: {dest_data['category']}")
            print(f"      tourism_zone: {dest_data['tourism_zone']}")
            print(f"      popular_score: {dest_data['popular_score']}")
            print(f"      quality_score: {dest_data['quality_score']}")
            print(f"      synthetic_tags: {dest_data['synthetic_tags']}")
            label_data = build_label_data(row)
            print(f"      primary_intent: {label_data['primary_intent']}")
            print(f"      core_labels: {label_data['core_labels']}")
            print()

        print("─" * 50)
        print("📋 DRY RUN SUMMARY")
        print(f"   CSV file:           {path}")
        print(f"   Total rows:         {total_rows}")
        print(f"   Active rows:        {active_rows}")
        print(f"   Skipped inactive:   {skipped_inactive}")
        print(f"   Would insert/update: {active_rows}")
        print(f"   Dry run:            True")
        print("─" * 50)
        return

    # ── 6. Database import ───────────────────────────────
    db = SessionLocal()
    try:
        # Clear existing if requested
        if clear_existing:
            print("🗑  Clearing existing destination data...")
            db.query(DestinationFacility).delete()
            db.query(DestinationLabel).delete()
            db.query(DestinationMedia).delete()
            db.query(Destination).delete()
            db.flush()
            print("   Cleared all destination tables.")

        # Collect existing slugs to avoid duplicates
        existing_slugs: set[str] = set()
        for (slug_val,) in db.query(Destination.slug).all():
            existing_slugs.add(slug_val)

        inserted = 0
        updated = 0
        errors = 0
        error_rows: list[str] = []

        for i, row in enumerate(filtered_rows):
            ext_id = safe_str(row.get("location_id", f"row-{i}"))
            try:
                _, action = upsert_destination(
                    db,
                    row,
                    existing_slugs,
                    scoring_context,
                )
                if action == "inserted":
                    inserted += 1
                else:
                    updated += 1
            except Exception as exc:
                errors += 1
                error_rows.append(f"{ext_id}: {exc}")
                print(f"  ❌ Error on {ext_id}: {exc}")
                db.rollback()
                # Re-create session state for next row
                continue

            # Progress indicator every 50 rows
            if (i + 1) % 50 == 0:
                print(f"  ... processed {i + 1}/{active_rows}")

        # ── 7. Commit ────────────────────────────────────
        db.commit()
        print(f"\n✅ Import committed to database.")

        # ── 8. Summary ───────────────────────────────────
        print()
        print("─" * 50)
        print("📋 IMPORT SUMMARY")
        print(f"   CSV file:           {path}")
        print(f"   Total rows:         {total_rows}")
        print(f"   Active rows:        {active_rows}")
        print(f"   Skipped inactive:   {skipped_inactive}")
        print(f"   Inserted:           {inserted}")
        print(f"   Updated:            {updated}")
        print(f"   Errors:             {errors}")
        print(f"   Dry run:            False")
        print("─" * 50)

        if error_rows:
            print("\n⚠ Error details:")
            for err in error_rows:
                print(f"   • {err}")

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Fatal error — rolled back: {exc}")
        sys.exit(1)
    finally:
        db.close()


# =========================================================================
# CLI
# =========================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import destination data from CSV into PostgreSQL",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the CSV file (relative to working directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate and preview without writing to the database",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of rows to import (for testing)",
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        default=False,
        help="Include rows that don't pass the active data filter",
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        default=False,
        help="Delete all existing destination data before import",
    )

    args = parser.parse_args()

    print()
    print("=" * 50)
    print(" MuterBandung — Destination CSV Import")
    print("=" * 50)
    print()

    run_import(
        csv_path=args.file,
        dry_run=args.dry_run,
        limit=args.limit,
        include_inactive=args.include_inactive,
        clear_existing=args.clear_existing,
    )


if __name__ == "__main__":
    main()
