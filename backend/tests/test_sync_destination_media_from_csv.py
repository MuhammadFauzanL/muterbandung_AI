"""
Unit tests for the safe destination media CSV sync script.

These tests avoid mutating the real database. They exercise CSV validation,
sync planning, and apply/dry-run behavior with lightweight fake objects.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.sync_destination_media_from_csv import (
    CsvMediaRow,
    apply_sync_plan,
    build_sync_plan,
    collect_media_rows,
)


class FakeMedia:
    def __init__(
        self,
        image_url="old-image",
        maps_url="old-maps",
        website_url="old-site",
        media_source="old-source",
        place_id="old-place",
        media_audit_status="old-status",
    ):
        self.image_url = image_url
        self.maps_url = maps_url
        self.website_url = website_url
        self.media_source = media_source
        self.place_id = place_id
        self.media_audit_status = media_audit_status


class FakeDestination:
    def __init__(self, external_id, name="Test Destination", media=None):
        self.external_id = external_id
        self.name = name
        self.media = media


def write_csv(path: Path, rows: list[dict], headers: list[str] | None = None) -> None:
    if headers is None:
        headers = [
            "location_id",
            "media_available",
            "media_image_url",
            "media_destination_url",
            "media_website",
            "media_source",
            "media_place_id",
            "media_audit_status",
        ]

    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row.get(header, "")) for header in headers))
    path.write_text("\n".join(lines), encoding="utf-8")


def test_collect_media_rows_requires_media_columns(tmp_path):
    csv_path = tmp_path / "missing_columns.csv"
    write_csv(
        csv_path,
        [{"location_id": "LOC-001", "media_available": "True"}],
        headers=["location_id", "media_available", "media_image_url"],
    )

    with pytest.raises(ValueError, match="Missing required media columns"):
        collect_media_rows(csv_path)


def test_collect_media_rows_skips_invalid_and_duplicate_rows(tmp_path):
    csv_path = tmp_path / "media.csv"
    write_csv(
        csv_path,
        [
            {
                "location_id": "LOC-001",
                "media_available": "True",
                "media_image_url": "https://cdn.example.com/loc-001.jpg",
                "media_destination_url": "https://maps.example.com/loc-001",
                "media_website": "",
                "media_source": "manual",
                "media_place_id": "place-1",
                "media_audit_status": "accepted",
            },
            {
                "location_id": "LOC-002",
                "media_available": "False",
                "media_image_url": "https://cdn.example.com/loc-002.jpg",
                "media_audit_status": "accepted",
            },
            {
                "location_id": "LOC-003",
                "media_available": "True",
                "media_image_url": "",
                "media_audit_status": "accepted",
            },
            {
                "location_id": "LOC-004",
                "media_available": "True",
                "media_image_url": "https://cdn.example.com/loc-004.jpg",
                "media_audit_status": "rejected",
            },
            {
                "location_id": "LOC-001",
                "media_available": "True",
                "media_image_url": "https://cdn.example.com/loc-001-duplicate.jpg",
                "media_audit_status": "accepted",
            },
        ],
    )

    rows, stats = collect_media_rows(csv_path)

    assert [row.location_id for row in rows] == ["LOC-001"]
    assert stats.total_rows == 5
    assert stats.processed_rows == 5
    assert stats.valid_rows == 1
    assert stats.skipped_invalid_media == 3
    assert stats.duplicate_location_id == 1
    assert stats.skip_reasons["media_available_not_true"] == 1
    assert stats.skip_reasons["missing_media_image_url"] == 1
    assert stats.skip_reasons["media_audit_status_not_accepted"] == 1
    assert stats.skip_reasons["duplicate_location_id"] == 1


def test_build_sync_plan_reports_missing_db_and_media_record():
    candidates = [
        CsvMediaRow(
            location_id="LOC-001",
            values={
                "image_url": "new-image",
                "maps_url": "new-maps",
                "website_url": None,
                "media_source": "new-source",
                "place_id": None,
                "media_audit_status": "accepted",
            },
        ),
        CsvMediaRow(location_id="LOC-002", values={"image_url": "new-image"}),
        CsvMediaRow(location_id="LOC-404", values={"image_url": "new-image"}),
    ]
    destinations = {
        "LOC-001": FakeDestination("LOC-001", media=FakeMedia()),
        "LOC-002": FakeDestination("LOC-002", media=None),
    }

    plan = build_sync_plan(candidates, destinations)

    assert plan.valid_rows == 3
    assert plan.matched_in_db == 2
    assert plan.missing_in_db == 1
    assert plan.missing_ids == ["LOC-404"]
    assert plan.missing_media_record == 1
    assert plan.changed == 1
    assert plan.unchanged == 0
    assert set(plan.changes[0].changes) == {
        "image_url",
        "maps_url",
        "media_source",
        "media_audit_status",
    }


def test_dry_run_does_not_mutate_media_object():
    media = FakeMedia()
    candidates = [
        CsvMediaRow(
            location_id="LOC-001",
            values={
                "image_url": "new-image",
                "maps_url": "new-maps",
                "website_url": None,
                "media_source": "new-source",
                "place_id": None,
                "media_audit_status": "manual_accepted",
            },
        )
    ]
    plan = build_sync_plan(
        candidates,
        {"LOC-001": FakeDestination("LOC-001", media=media)},
    )

    apply_sync_plan(plan, apply=False)

    assert media.image_url == "old-image"
    assert media.maps_url == "old-maps"
    assert media.website_url == "old-site"
    assert media.media_source == "old-source"
    assert media.place_id == "old-place"
    assert media.media_audit_status == "old-status"


def test_apply_updates_only_destination_media_fields():
    media = FakeMedia()
    destination = FakeDestination("LOC-001", name="Original Name", media=media)
    candidates = [
        CsvMediaRow(
            location_id="LOC-001",
            values={
                "image_url": "new-image",
                "maps_url": "new-maps",
                "website_url": None,
                "media_source": "new-source",
                "place_id": "new-place",
                "media_audit_status": "accepted",
            },
        )
    ]
    plan = build_sync_plan(candidates, {"LOC-001": destination})

    apply_sync_plan(plan, apply=True)

    assert destination.name == "Original Name"
    assert media.image_url == "new-image"
    assert media.maps_url == "new-maps"
    assert media.website_url == "old-site"
    assert media.media_source == "new-source"
    assert media.place_id == "new-place"
    assert media.media_audit_status == "accepted"
