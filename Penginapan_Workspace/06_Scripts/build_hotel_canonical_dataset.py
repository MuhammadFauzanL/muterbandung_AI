import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_INPUT = PENGINAPAN_WORKSPACE / "01_Raw_Data" / "dataset_hotel_original" / "dataset_hotel" / "dataset_hotel_cimahi_semua_kolom (2).csv"
DEFAULT_OUTPUT = PENGINAPAN_WORKSPACE / "02_Curated" / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv"
DEFAULT_SUMMARY = PENGINAPAN_WORKSPACE / "02_Curated" / "hotel_canonical_summary_2026-05-29.json"
DEFAULT_REPORT = PENGINAPAN_WORKSPACE / "04_Dokumentasi" / "HOTEL_CANONICAL_PIPELINE_2026-05-29.md"

MODEL_VERSION = "hotel_rating_sentiment_v1"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value):
    return str(value or "").strip()


def parse_float(value):
    text = clean_text(value)
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def parse_int(value):
    number = parse_float(value)
    if math.isnan(number):
        return pd.NA
    return int(round(number))


def safe_json_loads(value, default):
    text = clean_text(value)
    if not text:
        return default
    try:
        return json.loads(text)
    except Exception:
        return default


def bool_text(value):
    return "True" if bool(value) else "False"


def contains_any(text, keywords):
    lowered = clean_text(text).lower()
    return any(keyword in lowered for keyword in keywords)


def normalize_property_segment(row):
    name = clean_text(row.get("name"))
    raw_type = clean_text(row.get("type")).lower()
    lowered = name.lower()

    room_keywords = [
        "standard double room", "deluxe double room", "superior double room",
        "standard room", "deluxe room", "queen room", "king room", "twin room",
        "suite room", "zen rooms", "kamar", "kamarku",
    ]
    apartment_keywords = [
        "apartment", "apartemen", "gateway pasteur", "the edge", "studio",
        "unit", "sewa apartemen", "apt ", "one-bedroom", "two-bedroom",
        "2bedroom", "2 bedroom", "2br", "2 br",
    ]
    villa_keywords = ["villa"]
    guest_house_keywords = ["guest house", "guesthouse", "bed & breakfast", "kost", " kos"]
    homestay_keywords = ["homestay", "home stay"]

    if contains_any(lowered, villa_keywords):
        return "villa"
    if contains_any(lowered, apartment_keywords):
        return "apartment"
    if contains_any(lowered, guest_house_keywords):
        return "guest_house"
    if contains_any(lowered, homestay_keywords):
        return "guest_house"
    if contains_any(lowered, room_keywords):
        return "room_level_listing"
    if raw_type == "vacation rental":
        return "vacation_rental"
    return "hotel"


def amenity_flags(amenities):
    lowered = clean_text(amenities).lower()
    return {
        "has_wifi": contains_any(lowered, ["wi-fi", "wifi"]),
        "has_parking": contains_any(lowered, ["parking", "parkir"]),
        "has_pool": contains_any(lowered, ["pool", "kolam renang"]),
        "has_air_conditioning": contains_any(lowered, ["air conditioning", "ber-ac", "ac"]),
        "has_restaurant": contains_any(lowered, ["restaurant", "restoran"]),
        "has_room_service": contains_any(lowered, ["room service"]),
        "has_laundry": contains_any(lowered, ["laundry"]),
        "wheelchair_accessible": contains_any(lowered, ["accessible", "kursi roda"]),
        "kid_friendly": contains_any(lowered, ["kid-friendly", "cocok untuk anak", "anak"]),
        "pet_friendly": contains_any(lowered, ["pet-friendly", "boleh bawa hewan", "hewan peliharaan"]),
        "smoke_free": contains_any(lowered, ["smoke-free", "bebas asap rokok"]),
        "kitchen_available": contains_any(lowered, ["kitchen", "dapur", "kompor"]),
    }


def parse_images(value):
    images = safe_json_loads(value, [])
    if not isinstance(images, list):
        return "", 0
    urls = [
        clean_text(item.get("original_image"))
        for item in images
        if isinstance(item, dict) and clean_text(item.get("original_image"))
    ]
    return (urls[0] if urls else ""), len(urls)


def parse_star_distribution(value):
    ratings = safe_json_loads(value, [])
    stars = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    if not isinstance(ratings, list):
        return stars
    for item in ratings:
        if not isinstance(item, dict):
            continue
        star = parse_int(item.get("stars"))
        count = parse_int(item.get("count"))
        if pd.isna(star) or pd.isna(count):
            continue
        if int(star) in stars:
            stars[int(star)] += int(count)
    return stars


def parse_review_breakdown(value):
    breakdown = safe_json_loads(value, [])
    if not isinstance(breakdown, list):
        return {
            "review_breakdown_aspect_count": 0,
            "review_breakdown_positive": 0,
            "review_breakdown_negative": 0,
            "review_breakdown_neutral": 0,
            "review_breakdown_top_aspects": "",
        }
    positive = 0
    negative = 0
    neutral = 0
    aspects = []
    for item in breakdown:
        if not isinstance(item, dict):
            continue
        for source_key, accumulator in [
            ("positive", "positive"),
            ("negative", "negative"),
            ("neutral", "neutral"),
        ]:
            parsed = parse_int(item.get(source_key))
            parsed = 0 if pd.isna(parsed) else int(parsed)
            if accumulator == "positive":
                positive += parsed
            elif accumulator == "negative":
                negative += parsed
            else:
                neutral += parsed
        name = clean_text(item.get("name"))
        if name:
            aspects.append(name)
    return {
        "review_breakdown_aspect_count": len(aspects),
        "review_breakdown_positive": positive,
        "review_breakdown_negative": negative,
        "review_breakdown_neutral": neutral,
        "review_breakdown_top_aspects": "; ".join(aspects[:6]),
    }


def review_confidence_label(review_count):
    if pd.isna(review_count):
        return "missing_review_confidence"
    count = float(review_count)
    if count < 30:
        return "low_review_confidence"
    if count < 200:
        return "medium_review_confidence"
    return "high_review_confidence"


def sentiment_label(score):
    if pd.isna(score):
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


def raw_sentiment_from_rating_distribution(stars, overall_rating):
    total = sum(stars.values())
    if total > 0:
        positive = (stars[4] + stars[5]) / total
        neutral = stars[3] / total
        negative = (stars[1] + stars[2]) / total
        return {
            "positive_ratio": positive,
            "neutral_ratio": neutral,
            "negative_ratio": negative,
            "rating_sentiment_score": positive - negative,
            "rating_sentiment_source": "rating_distribution",
            "rating_distribution_total": total,
        }

    if not pd.isna(overall_rating):
        score = max(-1.0, min(1.0, (float(overall_rating) - 3.0) / 2.0))
        return {
            "positive_ratio": pd.NA,
            "neutral_ratio": pd.NA,
            "negative_ratio": pd.NA,
            "rating_sentiment_score": score,
            "rating_sentiment_source": "overall_rating_fallback",
            "rating_distribution_total": pd.NA,
        }

    return {
        "positive_ratio": pd.NA,
        "neutral_ratio": pd.NA,
        "negative_ratio": pd.NA,
        "rating_sentiment_score": pd.NA,
        "rating_sentiment_source": "unavailable",
        "rating_distribution_total": pd.NA,
    }


def quality_score(flags):
    weights = {
        "coordinate_available": 0.12,
        "image_available": 0.14,
        "rating_available": 0.18,
        "price_available": 0.14,
        "amenities_available": 0.14,
        "description_available": 0.08,
        "source_link_available": 0.06,
        "checkin_checkout_available": 0.06,
        "hotel_class_available": 0.04,
        "reviews_breakdown_available": 0.04,
    }
    return round(sum(weight for flag, weight in weights.items() if flags.get(flag)), 4)


def build_canonical(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT, summary_path=DEFAULT_SUMMARY, report_path=DEFAULT_REPORT):
    input_path = Path(input_path)
    output_path = Path(output_path)
    summary_path = Path(summary_path)
    report_path = Path(report_path)

    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    rows = []
    raw_sentiments = []
    review_counts_for_prior = []

    p95_review_count = pd.to_numeric(df["reviews"].replace("", pd.NA), errors="coerce").quantile(0.95)
    if pd.isna(p95_review_count) or p95_review_count <= 0:
        p95_review_count = 1.0

    for index, row in df.iterrows():
        images_primary, image_count = parse_images(row.get("images"))
        stars = parse_star_distribution(row.get("ratings"))
        review_breakdown = parse_review_breakdown(row.get("reviews_breakdown"))

        overall_rating = parse_float(row.get("overall_rating"))
        reviews = parse_int(row.get("reviews"))
        price_lowest = parse_int(row.get("rate_per_night_extracted_lowest"))
        price_before_tax = parse_int(row.get("rate_per_night_extracted_before_taxes_fees"))
        latitude = parse_float(row.get("gps_coordinates_latitude"))
        longitude = parse_float(row.get("gps_coordinates_longitude"))
        hotel_class = parse_int(row.get("extracted_hotel_class"))
        location_rating = parse_float(row.get("location_rating"))

        sentiment = raw_sentiment_from_rating_distribution(stars, overall_rating)
        if not pd.isna(sentiment["rating_sentiment_score"]):
            raw_sentiments.append(float(sentiment["rating_sentiment_score"]))
            effective_n = reviews if not pd.isna(reviews) else sentiment["rating_distribution_total"]
            if not pd.isna(effective_n):
                review_counts_for_prior.append(min(float(effective_n), float(p95_review_count)))

        amenities = clean_text(row.get("amenities"))
        amenity_flag_values = amenity_flags(amenities)
        property_segment = normalize_property_segment(row)

        flags = {
            "coordinate_available": not pd.isna(latitude) and not pd.isna(longitude),
            "image_available": bool(images_primary),
            "rating_available": not pd.isna(overall_rating) and not pd.isna(reviews),
            "price_available": not pd.isna(price_lowest),
            "amenities_available": bool(amenities),
            "description_available": bool(clean_text(row.get("description"))),
            "source_link_available": bool(clean_text(row.get("link"))),
            "checkin_checkout_available": bool(clean_text(row.get("check_in_time"))) and bool(clean_text(row.get("check_out_time"))),
            "hotel_class_available": not pd.isna(hotel_class),
            "reviews_breakdown_available": review_breakdown["review_breakdown_aspect_count"] > 0,
        }

        rows.append({
            "hotel_id": f"HOTEL-{index + 1:03d}",
            "source_property_token": clean_text(row.get("property_token")),
            "source_page_number": clean_text(row.get("page_number")),
            "name": clean_text(row.get("name")),
            "raw_type": clean_text(row.get("type")),
            "property_segment": property_segment,
            "is_room_level_listing": bool_text(property_segment == "room_level_listing"),
            "is_apartment_listing": bool_text(property_segment == "apartment"),
            "is_budget_chain_listing": bool_text(contains_any(row.get("name"), ["oyo", "reddoorz", "collection o", "spot on", "super oyo", "sans"])),
            "latitude": latitude,
            "longitude": longitude,
            "coordinate_available": bool_text(flags["coordinate_available"]),
            "description": clean_text(row.get("description")),
            "source_link": clean_text(row.get("link")),
            "check_in_time": clean_text(row.get("check_in_time")),
            "check_out_time": clean_text(row.get("check_out_time")),
            "price_lowest": price_lowest,
            "price_before_taxes_fees": price_before_tax,
            "price_display": clean_text(row.get("rate_per_night_lowest")),
            "hotel_class": hotel_class,
            "hotel_class_label": clean_text(row.get("hotel_class")),
            "overall_rating": overall_rating,
            "reviews": reviews,
            "location_rating": location_rating,
            "star_5_count": stars[5],
            "star_4_count": stars[4],
            "star_3_count": stars[3],
            "star_2_count": stars[2],
            "star_1_count": stars[1],
            "rating_distribution_total": sentiment["rating_distribution_total"],
            "positive_rating_ratio": sentiment["positive_ratio"],
            "neutral_rating_ratio": sentiment["neutral_ratio"],
            "negative_rating_ratio": sentiment["negative_ratio"],
            "rating_sentiment_score": sentiment["rating_sentiment_score"],
            "adjusted_rating_sentiment_score": pd.NA,
            "rating_sentiment_label": sentiment_label(sentiment["rating_sentiment_score"]),
            "review_confidence_label": review_confidence_label(reviews),
            "review_count_p95": round(float(p95_review_count), 4),
            "rating_sentiment_source": sentiment["rating_sentiment_source"],
            "rating_sentiment_model_version": MODEL_VERSION,
            "amenities": amenities,
            "primary_image_url": images_primary,
            "image_count": image_count,
            "nearby_places_count": len(safe_json_loads(row.get("nearby_places"), [])) if isinstance(safe_json_loads(row.get("nearby_places"), []), list) else 0,
            **review_breakdown,
            **{key: bool_text(value) for key, value in flags.items()},
            **{key: bool_text(value) for key, value in amenity_flag_values.items()},
            "data_quality_score": quality_score(flags),
            "canonical_source": str(input_path).replace("\\", "/"),
            "generated_at": now_iso(),
        })

    canonical = pd.DataFrame(rows)

    available_scores = pd.to_numeric(canonical["rating_sentiment_score"], errors="coerce")
    available_reviews = pd.to_numeric(canonical["reviews"], errors="coerce")
    effective_reviews = available_reviews.fillna(pd.to_numeric(canonical["rating_distribution_total"], errors="coerce")).fillna(0)
    effective_reviews = effective_reviews.clip(upper=float(p95_review_count))

    if available_scores.notna().any():
        weights = effective_reviews.where(effective_reviews.gt(0), 1.0)
        prior = float((available_scores.fillna(0) * weights).sum() / weights[available_scores.notna()].sum())
    else:
        prior = 0.0

    shrinkage_strength = 50.0
    adjusted = []
    for score_value, review_count in zip(available_scores, effective_reviews):
        if pd.isna(score_value):
            adjusted.append(pd.NA)
            continue
        weight = float(review_count) / (float(review_count) + shrinkage_strength)
        adjusted.append(round(weight * float(score_value) + (1 - weight) * prior, 4))

    canonical["rating_sentiment_prior_score"] = round(prior, 4)
    canonical["rating_sentiment_shrinkage_strength"] = shrinkage_strength
    canonical["adjusted_rating_sentiment_score"] = adjusted
    canonical["adjusted_rating_sentiment_label"] = canonical["adjusted_rating_sentiment_score"].apply(sentiment_label)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_csv(output_path, index=False)

    summary = {
        "generated_at": now_iso(),
        "input_path": str(input_path),
        "output_path": str(output_path),
        "row_count": int(len(canonical)),
        "column_count": int(len(canonical.columns)),
        "property_segment_counts": canonical["property_segment"].value_counts(dropna=False).to_dict(),
        "readiness": {
            "strong_core_ready": int(
                (
                    canonical["coordinate_available"].eq("True")
                    & canonical["image_available"].eq("True")
                    & canonical["rating_available"].eq("True")
                    & canonical["price_available"].eq("True")
                    & canonical["amenities_available"].eq("True")
                ).sum()
            ),
            "usable_without_price_required": int(
                (
                    canonical["coordinate_available"].eq("True")
                    & canonical["image_available"].eq("True")
                    & canonical["rating_available"].eq("True")
                    & canonical["amenities_available"].eq("True")
                ).sum()
            ),
            "minimal_usable": int(
                (
                    canonical["coordinate_available"].eq("True")
                    & canonical["image_available"].eq("True")
                    & (
                        canonical["rating_available"].eq("True")
                        | canonical["price_available"].eq("True")
                        | canonical["amenities_available"].eq("True")
                    )
                ).sum()
            ),
        },
        "quality_flags": {
            flag: int(canonical[flag].eq("True").sum())
            for flag in [
                "rating_available",
                "price_available",
                "amenities_available",
                "image_available",
                "description_available",
                "source_link_available",
                "reviews_breakdown_available",
            ]
        },
        "review_confidence_counts": canonical["review_confidence_label"].value_counts(dropna=False).to_dict(),
        "sentiment_source_counts": canonical["rating_sentiment_source"].value_counts(dropna=False).to_dict(),
        "rating_sentiment_prior_score": round(prior, 4),
        "review_count_p95": round(float(p95_review_count), 4),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(report_path, canonical, summary)
    return summary


def write_report(report_path, canonical, summary):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Hotel Canonical Pipeline - 2026-05-29",
        "",
        f"Generated at: `{summary['generated_at']}`",
        f"Input: `{summary['input_path']}`",
        f"Output: `{summary['output_path']}`",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary['row_count']}`",
        f"- Columns: `{summary['column_count']}`",
        f"- Rating sentiment model version: `{MODEL_VERSION}`",
        f"- Rating sentiment prior score: `{summary['rating_sentiment_prior_score']}`",
        f"- Review count p95 cap: `{summary['review_count_p95']}`",
        "",
        "## Property Segments",
        "",
        "| Segment | Count |",
        "| --- | ---: |",
    ]
    for key, value in summary["property_segment_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Quality Flags", "", "| Flag | Count |", "| --- | ---: |"])
    for key, value in summary["quality_flags"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Readiness", "", "| Definition | Count |", "| --- | ---: |"])
    for key, value in summary["readiness"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Review Confidence", "", "| Label | Count |", "| --- | ---: |"])
    for key, value in summary["review_confidence_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Rating Sentiment Source", "", "| Source | Count |", "| --- | ---: |"])
    for key, value in summary["sentiment_source_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Sentiment here is `rating-derived sentiment`, not NLP over raw comments.",
            "- `ratings` distribution is preferred when available.",
            "- `overall_rating` is used only as fallback when star distribution is missing.",
            "- Bayesian shrinkage is applied using p95 review count cap so very high review-count outliers do not dominate.",
            "- Mixed entities are retained and labeled through `property_segment` instead of being removed.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()
    summary = build_canonical(args.input, args.output, args.summary, args.report)
    print("Hotel canonical dataset built")
    print(f"rows={summary['row_count']}")
    print(f"columns={summary['column_count']}")
    print(f"output={summary['output_path']}")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
