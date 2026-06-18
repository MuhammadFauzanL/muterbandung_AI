"""
Unit tests for the destination gallery CSV importer.

These tests avoid mutating the real database. They validate CSV parsing,
planning, and ORM object creation with lightweight fake destination objects.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from scripts.import_destination_gallery_images import (
    CsvGalleryImage,
    build_gallery_models,
    build_import_plan,
    collect_gallery_rows,
    group_gallery_rows,
)


class FakeDestination:
    def __init__(
        self,
        external_id: str,
        name: str = "Test Destination",
        gallery_images: list | None = None,
    ):
        self.id = uuid.uuid4()
        self.external_id = external_id
        self.name = name
        self.gallery_images = gallery_images or []


def write_csv(path: Path, rows: list[dict], headers: list[str] | None = None) -> None:
    if headers is None:
        headers = [
            "location_id",
            "location_name",
            "gallery_index",
            "source_image_url",
            "media_storage_url",
            "media_public_id",
            "media_upload_status",
            "media_upload_error",
            "match_confidence",
            "matched_title",
        ]

    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row.get(header, "")) for header in headers))
    path.write_text("\n".join(lines), encoding="utf-8")


def test_collect_gallery_rows_requires_gallery_columns(tmp_path):
    csv_path = tmp_path / "missing_columns.csv"
    write_csv(
        csv_path,
        [{"location_id": "LOC-001"}],
        headers=["location_id", "gallery_index", "media_storage_url"],
    )

    with pytest.raises(ValueError, match="Missing required gallery columns"):
        collect_gallery_rows(csv_path)


def test_collect_gallery_rows_skips_invalid_and_duplicate_rows(tmp_path):
    csv_path = tmp_path / "gallery.csv"
    write_csv(
        csv_path,
        [
            {
                "location_id": "LOC-001",
                "location_name": "One",
                "gallery_index": "1",
                "source_image_url": "https://source.example.com/1.jpg",
                "media_storage_url": "https://cdn.example.com/1.jpg",
                "media_public_id": "muter/loc-001/1",
                "media_upload_status": "uploaded",
                "match_confidence": "exact",
                "matched_title": "One",
            },
            {
                "location_id": "LOC-002",
                "gallery_index": "",
                "media_storage_url": "https://cdn.example.com/2.jpg",
                "media_upload_status": "uploaded",
            },
            {
                "location_id": "LOC-003",
                "gallery_index": "1",
                "media_storage_url": "",
                "media_upload_status": "uploaded",
            },
            {
                "location_id": "LOC-004",
                "gallery_index": "1",
                "media_storage_url": "https://cdn.example.com/4.jpg",
                "media_upload_status": "failed",
            },
            {
                "location_id": "LOC-001",
                "gallery_index": "1",
                "media_storage_url": "https://cdn.example.com/duplicate.jpg",
                "media_upload_status": "uploaded",
            },
        ],
    )

    rows, stats = collect_gallery_rows(csv_path)

    assert len(rows) == 1
    assert rows[0].location_id == "LOC-001"
    assert rows[0].sort_order == 1
    assert rows[0].image_url == "https://cdn.example.com/1.jpg"
    assert stats.total_rows == 5
    assert stats.processed_rows == 5
    assert stats.valid_rows == 1
    assert stats.skipped_invalid_rows == 3
    assert stats.duplicate_gallery_index == 1
    assert stats.skip_reasons["invalid_gallery_index"] == 1
    assert stats.skip_reasons["missing_media_storage_url"] == 1
    assert stats.skip_reasons["upload_status_not_uploaded"] == 1
    assert stats.skip_reasons["duplicate_gallery_index"] == 1


def test_group_gallery_rows_orders_by_gallery_index():
    rows = [
        CsvGalleryImage("LOC-001", 3, "image-3", None, None, None, None, "uploaded"),
        CsvGalleryImage("LOC-001", 1, "image-1", None, None, None, None, "uploaded"),
        CsvGalleryImage("LOC-001", 2, "image-2", None, None, None, None, "uploaded"),
    ]

    grouped = group_gallery_rows(rows)

    assert [image.image_url for image in grouped["LOC-001"]] == [
        "image-1",
        "image-2",
        "image-3",
    ]


def test_build_import_plan_reports_missing_destinations_and_existing_replacements():
    rows = [
        CsvGalleryImage("LOC-001", 1, "image-1", None, None, None, None, "uploaded"),
        CsvGalleryImage("LOC-001", 2, "image-2", None, None, None, None, "uploaded"),
        CsvGalleryImage("LOC-404", 1, "image-x", None, None, None, None, "uploaded"),
    ]
    destinations = {
        "LOC-001": FakeDestination(
            "LOC-001",
            gallery_images=[object(), object(), object(), object()],
        )
    }

    plan = build_import_plan(rows, destinations)

    assert plan.valid_destinations == 2
    assert plan.matched_destinations == 1
    assert plan.missing_destinations == 1
    assert plan.missing_ids == ["LOC-404"]
    assert plan.images_to_import == 2
    assert plan.existing_images_to_replace == 4


def test_build_gallery_models_only_uses_gallery_fields():
    destination = FakeDestination("LOC-001", name="Original Name")
    rows = [
        CsvGalleryImage(
            location_id="LOC-001",
            sort_order=1,
            image_url="https://cdn.example.com/1.jpg",
            source_image_url="https://source.example.com/1.jpg",
            media_public_id="muter/loc-001/1",
            match_confidence="exact",
            matched_title="Matched Name",
            upload_status="uploaded",
        )
    ]
    plan = build_import_plan(rows, {"LOC-001": destination})

    models = build_gallery_models(plan)

    assert destination.name == "Original Name"
    assert len(models) == 1
    assert models[0].destination_id == destination.id
    assert models[0].sort_order == 1
    assert models[0].image_url == "https://cdn.example.com/1.jpg"
    assert models[0].source_image_url == "https://source.example.com/1.jpg"
    assert models[0].media_public_id == "muter/loc-001/1"
    assert models[0].match_confidence == "exact"
    assert models[0].matched_title == "Matched Name"
    assert models[0].upload_status == "uploaded"
