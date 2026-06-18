#!/usr/bin/env python3
"""
Import destination gallery images from wisata_image.csv.

This importer only touches destination_gallery_images. It does not update
hero images, destination scores, labels, favorites, or user events.

Usage:
    python scripts/import_destination_gallery_images.py --file data/wisata_image.csv --dry-run
    python scripts/import_destination_gallery_images.py --file data/wisata_image.csv --apply
"""

from __future__ import annotations

import argparse
import csv
import sys
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy.orm import joinedload

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.destination import Destination  # noqa: E402
from app.models.destination_gallery_image import DestinationGalleryImage  # noqa: E402


REQUIRED_COLUMNS = [
    "location_id",
    "location_name",
    "gallery_index",
    "source_image_url",
    "media_storage_url",
    "media_public_id",
    "media_upload_status",
    "match_confidence",
    "matched_title",
]


@dataclass(frozen=True)
class CsvGalleryImage:
    """One validated gallery image row from CSV."""

    location_id: str
    sort_order: int
    image_url: str
    source_image_url: str | None
    media_public_id: str | None
    match_confidence: str | None
    matched_title: str | None
    upload_status: str | None


@dataclass
class ReadStats:
    """CSV read and validation counters."""

    total_rows: int = 0
    processed_rows: int = 0
    valid_rows: int = 0
    skipped_invalid_rows: int = 0
    duplicate_gallery_index: int = 0
    skip_reasons: Counter[str] = field(default_factory=Counter)


@dataclass
class DestinationGalleryBatch:
    """Gallery images planned for one matched destination."""

    destination_id: uuid.UUID
    external_id: str
    destination_name: str
    existing_image_count: int
    images: list[CsvGalleryImage]


@dataclass
class ImportPlan:
    """Computed gallery import plan before optional database mutation."""

    read_stats: ReadStats
    valid_destinations: int = 0
    matched_destinations: int = 0
    missing_destinations: int = 0
    images_to_import: int = 0
    existing_images_to_replace: int = 0
    batches: list[DestinationGalleryBatch] = field(default_factory=list)
    missing_ids: list[str] = field(default_factory=list)


def safe_str(value: Any) -> str | None:
    """Return a trimmed string, or None for empty/null values."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def safe_int(value: Any) -> int | None:
    """Parse an integer, accepting values like '1.0'."""
    text = safe_str(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def validate_headers(headers: list[str]) -> list[str]:
    """Return required CSV columns that are missing."""
    header_set = set(headers)
    return [column for column in REQUIRED_COLUMNS if column not in header_set]


def _row_skip_reason(row: dict[str, Any]) -> str | None:
    """Return why a row is not eligible for gallery import."""
    if safe_str(row.get("location_id")) is None:
        return "missing_location_id"
    if safe_int(row.get("gallery_index")) is None:
        return "invalid_gallery_index"
    if safe_str(row.get("media_storage_url")) is None:
        return "missing_media_storage_url"
    if (safe_str(row.get("media_upload_status")) or "").lower() != "uploaded":
        return "upload_status_not_uploaded"
    return None


def collect_gallery_rows(
    csv_path: str | Path,
    limit: int | None = None,
) -> tuple[list[CsvGalleryImage], ReadStats]:
    """Read and validate gallery CSV rows without touching the database."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        missing = validate_headers(headers)
        if missing:
            missing_list = ", ".join(missing)
            raise ValueError(f"Missing required gallery columns: {missing_list}")
        rows = list(reader)

    stats = ReadStats(total_rows=len(rows))
    if limit is not None:
        rows = rows[:limit]
    stats.processed_rows = len(rows)

    seen_keys: set[tuple[str, int]] = set()
    valid_rows: list[CsvGalleryImage] = []

    for row in rows:
        skip_reason = _row_skip_reason(row)
        if skip_reason:
            stats.skipped_invalid_rows += 1
            stats.skip_reasons[skip_reason] += 1
            continue

        location_id = safe_str(row.get("location_id"))
        sort_order = safe_int(row.get("gallery_index"))
        assert location_id is not None
        assert sort_order is not None

        key = (location_id, sort_order)
        if key in seen_keys:
            stats.duplicate_gallery_index += 1
            stats.skip_reasons["duplicate_gallery_index"] += 1
            continue
        seen_keys.add(key)

        valid_rows.append(
            CsvGalleryImage(
                location_id=location_id,
                sort_order=sort_order,
                image_url=safe_str(row.get("media_storage_url")) or "",
                source_image_url=safe_str(row.get("source_image_url")),
                media_public_id=safe_str(row.get("media_public_id")),
                match_confidence=safe_str(row.get("match_confidence")),
                matched_title=safe_str(row.get("matched_title")),
                upload_status=safe_str(row.get("media_upload_status")),
            )
        )

    stats.valid_rows = len(valid_rows)
    return valid_rows, stats


def group_gallery_rows(rows: list[CsvGalleryImage]) -> dict[str, list[CsvGalleryImage]]:
    """Group gallery rows by location_id and sort by gallery index."""
    grouped: dict[str, list[CsvGalleryImage]] = defaultdict(list)
    for row in rows:
        grouped[row.location_id].append(row)

    return {
        location_id: sorted(images, key=lambda image: image.sort_order)
        for location_id, images in grouped.items()
    }


def build_import_plan(
    rows: list[CsvGalleryImage],
    destinations_by_external_id: dict[str, Destination],
    read_stats: ReadStats | None = None,
) -> ImportPlan:
    """Build a non-mutating import plan from CSV rows and DB destinations."""
    grouped = group_gallery_rows(rows)
    plan = ImportPlan(read_stats=read_stats or ReadStats())
    plan.valid_destinations = len(grouped)

    for location_id, images in grouped.items():
        destination = destinations_by_external_id.get(location_id)
        if destination is None:
            plan.missing_destinations += 1
            plan.missing_ids.append(location_id)
            continue

        existing_image_count = len(destination.gallery_images or [])
        plan.matched_destinations += 1
        plan.images_to_import += len(images)
        plan.existing_images_to_replace += existing_image_count
        plan.batches.append(
            DestinationGalleryBatch(
                destination_id=destination.id,
                external_id=destination.external_id,
                destination_name=destination.name,
                existing_image_count=existing_image_count,
                images=images,
            )
        )

    return plan


def build_gallery_models(plan: ImportPlan) -> list[DestinationGalleryImage]:
    """Create ORM objects for planned gallery images."""
    models: list[DestinationGalleryImage] = []
    for batch in plan.batches:
        for image in batch.images:
            models.append(
                DestinationGalleryImage(
                    id=uuid.uuid4(),
                    destination_id=batch.destination_id,
                    sort_order=image.sort_order,
                    image_url=image.image_url,
                    source_image_url=image.source_image_url,
                    media_public_id=image.media_public_id,
                    match_confidence=image.match_confidence,
                    matched_title=image.matched_title,
                    upload_status=image.upload_status,
                )
            )
    return models


def apply_import_plan(db, plan: ImportPlan, *, apply: bool) -> None:
    """Replace gallery rows for matched destinations when apply=True."""
    if not apply or not plan.batches:
        return

    destination_ids = [batch.destination_id for batch in plan.batches]
    db.query(DestinationGalleryImage).filter(
        DestinationGalleryImage.destination_id.in_(destination_ids)
    ).delete(synchronize_session=False)
    db.add_all(build_gallery_models(plan))


def _print_summary(plan: ImportPlan, *, apply: bool, preview_limit: int = 8) -> None:
    """Print a concise import summary."""
    stats = plan.read_stats
    mode = "APPLY" if apply else "DRY RUN"

    print()
    print("=" * 68)
    print(f" MuterBandung Destination Gallery Import - {mode}")
    print("=" * 68)
    print(f"CSV rows total:              {stats.total_rows}")
    print(f"CSV rows processed:          {stats.processed_rows}")
    print(f"Valid image rows:            {stats.valid_rows}")
    print(f"Skipped invalid rows:        {stats.skipped_invalid_rows}")
    print(f"Duplicate gallery indexes:   {stats.duplicate_gallery_index}")
    print(f"Valid destinations in CSV:   {plan.valid_destinations}")
    print(f"Matched destinations in DB:  {plan.matched_destinations}")
    print(f"Missing destinations in DB:  {plan.missing_destinations}")
    print(f"Existing images to replace:  {plan.existing_images_to_replace}")
    print(f"{'Imported' if apply else 'Would import'} images:          {plan.images_to_import}")

    if stats.skip_reasons:
        print()
        print("Skip reasons:")
        for reason, count in stats.skip_reasons.most_common():
            print(f"  - {reason}: {count}")

    if plan.missing_ids:
        print()
        print("Missing destination IDs in DB:")
        for location_id in plan.missing_ids[:preview_limit]:
            print(f"  - {location_id}")
        if len(plan.missing_ids) > preview_limit:
            print(f"  ... and {len(plan.missing_ids) - preview_limit} more")

    if plan.batches:
        print()
        print("Preview batches:")
        for batch in plan.batches[:preview_limit]:
            first_image = batch.images[0].image_url if batch.images else "-"
            print(
                f"  - {batch.external_id} | {batch.destination_name} "
                f"| {len(batch.images)} images"
            )
            print(f"    first image: {first_image}")
        if len(plan.batches) > preview_limit:
            print(f"  ... and {len(plan.batches) - preview_limit} more destinations")

    print("=" * 68)
    if not apply:
        print("No database changes were committed. Re-run with --apply to import.")


def run_import(csv_path: str, *, apply: bool, limit: int | None = None) -> ImportPlan:
    """Read CSV, compare with DB, optionally replace gallery rows, and return plan."""
    rows, read_stats = collect_gallery_rows(csv_path, limit=limit)
    grouped = group_gallery_rows(rows)
    external_ids = list(grouped)

    db = SessionLocal()
    try:
        destinations = (
            db.query(Destination)
            .options(joinedload(Destination.gallery_images))
            .filter(Destination.external_id.in_(external_ids))
            .all()
            if external_ids
            else []
        )
        destinations_by_external_id = {
            destination.external_id: destination for destination in destinations
        }

        plan = build_import_plan(rows, destinations_by_external_id, read_stats)
        apply_import_plan(db, plan, apply=apply)

        if apply:
            db.commit()
        else:
            db.rollback()

        _print_summary(plan, apply=apply)
        return plan
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import destination detail gallery images from wisata_image.csv",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="CSV path, for example data/wisata_image.csv",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview without committing changes",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Replace gallery rows for matched destinations",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N CSV rows for a small test run",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        run_import(args.file, apply=args.apply, limit=args.limit)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
