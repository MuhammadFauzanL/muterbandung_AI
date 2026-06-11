from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from build_hotel_training_from_google_hotels_json import (
    CSV_COLUMNS,
    add_rating_sentiment,
    clean_text,
    flatten_record,
    json_text,
    now_iso,
)


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_JSON_DIR = PENGINAPAN_WORKSPACE / "01_Raw_Data" / "google_hotels_search_json"
DEFAULT_RAW_MASTER_CSV = (
    PENGINAPAN_WORKSPACE
    / "01_Raw_Data"
    / "generated_raw_csv"
    / "HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.csv"
)
DEFAULT_SOURCE_INVENTORY_CSV = (
    PENGINAPAN_WORKSPACE
    / "01_Raw_Data"
    / "generated_raw_csv"
    / "HOTEL_GOOGLE_SEARCH_JSON_SOURCE_INVENTORY_2026-06-02.csv"
)
DEFAULT_SUMMARY_JSON = (
    PENGINAPAN_WORKSPACE
    / "02_Curated"
    / "hotel_google_search_raw_master_summary_2026-06-02.json"
)
DEFAULT_REPORT_MD = (
    PENGINAPAN_WORKSPACE
    / "04_Dokumentasi"
    / "HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.md"
)
DEFAULT_NOTEBOOK = PENGINAPAN_WORKSPACE / "03_Notebooks" / "penginapan_training.ipynb"

NOTEBOOK_TAG = "hotel_raw_master_json_to_csv_2026_06_02"

EXTRA_RAW_COLUMNS = [
    "raw_master_id",
    "source_file_sha256",
    "source_file_duplicate_status",
    "source_bucket",
    "json_record_index",
    "source_query_area",
    "search_max_pages_set",
    "search_pagination_limit_reached",
    "price_display",
    "ad_price_display",
    "ad_extracted_price",
    "raw_property_json",
]

RAW_MASTER_COLUMNS = EXTRA_RAW_COLUMNS + [column for column in CSV_COLUMNS if column not in EXTRA_RAW_COLUMNS]

SOURCE_INVENTORY_COLUMNS = [
    "source_file",
    "source_file_sha256",
    "duplicate_status",
    "duplicate_of",
    "processed",
    "query",
    "check_in_date",
    "check_out_date",
    "vacation_rentals",
    "max_pages_set",
    "page_count_local",
    "records_properties",
    "records_ads",
    "records_total",
    "unique_names_raw",
    "search_total_results_first_page",
    "search_properties_count_first_page",
    "search_pages_processed_first_page",
    "pagination_limit_reached_first_page",
]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_pages(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Input JSON must be a list of pages: {path}")
    return data


def query_area(query: str) -> str:
    match = re.search(
        r"\bin\s+(.+?)(?:,\s*Jawa Barat|,\s*West Java|,\s*Indonesia|$)",
        clean_text(query),
        flags=re.IGNORECASE,
    )
    return clean_text(match.group(1)) if match else clean_text(query)


def extract_price_display(prop: dict) -> str:
    rate_per_night = prop.get("rate_per_night") or {}
    total_rate = prop.get("total_rate") or {}
    for container, key in (
        (rate_per_night, "lowest"),
        (rate_per_night, "before_taxes_fees"),
        (total_rate, "lowest"),
        (total_rate, "before_taxes_fees"),
    ):
        if isinstance(container, dict) and clean_text(container.get(key)):
            return clean_text(container.get(key))
    return clean_text(prop.get("price"))


def extract_ad_price(prop: dict) -> tuple[str, str]:
    return clean_text(prop.get("price")), clean_text(prop.get("extracted_price"))


def flatten_source_file(path: Path, file_hash: str, generated_at: str) -> tuple[list[dict], dict]:
    pages = load_pages(path)
    first_page = pages[0] if pages else {}
    first_params = first_page.get("search_parameters") or {}
    first_meta = first_page.get("search_metadata") or {}
    rows = []
    names = set()
    properties_count = 0
    ads_count = 0
    record_index = 0

    for page in pages:
        search_parameters = page.get("search_parameters") or {}
        search_metadata = page.get("search_metadata") or {}
        for bucket in ("properties", "ads"):
            records = page.get(bucket) or []
            if bucket == "properties":
                properties_count += len(records)
            else:
                ads_count += len(records)
            for prop in records:
                if not isinstance(prop, dict):
                    continue
                record_index += 1
                row = flatten_record(page, prop, path, generated_at)
                name = clean_text(prop.get("name"))
                if name:
                    names.add(name.lower())
                ad_price_display, ad_extracted_price = extract_ad_price(prop)
                row.update(
                    {
                        "raw_master_id": "",
                        "source_file_sha256": file_hash,
                        "source_file_duplicate_status": "unique_file",
                        "source_bucket": bucket,
                        "json_record_index": record_index,
                        "source_query_area": query_area(search_parameters.get("q")),
                        "search_max_pages_set": search_parameters.get("max_pages", ""),
                        "search_pagination_limit_reached": search_metadata.get("pagination_limit_reached", ""),
                        "price_display": extract_price_display(prop),
                        "ad_price_display": ad_price_display,
                        "ad_extracted_price": ad_extracted_price,
                        "raw_property_json": json_text(prop),
                    }
                )
                rows.append(row)

    inventory = {
        "source_file": path.name,
        "source_file_sha256": file_hash,
        "duplicate_status": "unique_file",
        "duplicate_of": "",
        "processed": "True",
        "query": clean_text(first_params.get("q")),
        "check_in_date": clean_text(first_params.get("check_in_date")),
        "check_out_date": clean_text(first_params.get("check_out_date")),
        "vacation_rentals": first_params.get("vacation_rentals", ""),
        "max_pages_set": first_params.get("max_pages", ""),
        "page_count_local": len(pages),
        "records_properties": properties_count,
        "records_ads": ads_count,
        "records_total": properties_count + ads_count,
        "unique_names_raw": len(names),
        "search_total_results_first_page": first_meta.get("total_results", ""),
        "search_properties_count_first_page": first_meta.get("properties_count", ""),
        "search_pages_processed_first_page": first_meta.get("pages_processed", ""),
        "pagination_limit_reached_first_page": first_meta.get("pagination_limit_reached", ""),
    }
    return rows, inventory


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(raw_rows: list[dict], inventory_rows: list[dict], raw_csv: Path, inventory_csv: Path) -> dict:
    unique_names = {clean_text(row.get("name")).lower() for row in raw_rows if clean_text(row.get("name"))}
    unique_tokens = {clean_text(row.get("property_token")) for row in raw_rows if clean_text(row.get("property_token"))}
    duplicate_files = [row for row in inventory_rows if row["duplicate_status"] == "duplicate_file"]
    processed_files = [row for row in inventory_rows if row["processed"] == "True"]
    return {
        "generated_at": now_iso(),
        "json_source_count": len(inventory_rows),
        "json_processed_count": len(processed_files),
        "json_duplicate_file_count": len(duplicate_files),
        "raw_master_csv_path": str(raw_csv),
        "source_inventory_csv_path": str(inventory_csv),
        "raw_records": len(raw_rows),
        "raw_unique_names": len(unique_names),
        "raw_unique_property_tokens": len(unique_tokens),
        "source_bucket_counts": dict(Counter(row["source_bucket"] for row in raw_rows)),
        "raw_type_counts": dict(Counter(row["raw_type"] for row in raw_rows)),
        "property_segment_counts": dict(Counter(row["property_segment"] for row in raw_rows)),
        "query_area_counts": dict(Counter(row["source_query_area"] for row in raw_rows)),
        "quality_flags": {
            "coordinate_available": sum(row.get("coordinate_available_flag") == "True" for row in raw_rows),
            "rating_available": sum(row.get("rating_available") == "True" for row in raw_rows),
            "price_available": sum(row.get("price_available") == "True" for row in raw_rows),
            "amenities_available": sum(row.get("amenities_available") == "True" for row in raw_rows),
            "image_available": sum(row.get("image_available") == "True" for row in raw_rows),
            "source_link_available": sum(row.get("source_link_available") == "True" for row in raw_rows),
        },
        "duplicate_files": [
            {
                "source_file": row["source_file"],
                "duplicate_of": row["duplicate_of"],
                "source_file_sha256": row["source_file_sha256"],
            }
            for row in duplicate_files
        ],
    }


def markdown_table(mapping: dict, key_label: str, value_label: str) -> str:
    if not mapping:
        return f"| {key_label} | {value_label} |\n|---|---:|\n"
    lines = [f"| {key_label} | {value_label} |", "|---|---:|"]
    for key, value in sorted(mapping.items(), key=lambda item: str(item[0])):
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict) -> None:
    duplicate_text = "\n".join(
        f"- `{item['source_file']}` duplicate of `{item['duplicate_of']}`"
        for item in summary["duplicate_files"]
    ) or "- Tidak ada duplicate file berdasarkan SHA256."
    text = f"""# Hotel Google Search Raw Master - 2026-06-02

Dokumen ini mencatat proses konversi JSON Google Hotels Search menjadi CSV tabular raw master.

## Output

- Raw master CSV: `{summary['raw_master_csv_path']}`
- Source inventory CSV: `{summary['source_inventory_csv_path']}`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| JSON source terdeteksi | {summary['json_source_count']} |
| JSON diproses | {summary['json_processed_count']} |
| JSON duplicate file | {summary['json_duplicate_file_count']} |
| Raw records | {summary['raw_records']} |
| Unique names raw | {summary['raw_unique_names']} |
| Unique property token | {summary['raw_unique_property_tokens']} |

## Source Bucket

{markdown_table(summary['source_bucket_counts'], 'Bucket', 'Jumlah')}

## Segment Properti

{markdown_table(summary['property_segment_counts'], 'Segment', 'Jumlah')}

## Query Area

{markdown_table(summary['query_area_counts'], 'Query area', 'Jumlah')}

## Duplicate File

{duplicate_text}

## Catatan

- Tahap ini belum melakukan dedupe properti/canonical.
- File duplikat penuh berdasarkan SHA256 tidak diproses ke raw master.
- CSV raw master dipakai sebagai input tahap berikutnya: dedupe, region validation, property classification, dan canonical candidate.
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
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        nb = json.loads(path.read_text(encoding="utf-8"))
    else:
        nb = {
            "cells": [],
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "pygments_lexer": "ipython3"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }

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
## Fase A - JSON Google Hotels Search ke CSV Raw Master

Bagian ini mendokumentasikan proses mengubah seluruh JSON Google Hotels Search di workspace penginapan menjadi CSV tabular.

Tujuan tahap ini:

- Membaca semua file JSON di `Penginapan_Workspace/01_Raw_Data/google_hotels_search_json/`.
- Mengabaikan file JSON yang duplikat penuh berdasarkan SHA256.
- Membuka struktur `properties` dan `ads`.
- Membuat CSV raw master yang masih berisi data mentah tabular.
- Membuat inventory sumber agar query, jumlah page, jumlah record, dan duplicate file bisa diaudit.

Hasil terakhir:

- JSON terdeteksi: {summary['json_source_count']}
- JSON diproses: {summary['json_processed_count']}
- Duplicate file: {summary['json_duplicate_file_count']}
- Raw records: {summary['raw_records']}
- Unique names raw: {summary['raw_unique_names']}
- Raw master CSV: `{summary['raw_master_csv_path']}`
- Source inventory CSV: `{summary['source_inventory_csv_path']}`

Catatan: tahap ini belum dedupe properti dan belum membangun canonical dataset.
""",
            ),
            notebook_cell(
                "code",
                """
# Rebuild CSV raw master dari seluruh JSON Google Hotels Search.
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

subprocess.run(
    [
        sys.executable,
        str(PROJECT_ROOT / "Penginapan_Workspace" / "06_Scripts" / "flatten_google_hotels_json_to_raw_master.py"),
        "--skip-notebook-update",
    ],
    check=True,
)
""",
            ),
            notebook_cell(
                "code",
                """
# Baca ringkasan dan inventory sumber JSON.
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

summary_path = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "hotel_google_search_raw_master_summary_2026-06-02.json"
inventory_csv = PROJECT_ROOT / "Penginapan_Workspace" / "01_Raw_Data" / "generated_raw_csv" / "HOTEL_GOOGLE_SEARCH_JSON_SOURCE_INVENTORY_2026-06-02.csv"

summary = json.loads(summary_path.read_text(encoding="utf-8"))
inventory_df = pd.read_csv(inventory_csv)

summary, inventory_df[[
    "source_file",
    "duplicate_status",
    "processed",
    "query",
    "page_count_local",
    "records_total",
    "unique_names_raw",
]].sort_values(["processed", "source_file"], ascending=[False, True]).head(25)
""",
            ),
            notebook_cell(
                "code",
                """
# Preview CSV raw master.
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

raw_master_csv = PROJECT_ROOT / "Penginapan_Workspace" / "01_Raw_Data" / "generated_raw_csv" / "HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.csv"
raw_master_df = pd.read_csv(raw_master_csv)

raw_master_df[[
    "raw_master_id",
    "source_file",
    "source_bucket",
    "source_query_area",
    "name",
    "raw_type",
    "property_segment",
    "latitude",
    "longitude",
    "overall_rating",
    "reviews",
    "price_lowest",
    "data_quality_score",
]].head(20)
""",
            ),
            notebook_cell(
                "markdown",
                """
### Interpretasi Tahap Ini

CSV raw master adalah hasil tabular dari JSON, bukan dataset final.

Yang sudah aman pada tahap ini:

- JSON sudah berubah menjadi tabel.
- Source lineage per baris tersedia melalui `source_file`, `source_file_sha256`, `source_page_number`, dan `source_query_area`.
- File duplikat penuh tidak ikut diproses ke raw master.
- Kolom dasar seperti koordinat, rating, harga, fasilitas, gambar, dan quality flag awal sudah tersedia.

Langkah berikutnya setelah tahap ini:

1. Dedupe antar properti.
2. Region validation Bandung Raya.
3. Property type classification lanjutan.
4. Build `PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA`.
""",
            ),
        ]
    )
    nb["cells"] = cells
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def build(
    json_dir: Path,
    raw_master_csv: Path,
    source_inventory_csv: Path,
    summary_json: Path,
    report_md: Path,
    notebook: Path,
    update_nb: bool,
) -> dict:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    json_files = sorted(json_dir.glob("*.json"))
    seen_hashes: dict[str, str] = {}
    raw_rows = []
    inventory_rows = []

    for path in json_files:
        file_hash = file_sha256(path)
        if file_hash in seen_hashes:
            inventory_rows.append(
                {
                    "source_file": path.name,
                    "source_file_sha256": file_hash,
                    "duplicate_status": "duplicate_file",
                    "duplicate_of": seen_hashes[file_hash],
                    "processed": "False",
                    "query": "",
                    "check_in_date": "",
                    "check_out_date": "",
                    "vacation_rentals": "",
                    "max_pages_set": "",
                    "page_count_local": "",
                    "records_properties": "",
                    "records_ads": "",
                    "records_total": "",
                    "unique_names_raw": "",
                    "search_total_results_first_page": "",
                    "search_properties_count_first_page": "",
                    "search_pages_processed_first_page": "",
                    "pagination_limit_reached_first_page": "",
                }
            )
            continue

        seen_hashes[file_hash] = path.name
        rows, inventory = flatten_source_file(path, file_hash, generated_at)
        raw_rows.extend(rows)
        inventory_rows.append(inventory)

    add_rating_sentiment(raw_rows)
    for index, row in enumerate(raw_rows, start=1):
        row["raw_master_id"] = f"HRAW-{index:05d}"

    write_csv(raw_master_csv, raw_rows, RAW_MASTER_COLUMNS)
    write_csv(source_inventory_csv, inventory_rows, SOURCE_INVENTORY_COLUMNS)

    summary = summarize(raw_rows, inventory_rows, raw_master_csv, source_inventory_csv)
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(report_md, summary)
    if update_nb:
        update_notebook(notebook, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten all Google Hotels Search JSON files into a raw master CSV.")
    parser.add_argument("--json-dir", type=Path, default=DEFAULT_JSON_DIR)
    parser.add_argument("--raw-master-csv", type=Path, default=DEFAULT_RAW_MASTER_CSV)
    parser.add_argument("--source-inventory-csv", type=Path, default=DEFAULT_SOURCE_INVENTORY_CSV)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--skip-notebook-update", action="store_true")
    args = parser.parse_args()

    summary = build(
        json_dir=args.json_dir,
        raw_master_csv=args.raw_master_csv,
        source_inventory_csv=args.source_inventory_csv,
        summary_json=args.summary_json,
        report_md=args.report_md,
        notebook=args.notebook,
        update_nb=not args.skip_notebook_update,
    )
    print(f"json_source_count={summary['json_source_count']}")
    print(f"json_processed_count={summary['json_processed_count']}")
    print(f"json_duplicate_file_count={summary['json_duplicate_file_count']}")
    print(f"raw_records={summary['raw_records']}")
    print(f"raw_unique_names={summary['raw_unique_names']}")
    print(f"raw_master_csv={summary['raw_master_csv_path']}")
    print(f"source_inventory_csv={summary['source_inventory_csv_path']}")


if __name__ == "__main__":
    main()
