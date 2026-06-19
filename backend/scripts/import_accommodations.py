#!/usr/bin/env python3
"""
CSV Import Script for Accommodation Data
========================================

Reads the curated lodging CSV dataset and populates the accommodations table.

Usage:
    python scripts/import_accommodations.py --file data/penginapan_data.csv --dry-run
    python scripts/import_accommodations.py --file data/penginapan_data.csv
    python scripts/import_accommodations.py --file data/penginapan_data.csv --clear-existing
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.accommodation import Accommodation  # noqa: E402


REQUIRED_COLUMNS: list[str] = [
    "location_id",
    "location_name",
    "category",
    "subcategory",
    "latitude",
    "longitude",
    "price_min",
    "price_max",
    "deskripsi_google",
    "avg_rating",
    "total_ulasan",
    "ulasan_positif",
    "ulasan_negatif",
    "sentimen_label_lokasi",
    "avg_sentimen_skor",
    "sentiment_score",
    "sentiment_available",
    "media_image_url",
    "media_destination_url",
    "media_website",
    "media_source",
    "media_available",
    "display_status",
    "is_active_verified",
    "coordinate_verified",
    "distance_from_alun_alun_km",
    "kota_kabupaten",
    "kecamatan",
]


FACILITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Wi-Fi": ("wi-fi", "wifi", "free wi-fi", "wi fi"),
    "Parkir": ("parkir", "parking", "free parking"),
    "AC": ("ber-ac", "air conditioning", "ac"),
    "Restoran": ("restaurant", "restoran"),
    "Dapur": ("dapur", "kitchen"),
    "Kolam Renang": ("kolam renang", "pool"),
    "Gym": ("gym", "fitness"),
    "Sarapan": ("breakfast", "sarapan"),
    "Ramah Anak": ("cocok untuk anak", "child", "children"),
    "Bebas Asap Rokok": ("bebas asap rokok", "non-smoking"),
    "Akses Difabel": ("dapat diakses pengguna kursi roda", "wheelchair"),
}


def safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def safe_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def safe_bool(value: Any) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def generate_slug(name: str, external_id: str, existing_slugs: set[str]) -> str:
    slug = unicodedata.normalize("NFKD", name)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        slug = external_id.lower()
    if slug in existing_slugs:
        slug = f"{slug}-{external_id.lower()}"
    existing_slugs.add(slug)
    return slug


def extract_facilities(description: str | None) -> list[str]:
    text = (description or "").lower()
    facilities: list[str] = []
    for label, keywords in FACILITY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            facilities.append(label)
    return facilities


def calculate_quality_score(row: dict) -> float:
    rating = safe_float(row.get("avg_rating"))
    total_reviews = safe_int(row.get("total_ulasan"))
    sentiment_score = safe_float(row.get("sentiment_score"))
    avg_sentiment_score = safe_float(row.get("avg_sentimen_skor"))

    rating_score = max(0.0, min(100.0, (rating or 0.0) * 20.0))
    review_score = (
        max(0.0, min(100.0, math.log1p(total_reviews) / math.log1p(10000) * 100))
        if total_reviews
        else 0.0
    )
    sentiment_value = sentiment_score
    if sentiment_value is None and avg_sentiment_score is not None:
        # This source sometimes uses a wider sentiment scale. Keep it bounded.
        sentiment_value = max(0.0, min(100.0, avg_sentiment_score * 20.0))
    sentiment_value = sentiment_value or 0.0

    completeness_checks = [
        safe_str(row.get("location_name")) is not None,
        safe_float(row.get("latitude")) is not None,
        safe_float(row.get("longitude")) is not None,
        safe_str(row.get("media_image_url")) is not None,
        safe_str(row.get("media_destination_url")) is not None,
        safe_int(row.get("price_min")) is not None,
        rating is not None,
        total_reviews is not None,
        bool(extract_facilities(row.get("deskripsi_google"))),
    ]
    completeness_score = (
        sum(1 for item in completeness_checks if item) / len(completeness_checks) * 100
    )

    return round(
        0.45 * rating_score
        + 0.25 * review_score
        + 0.20 * completeness_score
        + 0.10 * sentiment_value,
        2,
    )


def validate_columns(header: list[str]) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def read_rows(csv_path: Path, limit: int | None = None) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        validate_columns(reader.fieldnames or [])
        rows = []
        for index, row in enumerate(reader):
            if limit is not None and index >= limit:
                break
            rows.append(row)
        return rows


def read_gallery_images(csv_path: Path) -> dict[str, str]:
    """Read gallery CSV and return the best (lowest image_order) image for each location."""
    if not csv_path.exists():
        return {}
    
    gallery: dict[str, list[tuple[int, str]]] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            loc_id = row.get("location_id")
            image_url = row.get("image_url")
            image_order = safe_int(row.get("image_order")) or 999
            if loc_id and image_url:
                gallery.setdefault(loc_id, []).append((image_order, image_url))
                
    best_images = {}
    for loc_id, images in gallery.items():
        images.sort(key=lambda x: x[0])
        best_images[loc_id] = images[0][1]
        
    return best_images


def import_accommodations(
    csv_path: Path,
    *,
    gallery_csv_path: Path | None = None,
    dry_run: bool = False,
    clear_existing: bool = False,
    include_inactive: bool = False,
    limit: int | None = None,
) -> None:
    rows = read_rows(csv_path, limit=limit)
    
    gallery_images = {}
    if gallery_csv_path and gallery_csv_path.exists():
        gallery_images = read_gallery_images(gallery_csv_path)

    db = SessionLocal()
    inserted = 0
    updated = 0
    skipped = 0
    errors = 0

    try:
        if clear_existing and not dry_run:
            deleted = db.query(Accommodation).delete()
            print(f"🧹 Cleared existing accommodations: {deleted}")

        existing_slugs = {
            slug
            for (slug,) in db.query(Accommodation.slug).all()
            if slug
        }

        for row in rows:
            external_id = safe_str(row.get("location_id"))
            name = safe_str(row.get("location_name"))
            if not external_id or not name:
                errors += 1
                continue

            display_status = safe_str(row.get("display_status"))
            is_active = safe_bool(row.get("is_active_verified"))
            if not include_inactive and (
                display_status != "active_candidate" or is_active is not True
            ):
                skipped += 1
                continue

            accommodation = (
                db.query(Accommodation)
                .filter(Accommodation.external_id == external_id)
                .first()
            )
            created = accommodation is None
            if accommodation is None:
                accommodation = Accommodation(external_id=external_id)
            elif accommodation.slug:
                existing_slugs.discard(accommodation.slug)

            accommodation.slug = generate_slug(name, external_id, existing_slugs)
            accommodation.name = name
            accommodation.category = safe_str(row.get("category"))
            accommodation.accommodation_type = safe_str(row.get("subcategory"))
            accommodation.description = safe_str(row.get("deskripsi_google"))
            accommodation.facilities = extract_facilities(accommodation.description)
            accommodation.latitude = safe_float(row.get("latitude"))
            accommodation.longitude = safe_float(row.get("longitude"))
            accommodation.city = safe_str(row.get("kota_kabupaten"))
            accommodation.district = safe_str(row.get("kecamatan"))
            accommodation.distance_from_center_km = safe_float(
                row.get("distance_from_alun_alun_km"),
            )
            accommodation.coordinate_verified = safe_bool(
                row.get("coordinate_verified"),
            )
            accommodation.price_min = safe_int(row.get("price_min"))
            accommodation.price_max = safe_int(row.get("price_max"))
            accommodation.avg_rating = safe_float(row.get("avg_rating"))
            accommodation.total_reviews = safe_int(row.get("total_ulasan"))
            accommodation.positive_reviews = safe_int(row.get("ulasan_positif"))
            accommodation.negative_reviews = safe_int(row.get("ulasan_negatif"))
            accommodation.sentiment_score = safe_float(row.get("sentiment_score"))
            accommodation.avg_sentiment_score = safe_float(
                row.get("avg_sentimen_skor"),
            )
            accommodation.sentiment_label = safe_str(
                row.get("sentimen_label_lokasi"),
            )
            accommodation.sentiment_available = safe_bool(
                row.get("sentiment_available"),
            )
            accommodation.image_url = safe_str(row.get("media_image_url"))
            if not accommodation.image_url and external_id in gallery_images:
                accommodation.image_url = gallery_images[external_id]
                
            accommodation.destination_url = safe_str(row.get("media_destination_url"))
            accommodation.website_url = safe_str(row.get("media_website"))
            accommodation.media_source = safe_str(row.get("media_source"))
            accommodation.media_available = (
                safe_bool(row.get("media_available"))
                if safe_bool(row.get("media_available")) is not None
                else bool(accommodation.image_url)
            )
            accommodation.display_status = display_status
            accommodation.is_active = is_active
            accommodation.quality_score = calculate_quality_score(row)
            accommodation.source_payload = {
                key: value for key, value in row.items() if safe_str(value)
            }

            if not dry_run:
                db.add(accommodation)

            if created:
                inserted += 1
            else:
                updated += 1

        if dry_run:
            db.rollback()
        else:
            db.commit()

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("\n✅ Accommodation import completed." if not dry_run else "\n✅ Dry run completed.")
    print("─" * 50)
    print(f"CSV file:           {csv_path}")
    print(f"Total rows:         {len(rows)}")
    print(f"Inserted:           {inserted}")
    print(f"Updated:            {updated}")
    print(f"Skipped inactive:   {skipped}")
    print(f"Errors:             {errors}")
    print(f"Dry run:            {dry_run}")
    print("─" * 50)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import accommodation CSV data")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("data/penginapan_data.csv"),
        help="Path to accommodation CSV file",
    )
    parser.add_argument(
        "--gallery-file",
        type=Path,
        default=Path("data/penginapan_gallery_data.csv"),
        help="Path to accommodation gallery CSV file for image fallbacks",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clear-existing", action="store_true")
    parser.add_argument("--include-inactive", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = args.file
    if not csv_path.is_absolute():
        csv_path = _BACKEND_DIR / csv_path
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")
        
    gallery_csv_path = args.gallery_file
    if not gallery_csv_path.is_absolute():
        gallery_csv_path = _BACKEND_DIR / gallery_csv_path

    import_accommodations(
        csv_path,
        gallery_csv_path=gallery_csv_path,
        dry_run=args.dry_run,
        clear_existing=args.clear_existing,
        include_inactive=args.include_inactive,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
