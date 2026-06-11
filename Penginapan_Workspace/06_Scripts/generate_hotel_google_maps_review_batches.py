from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_SOURCE = PENGINAPAN_WORKSPACE / "02_Curated" / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv"
DEFAULT_TARGETS = PENGINAPAN_WORKSPACE / "02_Curated" / "hotel_google_maps_review_targets_2026-06-01.csv"
DEFAULT_OUTPUT_DIR = PENGINAPAN_WORKSPACE / "05_Apify_Review_Batches" / "Hotel_Review_Batches"
DEFAULT_REPORT = PENGINAPAN_WORKSPACE / "04_Dokumentasi" / "HOTEL_GOOGLE_MAPS_REVIEW_SCRAPING_PLAN_2026-06-01.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def number(value):
    text = clean_text(value)
    if not text:
        return ""
    try:
        value = float(text)
    except ValueError:
        return ""
    if math.isnan(value):
        return ""
    if value.is_integer():
        return int(value)
    return round(value, 7)


def bool_text(value) -> str:
    return "True" if bool(value) else "False"


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
    ]
    villa_keywords = ["villa"]
    guest_house_keywords = ["guest house", "guesthouse", "homestay", "home stay", "bed & breakfast", "kost", " kos"]
    hotel_keywords = ["hotel", "reddoorz", "oyo", "residence", "sans "]

    if contains_any(lowered, villa_keywords):
        return "villa"
    if contains_any(lowered, apartment_keywords):
        return "apartment"
    if contains_any(lowered, guest_house_keywords):
        return "guest_house"
    if contains_any(lowered, room_keywords):
        return "room_level_listing"
    if contains_any(lowered, hotel_keywords) or raw == "hotel":
        return "hotel"
    if raw == "vacation rental":
        return "vacation_rental"
    return "hotel"


def derived_review_confidence_label(reviews) -> str:
    count = number(reviews)
    if count == "":
        return "missing_review_confidence"
    if float(count) < 30:
        return "low_review_confidence"
    if float(count) < 200:
        return "medium_review_confidence"
    return "high_review_confidence"


def derived_quality_score(row: dict) -> float:
    weights = {
        "coordinate_available": 0.25,
        "rating_available": 0.20,
        "price_available": 0.15,
        "amenities_available": 0.15,
        "image_available": 0.15,
        "source_link_available": 0.10,
    }
    score = 0.0
    for field, weight in weights.items():
        if row.get(field) == "True":
            score += weight
    return round(score, 4)


def review_priority(row: dict) -> str:
    label = clean_text(row.get("review_confidence_label"))
    rating_available = clean_text(row.get("rating_available"))
    if label == "missing_review_confidence" or rating_available == "False":
        return "P0_missing_rating_review"
    if label == "low_review_confidence":
        return "P1_low_review_confidence"
    if label == "medium_review_confidence":
        return "P2_medium_review_confidence"
    return "P3_high_review_confidence"


def make_query(row: dict) -> str:
    name = clean_text(row.get("name"))
    lat = clean_text(row.get("latitude"))
    lon = clean_text(row.get("longitude"))
    segment = clean_text(row.get("property_segment"))
    if lat and lon:
        return f"{name} {lat},{lon}"
    if segment in {"villa", "apartment", "vacation_rental"}:
        return f"{name} Bandung Jawa Barat"
    return f"{name} Cimahi Bandung Jawa Barat"


def make_maps_search_url(query: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_source_row(row: dict, index: int, source_path: Path) -> dict:
    name = clean_text(row.get("name"))
    raw_type = clean_text(row.get("raw_type")) or clean_text(row.get("type"))
    lat = clean_text(row.get("latitude")) or clean_text(row.get("gps_coordinates_latitude"))
    lon = clean_text(row.get("longitude")) or clean_text(row.get("gps_coordinates_longitude"))
    segment = clean_text(row.get("property_segment")) or normalize_property_segment(name, raw_type)
    reviews = clean_text(row.get("reviews"))
    rating = clean_text(row.get("overall_rating"))
    rating_available = clean_text(row.get("rating_available")) or bool_text(bool(rating and reviews))
    price_available = clean_text(row.get("price_available")) or bool_text(
        bool(
            clean_text(row.get("price_lowest"))
            or clean_text(row.get("rate_per_night_extracted_lowest"))
            or clean_text(row.get("total_rate_extracted_lowest"))
        )
    )
    amenities_available = clean_text(row.get("amenities_available")) or bool_text(bool(clean_text(row.get("amenities"))))
    image_available = clean_text(row.get("image_available")) or bool_text(bool(clean_text(row.get("primary_image_url")) or clean_text(row.get("images"))))
    source_link_available = clean_text(row.get("source_link_available")) or bool_text(bool(clean_text(row.get("source_link")) or clean_text(row.get("link"))))
    normalized = {
        "hotel_id": clean_text(row.get("hotel_id")) or f"HOTEL-OLD-{index:03d}",
        "name": name,
        "property_segment": segment,
        "latitude": lat,
        "longitude": lon,
        "overall_rating": rating,
        "reviews": reviews,
        "review_confidence_label": clean_text(row.get("review_confidence_label")) or derived_review_confidence_label(reviews),
        "rating_available": rating_available,
        "price_available": price_available,
        "amenities_available": amenities_available,
        "image_available": image_available,
        "source_link_available": source_link_available,
        "data_quality_score": clean_text(row.get("data_quality_score")),
        "source_dataset": str(source_path),
    }
    normalized["coordinate_available"] = bool_text(bool(lat and lon))
    if not normalized["data_quality_score"]:
        normalized["data_quality_score"] = derived_quality_score(normalized)
    return normalized


def build_targets(source_path: Path) -> list[dict]:
    source_rows = read_rows(source_path)
    targets = []
    seen = set()
    for index, row in enumerate(source_rows, start=1):
        normalized = normalize_source_row(row, index, source_path)
        name = normalized["name"]
        if not name:
            continue
        hotel_id = normalized["hotel_id"]
        lat = clean_text(normalized.get("latitude"))
        lon = clean_text(normalized.get("longitude"))
        dedupe_key = (name.lower(), lat, lon)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        query = make_query(normalized)
        targets.append(
            {
                "review_target_id": f"HREV-{len(targets) + 1:04d}",
                "hotel_id": hotel_id,
                "name": name,
                "property_segment": normalized["property_segment"],
                "latitude": number(normalized.get("latitude")),
                "longitude": number(normalized.get("longitude")),
                "overall_rating": number(normalized.get("overall_rating")),
                "reviews_existing": number(normalized.get("reviews")),
                "review_confidence_label": normalized["review_confidence_label"],
                "rating_available": normalized["rating_available"],
                "price_available": normalized["price_available"],
                "amenities_available": normalized["amenities_available"],
                "image_available": normalized["image_available"],
                "data_quality_score": number(normalized.get("data_quality_score")),
                "review_scrape_priority": review_priority(normalized),
                "google_maps_search_query": query,
                "google_maps_search_url": make_maps_search_url(query),
                "source_dataset": str(source_path),
            }
        )
    return targets


def write_targets(path: Path, targets: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(targets[0].keys()) if targets else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(targets)


def apify_config(search_strings: list[str], max_reviews: int) -> dict:
    return {
        "language": "id",
        "maxReviews": max_reviews,
        "maxCrawledPlacesPerSearch": 1,
        "reviewsSort": "newest",
        "scrapePlaceDetailPage": False,
        "includeWebResults": False,
        "skipClosedPlaces": False,
        "searchStringsArray": search_strings,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")


def write_batches(output_dir: Path, targets: list[dict], batch_size: int, max_reviews: int) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    batch_paths = []
    for start in range(0, len(targets), batch_size):
        batch = targets[start : start + batch_size]
        batch_number = (start // batch_size) + 1
        path = output_dir / f"apify_hotel_google_maps_reviews_batch_{batch_number:02d}.json"
        write_json(path, apify_config([row["google_maps_search_url"] for row in batch], max_reviews))
        batch_paths.append(path)
    return batch_paths


def select_test_targets(targets: list[dict], test_size: int) -> list[dict]:
    preferred_segments = {"hotel", "guest_house", "villa"}
    preferred_confidence = {"high_review_confidence", "medium_review_confidence"}
    preferred = [
        row
        for row in targets
        if row["property_segment"] in preferred_segments
        and row["review_confidence_label"] in preferred_confidence
    ]
    preferred.sort(
        key=lambda row: (
            row["property_segment"] != "hotel",
            -float(row["data_quality_score"] or 0),
            clean_text(row["name"]).lower(),
        )
    )
    if len(preferred) >= test_size:
        return preferred[:test_size]
    fallback = [row for row in targets if row not in preferred]
    fallback.sort(key=lambda row: (-float(row["data_quality_score"] or 0), clean_text(row["name"]).lower()))
    return (preferred + fallback)[:test_size]


def markdown_table(mapping: dict, key_header: str, value_header: str) -> str:
    lines = [f"| {key_header} | {value_header} |", "| --- | ---: |"]
    for key, value in mapping.items():
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Hotel Google Maps Review Scraping Plan - 2026-06-01",
        "",
        f"Generated at: `{summary['generated_at']}`",
        f"Source dataset: `{summary['source_dataset']}`",
        f"Target CSV: `{summary['target_csv']}`",
        f"Batch folder: `{summary['batch_folder']}`",
        "",
        "## Ringkasan",
        "",
        f"- Total target hotel/penginapan: `{summary['target_count']}`",
        f"- Batch size: `{summary['batch_size']}`",
        f"- Total batch: `{summary['batch_count']}`",
        f"- Max reviews per target: `{summary['max_reviews']}`",
        f"- Estimasi maksimum review kalau semua berhasil: `{summary['target_count'] * summary['max_reviews']}`",
        "",
        "## Segment Target",
        "",
        markdown_table(summary["segment_counts"], "Segment", "Jumlah"),
        "",
        "## Prioritas Scraping",
        "",
        markdown_table(summary["priority_counts"], "Priority", "Jumlah"),
        "",
        "## File JSON Yang Dibuat",
        "",
    ]
    lines.extend(f"- `{path}`" for path in summary["batch_paths"])
    lines.extend(
        [
            "",
            "## Cara Pakai",
            "",
            "1. Jalankan batch test dulu: `apify_hotel_google_maps_reviews_test_10.json`. Test batch ini sengaja berisi target yang relatif jelas, bukan hanya data P0.",
            "2. Setelah hasil test cocok dengan nama hotel/penginapan target, lanjutkan batch 01, 02, dan seterusnya.",
            "3. Simpan output hasil scraper sebagai dataset baru, jangan langsung timpa dataset training.",
            "4. Setelah review comment terkumpul, baru jalankan pipeline NLP/sentiment hotel.",
            "",
            "## Catatan Penting",
            "",
            "- Dataset hotel saat ini tidak punya `query_place_id` Google Maps, jadi target dibuat memakai Google Maps search URL berbasis nama dan koordinat.",
            "- Karena belum memakai place id langsung, hasil scraper wajib dicek match-nya: nama hasil, koordinat, rating, dan alamat harus cocok.",
            "- `maxCrawledPlacesPerSearch` dibuat `1` agar tiap query hanya mengambil satu tempat paling relevan.",
            "- `reviewsSort` memakai `newest` agar komentar terbaru masuk terlebih dahulu.",
            "- Untuk training NLP, jangan campur komentar hotel dengan wisata sebelum diberi label domain `hotel_review`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(source: Path, targets_csv: Path, output_dir: Path, report: Path, batch_size: int, max_reviews: int, test_size: int) -> dict:
    targets = build_targets(source)
    targets.sort(
        key=lambda row: (
            row["review_scrape_priority"],
            row["property_segment"],
            clean_text(row["name"]).lower(),
        )
    )
    for index, row in enumerate(targets, start=1):
        row["review_target_id"] = f"HREV-{index:04d}"

    write_targets(targets_csv, targets)
    batch_paths = write_batches(output_dir, targets, batch_size, max_reviews)

    test_targets = select_test_targets(targets, test_size)
    test_path = output_dir / f"apify_hotel_google_maps_reviews_test_{test_size}.json"
    write_json(test_path, apify_config([row["google_maps_search_url"] for row in test_targets], max_reviews))

    all_path = output_dir / "apify_hotel_google_maps_reviews_all_181.json"
    write_json(all_path, apify_config([row["google_maps_search_url"] for row in targets], max_reviews))

    summary = {
        "generated_at": now_iso(),
        "source_dataset": str(source),
        "target_csv": str(targets_csv),
        "batch_folder": str(output_dir),
        "target_count": len(targets),
        "batch_size": batch_size,
        "batch_count": len(batch_paths),
        "max_reviews": max_reviews,
        "segment_counts": dict(Counter(row["property_segment"] for row in targets)),
        "priority_counts": dict(Counter(row["review_scrape_priority"] for row in targets)),
        "batch_paths": [str(test_path), str(all_path), *[str(path) for path in batch_paths]],
    }
    write_report(report, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Apify Google Maps review batches for hotel dataset.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--targets-csv", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--max-reviews", type=int, default=50)
    parser.add_argument("--test-size", type=int, default=10)
    args = parser.parse_args()

    summary = build(
        source=args.source,
        targets_csv=args.targets_csv,
        output_dir=args.output_dir,
        report=args.report,
        batch_size=args.batch_size,
        max_reviews=args.max_reviews,
        test_size=args.test_size,
    )
    print("Hotel Google Maps review batches generated")
    print(f"targets={summary['target_count']}")
    print(f"batch_count={summary['batch_count']}")
    print(f"max_reviews={summary['max_reviews']}")
    print(f"target_csv={summary['target_csv']}")
    print(f"batch_folder={summary['batch_folder']}")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
