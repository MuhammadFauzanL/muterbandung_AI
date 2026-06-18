#!/usr/bin/env python3
"""
Safely sync destination media fields from a curated CSV snapshot.

This script is intentionally narrower than import_destinations.py:
it updates only existing destination_media records matched by
CSV location_id -> destinations.external_id. It does not create, delete,
activate, deactivate, or rescore destinations.

Usage:
    python scripts/sync_destination_media_from_csv.py --file data/wisata_populer.csv --dry-run
    python scripts/sync_destination_media_from_csv.py --file data/wisata_populer.csv --apply
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy.orm import joinedload

# Ensure the backend package is importable when running from backend/.
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.destination import Destination  # noqa: E402


REQUIRED_COLUMNS = [
    "location_id",
    "media_available",
    "media_image_url",
    "media_destination_url",
    "media_website",
    "media_source",
    "media_place_id",
    "media_audit_status",
]

ACCEPTED_AUDIT_STATUSES = {"accepted", "manual_accepted"}

# (DestinationMedia attribute, CSV column, overwrite with blank?)
MEDIA_FIELD_MAP = [
    ("image_url", "media_image_url", True),
    ("maps_url", "media_destination_url", False),
    ("website_url", "media_website", False),
    ("media_source", "media_source", False),
    ("place_id", "media_place_id", False),
    ("media_audit_status", "media_audit_status", False),
]


@dataclass(frozen=True)
class CsvMediaRow:
    """Validated media data from one CSV row."""

    location_id: str
    values: dict[str, str | None]


@dataclass
class ReadStats:
    """CSV read and validation counters."""

    total_rows: int = 0
    processed_rows: int = 0
    valid_rows: int = 0
    skipped_invalid_media: int = 0
    duplicate_location_id: int = 0
    skip_reasons: Counter[str] = field(default_factory=Counter)


@dataclass
class MediaChange:
    """Pending field changes for one destination media record."""

    location_id: str
    destination_name: str
    media: Any
    changes: dict[str, tuple[str | None, str | None]]


@dataclass
class SyncPlan:
    """Computed sync plan before optional database mutation."""

    read_stats: ReadStats
    valid_rows: int = 0
    matched_in_db: int = 0
    missing_in_db: int = 0
    missing_media_record: int = 0
    changed: int = 0
    unchanged: int = 0
    changes: list[MediaChange] = field(default_factory=list)
    missing_ids: list[str] = field(default_factory=list)


def safe_str(value: Any) -> str | None:
    """Return a trimmed string, or None for empty/null values."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def safe_bool(value: Any) -> bool | None:
    """Parse common boolean strings."""
    text = safe_str(value)
    if text is None:
        return None
    normalized = text.lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    return None


def validate_headers(headers: list[str]) -> list[str]:
    """Return required CSV columns that are missing."""
    header_set = set(headers)
    return [column for column in REQUIRED_COLUMNS if column not in header_set]


def _row_skip_reason(row: dict[str, Any]) -> str | None:
    """Return why a row is not eligible for media sync."""
    if safe_str(row.get("location_id")) is None:
        return "missing_location_id"
    if safe_bool(row.get("media_available")) is not True:
        return "media_available_not_true"
    if safe_str(row.get("media_image_url")) is None:
        return "missing_media_image_url"

    audit_status = (safe_str(row.get("media_audit_status")) or "").lower()
    if audit_status not in ACCEPTED_AUDIT_STATUSES:
        return "media_audit_status_not_accepted"

    return None


def collect_media_rows(csv_path: str | Path, limit: int | None = None) -> tuple[list[CsvMediaRow], ReadStats]:
    """Read and validate CSV media rows without touching the database."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        missing = validate_headers(headers)
        if missing:
            missing_list = ", ".join(missing)
            raise ValueError(f"Missing required media columns: {missing_list}")

        rows = list(reader)

    stats = ReadStats(total_rows=len(rows))
    if limit is not None:
        rows = rows[:limit]
    stats.processed_rows = len(rows)

    seen_location_ids: set[str] = set()
    valid_rows: list[CsvMediaRow] = []

    for row in rows:
        location_id = safe_str(row.get("location_id"))
        skip_reason = _row_skip_reason(row)
        if skip_reason:
            stats.skipped_invalid_media += 1
            stats.skip_reasons[skip_reason] += 1
            continue

        assert location_id is not None
        if location_id in seen_location_ids:
            stats.duplicate_location_id += 1
            stats.skip_reasons["duplicate_location_id"] += 1
            continue
        seen_location_ids.add(location_id)

        values = {
            attr: safe_str(row.get(column))
            for attr, column, _overwrite_blank in MEDIA_FIELD_MAP
        }
        valid_rows.append(CsvMediaRow(location_id=location_id, values=values))

    stats.valid_rows = len(valid_rows)
    return valid_rows, stats


def _field_changes(media: Any, candidate: CsvMediaRow) -> dict[str, tuple[str | None, str | None]]:
    """Compare current media with candidate values."""
    changes: dict[str, tuple[str | None, str | None]] = {}
    overwrite_blank_by_attr = {
        attr: overwrite_blank for attr, _column, overwrite_blank in MEDIA_FIELD_MAP
    }

    for attr, new_value in candidate.values.items():
        if new_value is None and not overwrite_blank_by_attr[attr]:
            continue
        old_value = safe_str(getattr(media, attr, None))
        if old_value != new_value:
            changes[attr] = (old_value, new_value)

    return changes


def build_sync_plan(
    candidates: list[CsvMediaRow],
    destinations_by_external_id: dict[str, Destination],
    read_stats: ReadStats | None = None,
) -> SyncPlan:
    """Build a non-mutating sync plan from validated rows and DB objects."""
    plan = SyncPlan(read_stats=read_stats or ReadStats())
    plan.valid_rows = len(candidates)

    for candidate in candidates:
        destination = destinations_by_external_id.get(candidate.location_id)
        if destination is None:
            plan.missing_in_db += 1
            plan.missing_ids.append(candidate.location_id)
            continue

        plan.matched_in_db += 1
        media = destination.media
        if media is None:
            plan.missing_media_record += 1
            continue

        changes = _field_changes(media, candidate)
        if not changes:
            plan.unchanged += 1
            continue

        plan.changed += 1
        plan.changes.append(
            MediaChange(
                location_id=candidate.location_id,
                destination_name=destination.name,
                media=media,
                changes=changes,
            )
        )

    return plan


def apply_sync_plan(plan: SyncPlan, *, apply: bool) -> None:
    """Apply planned changes to SQLAlchemy media objects when requested."""
    if not apply:
        return

    for change in plan.changes:
        for attr, (_old_value, new_value) in change.changes.items():
            setattr(change.media, attr, new_value)


def _print_summary(plan: SyncPlan, *, apply: bool, preview_limit: int = 8) -> None:
    """Print a concise, auditable sync summary."""
    stats = plan.read_stats
    mode = "APPLY" if apply else "DRY RUN"

    print()
    print("=" * 64)
    print(f" MuterBandung Destination Media Sync - {mode}")
    print("=" * 64)
    print(f"CSV rows total:          {stats.total_rows}")
    print(f"CSV rows processed:      {stats.processed_rows}")
    print(f"Valid media rows:        {stats.valid_rows}")
    print(f"Skipped invalid media:   {stats.skipped_invalid_media}")
    print(f"Duplicate location_id:   {stats.duplicate_location_id}")
    print(f"Matched in DB:           {plan.matched_in_db}")
    print(f"Missing in DB:           {plan.missing_in_db}")
    print(f"Missing media record:    {plan.missing_media_record}")
    print(f"{'Updated' if apply else 'Would update'}:           {plan.changed}")
    print(f"Unchanged:               {plan.unchanged}")

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

    if plan.changes:
        print()
        print("Preview changes:")
        for change in plan.changes[:preview_limit]:
            changed_fields = ", ".join(sorted(change.changes))
            image_old, image_new = change.changes.get("image_url", (None, None))
            print(f"  - {change.location_id} | {change.destination_name}")
            print(f"    fields: {changed_fields}")
            if image_new is not None:
                print(f"    image before: {image_old}")
                print(f"    image after:  {image_new}")
        if len(plan.changes) > preview_limit:
            print(f"  ... and {len(plan.changes) - preview_limit} more changed destinations")

    print("=" * 64)
    if not apply:
        print("No database changes were committed. Re-run with --apply to sync.")


def run_sync(csv_path: str, *, apply: bool, limit: int | None = None) -> SyncPlan:
    """Read CSV, compare with DB, optionally apply changes, and return plan."""
    candidates, read_stats = collect_media_rows(csv_path, limit=limit)

    db = SessionLocal()
    try:
        external_ids = [candidate.location_id for candidate in candidates]
        destinations = (
            db.query(Destination)
            .options(joinedload(Destination.media))
            .filter(Destination.external_id.in_(external_ids))
            .all()
            if external_ids
            else []
        )
        destinations_by_external_id = {
            destination.external_id: destination for destination in destinations
        }

        plan = build_sync_plan(candidates, destinations_by_external_id, read_stats)
        apply_sync_plan(plan, apply=apply)

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
        description="Safely sync destination media URLs from wisata_populer.csv",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="CSV path, for example data/wisata_populer.csv",
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
        help="Commit media updates to the database",
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
        run_sync(args.file, apply=args.apply, limit=args.limit)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
