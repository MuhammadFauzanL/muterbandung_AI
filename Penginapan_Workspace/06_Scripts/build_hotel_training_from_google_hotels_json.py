from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_INPUT = PENGINAPAN_WORKSPACE / "01_Raw_Data" / "google_hotels_search_json" / "dataset_google-hotels-search-scraper_2026-06-01_15-03-10-905.json"
DEFAULT_RAW_CSV = PENGINAPAN_WORKSPACE / "01_Raw_Data" / "generated_raw_csv" / "HOTEL_GOOGLE_SEARCH_RAW_2026-06-01.csv"
DEFAULT_TRAINING_CSV = PENGINAPAN_WORKSPACE / "02_Curated" / "HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv"
DEFAULT_SUMMARY_JSON = PENGINAPAN_WORKSPACE / "02_Curated" / "hotel_training_google_search_summary_2026-06-01.json"
DEFAULT_REPORT = PENGINAPAN_WORKSPACE / "04_Dokumentasi" / "HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.md"
DEFAULT_NOTEBOOK = PENGINAPAN_WORKSPACE / "03_Notebooks" / "penginapan_training.ipynb"

MODEL_VERSION = "hotel_google_search_rating_sentiment_v1"
SHRINKAGE_STRENGTH = 50.0
NOTEBOOK_TAG = "hotel_training_google_search_2026_06_01"


CSV_COLUMNS = [
    "hotel_training_id",
    "property_token",
    "duplicate_occurrence_count",
    "source_pages",
    "source_file",
    "source_page_number",
    "search_timestamp",
    "query",
    "gl",
    "hl",
    "currency",
    "check_in_date",
    "check_out_date",
    "adults",
    "children",
    "vacation_rentals_search",
    "search_total_results",
    "search_properties_count",
    "search_pages_processed",
    "raw_type",
    "property_segment",
    "name",
    "latitude",
    "longitude",
    "coordinate_available",
    "link",
    "check_in_time",
    "check_out_time",
    "price_lowest",
    "price_before_taxes_fees",
    "total_price_lowest",
    "total_price_before_taxes_fees",
    "price_source_count",
    "price_sources",
    "overall_rating",
    "reviews",
    "location_rating",
    "rating_sentiment_score",
    "adjusted_rating_sentiment_score",
    "rating_sentiment_label",
    "adjusted_rating_sentiment_label",
    "review_confidence_label",
    "review_count_p95",
    "rating_sentiment_source",
    "rating_sentiment_model_version",
    "rating_sentiment_prior_score",
    "rating_sentiment_shrinkage_strength",
    "amenities",
    "amenities_count",
    "excluded_amenities",
    "excluded_amenities_count",
    "essential_info",
    "essential_info_count",
    "nearby_place_names",
    "nearby_places_count",
    "primary_image_url",
    "image_count",
    "coordinate_available_flag",
    "rating_available",
    "price_available",
    "amenities_available",
    "image_available",
    "source_link_available",
    "checkin_checkout_available",
    "nearby_places_available",
    "data_quality_score",
    "prices_json",
    "nearby_places_json",
    "health_and_safety_json",
    "generated_at",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def bool_text(value) -> str:
    return "True" if bool(value) else "False"


def json_text(value) -> str:
    if value in (None, "", [], {}):
        return ""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def join_text(values) -> str:
    if not isinstance(values, list):
        return ""
    output = []
    for value in values:
        if isinstance(value, (dict, list)):
            output.append(json_text(value))
        else:
            text = clean_text(value)
            if text:
                output.append(text)
    return "; ".join(output)


def number(value):
    if value is None or value == "":
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if math.isnan(numeric):
        return ""
    if numeric.is_integer():
        return int(numeric)
    return round(numeric, 4)


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = clean_text(text).lower()
    return any(keyword in lowered for keyword in keywords)


def normalize_property_segment(name: str, raw_type: str) -> str:
    lowered = clean_text(name).lower()
    raw = clean_text(raw_type).lower()

    room_keywords = [
        "standard double room",
        "deluxe double room",
        "superior double room",
        "standard room",
        "deluxe room",
        "queen room",
        "king room",
        "twin room",
        "triple room",
        "family room",
        "family triple room",
        "suite room",
        "zen rooms",
        "kamar",
        "kamarku",
    ]
    apartment_keywords = [
        "apartment",
        "apartemen",
        "gateway pasteur",
        "the edge",
        "jarrdin",
        "studio",
        "unit",
        "sewa apartemen",
        "apt ",
        "one-bedroom",
        "two-bedroom",
        "2bedroom",
        "2 bedroom",
        "2br",
        "2 br",
        "1br",
        "1 br",
    ]
    villa_keywords = ["villa"]
    guest_house_keywords = [
        "guest house",
        "guesthouse",
        "homestay",
        "home stay",
        "bed & breakfast",
        "kost",
        " kos",
    ]
    hotel_keywords = ["hotel", "reddoorz", "oyo", "residence", "sans "]

    if contains_any(lowered, villa_keywords):
        return "villa"
    if contains_any(lowered, apartment_keywords):
        return "apartment"
    if contains_any(lowered, guest_house_keywords):
        return "guest_house"
    if contains_any(lowered, room_keywords):
        return "room_level_listing"
    if contains_any(lowered, hotel_keywords):
        return "hotel"
    if raw == "vacation rental":
        return "vacation_rental"
    return "hotel"


def review_confidence_label(review_count) -> str:
    if review_count in ("", None):
        return "missing_review_confidence"
    count = float(review_count)
    if count < 30:
        return "low_review_confidence"
    if count < 200:
        return "medium_review_confidence"
    return "high_review_confidence"


def sentiment_label(score) -> str:
    if score in ("", None):
        return "Tidak Tersedia"
    score = float(score)
    if score >= 0.60:
        return "Sangat Positif"
    if score >= 0.20:
        return "Positif"
    if score > -0.20:
        return "Netral"
    if score > -0.60:
        return "Negatif"
    return "Sangat Negatif"


def rating_sentiment_score(overall_rating):
    if overall_rating in ("", None):
        return ""
    rating = float(overall_rating)
    return max(-1.0, min(1.0, (rating - 3.0) / 2.0))


def first_image_url(images) -> str:
    if not isinstance(images, list):
        return ""
    for item in images:
        if isinstance(item, dict):
            url = clean_text(item.get("original_image"))
            if url:
                return url
    return ""


def price_sources(prices) -> str:
    if not isinstance(prices, list):
        return ""
    sources = []
    for item in prices:
        if isinstance(item, dict):
            source = clean_text(item.get("source"))
            if source:
                sources.append(source)
    return "; ".join(dict.fromkeys(sources))


def extract_nested_number(container, *keys):
    current = container
    for key in keys:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
    return number(current)


def quality_score(row: dict) -> float:
    weights = {
        "coordinate_available_flag": 0.20,
        "rating_available": 0.15,
        "price_available": 0.15,
        "amenities_available": 0.15,
        "image_available": 0.15,
        "source_link_available": 0.10,
        "checkin_checkout_available": 0.05,
        "nearby_places_available": 0.05,
    }
    score = 0.0
    for field, weight in weights.items():
        if row.get(field) == "True":
            score += weight
    return round(score, 4)


def flatten_record(page: dict, prop: dict, source_file: Path, generated_at: str) -> dict:
    search_parameters = page.get("search_parameters") or {}
    search_metadata = page.get("search_metadata") or {}
    coords = prop.get("gps_coordinates") or {}
    prices = prop.get("prices") or []
    nearby_places = prop.get("nearby_places") or []
    images = prop.get("images") or []
    amenities = prop.get("amenities") or []
    excluded = prop.get("excluded_amenities") or []
    essential_info = prop.get("essential_info") or []
    rate_per_night = prop.get("rate_per_night") or {}
    total_rate = prop.get("total_rate") or {}

    name = clean_text(prop.get("name"))
    raw_type = clean_text(prop.get("type"))
    latitude = number(coords.get("latitude"))
    longitude = number(coords.get("longitude"))
    overall_rating = number(prop.get("overall_rating"))
    reviews = number(prop.get("reviews"))
    location_rating = number(prop.get("location_rating"))
    price_lowest = extract_nested_number(rate_per_night, "extracted_lowest")
    price_before_taxes_fees = extract_nested_number(rate_per_night, "extracted_before_taxes_fees")
    total_price_lowest = extract_nested_number(total_rate, "extracted_lowest")
    total_price_before_taxes_fees = extract_nested_number(total_rate, "extracted_before_taxes_fees")

    row = {
        "hotel_training_id": "",
        "property_token": clean_text(prop.get("property_token")),
        "duplicate_occurrence_count": "",
        "source_pages": "",
        "source_file": source_file.name,
        "source_page_number": number(page.get("page_number")),
        "search_timestamp": clean_text(page.get("search_timestamp")),
        "query": clean_text(search_parameters.get("q")),
        "gl": clean_text(search_parameters.get("gl")),
        "hl": clean_text(search_parameters.get("hl")),
        "currency": clean_text(search_parameters.get("currency")),
        "check_in_date": clean_text(search_parameters.get("check_in_date")),
        "check_out_date": clean_text(search_parameters.get("check_out_date")),
        "adults": number(search_parameters.get("adults")),
        "children": number(search_parameters.get("children")),
        "vacation_rentals_search": bool_text(search_parameters.get("vacation_rentals")),
        "search_total_results": number(search_metadata.get("total_results")),
        "search_properties_count": number(search_metadata.get("properties_count")),
        "search_pages_processed": number(search_metadata.get("pages_processed")),
        "raw_type": raw_type,
        "property_segment": normalize_property_segment(name, raw_type),
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "coordinate_available": bool_text(latitude != "" and longitude != ""),
        "link": clean_text(prop.get("link")),
        "check_in_time": clean_text(prop.get("check_in_time")),
        "check_out_time": clean_text(prop.get("check_out_time")),
        "price_lowest": price_lowest,
        "price_before_taxes_fees": price_before_taxes_fees,
        "total_price_lowest": total_price_lowest,
        "total_price_before_taxes_fees": total_price_before_taxes_fees,
        "price_source_count": len(prices) if isinstance(prices, list) else 0,
        "price_sources": price_sources(prices),
        "overall_rating": overall_rating,
        "reviews": reviews,
        "location_rating": location_rating,
        "rating_sentiment_score": "",
        "adjusted_rating_sentiment_score": "",
        "rating_sentiment_label": "",
        "adjusted_rating_sentiment_label": "",
        "review_confidence_label": "",
        "review_count_p95": "",
        "rating_sentiment_source": "",
        "rating_sentiment_model_version": MODEL_VERSION,
        "rating_sentiment_prior_score": "",
        "rating_sentiment_shrinkage_strength": SHRINKAGE_STRENGTH,
        "amenities": join_text(amenities),
        "amenities_count": len(amenities) if isinstance(amenities, list) else 0,
        "excluded_amenities": join_text(excluded),
        "excluded_amenities_count": len(excluded) if isinstance(excluded, list) else 0,
        "essential_info": join_text(essential_info),
        "essential_info_count": len(essential_info) if isinstance(essential_info, list) else 0,
        "nearby_place_names": "; ".join(
            clean_text(item.get("name"))
            for item in nearby_places
            if isinstance(item, dict) and clean_text(item.get("name"))
        ),
        "nearby_places_count": len(nearby_places) if isinstance(nearby_places, list) else 0,
        "primary_image_url": first_image_url(images),
        "image_count": len(images) if isinstance(images, list) else 0,
        "coordinate_available_flag": "",
        "rating_available": "",
        "price_available": "",
        "amenities_available": "",
        "image_available": "",
        "source_link_available": "",
        "checkin_checkout_available": "",
        "nearby_places_available": "",
        "data_quality_score": "",
        "prices_json": json_text(prices),
        "nearby_places_json": json_text(nearby_places),
        "health_and_safety_json": json_text(prop.get("health_and_safety")),
        "generated_at": generated_at,
    }
    row["coordinate_available_flag"] = bool_text(row["latitude"] != "" and row["longitude"] != "")
    row["rating_available"] = bool_text(row["overall_rating"] != "" and row["reviews"] != "")
    row["price_available"] = bool_text(row["price_lowest"] != "" or row["total_price_lowest"] != "")
    row["amenities_available"] = bool_text(row["amenities_count"] > 0)
    row["image_available"] = bool_text(row["primary_image_url"] != "")
    row["source_link_available"] = bool_text(row["link"] != "")
    row["checkin_checkout_available"] = bool_text(row["check_in_time"] != "" and row["check_out_time"] != "")
    row["nearby_places_available"] = bool_text(row["nearby_places_count"] > 0)
    row["data_quality_score"] = quality_score(row)
    return row


def add_rating_sentiment(rows: list[dict]) -> None:
    scores = []
    weights = []
    review_counts = [float(row["reviews"]) for row in rows if row["reviews"] != ""]
    if review_counts:
        sorted_counts = sorted(review_counts)
        index = int(math.ceil(0.95 * len(sorted_counts))) - 1
        review_count_p95 = sorted_counts[max(0, min(index, len(sorted_counts) - 1))]
    else:
        review_count_p95 = 1.0

    for row in rows:
        score = rating_sentiment_score(row["overall_rating"])
        if score == "":
            continue
        effective_reviews = float(row["reviews"]) if row["reviews"] != "" else 1.0
        capped_reviews = min(effective_reviews, review_count_p95)
        scores.append(float(score) * capped_reviews)
        weights.append(capped_reviews)
    prior = sum(scores) / sum(weights) if weights else 0.0

    for row in rows:
        score = rating_sentiment_score(row["overall_rating"])
        row["review_count_p95"] = round(review_count_p95, 4)
        row["rating_sentiment_prior_score"] = round(prior, 4)
        if score == "":
            row["rating_sentiment_score"] = ""
            row["adjusted_rating_sentiment_score"] = ""
            row["rating_sentiment_label"] = "Tidak Tersedia"
            row["adjusted_rating_sentiment_label"] = "Tidak Tersedia"
            row["review_confidence_label"] = "missing_review_confidence"
            row["rating_sentiment_source"] = "unavailable"
            continue

        reviews = float(row["reviews"]) if row["reviews"] != "" else 1.0
        effective_reviews = min(reviews, review_count_p95)
        weight = effective_reviews / (effective_reviews + SHRINKAGE_STRENGTH)
        adjusted = (weight * float(score)) + ((1.0 - weight) * prior)

        row["rating_sentiment_score"] = round(float(score), 4)
        row["adjusted_rating_sentiment_score"] = round(adjusted, 4)
        row["rating_sentiment_label"] = sentiment_label(score)
        row["adjusted_rating_sentiment_label"] = sentiment_label(adjusted)
        row["review_confidence_label"] = review_confidence_label(row["reviews"])
        row["rating_sentiment_source"] = "overall_rating_fallback"


def deduplicate_rows(raw_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in raw_rows:
        token = row["property_token"] or f"{row['name']}|{row['latitude']}|{row['longitude']}"
        grouped[token].append(row)

    selected_rows = []
    for rows in grouped.values():
        pages = sorted({int(row["source_page_number"]) for row in rows if row["source_page_number"] != ""})
        selected = max(
            rows,
            key=lambda row: (
                float(row["data_quality_score"]),
                row["rating_available"] == "True",
                row["price_available"] == "True",
                int(row["amenities_count"]),
                int(row["image_count"]),
                row["source_link_available"] == "True",
                -int(row["source_page_number"] or 9999),
            ),
        ).copy()
        selected["duplicate_occurrence_count"] = len(rows)
        selected["source_pages"] = ";".join(str(page) for page in pages)
        selected_rows.append(selected)

    selected_rows.sort(key=lambda row: (int(str(row["source_page_number"]) or 9999), clean_text(row["name"]).lower()))
    for index, row in enumerate(selected_rows, start=1):
        row["hotel_training_id"] = f"HTRAIN-{index:04d}"
    return selected_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def count_true(rows: list[dict], field: str) -> int:
    return sum(1 for row in rows if row.get(field) == "True")


def summarize_rows(raw_rows: list[dict], training_rows: list[dict], pages: list[dict], input_path: Path, raw_csv: Path, training_csv: Path) -> dict:
    duplicate_groups = sum(1 for row in training_rows if int(row["duplicate_occurrence_count"]) > 1)
    duplicate_rows = len(raw_rows) - len(training_rows)
    return {
        "generated_at": now_iso(),
        "input_path": str(input_path),
        "raw_csv_path": str(raw_csv),
        "training_csv_path": str(training_csv),
        "page_count": len(pages),
        "raw_property_records": len(raw_rows),
        "unique_property_tokens": len(training_rows),
        "duplicate_property_groups": duplicate_groups,
        "duplicate_property_rows": duplicate_rows,
        "search_parameters": pages[0].get("search_parameters", {}) if pages else {},
        "search_metadata_first_page": pages[0].get("search_metadata", {}) if pages else {},
        "raw_type_counts": dict(Counter(row["raw_type"] for row in raw_rows)),
        "property_segment_counts_raw": dict(Counter(row["property_segment"] for row in raw_rows)),
        "property_segment_counts_training": dict(Counter(row["property_segment"] for row in training_rows)),
        "quality_flags_training": {
            "coordinate_available": count_true(training_rows, "coordinate_available_flag"),
            "rating_available": count_true(training_rows, "rating_available"),
            "price_available": count_true(training_rows, "price_available"),
            "amenities_available": count_true(training_rows, "amenities_available"),
            "image_available": count_true(training_rows, "image_available"),
            "source_link_available": count_true(training_rows, "source_link_available"),
            "checkin_checkout_available": count_true(training_rows, "checkin_checkout_available"),
            "nearby_places_available": count_true(training_rows, "nearby_places_available"),
        },
        "review_confidence_counts_training": dict(Counter(row["review_confidence_label"] for row in training_rows)),
        "sentiment_source_counts_training": dict(Counter(row["rating_sentiment_source"] for row in training_rows)),
        "readiness_training": {
            "strong_core_ready": sum(
                1
                for row in training_rows
                if row["coordinate_available_flag"] == "True"
                and row["rating_available"] == "True"
                and row["price_available"] == "True"
                and row["amenities_available"] == "True"
                and row["image_available"] == "True"
            ),
            "recommendation_usable": sum(
                1
                for row in training_rows
                if row["coordinate_available_flag"] == "True"
                and row["image_available"] == "True"
                and (
                    row["rating_available"] == "True"
                    or row["price_available"] == "True"
                    or row["amenities_available"] == "True"
                )
            ),
            "minimal_usable": sum(
                1
                for row in training_rows
                if row["name"] and row["coordinate_available_flag"] == "True"
            ),
        },
        "rating_sentiment_model_version": MODEL_VERSION,
        "review_count_p95": training_rows[0]["review_count_p95"] if training_rows else "",
        "rating_sentiment_prior_score": training_rows[0]["rating_sentiment_prior_score"] if training_rows else "",
    }


def markdown_table(mapping: dict, key_header: str, value_header: str) -> str:
    lines = [f"| {key_header} | {value_header} |", "| --- | ---: |"]
    for key, value in mapping.items():
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Hotel Training Google Search Pipeline - 2026-06-01",
        "",
        f"Generated at: `{summary['generated_at']}`",
        f"Input JSON: `{summary['input_path']}`",
        f"Raw CSV: `{summary['raw_csv_path']}`",
        f"Training CSV: `{summary['training_csv_path']}`",
        "",
        "## Ringkasan Data",
        "",
        f"- Halaman hasil pencarian: `{summary['page_count']}`",
        f"- Record properti mentah: `{summary['raw_property_records']}`",
        f"- Properti unik berdasarkan `property_token`: `{summary['unique_property_tokens']}`",
        f"- Grup duplikat: `{summary['duplicate_property_groups']}`",
        f"- Baris duplikat yang disatukan: `{summary['duplicate_property_rows']}`",
        "",
        "## Parameter Pencarian",
        "",
        markdown_table(summary["search_parameters"], "Parameter", "Value"),
        "",
        "## Segment Training",
        "",
        markdown_table(summary["property_segment_counts_training"], "Segment", "Jumlah"),
        "",
        "## Quality Flags Training",
        "",
        markdown_table(summary["quality_flags_training"], "Flag", "Terisi"),
        "",
        "## Review Confidence",
        "",
        markdown_table(summary["review_confidence_counts_training"], "Label", "Jumlah"),
        "",
        "## Readiness Training",
        "",
        markdown_table(summary["readiness_training"], "Level", "Jumlah"),
        "",
        "## Catatan Engineering",
        "",
        "- File JSON berisi hasil pencarian Google Hotels per halaman, jadi proses pertama adalah flatten `properties` menjadi baris CSV.",
        "- CSV raw menyimpan semua occurrence dari halaman pencarian.",
        "- CSV training menyatukan duplikat berdasarkan `property_token` dan memilih baris dengan quality score terbaik.",
        "- Dataset ini berasal dari pencarian dengan `vacation_rentals=True`, sehingga komposisinya cenderung kuat untuk villa, apartment, dan penginapan sewa.",
        "- Sentiment di dataset ini adalah rating-based sentiment dari `overall_rating` dan `reviews`, bukan NLP komentar.",
        "- Bayesian shrinkage tetap dipakai agar properti dengan review sedikit tidak terlalu percaya diri.",
        "- Untuk LLM, gunakan `quality_flags`, `review_confidence_label`, dan `data_quality_score` sebelum membuat klaim harga, fasilitas, rating, atau visual.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def write_notebook(path: Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = {
        "cells": [
            notebook_cell(
                "markdown",
                f"""
# Hotel Training - Google Hotels Search 2026-06-01

Notebook ini khusus untuk pipeline hotel, terpisah dari `wisata_training.ipynb`.

Tujuan:
- Membaca JSON Google Hotels Search.
- Mengubah hasil per halaman menjadi CSV raw.
- Membuat CSV training yang sudah deduplicate berdasarkan `property_token`.
- Menambahkan segment properti, quality flags, rating-based sentiment, dan review confidence.

Hasil terakhir:
- Halaman: {summary["page_count"]}
- Raw records: {summary["raw_property_records"]}
- Unique training records: {summary["unique_property_tokens"]}
- Raw CSV: `{summary["raw_csv_path"]}`
- Training CSV: `{summary["training_csv_path"]}`
""",
            ),
            notebook_cell(
                "code",
                """
# Rebuild hotel training dataset dari JSON sumber.
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

subprocess.run(
    [sys.executable, str(PROJECT_ROOT / "Penginapan_Workspace" / "06_Scripts" / "build_hotel_training_from_google_hotels_json.py")],
    check=True,
)
""",
            ),
            notebook_cell(
                "code",
                """
# Baca ringkasan hasil pipeline.
import json
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

summary_path = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "hotel_training_google_search_summary_2026-06-01.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
summary
""",
            ),
            notebook_cell(
                "code",
                """
# Preview data training hotel.
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

training_csv = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv"
hotel_training_df = pd.read_csv(training_csv)

hotel_training_df[
    [
        "hotel_training_id",
        "name",
        "property_segment",
        "overall_rating",
        "reviews",
        "price_lowest",
        "adjusted_rating_sentiment_score",
        "review_confidence_label",
        "data_quality_score",
    ]
].head(10)
""",
            ),
            notebook_cell(
                "markdown",
                """
## Aturan penggunaan

- Gunakan CSV training untuk recommender, bukan CSV raw, karena raw masih berisi duplikat antar halaman.
- Untuk klaim harga, wajib `price_available == True`.
- Untuk klaim fasilitas, wajib `amenities_available == True`.
- Untuk kartu visual, wajib `image_available == True`.
- Untuk ranking berbasis rating, prioritaskan `review_confidence_label` medium atau high.
- Karena sumber ini memakai `vacation_rentals=True`, jangan anggap semua baris sebagai hotel formal.
""",
            ),
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def build(input_path: Path, raw_csv: Path, training_csv: Path, summary_json: Path, report: Path, notebook: Path) -> dict:
    pages = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(pages, list):
        raise ValueError("Input JSON must be a list of search result pages.")

    generated_at = now_iso()
    raw_rows = []
    for page in pages:
        for prop in page.get("properties") or []:
            raw_rows.append(flatten_record(page, prop, input_path, generated_at))

    add_rating_sentiment(raw_rows)
    training_rows = deduplicate_rows(raw_rows)
    add_rating_sentiment(training_rows)

    write_csv(raw_csv, raw_rows)
    write_csv(training_csv, training_rows)

    summary = summarize_rows(raw_rows, training_rows, pages, input_path, raw_csv, training_csv)
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(report, summary)
    write_notebook(notebook, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build hotel training CSV from Google Hotels Search JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--raw-csv", type=Path, default=DEFAULT_RAW_CSV)
    parser.add_argument("--training-csv", type=Path, default=DEFAULT_TRAINING_CSV)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    args = parser.parse_args()

    summary = build(
        input_path=args.input,
        raw_csv=args.raw_csv,
        training_csv=args.training_csv,
        summary_json=args.summary_json,
        report=args.report,
        notebook=args.notebook,
    )

    print("Hotel training dataset built")
    print(f"pages={summary['page_count']}")
    print(f"raw_records={summary['raw_property_records']}")
    print(f"unique_training_records={summary['unique_property_tokens']}")
    print(f"raw_csv={args.raw_csv}")
    print(f"training_csv={args.training_csv}")
    print(f"report={args.report}")
    print(f"notebook={args.notebook}")


if __name__ == "__main__":
    main()
