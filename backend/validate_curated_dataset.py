import argparse
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DEFAULT_DATASET_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
DEFAULT_JSON_OUTPUT = Path("Wisata_Workspace/01_Dataset/3_Curated/data_validation_results.json")
DEFAULT_MARKDOWN_OUTPUT = Path("Wisata_Workspace/03_Dokumentasi/DATA_VALIDATION_REPORT_2026-05-25.md")

SCHEMA_VERSION = "muterbandung.data_validation.v1"
VALID_AVAILABLE_SENTIMENT_PROVENANCE = {
    ("tfidf_linearsvc", "run_nlp_pipeline_v2"),
    ("google_maps_stars_fallback", "compass_manual_accepted_2026-06-09"),
}

REQUIRED_COLUMNS = [
    "location_id",
    "location_name",
    "category",
    "multi_labels",
    "latitude",
    "longitude",
    "price_min",
    "price_max",
    "price_type",
    "jam_buka_weekday",
    "jam_tutup_weekday",
    "jam_buka_weekend",
    "jam_tutup_weekend",
    "estimasi_durasi_menit",
    "deskripsi_google",
    "tags_sintetis",
    "avg_rating",
    "total_ulasan",
    "final_primary_intent",
    "final_core_labels",
    "final_secondary_labels",
    "final_avoid_labels",
    "curation_action",
    "display_status",
    "is_active_verified",
    "price_verified",
    "night_verified",
    "indoor_verified",
    "child_friendly_verified",
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
    "open_24h_verified",
    "crowd_level",
    "shopping_subtype",
    "coordinate_verified",
    "safety_verified",
    "sentiment_score",
    "sentiment_model_source",
    "sentiment_model_version",
    "sentiment_available",
    "media_available",
    "media_image_url",
    "media_destination_url",
    "media_website",
    "media_source",
    "media_place_id",
    "media_match_score",
    "media_match_method",
    "media_audit_status",
]

ACTIVE_REQUIRED_TEXT_COLUMNS = [
    "location_name",
    "category",
    "deskripsi_google",
    "tags_sintetis",
    "final_primary_intent",
    "final_core_labels",
    "price_type",
]

BOOL_COLUMNS = [
    "price_verified",
    "night_verified",
    "indoor_verified",
    "child_friendly_verified",
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
    "open_24h_verified",
    "coordinate_verified",
    "safety_verified",
    "sentiment_available",
    "media_available",
]

STATUS_VALUES = {"active_candidate", "exclude_scope", "status_uncertain", "temporarily_hidden"}
CURATION_ACTION_VALUES = {"keep", "remove", "needs_review", "hide_temporarily"}
STATUS_ACTION_MAP = {
    "active_candidate": "keep",
    "exclude_scope": "remove",
    "status_uncertain": "needs_review",
    "temporarily_hidden": "hide_temporarily",
}
PRICE_TYPES = {"Gratis", "Per Orang", "Berbayar"}
CROWD_LEVELS = {"unknown", "low", "medium", "high"}
MEDIA_AUDIT_VALUES = {"accepted", "manual_accepted", "missing"}
MEDIA_AVAILABLE_AUDIT_VALUES = {"accepted", "manual_accepted"}
TIME_FIELDS = [
    "jam_buka",
    "jam_tutup",
    "jam_buka_weekday",
    "jam_tutup_weekday",
    "jam_buka_weekend",
    "jam_tutup_weekend",
]


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    count: int
    field: str | None = None
    sample_rows: list[dict] | None = None


class DatasetValidator:
    def __init__(self, df: pd.DataFrame, dataset_path: str | Path):
        self.df = df
        self.dataset_path = str(dataset_path)
        self.issues: list[ValidationIssue] = []
        self.stats: dict = {}

    def has_columns(self, *columns):
        return all(column in self.df.columns for column in columns)

    def text(self, column):
        return self.df[column].fillna("").astype(str).str.strip()

    def lower_text(self, column):
        return self.text(column).str.lower()

    def is_blank(self, column):
        return self.text(column).eq("")

    def sample_rows(self, mask, limit=10):
        samples = []
        if isinstance(mask, pd.Series):
            indexes = self.df.index[mask.fillna(False)].tolist()[:limit]
        else:
            indexes = []
        for index in indexes:
            row = self.df.loc[index]
            samples.append({
                "row_number": int(index) + 2,
                "location_id": str(row.get("location_id", "")).strip(),
                "location_name": str(row.get("location_name", "")).strip(),
            })
        return samples

    def add_issue(self, severity, code, message, mask=None, field=None, count=None, sample_rows=None):
        if mask is not None:
            count = int(mask.fillna(False).sum())
            if count == 0:
                return
            sample_rows = self.sample_rows(mask)
        elif count is None:
            count = 1
        if count == 0:
            return
        self.issues.append(ValidationIssue(
            severity=severity,
            code=code,
            message=message,
            count=int(count),
            field=field,
            sample_rows=sample_rows or [],
        ))

    def numeric(self, column):
        raw = self.text(column)
        parsed = pd.to_numeric(raw.replace("", pd.NA), errors="coerce")
        invalid = raw.ne("") & parsed.isna()
        return parsed, invalid

    def boolean_mask(self, column, allow_blank=False):
        raw = self.lower_text(column)
        allowed = {"true", "false"}
        if allow_blank:
            allowed.add("")
        return ~raw.isin(allowed)

    def active_mask(self):
        if "display_status" not in self.df.columns:
            return pd.Series(False, index=self.df.index)
        return self.text("display_status").eq("active_candidate")

    def validate(self):
        self.validate_schema()
        if any(issue.code == "E_SCHEMA_MISSING_COLUMNS" for issue in self.issues):
            self.collect_summary()
            return self.result()

        self.validate_identity()
        self.validate_status()
        self.validate_core_text()
        self.validate_numeric_fields()
        self.validate_price_contract()
        self.validate_time_contract()
        self.validate_boolean_and_verification_flags()
        self.validate_sentiment_contract()
        self.validate_media_contract()
        self.collect_summary()
        return self.result()

    def validate_schema(self):
        duplicate_columns = pd.Series(self.df.columns)[pd.Series(self.df.columns).duplicated()].tolist()
        if duplicate_columns:
            self.add_issue(
                "ERROR",
                "E_SCHEMA_DUPLICATE_COLUMNS",
                f"Duplicate columns found: {', '.join(duplicate_columns)}.",
                count=len(duplicate_columns),
            )

        missing = [column for column in REQUIRED_COLUMNS if column not in self.df.columns]
        if missing:
            self.add_issue(
                "ERROR",
                "E_SCHEMA_MISSING_COLUMNS",
                f"Required columns missing: {', '.join(missing)}.",
                count=len(missing),
            )

    def validate_identity(self):
        self.add_issue(
            "ERROR",
            "E_EMPTY_DATASET",
            "Dataset has no rows.",
            count=1 if len(self.df) == 0 else 0,
        )
        self.add_issue(
            "ERROR",
            "E_LOCATION_ID_MISSING",
            "location_id is required for every row.",
            mask=self.is_blank("location_id"),
            field="location_id",
        )
        duplicate_mask = self.text("location_id").duplicated(keep=False) & ~self.is_blank("location_id")
        self.add_issue(
            "ERROR",
            "E_LOCATION_ID_DUPLICATE",
            "location_id must be unique.",
            mask=duplicate_mask,
            field="location_id",
        )
        active_count = int(self.active_mask().sum())
        self.add_issue(
            "ERROR",
            "E_NO_ACTIVE_CANDIDATES",
            "Dataset must contain active candidates.",
            count=1 if active_count == 0 else 0,
            field="display_status",
        )

    def validate_status(self):
        display_status = self.text("display_status")
        invalid_status = ~display_status.isin(STATUS_VALUES)
        self.add_issue(
            "ERROR",
            "E_DISPLAY_STATUS_INVALID",
            f"display_status must be one of: {', '.join(sorted(STATUS_VALUES))}.",
            mask=invalid_status,
            field="display_status",
        )

        curation_action = self.text("curation_action")
        invalid_action = ~curation_action.isin(CURATION_ACTION_VALUES)
        self.add_issue(
            "ERROR",
            "E_CURATION_ACTION_INVALID",
            f"curation_action must be one of: {', '.join(sorted(CURATION_ACTION_VALUES))}.",
            mask=invalid_action,
            field="curation_action",
        )

        expected_action = display_status.map(STATUS_ACTION_MAP).fillna("")
        mismatch = display_status.isin(STATUS_VALUES) & curation_action.isin(CURATION_ACTION_VALUES) & curation_action.ne(expected_action)
        self.add_issue(
            "ERROR",
            "E_STATUS_ACTION_MISMATCH",
            "display_status and curation_action must stay semantically aligned.",
            mask=mismatch,
            field="display_status,curation_action",
        )

    def validate_core_text(self):
        active = self.active_mask()
        for column in ACTIVE_REQUIRED_TEXT_COLUMNS:
            mask = active & self.is_blank(column)
            self.add_issue(
                "ERROR",
                "E_ACTIVE_CORE_TEXT_MISSING",
                f"Active candidates must have {column}.",
                mask=mask,
                field=column,
            )

        short_description = active & self.text("deskripsi_google").ne("") & self.text("deskripsi_google").str.len().lt(20)
        self.add_issue(
            "WARNING",
            "W_DESCRIPTION_TOO_SHORT",
            "Some active descriptions are very short; LLM should not over-explain them.",
            mask=short_description,
            field="deskripsi_google",
        )

        if "label_scores_json" in self.df.columns:
            invalid_json_indexes = []
            for index, value in self.text("label_scores_json").items():
                if not value:
                    continue
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    invalid_json_indexes.append(index)
            invalid_json = self.df.index.to_series().isin(invalid_json_indexes)
            self.add_issue(
                "ERROR",
                "E_LABEL_SCORES_JSON_INVALID",
                "label_scores_json must be valid JSON when present.",
                mask=invalid_json,
                field="label_scores_json",
            )

    def validate_numeric_fields(self):
        numeric_specs = {
            "latitude": (-90.0, 90.0, False),
            "longitude": (-180.0, 180.0, False),
            "price_min": (0.0, None, False),
            "price_max": (0.0, None, False),
            "avg_rating": (0.0, 5.0, True),
            "total_ulasan": (0.0, None, False),
            "sentiment_score": (-1.0, 1.0, False),
            "estimasi_durasi_menit": (1.0, 1440.0, False),
            "label_confidence": (0.0, 1.0, True),
            "manual_review_confidence": (0.0, 1.0, True),
            "media_match_score": (0.0, 1.0, True),
            "distance_from_alun_alun_km": (0.0, None, True),
        }
        for column, (min_value, max_value, allow_blank) in numeric_specs.items():
            if column not in self.df.columns:
                continue
            values, invalid = self.numeric(column)
            if allow_blank:
                invalid = invalid & ~self.is_blank(column)
            self.add_issue(
                "ERROR",
                "E_NUMERIC_INVALID",
                f"{column} must be numeric.",
                mask=invalid,
                field=column,
            )
            if min_value is not None:
                self.add_issue(
                    "ERROR",
                    "E_NUMERIC_BELOW_MIN",
                    f"{column} must be greater than or equal to {min_value}.",
                    mask=values.notna() & values.lt(min_value),
                    field=column,
                )
            if max_value is not None:
                self.add_issue(
                    "ERROR",
                    "E_NUMERIC_ABOVE_MAX",
                    f"{column} must be less than or equal to {max_value}.",
                    mask=values.notna() & values.gt(max_value),
                    field=column,
                )

        lat, _ = self.numeric("latitude")
        lon, _ = self.numeric("longitude")
        outside_operating_region = lat.notna() & lon.notna() & ~(
            lat.between(-7.6, -6.4) & lon.between(107.0, 108.3)
        )
        self.add_issue(
            "WARNING",
            "W_COORDINATE_OUTSIDE_OPERATING_REGION",
            "Coordinate is outside the broad Bandung Raya/Sumedang operating envelope.",
            mask=outside_operating_region,
            field="latitude,longitude",
        )

        active_rating_missing = self.active_mask() & self.is_blank("avg_rating")
        self.add_issue(
            "WARNING",
            "W_ACTIVE_RATING_MISSING",
            "Active candidates with missing avg_rating rely on runtime median fallback.",
            mask=active_rating_missing,
            field="avg_rating",
        )

    def validate_price_contract(self):
        price_type = self.text("price_type")
        invalid_price_type = ~price_type.isin(PRICE_TYPES)
        self.add_issue(
            "ERROR",
            "E_PRICE_TYPE_INVALID",
            f"price_type must be one of: {', '.join(sorted(PRICE_TYPES))}.",
            mask=invalid_price_type,
            field="price_type",
        )

        price_min, _ = self.numeric("price_min")
        price_max, _ = self.numeric("price_max")
        self.add_issue(
            "ERROR",
            "E_PRICE_MIN_GT_MAX",
            "price_min must not exceed price_max.",
            mask=price_min.notna() & price_max.notna() & price_min.gt(price_max),
            field="price_min,price_max",
        )
        self.add_issue(
            "ERROR",
            "E_PRICE_FREE_INCONSISTENT",
            "Rows marked Gratis must have price_min=0 and price_max=0.",
            mask=price_type.eq("Gratis") & (price_min.ne(0) | price_max.ne(0)),
            field="price_type,price_min,price_max",
        )
        self.add_issue(
            "WARNING",
            "W_ZERO_PRICE_NOT_MARKED_FREE",
            "Rows with zero max price should usually be marked Gratis.",
            mask=price_type.ne("Gratis") & price_max.eq(0),
            field="price_type,price_max",
        )

    def valid_time_mask(self, column):
        value = self.text(column)
        time_pattern = r"^(?:[01]?\d|2[0-3]):[0-5]\d$"
        return value.eq("") | value.eq("Tutup") | value.str.match(time_pattern)

    def validate_time_pair(self, open_column, close_column, severity_for_missing="WARNING"):
        open_value = self.text(open_column)
        close_value = self.text(close_column)
        one_missing = open_value.eq("") ^ close_value.eq("")
        self.add_issue(
            severity_for_missing,
            "W_TIME_PAIR_INCOMPLETE" if severity_for_missing == "WARNING" else "E_TIME_PAIR_INCOMPLETE",
            f"{open_column} and {close_column} should be filled together.",
            mask=one_missing,
            field=f"{open_column},{close_column}",
        )
        closed_mismatch = (open_value.eq("Tutup") ^ close_value.eq("Tutup"))
        self.add_issue(
            "ERROR",
            "E_TIME_CLOSED_MISMATCH",
            f"{open_column} and {close_column} must both be Tutup when closed.",
            mask=closed_mismatch,
            field=f"{open_column},{close_column}",
        )

    def validate_time_contract(self):
        for column in TIME_FIELDS:
            if column not in self.df.columns:
                continue
            self.add_issue(
                "ERROR",
                "E_TIME_FORMAT_INVALID",
                f"{column} must be blank, Tutup, or HH:MM.",
                mask=~self.valid_time_mask(column),
                field=column,
            )

        for open_column, close_column in [
            ("jam_buka", "jam_tutup"),
            ("jam_buka_weekday", "jam_tutup_weekday"),
            ("jam_buka_weekend", "jam_tutup_weekend"),
        ]:
            if self.has_columns(open_column, close_column):
                self.validate_time_pair(open_column, close_column)

        active = self.active_mask()
        active_weekday_missing = active & (self.is_blank("jam_buka_weekday") | self.is_blank("jam_tutup_weekday"))
        active_weekend_missing = active & (self.is_blank("jam_buka_weekend") | self.is_blank("jam_tutup_weekend"))
        self.add_issue(
            "WARNING",
            "W_ACTIVE_WEEKDAY_HOURS_MISSING",
            "Active candidates missing weekday hours need caveats in UI/LLM output.",
            mask=active_weekday_missing,
            field="jam_buka_weekday,jam_tutup_weekday",
        )
        self.add_issue(
            "WARNING",
            "W_ACTIVE_WEEKEND_HOURS_MISSING",
            "Active candidates missing weekend hours need caveats in UI/LLM output.",
            mask=active_weekend_missing,
            field="jam_buka_weekend,jam_tutup_weekend",
        )

        open_24h = self.lower_text("open_24h_verified").eq("true")
        looks_24h = (
            self.text("jam_buka_weekday").eq("00:00")
            & self.text("jam_tutup_weekday").eq("23:59")
            & self.text("jam_buka_weekend").eq("00:00")
            & self.text("jam_tutup_weekend").eq("23:59")
        )
        self.add_issue(
            "WARNING",
            "W_OPEN_24H_FLAG_HOURS_MISMATCH",
            "open_24h_verified=True should align with 00:00-23:59 weekday/weekend hours.",
            mask=open_24h & ~looks_24h,
            field="open_24h_verified",
        )

    def validate_boolean_and_verification_flags(self):
        for column in BOOL_COLUMNS:
            if column not in self.df.columns:
                continue
            self.add_issue(
                "ERROR",
                "E_BOOLEAN_INVALID",
                f"{column} must be True or False.",
                mask=self.boolean_mask(column),
                field=column,
            )

        self.add_issue(
            "ERROR",
            "E_IS_ACTIVE_VERIFIED_INVALID",
            "is_active_verified must be True, False, or blank.",
            mask=self.boolean_mask("is_active_verified", allow_blank=True),
            field="is_active_verified",
        )

        active = self.active_mask()
        missing_active_verification = active & self.is_blank("is_active_verified")
        self.add_issue(
            "WARNING",
            "W_ACTIVE_VERIFICATION_MISSING",
            "Active candidates missing is_active_verified must not be described as verified.",
            mask=missing_active_verification,
            field="is_active_verified",
        )

        coordinate_unverified = active & self.lower_text("coordinate_verified").eq("false")
        self.add_issue(
            "WARNING",
            "W_ACTIVE_COORDINATE_UNVERIFIED",
            "Active candidates with coordinate_verified=False should be treated carefully for distance claims.",
            mask=coordinate_unverified,
            field="coordinate_verified",
        )

        facility_columns = [
            "parking_verified",
            "wheelchair_accessible_verified",
            "toilet_verified",
            "mushola_verified",
            "pet_friendly_verified",
        ]
        facility_verified_any = pd.Series(False, index=self.df.index)
        for column in facility_columns:
            facility_verified_any = facility_verified_any | self.lower_text(column).eq("true")
        self.add_issue(
            "WARNING",
            "W_ACTIVE_FACILITY_VERIFICATION_SPARSE",
            "Active candidates with no verified facility flags require conservative LLM wording.",
            mask=active & ~facility_verified_any,
            field="facility_verified_flags",
        )

        invalid_crowd = ~self.lower_text("crowd_level").isin(CROWD_LEVELS)
        self.add_issue(
            "ERROR",
            "E_CROWD_LEVEL_INVALID",
            f"crowd_level must be one of: {', '.join(sorted(CROWD_LEVELS))}.",
            mask=invalid_crowd,
            field="crowd_level",
        )

    def validate_sentiment_contract(self):
        sentiment_available = self.lower_text("sentiment_available")
        source = self.text("sentiment_model_source")
        version = self.text("sentiment_model_version")
        total_reviews, _ = self.numeric("total_ulasan")

        available = sentiment_available.eq("true")
        unavailable = sentiment_available.eq("false")
        self.add_issue(
            "ERROR",
            "E_SENTIMENT_AVAILABLE_INVALID",
            "sentiment_available must be True or False.",
            mask=~sentiment_available.isin({"true", "false"}),
            field="sentiment_available",
        )
        self.add_issue(
            "ERROR",
            "E_SENTIMENT_AVAILABLE_PROVENANCE_INVALID",
            "Available sentiment must use approved NLP or Google Maps stars fallback provenance.",
            mask=available & ~pd.Series(
                list(zip(source, version)),
                index=self.df.index,
            ).isin(VALID_AVAILABLE_SENTIMENT_PROVENANCE),
            field="sentiment_model_source,sentiment_model_version",
        )
        self.add_issue(
            "ERROR",
            "E_SENTIMENT_UNAVAILABLE_PROVENANCE_INVALID",
            "Unavailable sentiment must use source=unavailable and blank version.",
            mask=unavailable & (source.ne("unavailable") | version.ne("")),
            field="sentiment_model_source,sentiment_model_version",
        )
        self.add_issue(
            "WARNING",
            "W_SENTIMENT_AVAILABLE_WITHOUT_REVIEWS",
            "Rows with sentiment_available=True should have total_ulasan > 0.",
            mask=available & total_reviews.fillna(0).le(0),
            field="sentiment_available,total_ulasan",
        )
        self.add_issue(
            "WARNING",
            "W_ACTIVE_SENTIMENT_UNAVAILABLE",
            "Active candidates with unavailable sentiment need neutral/caveated LLM wording.",
            mask=self.active_mask() & unavailable,
            field="sentiment_available",
        )

    def validate_media_contract(self):
        media_available = self.lower_text("media_available")
        audit_status = self.text("media_audit_status")
        image_url = self.text("media_image_url")
        destination_url = self.text("media_destination_url")
        website = self.text("media_website")

        available = media_available.eq("true")
        unavailable = media_available.eq("false")
        self.add_issue(
            "ERROR",
            "E_MEDIA_AVAILABLE_INVALID",
            "media_available must be True or False.",
            mask=~media_available.isin({"true", "false"}),
            field="media_available",
        )
        self.add_issue(
            "ERROR",
            "E_MEDIA_AUDIT_STATUS_INVALID",
            f"media_audit_status must be one of: {', '.join(sorted(MEDIA_AUDIT_VALUES))}.",
            mask=~audit_status.isin(MEDIA_AUDIT_VALUES),
            field="media_audit_status",
        )
        has_media_url = image_url.str.startswith("http") | destination_url.str.startswith("http")
        self.add_issue(
            "ERROR",
            "E_MEDIA_AVAILABLE_WITHOUT_URL",
            "Rows with media_available=True must expose an audited image or destination URL.",
            mask=available & ~has_media_url,
            field="media_image_url,media_destination_url",
        )
        self.add_issue(
            "ERROR",
            "E_MEDIA_AVAILABLE_AUDIT_MISMATCH",
            "Rows with media_available=True must have media_audit_status=accepted or manual_accepted.",
            mask=available & ~audit_status.isin(MEDIA_AVAILABLE_AUDIT_VALUES),
            field="media_available,media_audit_status",
        )
        self.add_issue(
            "WARNING",
            "W_MEDIA_UNAVAILABLE_WITH_URL",
            "Rows with media_available=False should not carry image/destination URLs.",
            mask=unavailable & has_media_url,
            field="media_available,media_image_url,media_destination_url",
        )
        self.add_issue(
            "WARNING",
            "W_ACTIVE_MEDIA_UNAVAILABLE",
            "Active candidates without media need conservative UI/LLM presentation.",
            mask=self.active_mask() & unavailable,
            field="media_available",
        )
        self.add_issue(
            "INFO",
            "I_ACTIVE_WEBSITE_MISSING",
            "Active candidates without official/reference website.",
            mask=self.active_mask() & website.eq(""),
            field="media_website",
        )

    def collect_summary(self):
        active = self.active_mask()
        severity_counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + issue.count

        self.stats = {
            "dataset_path": self.dataset_path,
            "row_count": int(len(self.df)),
            "column_count": int(len(self.df.columns)),
            "unique_location_id_count": int(self.text("location_id").nunique()) if "location_id" in self.df.columns else 0,
            "active_candidate_count": int(active.sum()),
            "error_count": int(severity_counts.get("ERROR", 0)),
            "warning_count": int(severity_counts.get("WARNING", 0)),
            "info_count": int(severity_counts.get("INFO", 0)),
            "issue_count": int(len(self.issues)),
            "status_counts": self.text("display_status").value_counts(dropna=False).to_dict()
            if "display_status" in self.df.columns else {},
            "data_version": self.data_version(),
            "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        if self.stats["error_count"] == 0 and self.stats["warning_count"] == 0:
            self.stats["gate_status"] = "PASS"
        elif self.stats["error_count"] == 0:
            self.stats["gate_status"] = "PASS_WITH_WARNINGS"
        else:
            self.stats["gate_status"] = "FAIL"

    def data_version(self):
        path = Path(self.dataset_path)
        if not path.exists():
            return "unknown"
        return f"{path.name}:{int(path.stat().st_mtime)}:{path.stat().st_size}"

    def result(self):
        return {
            "schema_version": SCHEMA_VERSION,
            "summary": self.stats,
            "issues": [asdict(issue) for issue in self.issues],
        }


def validate_dataframe(df, dataset_path="<dataframe>"):
    return DatasetValidator(df, dataset_path).validate()


def validate_dataset(dataset_path=DEFAULT_DATASET_PATH):
    df = pd.read_csv(dataset_path, dtype=str, keep_default_na=False)
    return validate_dataframe(df, dataset_path)


def write_json(result, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def issue_sort_key(issue):
    severity_order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    return (severity_order.get(issue["severity"], 9), issue["code"])


def render_markdown(result):
    summary = result["summary"]
    lines = [
        "# Data Validation Report - 2026-05-25",
        "",
        f"Schema version: `{result['schema_version']}`",
        f"Dataset: `{summary['dataset_path']}`",
        f"Data version: `{summary['data_version']}`",
        f"Validated at: `{summary['validated_at']}`",
        "",
        "## Gate Status",
        "",
        f"DATA VALIDATION GATE: **{summary['gate_status']}**",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Rows | {summary['row_count']} |",
        f"| Columns | {summary['column_count']} |",
        f"| Unique location IDs | {summary['unique_location_id_count']} |",
        f"| Active candidates | {summary['active_candidate_count']} |",
        f"| Error rows counted | {summary['error_count']} |",
        f"| Warning rows counted | {summary['warning_count']} |",
        f"| Info rows counted | {summary['info_count']} |",
        "",
        "## Status Distribution",
        "",
        "| display_status | Count |",
        "| --- | ---: |",
    ]

    for status, count in summary.get("status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend([
        "",
        "## Issues",
        "",
        "| Severity | Code | Field | Count | Message |",
        "| --- | --- | --- | ---: | --- |",
    ])

    issues = sorted(result["issues"], key=issue_sort_key)
    if not issues:
        lines.append("| INFO | I_NO_ISSUES | - | 0 | No validation issues found. |")
    else:
        for issue in issues:
            field = issue.get("field") or "-"
            message = str(issue["message"]).replace("|", "\\|")
            lines.append(
                f"| {issue['severity']} | `{issue['code']}` | `{field}` | {issue['count']} | {message} |"
            )

    lines.extend([
        "",
        "## Sample Rows",
        "",
    ])

    sample_issue_count = 0
    for issue in issues:
        rows = issue.get("sample_rows") or []
        if not rows:
            continue
        sample_issue_count += 1
        lines.extend([
            f"### {issue['severity']} - {issue['code']}",
            "",
            "| Row | location_id | location_name |",
            "| ---: | --- | --- |",
        ])
        for row in rows:
            location_name = str(row.get("location_name", "")).replace("|", "\\|")
            lines.append(f"| {row.get('row_number')} | `{row.get('location_id')}` | {location_name} |")
        lines.append("")

    if sample_issue_count == 0:
        lines.append("No sample rows.")
        lines.append("")

    lines.extend([
        "## LLM Readiness Interpretation",
        "",
    ])
    if summary["gate_status"] == "FAIL":
        lines.append("LLM integration must not proceed. Fix ERROR issues first.")
    elif summary["gate_status"] == "PASS_WITH_WARNINGS":
        lines.append(
            "No blocking data contract errors were found. LLM integration can only proceed if warning fields remain guarded by evidence-pack caveats."
        )
    else:
        lines.append("Dataset passed without blocking errors or warnings.")
    lines.append("")
    return "\n".join(lines)


def write_markdown(result, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(result), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the canonical MuterBandung curated dataset.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH), help="Path to curated dataset CSV.")
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT), help="Path to JSON validation result.")
    parser.add_argument("--markdown-output", default=str(DEFAULT_MARKDOWN_OUTPUT), help="Path to Markdown report.")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Return exit code 1 when warnings exist.")
    args = parser.parse_args(argv)

    result = validate_dataset(args.dataset)
    write_json(result, args.json_output)
    write_markdown(result, args.markdown_output)

    summary = result["summary"]
    print("MuterBandung Data Validation")
    print("=" * 40)
    print(f"Dataset: {summary['dataset_path']}")
    print(f"Gate: {summary['gate_status']}")
    print(f"Rows: {summary['row_count']}")
    print(f"Active candidates: {summary['active_candidate_count']}")
    print(f"Errors: {summary['error_count']}")
    print(f"Warnings: {summary['warning_count']}")
    print(f"JSON: {args.json_output}")
    print(f"Markdown: {args.markdown_output}")

    if summary["error_count"] > 0:
        return 1
    if args.fail_on_warnings and summary["warning_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
