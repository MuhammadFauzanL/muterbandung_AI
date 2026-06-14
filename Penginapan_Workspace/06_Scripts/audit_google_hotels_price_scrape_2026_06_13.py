import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"

RAW_PATTERN = "dataset_google-hotels-search-scraper_2026-06-13_10-*.json"
PRIMARY_PATH = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_REVIEW_COMPLETED_2026-06-13.csv"
DATE_TAG = "2026-06-13"

FLATTENED_OUTPUT = CURATED_DIR / f"PENGINAPAN_GOOGLE_HOTELS_PRICE_SCRAPE_FLATTENED_{DATE_TAG}.csv"
MATCH_AUDIT_OUTPUT = CURATED_DIR / f"PENGINAPAN_GOOGLE_HOTELS_PRICE_MATCH_AUDIT_{DATE_TAG}.csv"
SAFE_FILL_OUTPUT = CURATED_DIR / f"PENGINAPAN_GOOGLE_HOTELS_PRICE_SAFE_FILL_CANDIDATES_{DATE_TAG}.csv"
NEEDS_REVIEW_OUTPUT = CURATED_DIR / f"PENGINAPAN_GOOGLE_HOTELS_PRICE_NEEDS_REVIEW_CANDIDATES_{DATE_TAG}.csv"
SUMMARY_OUTPUT = CURATED_DIR / f"penginapan_google_hotels_price_scrape_audit_{DATE_TAG}.json"


def clean_text(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_text(value):
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def coerce_float(value):
    try:
        if value in ("", None):
            return None
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = coerce_float(lat1)
    lon1 = coerce_float(lon1)
    lat2 = coerce_float(lat2)
    lon2 = coerce_float(lon2)
    if None in (lat1, lon1, lat2, lon2):
        return None
    radius_km = 6371.0088
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(a))


def read_unique_raw_files():
    files = sorted(ROOT.glob(RAW_PATTERN))
    seen_hashes = {}
    unique_files = []
    duplicate_files = []
    for path in files:
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        if digest in seen_hashes:
            duplicate_files.append(
                {
                    "duplicate_file": path.name,
                    "same_as": seen_hashes[digest],
                    "hash": digest,
                }
            )
            continue
        seen_hashes[digest] = path.name
        unique_files.append(path)
    return files, unique_files, duplicate_files


def flatten_google_hotels():
    all_files, unique_files, duplicate_files = read_unique_raw_files()
    page_rows = []
    property_rows = []

    for path in unique_files:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, list):
            continue
        for page in data:
            if not isinstance(page, dict):
                continue
            params = page.get("search_parameters", {}) or {}
            meta = page.get("search_metadata", {}) or {}
            properties = page.get("properties") or []
            page_rows.append(
                {
                    "source_file": path.name,
                    "query": params.get("q"),
                    "gl": params.get("gl"),
                    "hl": params.get("hl"),
                    "currency": params.get("currency"),
                    "check_in_date": params.get("check_in_date"),
                    "check_out_date": params.get("check_out_date"),
                    "adults": params.get("adults"),
                    "children": params.get("children"),
                    "vacation_rentals_query": params.get("vacation_rentals"),
                    "max_pages": params.get("max_pages"),
                    "page_number": page.get("page_number"),
                    "total_results": meta.get("total_results"),
                    "properties_count_metadata": meta.get("properties_count"),
                    "pages_processed": meta.get("pages_processed"),
                    "pagination_limit_reached": meta.get("pagination_limit_reached"),
                    "property_rows": len(properties),
                }
            )

            for item in properties:
                if not isinstance(item, dict):
                    continue
                coords = item.get("gps_coordinates") or {}
                rate = item.get("rate_per_night") or {}
                total = item.get("total_rate") or {}
                prices = item.get("prices") or []
                images = item.get("images") or []
                amenities = item.get("amenities") or []
                property_rows.append(
                    {
                        "source_file": path.name,
                        "query": params.get("q"),
                        "vacation_rentals_query": params.get("vacation_rentals"),
                        "page_number": page.get("page_number"),
                        "raw_type": item.get("type"),
                        "name": item.get("name"),
                        "name_norm": normalize_text(item.get("name")),
                        "description": item.get("description"),
                        "property_token": item.get("property_token"),
                        "latitude": coerce_float(coords.get("latitude")),
                        "longitude": coerce_float(coords.get("longitude")),
                        "price_lowest": coerce_float(rate.get("extracted_lowest")),
                        "price_display": rate.get("lowest"),
                        "price_before_taxes_fees": coerce_float(rate.get("extracted_before_taxes_fees")),
                        "total_price_lowest": coerce_float(total.get("extracted_lowest")),
                        "total_price_display": total.get("lowest"),
                        "overall_rating": coerce_float(item.get("overall_rating") or item.get("rating")),
                        "reviews": coerce_float(item.get("reviews")),
                        "hotel_class": item.get("hotel_class"),
                        "extracted_hotel_class": item.get("extracted_hotel_class"),
                        "check_in_time": item.get("check_in_time"),
                        "check_out_time": item.get("check_out_time"),
                        "link": item.get("link"),
                        "price_source_count": len(prices),
                        "price_sources": "; ".join(
                            clean_text(price.get("source")) for price in prices if isinstance(price, dict) and price.get("source")
                        ),
                        "amenities": "; ".join(map(clean_text, amenities)) if isinstance(amenities, list) else "",
                        "amenities_count": len(amenities) if isinstance(amenities, list) else 0,
                        "primary_image_url": images[0].get("thumbnail") if images and isinstance(images[0], dict) else "",
                        "images_count": len(images) if isinstance(images, list) else 0,
                    }
                )

    return pd.DataFrame(property_rows), pd.DataFrame(page_rows), all_files, unique_files, duplicate_files


def is_missing_number(value):
    return coerce_float(value) is None


def choose_best_candidate(group):
    ranked = group.copy()
    ranked["_has_price"] = ranked["scrape_price_lowest"].notna().astype(int)
    ranked["_has_rating"] = ranked["scrape_overall_rating"].notna().astype(int)
    ranked["_has_reviews"] = ranked["scrape_reviews"].notna().astype(int)
    ranked["_distance"] = ranked["distance_km"].fillna(9999)
    ranked["_price"] = ranked["scrape_price_lowest"].fillna(10**12)
    ranked = ranked.sort_values(
        ["_has_price", "_has_rating", "_has_reviews", "_distance", "_price"],
        ascending=[False, False, False, True, True],
    )
    return ranked.iloc[0]


def build_matches(flattened, primary):
    primary = primary.copy()
    primary["name_norm"] = primary["name"].map(normalize_text)
    lookup = {key: frame.copy() for key, frame in primary.groupby("name_norm") if key}

    match_rows = []
    for _, row in flattened.iterrows():
        name_norm = row.get("name_norm", "")
        if not name_norm or name_norm not in lookup:
            continue
        for _, target in lookup[name_norm].iterrows():
            distance = haversine_km(row["latitude"], row["longitude"], target["latitude"], target["longitude"])
            if distance is not None and distance > 1.0:
                continue
            price_missing = is_missing_number(target.get("price_lowest"))
            rating_missing = is_missing_number(target.get("overall_rating")) or is_missing_number(target.get("reviews"))
            fillable_price = price_missing and not is_missing_number(row.get("price_lowest"))
            fillable_rating = rating_missing and (
                not is_missing_number(row.get("overall_rating")) or not is_missing_number(row.get("reviews"))
            )
            if distance is not None and distance <= 0.1:
                match_confidence = "safe_apply_candidate"
            else:
                match_confidence = "needs_review_candidate"
            match_rows.append(
                {
                    "penginapan_id": target["penginapan_id"],
                    "primary_name": target["name"],
                    "scrape_name": row["name"],
                    "match_method": "exact_normalized_name",
                    "match_confidence": match_confidence,
                    "distance_km": None if distance is None else round(distance, 6),
                    "primary_property_type": target.get("property_type_final_after_p3"),
                    "scrape_type": row.get("raw_type"),
                    "primary_priority_before": target.get("completion_priority_data_focus"),
                    "primary_price_before": target.get("price_lowest"),
                    "scrape_price_lowest": row.get("price_lowest"),
                    "scrape_price_display": row.get("price_display"),
                    "primary_rating_before": target.get("overall_rating"),
                    "primary_reviews_before": target.get("reviews"),
                    "scrape_overall_rating": row.get("overall_rating"),
                    "scrape_reviews": row.get("reviews"),
                    "fillable_price": bool(fillable_price),
                    "fillable_rating_reviews": bool(fillable_rating),
                    "query": row.get("query"),
                    "source_file": row.get("source_file"),
                    "page_number": row.get("page_number"),
                    "property_token": row.get("property_token"),
                    "link": row.get("link"),
                    "price_sources": row.get("price_sources"),
                    "hotel_class": row.get("hotel_class"),
                    "check_in_time": row.get("check_in_time"),
                    "check_out_time": row.get("check_out_time"),
                    "primary_image_url": row.get("primary_image_url"),
                    "amenities": row.get("amenities"),
                }
            )

    if not match_rows:
        return pd.DataFrame()
    matches = pd.DataFrame(match_rows)
    matches = matches.drop_duplicates(
        subset=[
            "penginapan_id",
            "scrape_name",
            "scrape_price_lowest",
            "scrape_overall_rating",
            "scrape_reviews",
            "property_token",
        ]
    )
    return matches


def build_final_candidate_tables(matches):
    if matches.empty:
        return pd.DataFrame(), pd.DataFrame()

    fillable = matches[matches["fillable_price"] | matches["fillable_rating_reviews"]].copy()
    if fillable.empty:
        return fillable, fillable

    safe = fillable[fillable["match_confidence"].eq("safe_apply_candidate")].copy()
    needs_review = fillable[~fillable["match_confidence"].eq("safe_apply_candidate")].copy()

    if not safe.empty:
        best_rows = [choose_best_candidate(group) for _, group in safe.groupby("penginapan_id")]
        safe = pd.DataFrame(best_rows).drop(columns=[col for col in ["_has_price", "_has_rating", "_has_reviews", "_distance", "_price"] if col in safe.columns])
        safe["recommended_action"] = safe.apply(
            lambda row: "fill_price_and_rating_reviews"
            if row["fillable_price"] and row["fillable_rating_reviews"]
            else ("fill_price" if row["fillable_price"] else "fill_rating_reviews"),
            axis=1,
        )
        safe["audit_note"] = "Exact normalized name and coordinate distance <= 100m."

    if not needs_review.empty:
        best_rows = [choose_best_candidate(group) for _, group in needs_review.groupby("penginapan_id")]
        needs_review = pd.DataFrame(best_rows).drop(
            columns=[col for col in ["_has_price", "_has_rating", "_has_reviews", "_distance", "_price"] if col in needs_review.columns]
        )
        needs_review["recommended_action"] = "manual_check_before_apply"
        needs_review["audit_note"] = "Exact name match, but coordinate distance > 100m or coordinate unavailable."

    return safe, needs_review


def main():
    flattened, page_audit, all_files, unique_files, duplicate_files = flatten_google_hotels()
    primary = pd.read_csv(PRIMARY_PATH)
    matches = build_matches(flattened, primary)
    safe, needs_review = build_final_candidate_tables(matches)

    flattened.to_csv(FLATTENED_OUTPUT, index=False, encoding="utf-8-sig")
    matches.to_csv(MATCH_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    safe.to_csv(SAFE_FILL_OUTPUT, index=False, encoding="utf-8-sig")
    needs_review.to_csv(NEEDS_REVIEW_OUTPUT, index=False, encoding="utf-8-sig")

    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_pattern": RAW_PATTERN,
        "raw_file_count": len(all_files),
        "unique_raw_file_count": len(unique_files),
        "duplicate_files": duplicate_files,
        "page_query_summary": page_audit.groupby(["query", "vacation_rentals_query", "max_pages"], dropna=False)
        .agg(
            files=("source_file", "nunique"),
            pages=("page_number", "count"),
            property_rows=("property_rows", "sum"),
            total_results=("total_results", "max"),
            pagination_limit_reached=("pagination_limit_reached", "max"),
        )
        .reset_index()
        .to_dict("records")
        if not page_audit.empty
        else [],
        "flattened_rows": int(len(flattened)),
        "unique_property_token_count": int(flattened["property_token"].nunique()) if not flattened.empty else 0,
        "unique_name_count": int(flattened["name_norm"].nunique()) if not flattened.empty else 0,
        "type_counts": flattened["raw_type"].fillna("blank").value_counts().to_dict() if not flattened.empty else {},
        "field_coverage": {
            "price_lowest": int(flattened["price_lowest"].notna().sum()) if not flattened.empty else 0,
            "overall_rating": int(flattened["overall_rating"].notna().sum()) if not flattened.empty else 0,
            "reviews": int(flattened["reviews"].notna().sum()) if not flattened.empty else 0,
            "coordinates": int(flattened[["latitude", "longitude"]].notna().all(axis=1).sum()) if not flattened.empty else 0,
            "link": int(flattened["link"].fillna("").astype(str).str.len().gt(0).sum()) if not flattened.empty else 0,
        },
        "price_stats": {
            key: (None if pd.isna(value) else round(float(value), 2))
            for key, value in pd.to_numeric(flattened["price_lowest"], errors="coerce").describe().to_dict().items()
        }
        if not flattened.empty
        else {},
        "match_rows": int(len(matches)),
        "matched_penginapan_ids": int(matches["penginapan_id"].nunique()) if not matches.empty else 0,
        "fillable_match_rows": int((matches["fillable_price"] | matches["fillable_rating_reviews"]).sum()) if not matches.empty else 0,
        "safe_fill_candidate_rows": int(len(safe)),
        "safe_fill_candidate_ids": int(safe["penginapan_id"].nunique()) if not safe.empty else 0,
        "safe_fill_price_ids": int(safe[safe["fillable_price"]]["penginapan_id"].nunique()) if not safe.empty else 0,
        "safe_fill_rating_review_ids": int(safe[safe["fillable_rating_reviews"]]["penginapan_id"].nunique()) if not safe.empty else 0,
        "needs_review_candidate_rows": int(len(needs_review)),
        "needs_review_candidate_ids": int(needs_review["penginapan_id"].nunique()) if not needs_review.empty else 0,
        "safe_candidate_priority_counts": safe["primary_priority_before"].value_counts().to_dict() if not safe.empty else {},
        "needs_review_priority_counts": needs_review["primary_priority_before"].value_counts().to_dict()
        if not needs_review.empty
        else {},
        "outputs": {
            "flattened": str(FLATTENED_OUTPUT.relative_to(ROOT)),
            "match_audit": str(MATCH_AUDIT_OUTPUT.relative_to(ROOT)),
            "safe_fill_candidates": str(SAFE_FILL_OUTPUT.relative_to(ROOT)),
            "needs_review_candidates": str(NEEDS_REVIEW_OUTPUT.relative_to(ROOT)),
        },
        "decision_notes": [
            "Audit ini belum mengubah master penginapan.",
            "Safe candidate hanya exact normalized name dan jarak koordinat <= 100 meter.",
            "Jika satu penginapan muncul berkali-kali, kandidat terbaik dipilih berdasarkan ada harga/rating, jarak terdekat, lalu harga termurah.",
            "Needs review disimpan terpisah agar tidak auto-apply data yang koordinatnya kurang dekat.",
        ],
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
