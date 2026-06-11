import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"

DEFAULT_DATASET = PENGINAPAN_WORKSPACE / "02_Curated" / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv"
DEFAULT_JSON = PENGINAPAN_WORKSPACE / "02_Curated" / "hotel_canonical_validation_results_2026-05-29.json"
DEFAULT_REPORT = PENGINAPAN_WORKSPACE / "04_Dokumentasi" / "HOTEL_VALIDATION_REPORT_2026-05-29.md"

SCHEMA_VERSION = "muterbandung.hotel_canonical_validation.v1"

REQUIRED_COLUMNS = [
    "hotel_id",
    "source_property_token",
    "name",
    "raw_type",
    "property_segment",
    "latitude",
    "longitude",
    "coordinate_available",
    "description",
    "source_link",
    "check_in_time",
    "check_out_time",
    "price_lowest",
    "hotel_class",
    "overall_rating",
    "reviews",
    "location_rating",
    "star_5_count",
    "star_4_count",
    "star_3_count",
    "star_2_count",
    "star_1_count",
    "positive_rating_ratio",
    "neutral_rating_ratio",
    "negative_rating_ratio",
    "rating_sentiment_score",
    "adjusted_rating_sentiment_score",
    "rating_sentiment_label",
    "adjusted_rating_sentiment_label",
    "review_confidence_label",
    "rating_sentiment_source",
    "rating_sentiment_model_version",
    "amenities",
    "primary_image_url",
    "image_count",
    "rating_available",
    "price_available",
    "amenities_available",
    "image_available",
    "description_available",
    "source_link_available",
    "data_quality_score",
]

BOOL_COLUMNS = [
    "is_room_level_listing",
    "is_apartment_listing",
    "is_budget_chain_listing",
    "coordinate_available",
    "rating_available",
    "price_available",
    "amenities_available",
    "image_available",
    "description_available",
    "source_link_available",
    "checkin_checkout_available",
    "hotel_class_available",
    "reviews_breakdown_available",
    "has_wifi",
    "has_parking",
    "has_pool",
    "has_air_conditioning",
    "has_restaurant",
    "has_room_service",
    "has_laundry",
    "wheelchair_accessible",
    "kid_friendly",
    "pet_friendly",
    "smoke_free",
    "kitchen_available",
]

PROPERTY_SEGMENTS = {
    "hotel",
    "guest_house",
    "villa",
    "apartment",
    "vacation_rental",
    "room_level_listing",
}

CONFIDENCE_LABELS = {
    "missing_review_confidence",
    "low_review_confidence",
    "medium_review_confidence",
    "high_review_confidence",
}

SENTIMENT_SOURCES = {"rating_distribution", "overall_rating_fallback", "unavailable"}


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    count: int
    field: str
    sample_rows: list


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def text(df, col):
    if col not in df.columns:
        return pd.Series([""] * len(df), index=df.index)
    return df[col].fillna("").astype(str).str.strip()


def numeric(df, col):
    if col not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")
    return pd.to_numeric(df[col].replace("", pd.NA), errors="coerce")


def sample_rows(df, mask):
    rows = []
    for idx, row in df[mask].head(10).iterrows():
        rows.append({
            "row_number": int(idx) + 2,
            "hotel_id": row.get("hotel_id", ""),
            "name": row.get("name", ""),
        })
    return rows


def add_issue(issues, df, severity, code, message, mask, field):
    mask = mask.fillna(False) if hasattr(mask, "fillna") else mask
    count = int(mask.sum())
    if count:
        issues.append(Issue(severity, code, message, count, field, sample_rows(df, mask)))


def validate(dataset_path=DEFAULT_DATASET, json_output=DEFAULT_JSON, report_output=DEFAULT_REPORT):
    dataset_path = Path(dataset_path)
    json_output = Path(json_output)
    report_output = Path(report_output)

    df = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    issues = []

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        issues.append(Issue(
            "ERROR",
            "E_REQUIRED_COLUMNS_MISSING",
            "Required hotel canonical columns are missing.",
            len(missing_columns),
            ",".join(missing_columns),
            [],
        ))

    if "hotel_id" in df.columns:
        add_issue(
            issues,
            df,
            "ERROR",
            "E_HOTEL_ID_DUPLICATE",
            "hotel_id must be unique.",
            text(df, "hotel_id").duplicated(keep=False),
            "hotel_id",
        )
        add_issue(
            issues,
            df,
            "ERROR",
            "E_HOTEL_ID_MISSING",
            "hotel_id must not be blank.",
            text(df, "hotel_id").eq(""),
            "hotel_id",
        )

    add_issue(
        issues,
        df,
        "ERROR",
        "E_NAME_MISSING",
        "Hotel/property name must not be blank.",
        text(df, "name").eq(""),
        "name",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_PROPERTY_SEGMENT_INVALID",
        f"property_segment must be one of: {', '.join(sorted(PROPERTY_SEGMENTS))}.",
        ~text(df, "property_segment").isin(PROPERTY_SEGMENTS),
        "property_segment",
    )

    for col in BOOL_COLUMNS:
        if col in df.columns:
            add_issue(
                issues,
                df,
                "ERROR",
                "E_BOOLEAN_INVALID",
                f"{col} must be True or False.",
                ~text(df, col).isin({"True", "False"}),
                col,
            )

    lat = numeric(df, "latitude")
    lon = numeric(df, "longitude")
    add_issue(
        issues,
        df,
        "ERROR",
        "E_COORDINATE_MISSING",
        "Latitude/longitude must be numeric.",
        lat.isna() | lon.isna(),
        "latitude,longitude",
    )
    add_issue(
        issues,
        df,
        "WARNING",
        "W_COORDINATE_OUTSIDE_BANDUNG_RAYA_BROAD_RANGE",
        "Coordinate is outside broad Bandung Raya operating range.",
        lat.notna() & lon.notna() & ~((lat >= -7.35) & (lat <= -6.50) & (lon >= 107.20) & (lon <= 108.00)),
        "latitude,longitude",
    )

    rating = numeric(df, "overall_rating")
    reviews = numeric(df, "reviews")
    price = numeric(df, "price_lowest")
    location_rating = numeric(df, "location_rating")
    quality = numeric(df, "data_quality_score")
    sentiment = numeric(df, "rating_sentiment_score")
    adjusted = numeric(df, "adjusted_rating_sentiment_score")

    add_issue(
        issues,
        df,
        "ERROR",
        "E_RATING_OUT_OF_RANGE",
        "overall_rating must be between 0 and 5 when present.",
        rating.notna() & ~((rating >= 0) & (rating <= 5)),
        "overall_rating",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_LOCATION_RATING_OUT_OF_RANGE",
        "location_rating must be between 0 and 5 when present.",
        location_rating.notna() & ~((location_rating >= 0) & (location_rating <= 5)),
        "location_rating",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_REVIEWS_NEGATIVE",
        "reviews must not be negative.",
        reviews.notna() & (reviews < 0),
        "reviews",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_PRICE_NEGATIVE",
        "price_lowest must not be negative.",
        price.notna() & (price < 0),
        "price_lowest",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_SENTIMENT_SCORE_OUT_OF_RANGE",
        "rating_sentiment_score must be between -1 and 1 when present.",
        sentiment.notna() & ~((sentiment >= -1) & (sentiment <= 1)),
        "rating_sentiment_score",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_ADJUSTED_SENTIMENT_SCORE_OUT_OF_RANGE",
        "adjusted_rating_sentiment_score must be between -1 and 1 when present.",
        adjusted.notna() & ~((adjusted >= -1) & (adjusted <= 1)),
        "adjusted_rating_sentiment_score",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_DATA_QUALITY_SCORE_OUT_OF_RANGE",
        "data_quality_score must be between 0 and 1.",
        quality.isna() | ~((quality >= 0) & (quality <= 1)),
        "data_quality_score",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_REVIEW_CONFIDENCE_INVALID",
        f"review_confidence_label must be one of: {', '.join(sorted(CONFIDENCE_LABELS))}.",
        ~text(df, "review_confidence_label").isin(CONFIDENCE_LABELS),
        "review_confidence_label",
    )
    add_issue(
        issues,
        df,
        "ERROR",
        "E_SENTIMENT_SOURCE_INVALID",
        f"rating_sentiment_source must be one of: {', '.join(sorted(SENTIMENT_SOURCES))}.",
        ~text(df, "rating_sentiment_source").isin(SENTIMENT_SOURCES),
        "rating_sentiment_source",
    )

    add_issue(
        issues,
        df,
        "WARNING",
        "W_RATING_MISSING",
        "Rows without rating/review count cannot be ranked by rating confidence.",
        text(df, "rating_available").eq("False"),
        "rating_available",
    )
    add_issue(
        issues,
        df,
        "WARNING",
        "W_PRICE_MISSING",
        "Rows without price should not be used for budget claims.",
        text(df, "price_available").eq("False"),
        "price_available",
    )
    add_issue(
        issues,
        df,
        "WARNING",
        "W_AMENITIES_MISSING",
        "Rows without amenities require conservative LLM wording.",
        text(df, "amenities_available").eq("False"),
        "amenities_available",
    )
    add_issue(
        issues,
        df,
        "WARNING",
        "W_DESCRIPTION_MISSING",
        "Rows without description need generated/curated description before rich LLM explanation.",
        text(df, "description_available").eq("False"),
        "description_available",
    )
    add_issue(
        issues,
        df,
        "WARNING",
        "W_IMAGE_MISSING",
        "Rows without primary image should not be used for visual cards.",
        text(df, "image_available").eq("False"),
        "image_available",
    )
    add_issue(
        issues,
        df,
        "WARNING",
        "W_LOW_REVIEW_CONFIDENCE",
        "Low/missing review confidence rows need shrinkage and cautious explanations.",
        text(df, "review_confidence_label").isin({"missing_review_confidence", "low_review_confidence"}),
        "review_confidence_label",
    )

    error_count = sum(issue.count for issue in issues if issue.severity == "ERROR")
    warning_count = sum(issue.count for issue in issues if issue.severity == "WARNING")
    gate_status = "PASS" if error_count == 0 and warning_count == 0 else "PASS_WITH_WARNINGS" if error_count == 0 else "FAIL"

    summary = {
        "schema_version": SCHEMA_VERSION,
        "dataset_path": str(dataset_path),
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "unique_hotel_id_count": int(text(df, "hotel_id").nunique()) if "hotel_id" in df.columns else 0,
        "error_count": int(error_count),
        "warning_count": int(warning_count),
        "issue_count": len(issues),
        "gate_status": gate_status,
        "property_segment_counts": text(df, "property_segment").value_counts(dropna=False).to_dict(),
        "review_confidence_counts": text(df, "review_confidence_label").value_counts(dropna=False).to_dict(),
        "quality_flag_counts": {
            flag: int(text(df, flag).eq("True").sum())
            for flag in [
                "rating_available",
                "price_available",
                "amenities_available",
                "image_available",
                "description_available",
                "source_link_available",
                "reviews_breakdown_available",
            ]
            if flag in df.columns
        },
        "validated_at": now_iso(),
    }
    payload = {
        "summary": summary,
        "issues": [asdict(issue) for issue in issues],
    }
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(report_output, summary, issues)
    return payload


def write_report(report_output, summary, issues):
    report_output = Path(report_output)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Hotel Validation Report - 2026-05-29",
        "",
        f"Generated at: `{summary['validated_at']}`",
        f"Dataset: `{summary['dataset_path']}`",
        f"Gate: `{summary['gate_status']}`",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary['row_count']}`",
        f"- Columns: `{summary['column_count']}`",
        f"- Unique hotel IDs: `{summary['unique_hotel_id_count']}`",
        f"- Errors: `{summary['error_count']}`",
        f"- Warnings: `{summary['warning_count']}`",
        "",
        "## Issues",
        "",
        "| Severity | Code | Field | Count | Message |",
        "| --- | --- | --- | ---: | --- |",
    ]
    if issues:
        for issue in issues:
            lines.append(f"| {issue.severity} | `{issue.code}` | `{issue.field}` | {issue.count} | {issue.message} |")
    else:
        lines.append("| - | - | - | 0 | No issues |")

    lines.extend(["", "## Property Segments", "", "| Segment | Count |", "| --- | ---: |"])
    for key, value in summary["property_segment_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Review Confidence", "", "| Label | Count |", "| --- | ---: |"])
    for key, value in summary["review_confidence_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Quality Flags", "", "| Flag | Count |", "| --- | ---: |"])
    for key, value in summary["quality_flag_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON))
    parser.add_argument("--report-output", default=str(DEFAULT_REPORT))
    args = parser.parse_args()
    payload = validate(args.dataset, args.json_output, args.report_output)
    summary = payload["summary"]
    print("Hotel canonical validation")
    print(f"dataset={summary['dataset_path']}")
    print(f"gate={summary['gate_status']}")
    print(f"rows={summary['row_count']}")
    print(f"errors={summary['error_count']}")
    print(f"warnings={summary['warning_count']}")
    print(f"json={args.json_output}")
    print(f"report={args.report_output}")


if __name__ == "__main__":
    main()
