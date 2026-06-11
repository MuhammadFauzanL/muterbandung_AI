from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from build_penginapan_canonical_candidate import (
    clean_text,
    parse_float,
    quality_label,
    region_bucket,
)


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_INPUT = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
)
DEFAULT_SUMMARY = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "penginapan_canonical_candidate_automated_audit_2026-06-02.json"
)
DEFAULT_FINDINGS = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "PENGINAPAN_CANONICAL_CANDIDATE_AUTOMATED_AUDIT_FINDINGS_2026-06-02.csv"
)
DEFAULT_MANUAL_QUEUE = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "PENGINAPAN_MANUAL_REVIEW_QUEUE_AUTOMATED_AUDIT_2026-06-02.csv"
)
DEFAULT_ADJUSTMENT_QUEUE = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "PENGINAPAN_AUTOMATED_AUDIT_ADJUSTMENT_PRIORITY_2026-06-02.csv"
)
DEFAULT_REPORT = (
    PENGINAPAN_WORKSPACE
    / "04_Dokumentasi"
    / "PENGINAPAN_CANONICAL_CANDIDATE_AUTOMATED_AUDIT_2026-06-02.md"
)
DEFAULT_NOTEBOOK = PENGINAPAN_WORKSPACE / "03_Notebooks" / "penginapan_training.ipynb"

NOTEBOOK_TAG = "penginapan_automated_audit_2026_06_02"

REQUIRED_COLUMNS = [
    "penginapan_id",
    "name",
    "property_type",
    "latitude",
    "longitude",
    "region_bucket",
    "region_validation_label",
    "overall_rating",
    "reviews",
    "price_lowest",
    "data_quality_score",
    "data_quality_label",
    "dedupe_key",
    "dedupe_group_size",
]

ALLOWED_PROPERTY_TYPES = {
    "hotel",
    "guest_house",
    "villa",
    "apartment",
    "vacation_rental",
    "room_level_listing",
}

ALLOWED_REGION_LABELS = {
    "bandung_raya_valid",
    "border_area",
    "outside_bandung_raya",
    "needs_review",
}

ALLOWED_QUALITY_LABELS = {"low", "medium", "high"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def add_finding(
    findings: list[dict],
    severity: str,
    code: str,
    message: str,
    field: str = "",
    penginapan_id: str = "",
    name: str = "",
    recommended_action: str = "",
) -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "field": field,
            "penginapan_id": penginapan_id,
            "name": name,
            "message": message,
            "recommended_action": recommended_action,
        }
    )


def is_empty(value) -> bool:
    return clean_text(value) == ""


def row_identity(row: pd.Series) -> tuple[str, str]:
    return clean_text(row.get("penginapan_id")), clean_text(row.get("name"))


def validate_schema(df: pd.DataFrame, findings: list[dict]) -> None:
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            add_finding(
                findings,
                "ERROR",
                "SCHEMA_MISSING_COLUMN",
                f"Kolom wajib tidak ditemukan: {column}",
                field=column,
                recommended_action=f"Tambahkan kolom `{column}` sebelum dataset dipakai.",
            )


def validate_ids(df: pd.DataFrame, findings: list[dict]) -> None:
    if "penginapan_id" not in df.columns:
        return
    missing = df[df["penginapan_id"].map(is_empty)]
    for _, row in missing.iterrows():
        pid, name = row_identity(row)
        add_finding(
            findings,
            "ERROR",
            "ID_MISSING",
            "penginapan_id kosong.",
            field="penginapan_id",
            penginapan_id=pid,
            name=name,
            recommended_action="Generate ulang penginapan_id yang stabil.",
        )
    duplicated = df[df["penginapan_id"].duplicated(keep=False)]
    for _, row in duplicated.iterrows():
        pid, name = row_identity(row)
        add_finding(
            findings,
            "ERROR",
            "ID_DUPLICATE",
            f"penginapan_id duplikat: {pid}",
            field="penginapan_id",
            penginapan_id=pid,
            name=name,
            recommended_action="Pastikan setiap penginapan_id unik.",
        )


def validate_names(df: pd.DataFrame, findings: list[dict]) -> None:
    if "name" not in df.columns:
        return
    missing = df[df["name"].map(is_empty)]
    for _, row in missing.iterrows():
        pid, name = row_identity(row)
        add_finding(
            findings,
            "ERROR",
            "NAME_MISSING",
            "Nama penginapan kosong.",
            field="name",
            penginapan_id=pid,
            name=name,
            recommended_action="Isi nama atau keluarkan baris dari candidate.",
        )


def validate_property_type(df: pd.DataFrame, findings: list[dict]) -> None:
    if "property_type" not in df.columns:
        return
    invalid = df[~df["property_type"].map(clean_text).isin(ALLOWED_PROPERTY_TYPES)]
    for _, row in invalid.iterrows():
        pid, name = row_identity(row)
        add_finding(
            findings,
            "ERROR",
            "PROPERTY_TYPE_INVALID",
            f"property_type tidak valid: {clean_text(row.get('property_type'))}",
            field="property_type",
            penginapan_id=pid,
            name=name,
            recommended_action=f"Gunakan salah satu: {', '.join(sorted(ALLOWED_PROPERTY_TYPES))}.",
        )

    room_level = df[df["property_type"].map(clean_text).eq("room_level_listing")]
    for _, row in room_level.iterrows():
        pid, name = row_identity(row)
        add_finding(
            findings,
            "MANUAL_REVIEW",
            "ROOM_LEVEL_LISTING",
            "Baris adalah room-level listing, bukan properti utama.",
            field="property_type",
            penginapan_id=pid,
            name=name,
            recommended_action="Jangan hapus otomatis; turunkan prioritas ranking atau gabungkan ke properti utama jika jelas.",
        )


def validate_coordinates_and_region(df: pd.DataFrame, findings: list[dict]) -> None:
    if not {"latitude", "longitude"}.issubset(df.columns):
        return

    for _, row in df.iterrows():
        pid, name = row_identity(row)
        lat = parse_float(row.get("latitude"))
        lon = parse_float(row.get("longitude"))
        if math.isnan(lat) or math.isnan(lon):
            add_finding(
                findings,
                "WARNING",
                "COORDINATE_MISSING",
                "Latitude/longitude kosong atau tidak numeric.",
                field="latitude,longitude",
                penginapan_id=pid,
                name=name,
                recommended_action="Cari koordinat manual atau set sebagai needs_review dan jangan pakai untuk ranking jarak.",
            )
            continue

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            add_finding(
                findings,
                "ERROR",
                "COORDINATE_RANGE_INVALID",
                "Latitude/longitude di luar rentang global.",
                field="latitude,longitude",
                penginapan_id=pid,
                name=name,
                recommended_action="Perbaiki koordinat atau keluarkan dari candidate.",
            )
            continue

        expected_bucket, expected_label, reason = region_bucket(lat, lon)
        actual_label = clean_text(row.get("region_validation_label"))
        actual_bucket = clean_text(row.get("region_bucket"))
        if actual_label not in ALLOWED_REGION_LABELS:
            add_finding(
                findings,
                "ERROR",
                "REGION_LABEL_INVALID",
                f"region_validation_label tidak valid: {actual_label}",
                field="region_validation_label",
                penginapan_id=pid,
                name=name,
                recommended_action=f"Gunakan salah satu: {', '.join(sorted(ALLOWED_REGION_LABELS))}.",
            )
        if actual_label != expected_label or actual_bucket != expected_bucket:
            add_finding(
                findings,
                "WARNING",
                "REGION_VALIDATION_MISMATCH",
                f"Region tersimpan `{actual_bucket}/{actual_label}` tidak sama dengan hasil audit `{expected_bucket}/{expected_label}`.",
                field="region_bucket,region_validation_label",
                penginapan_id=pid,
                name=name,
                recommended_action=f"Review region; alasan audit: {reason}.",
            )


def validate_numeric_fields(df: pd.DataFrame, findings: list[dict]) -> None:
    numeric_rules = {
        "overall_rating": ("ERROR", 0, 5, "Rating harus 0 sampai 5."),
        "location_rating": ("WARNING", 0, 5, "Location rating harus 0 sampai 5 jika tersedia."),
        "reviews": ("ERROR", 0, None, "Review count harus numeric dan tidak negatif."),
        "price_lowest": ("WARNING", 0, None, "Harga harus numeric dan tidak negatif jika tersedia."),
        "price_before_taxes_fees": ("WARNING", 0, None, "Harga sebelum pajak harus numeric dan tidak negatif jika tersedia."),
        "data_quality_score": ("ERROR", 0, 1, "data_quality_score harus 0 sampai 1."),
        "dedupe_group_size": ("ERROR", 1, None, "dedupe_group_size harus minimal 1."),
    }
    for field, (severity, min_value, max_value, message) in numeric_rules.items():
        if field not in df.columns:
            continue
        values = pd.to_numeric(df[field], errors="coerce")
        non_empty = ~df[field].map(is_empty)
        invalid_numeric = df[non_empty & values.isna()]
        for _, row in invalid_numeric.iterrows():
            pid, name = row_identity(row)
            add_finding(
                findings,
                severity,
                f"{field.upper()}_NOT_NUMERIC",
                f"{field} harus numeric jika tersedia.",
                field=field,
                penginapan_id=pid,
                name=name,
                recommended_action="Bersihkan format angka atau kosongkan jika memang tidak tersedia.",
            )

        invalid_range = pd.Series(False, index=df.index)
        if min_value is not None:
            invalid_range |= values < min_value
        if max_value is not None:
            invalid_range |= values > max_value
        invalid_range = df[non_empty & invalid_range.fillna(False)]
        for _, row in invalid_range.iterrows():
            pid, name = row_identity(row)
            add_finding(
                findings,
                severity,
                f"{field.upper()}_RANGE_INVALID",
                message,
                field=field,
                penginapan_id=pid,
                name=name,
                recommended_action="Perbaiki nilai numeric sesuai rentang valid.",
            )


def validate_quality_label(df: pd.DataFrame, findings: list[dict]) -> None:
    if not {"data_quality_score", "data_quality_label"}.issubset(df.columns):
        return
    invalid = df[~df["data_quality_label"].map(clean_text).isin(ALLOWED_QUALITY_LABELS)]
    for _, row in invalid.iterrows():
        pid, name = row_identity(row)
        add_finding(
            findings,
            "ERROR",
            "QUALITY_LABEL_INVALID",
            f"data_quality_label tidak valid: {clean_text(row.get('data_quality_label'))}",
            field="data_quality_label",
            penginapan_id=pid,
            name=name,
            recommended_action=f"Gunakan salah satu: {', '.join(sorted(ALLOWED_QUALITY_LABELS))}.",
        )
    for _, row in df.iterrows():
        expected = quality_label(row.get("data_quality_score"))
        actual = clean_text(row.get("data_quality_label"))
        if actual and actual != expected:
            pid, name = row_identity(row)
            add_finding(
                findings,
                "WARNING",
                "QUALITY_LABEL_MISMATCH",
                f"data_quality_label `{actual}` tidak sesuai score; expected `{expected}`.",
                field="data_quality_label,data_quality_score",
                penginapan_id=pid,
                name=name,
                recommended_action="Recompute data_quality_label dari data_quality_score.",
            )


def validate_missing_important(df: pd.DataFrame, findings: list[dict]) -> None:
    important_fields = {
        "overall_rating": ("MANUAL_REVIEW", "Rating kosong; masih boleh dipakai, tapi ranking berbasis rating harus diberi caveat."),
        "reviews": ("MANUAL_REVIEW", "Review count kosong; confidence review tidak kuat."),
        "price_lowest": ("MANUAL_REVIEW", "Harga kosong; jangan dianggap murah."),
        "link": ("WARNING", "Source link kosong; sulit diverifikasi atau dipakai untuk klik sumber."),
        "primary_image_url": ("MANUAL_REVIEW", "Gambar utama kosong; kartu visual perlu fallback."),
        "amenities": ("MANUAL_REVIEW", "Fasilitas kosong; LLM tidak boleh mengklaim fasilitas."),
    }
    for field, (severity, message) in important_fields.items():
        if field not in df.columns:
            continue
        missing = df[df[field].map(is_empty)]
        for _, row in missing.iterrows():
            pid, name = row_identity(row)
            add_finding(
                findings,
                severity,
                f"{field.upper()}_MISSING",
                message,
                field=field,
                penginapan_id=pid,
                name=name,
                recommended_action="Biarkan kosong dengan caveat atau lengkapi dari sumber tepercaya sebelum klaim digunakan.",
            )


def validate_duplicates(df: pd.DataFrame, findings: list[dict]) -> None:
    if "dedupe_key" in df.columns:
        duplicated = df[df["dedupe_key"].map(clean_text).ne("") & df["dedupe_key"].duplicated(keep=False)]
        for _, row in duplicated.iterrows():
            pid, name = row_identity(row)
            add_finding(
                findings,
                "ERROR",
                "DEDUPE_KEY_DUPLICATE",
                "dedupe_key masih duplikat setelah proses dedupe.",
                field="dedupe_key",
                penginapan_id=pid,
                name=name,
                recommended_action="Review ulang dedupe; canonical candidate tidak boleh punya dedupe_key duplikat kuat.",
            )

    if {"normalized_name", "latitude", "longitude"}.issubset(df.columns):
        temp = df.copy()
        temp["lat_round_4"] = pd.to_numeric(temp["latitude"], errors="coerce").round(4)
        temp["lon_round_4"] = pd.to_numeric(temp["longitude"], errors="coerce").round(4)
        temp["possible_duplicate_key"] = (
            temp["normalized_name"].map(clean_text)
            + "|"
            + temp["lat_round_4"].astype(str)
            + "|"
            + temp["lon_round_4"].astype(str)
        )
        possible = temp[
            temp["normalized_name"].map(clean_text).ne("")
            & temp["lat_round_4"].notna()
            & temp["lon_round_4"].notna()
            & temp["possible_duplicate_key"].duplicated(keep=False)
        ]
        for _, row in possible.iterrows():
            pid, name = row_identity(row)
            add_finding(
                findings,
                "MANUAL_REVIEW",
                "POSSIBLE_DUPLICATE_NAME_COORD",
                "Nama normalized + koordinat rounded masih sama dengan baris lain.",
                field="normalized_name,latitude,longitude",
                penginapan_id=pid,
                name=name,
                recommended_action="Review manual; jika benar properti sama, gabungkan atau pilih record kualitas terbaik.",
            )


def build_adjustment_queue(findings_df: pd.DataFrame) -> pd.DataFrame:
    if findings_df.empty:
        return pd.DataFrame(
            columns=[
                "priority",
                "penginapan_id",
                "name",
                "finding_codes",
                "finding_count",
                "recommended_next_step",
            ]
        )

    actionable_codes = {
        "COORDINATE_MISSING",
        "COORDINATE_RANGE_INVALID",
        "REGION_LABEL_INVALID",
        "REGION_VALIDATION_MISMATCH",
        "DEDUPE_KEY_DUPLICATE",
        "POSSIBLE_DUPLICATE_NAME_COORD",
        "ROOM_LEVEL_LISTING",
    }
    actionable = findings_df[findings_df["code"].isin(actionable_codes)].copy()
    if actionable.empty:
        return pd.DataFrame(
            columns=[
                "priority",
                "penginapan_id",
                "name",
                "finding_codes",
                "finding_count",
                "recommended_next_step",
            ]
        )

    rows = []
    for penginapan_id, group in actionable.groupby("penginapan_id", dropna=False):
        codes = sorted(set(group["code"]))
        name = clean_text(group["name"].iloc[0])
        if any(code in codes for code in ["COORDINATE_MISSING", "COORDINATE_RANGE_INVALID", "REGION_LABEL_INVALID", "REGION_VALIDATION_MISMATCH", "DEDUPE_KEY_DUPLICATE"]):
            priority = "P0"
            next_step = "Perbaiki sebelum dipakai untuk ranking jarak atau final canonical."
        elif "POSSIBLE_DUPLICATE_NAME_COORD" in codes:
            priority = "P1"
            next_step = "Review duplicate candidate; gabungkan jika memang properti sama."
        elif "ROOM_LEVEL_LISTING" in codes:
            priority = "P1"
            next_step = "Jangan hapus otomatis; pastikan ranking menurunkan prioritas room-level listing."
        else:
            priority = "P2"
            next_step = "Tambahkan caveat atau review saat finalisasi."
        rows.append(
            {
                "priority": priority,
                "penginapan_id": penginapan_id,
                "name": name,
                "finding_codes": "; ".join(codes),
                "finding_count": int(len(group)),
                "recommended_next_step": next_step,
            }
        )

    result = pd.DataFrame(rows)
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    return result.sort_values(
        by=["priority", "finding_count", "penginapan_id"],
        ascending=[True, False, True],
        key=lambda series: series.map(priority_order).fillna(99) if series.name == "priority" else series,
    )


def build_summary(
    df: pd.DataFrame,
    findings: list[dict],
    input_path: Path,
    findings_path: Path,
    manual_queue_path: Path,
    adjustment_queue_path: Path,
    adjustment_queue: pd.DataFrame,
) -> dict:
    severity_counts = Counter(finding["severity"] for finding in findings)
    code_counts = Counter(finding["code"] for finding in findings)
    field_counts = Counter(finding["field"] for finding in findings if finding["field"])
    row_finding_counts = defaultdict(int)
    for finding in findings:
        if finding["penginapan_id"]:
            row_finding_counts[finding["penginapan_id"]] += 1
    error_count = severity_counts.get("ERROR", 0)
    warning_count = severity_counts.get("WARNING", 0)
    manual_count = severity_counts.get("MANUAL_REVIEW", 0)
    gate = "FAIL" if error_count else ("PASS_WITH_WARNINGS" if warning_count or manual_count else "PASS")
    return {
        "generated_at": now_iso(),
        "input_path": str(input_path),
        "findings_csv_path": str(findings_path),
        "manual_review_queue_path": str(manual_queue_path),
        "adjustment_priority_queue_path": str(adjustment_queue_path),
        "gate": gate,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "finding_count": int(len(findings)),
        "affected_row_count": int(len(row_finding_counts)),
        "severity_counts": dict(severity_counts),
        "top_finding_codes": dict(code_counts.most_common(20)),
        "field_counts": dict(field_counts.most_common(20)),
        "property_type_counts": df["property_type"].value_counts(dropna=False).to_dict() if "property_type" in df.columns else {},
        "region_validation_counts": df["region_validation_label"].value_counts(dropna=False).to_dict() if "region_validation_label" in df.columns else {},
        "data_quality_label_counts": df["data_quality_label"].value_counts(dropna=False).to_dict() if "data_quality_label" in df.columns else {},
        "adjustment_priority_counts": adjustment_queue["priority"].value_counts(dropna=False).to_dict() if not adjustment_queue.empty else {},
        "adjustment_priorities": [
            "P0: Jika ada ERROR, perbaiki sebelum candidate dipakai.",
            "P1: Data tanpa koordinat tidak boleh dipakai untuk ranking jarak.",
            "P1: Room-level listing jangan dihapus otomatis, tetapi turunkan prioritas ranking.",
            "P1: Data tanpa amenities/gambar/harga/rating boleh dipakai dengan caveat, jangan diklaim lengkap oleh LLM.",
            "P2: Possible duplicate name+coordinate perlu review manual sebelum final canonical.",
        ],
    }


def markdown_table(mapping: dict, key_label: str, value_label: str) -> str:
    lines = [f"| {key_label} | {value_label} |", "|---|---:|"]
    if not mapping:
        lines.append("| - | 0 |")
        return "\n".join(lines)
    for key, value in mapping.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict) -> None:
    priorities = "\n".join(f"{index + 1}. {item}" for index, item in enumerate(summary["adjustment_priorities"]))
    text = f"""# Penginapan Canonical Candidate Automated Audit - 2026-06-02

Audit ini membaca `PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv` tanpa mengubah isi dataset.

## Gate

| Metrik | Nilai |
|---|---:|
| Gate | {summary['gate']} |
| Rows | {summary['row_count']} |
| Columns | {summary['column_count']} |
| Total findings | {summary['finding_count']} |
| Rows affected | {summary['affected_row_count']} |

## Severity

{markdown_table(summary['severity_counts'], 'Severity', 'Jumlah')}

## Top Finding Codes

{markdown_table(summary['top_finding_codes'], 'Code', 'Jumlah')}

## Property Type

{markdown_table(summary['property_type_counts'], 'Property type', 'Jumlah')}

## Region Validation

{markdown_table(summary['region_validation_counts'], 'Region', 'Jumlah')}

## Data Quality

{markdown_table(summary['data_quality_label_counts'], 'Quality label', 'Jumlah')}

## Output

- Findings CSV: `{summary['findings_csv_path']}`
- Manual review queue CSV: `{summary['manual_review_queue_path']}`
- Adjustment priority queue CSV: `{summary['adjustment_priority_queue_path']}`

## Adjustment Priority Queue

{markdown_table(summary['adjustment_priority_counts'], 'Priority', 'Jumlah')}

## Langkah Penyesuaian Yang Disarankan

{priorities}

## Catatan

- Banyak finding bertipe `MANUAL_REVIEW` bukan berarti data salah. Itu berarti data boleh dipakai, tetapi klaim/ranking harus hati-hati.
- Audit ini otomatis. Manual review utama cukup fokus ke `Adjustment Priority Queue`, bukan semua findings.
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


def update_notebook(path: Path, summary: dict) -> None:
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
## Fase A - Automated Audit Penginapan Canonical Candidate

Bagian ini mendokumentasikan audit otomatis untuk `PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv`.

Audit ini tidak mengubah data. Tujuannya adalah memberi gate dan daftar penyesuaian:

- Schema dan kolom wajib.
- ID unik.
- Koordinat dan region validation.
- Rating, reviews, harga, dan quality score.
- Property type.
- Room-level listing.
- Duplikasi kuat dan kemungkinan duplikasi.
- Missing field penting yang perlu caveat.

Hasil terakhir:

- Gate: `{summary['gate']}`
- Rows: {summary['row_count']}
- Findings: {summary['finding_count']}
- Affected rows: {summary['affected_row_count']}
- Findings CSV: `{summary['findings_csv_path']}`
- Manual review queue: `{summary['manual_review_queue_path']}`
- Adjustment priority queue: `{summary['adjustment_priority_queue_path']}`
""",
            ),
            notebook_cell(
                "code",
                """
# Jalankan ulang automated audit candidate penginapan.
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

subprocess.run(
    [
        sys.executable,
        str(PROJECT_ROOT / "Penginapan_Workspace" / "06_Scripts" / "audit_penginapan_canonical_candidate.py"),
        "--skip-notebook-update",
    ],
    check=True,
)
""",
            ),
            notebook_cell(
                "code",
                """
# Baca hasil audit otomatis.
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

summary_path = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "penginapan_canonical_candidate_automated_audit_2026-06-02.json"
findings_csv = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "PENGINAPAN_CANONICAL_CANDIDATE_AUTOMATED_AUDIT_FINDINGS_2026-06-02.csv"
manual_queue_csv = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "PENGINAPAN_MANUAL_REVIEW_QUEUE_AUTOMATED_AUDIT_2026-06-02.csv"
adjustment_queue_csv = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "PENGINAPAN_AUTOMATED_AUDIT_ADJUSTMENT_PRIORITY_2026-06-02.csv"

audit_summary = json.loads(summary_path.read_text(encoding="utf-8"))
findings_df = pd.read_csv(findings_csv)
manual_queue_df = pd.read_csv(manual_queue_csv)
adjustment_queue_df = pd.read_csv(adjustment_queue_csv)

audit_summary, findings_df["severity"].value_counts().to_dict(), findings_df["code"].value_counts().head(15).to_dict(), adjustment_queue_df.head(30)
""",
            ),
        ]
    )
    nb["cells"] = cells
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def run_audit(
    input_path: Path,
    summary_path: Path,
    findings_path: Path,
    manual_queue_path: Path,
    adjustment_queue_path: Path,
    report_path: Path,
    notebook_path: Path,
    update_nb: bool,
) -> dict:
    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    findings: list[dict] = []
    validate_schema(df, findings)
    validate_ids(df, findings)
    validate_names(df, findings)
    validate_property_type(df, findings)
    validate_coordinates_and_region(df, findings)
    validate_numeric_fields(df, findings)
    validate_quality_label(df, findings)
    validate_missing_important(df, findings)
    validate_duplicates(df, findings)

    findings_df = pd.DataFrame(findings)
    if findings_df.empty:
        findings_df = pd.DataFrame(
            columns=["severity", "code", "field", "penginapan_id", "name", "message", "recommended_action"]
        )

    manual_queue = findings_df[
        findings_df["code"].isin(
            [
                "COORDINATE_MISSING",
                "COORDINATE_RANGE_INVALID",
                "REGION_LABEL_INVALID",
                "REGION_VALIDATION_MISMATCH",
                "DEDUPE_KEY_DUPLICATE",
                "POSSIBLE_DUPLICATE_NAME_COORD",
                "ROOM_LEVEL_LISTING",
            ]
        )
    ].copy()
    manual_queue = manual_queue.sort_values(by=["severity", "code", "penginapan_id"])
    adjustment_queue = build_adjustment_queue(findings_df)

    findings_path.parent.mkdir(parents=True, exist_ok=True)
    manual_queue_path.parent.mkdir(parents=True, exist_ok=True)
    adjustment_queue_path.parent.mkdir(parents=True, exist_ok=True)
    findings_df.to_csv(findings_path, index=False)
    manual_queue.to_csv(manual_queue_path, index=False)
    adjustment_queue.to_csv(adjustment_queue_path, index=False)

    summary = build_summary(
        df,
        findings,
        input_path,
        findings_path,
        manual_queue_path,
        adjustment_queue_path,
        adjustment_queue,
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(report_path, summary)
    if update_nb:
        update_notebook(notebook_path, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated audit for penginapan canonical candidate.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--findings", type=Path, default=DEFAULT_FINDINGS)
    parser.add_argument("--manual-queue", type=Path, default=DEFAULT_MANUAL_QUEUE)
    parser.add_argument("--adjustment-queue", type=Path, default=DEFAULT_ADJUSTMENT_QUEUE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--skip-notebook-update", action="store_true")
    args = parser.parse_args()

    summary = run_audit(
        input_path=args.input,
        summary_path=args.summary,
        findings_path=args.findings,
        manual_queue_path=args.manual_queue,
        adjustment_queue_path=args.adjustment_queue,
        report_path=args.report,
        notebook_path=args.notebook,
        update_nb=not args.skip_notebook_update,
    )
    print(f"gate={summary['gate']}")
    print(f"rows={summary['row_count']}")
    print(f"findings={summary['finding_count']}")
    print(f"affected_rows={summary['affected_row_count']}")
    print(f"severity_counts={summary['severity_counts']}")
    print(f"findings_csv={summary['findings_csv_path']}")
    print(f"manual_review_queue={summary['manual_review_queue_path']}")
    print(f"adjustment_priority_queue={summary['adjustment_priority_queue_path']}")


if __name__ == "__main__":
    main()
