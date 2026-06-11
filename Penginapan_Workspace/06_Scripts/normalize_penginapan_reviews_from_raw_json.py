import json
import os
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
RAW_DIR = Path(
    os.getenv(
        "PENGINAPAN_REVIEW_RAW_DIR",
        str(WORKSPACE / "01_Raw_Data" / "google_maps_reviews_json"),
    )
)
CURATED_DIR = WORKSPACE / "02_Curated"

DATE_TAG = os.getenv("PENGINAPAN_REVIEW_OUTPUT_TAG", "2026-06-10_AVAILABLE_RAW")
TARGET_PATHS = [
    CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_READY_2026-06-05.csv",
    CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_TEST_BATCH_30_2026-06-05.csv",
]

NORMALIZED_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_REVIEW_{DATE_TAG}_NORMALIZED.csv"
UNMATCHED_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_REVIEW_{DATE_TAG}_UNMATCHED.csv"
SUMMARY_OUTPUT_PATH = CURATED_DIR / f"penginapan_review_{DATE_TAG.lower()}_normalize_summary.json"


def clean_text(value):
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_key(value):
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def coerce_float(value):
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def rounded_coord_key(lat, lon):
    lat_value = coerce_float(lat)
    lon_value = coerce_float(lon)
    if lat_value is None or lon_value is None:
        return ""
    return f"{lat_value:.4f},{lon_value:.4f}"


def extract_location(item):
    location = item.get("location")
    if isinstance(location, dict):
        return location.get("lat"), location.get("lng")
    if item.get("location/lat") not in ("", None) or item.get("location/lng") not in ("", None):
        return item.get("location/lat"), item.get("location/lng")
    return item.get("placeLatitude") or item.get("outputPlaceLatitude"), item.get("placeLongitude") or item.get(
        "outputPlaceLongitude"
    )


def read_records(path):
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype=str, keep_default_na=False).to_dict("records")

    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "data", "results", "reviews"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def load_targets():
    frames = []
    for path in TARGET_PATHS:
        if path.exists():
            temp = pd.read_csv(path)
            temp["_target_source_file"] = str(path)
            frames.append(temp)
    if not frames:
        raise FileNotFoundError("Tidak ada file target review penginapan yang tersedia.")

    targets = pd.concat(frames, ignore_index=True)
    targets = targets.drop_duplicates(subset=["review_target_id"], keep="first")
    for col in [
        "google_maps_search_query",
        "google_maps_search_url",
        "name",
        "latitude",
        "longitude",
    ]:
        if col not in targets.columns:
            targets[col] = ""
    targets["_query_key"] = targets["google_maps_search_query"].map(normalize_key)
    targets["_url_key"] = targets["google_maps_search_url"].map(clean_text)
    targets["_title_coord_key"] = targets.apply(
        lambda row: normalize_key(row.get("name")) + "|" + rounded_coord_key(row.get("latitude"), row.get("longitude")),
        axis=1,
    )
    return targets


def build_lookup(targets):
    query_map = {}
    url_map = {}
    coord_map = {}
    for _, row in targets.iterrows():
        row_dict = row.to_dict()
        if row["_query_key"]:
            query_map.setdefault(row["_query_key"], row_dict)
        if row["_url_key"]:
            url_map.setdefault(row["_url_key"], row_dict)
        if row["_title_coord_key"] and not row["_title_coord_key"].endswith("|"):
            coord_map.setdefault(row["_title_coord_key"], row_dict)
    return query_map, url_map, coord_map


def match_target(item, query_map, url_map, coord_map):
    search_query = clean_text(
        item.get("searchString")
        or item.get("outputSearchQuery")
        or item.get("searchQuery")
        or item.get("inputSearch")
        or ""
    )
    input_url = clean_text(item.get("inputUrl") or item.get("outputInputUrl") or "")
    place_url = clean_text(item.get("url") or item.get("placeUrl") or item.get("outputPlaceUrl") or "")
    title = clean_text(item.get("title") or item.get("placeName") or item.get("outputPlaceName") or "")
    lat, lon = extract_location(item)

    query_key = normalize_key(search_query)
    if query_key in query_map:
        return query_map[query_key], "query"
    if input_url in url_map:
        return url_map[input_url], "input_url"
    if place_url in url_map:
        return url_map[place_url], "place_url"

    coord_key = normalize_key(title) + "|" + rounded_coord_key(lat, lon)
    if coord_key in coord_map:
        return coord_map[coord_key], "title_coordinate"
    return {}, ""


def normalize_records():
    targets = load_targets()
    query_map, url_map, coord_map = build_lookup(targets)
    raw_files = sorted([*RAW_DIR.rglob("*.json"), *RAW_DIR.rglob("*.csv")])
    rows = []

    for raw_file in raw_files:
        for item in read_records(raw_file):
            if not isinstance(item, dict):
                continue
            target, match_method = match_target(item, query_map, url_map, coord_map)
            lat, lon = extract_location(item)
            title = clean_text(item.get("title") or item.get("placeName") or item.get("outputPlaceName") or "")
            target_name = clean_text(target.get("name", ""))
            similarity = SequenceMatcher(None, normalize_key(title), normalize_key(target_name)).ratio() if target_name else 0.0

            row = {
                "source_raw_file": raw_file.name,
                "searchString": clean_text(
                    item.get("searchString")
                    or item.get("outputSearchQuery")
                    or item.get("searchQuery")
                    or item.get("inputSearch")
                    or ""
                ),
                "reviewerId": item.get("reviewerId") or item.get("outputReviewerId"),
                "reviewerUrl": item.get("reviewerUrl") or item.get("outputReviewerUrl"),
                "name_review": item.get("name") or item.get("reviewerName") or item.get("outputReviewerName"),
                "reviewerNumberOfReviews": item.get("reviewerNumberOfReviews") or item.get("outputReviewerTotalReviews"),
                "isLocalGuide": item.get("isLocalGuide") or item.get("outputIsLocalGuide"),
                "reviewerPhotoUrl": item.get("reviewerPhotoUrl") or item.get("outputReviewerPhotoUrl"),
                "text": item.get("text") or item.get("outputText"),
                "textTranslated": item.get("textTranslated") or item.get("outputTextTranslated"),
                "publishAt": item.get("publishAt") or item.get("publishedAt") or item.get("outputPublishedAt"),
                "publishedAtDate": item.get("publishedAtDate") or item.get("publishedAtIso") or item.get("outputPublishedAtIso"),
                "likesCount": item.get("likesCount"),
                "reviewId": item.get("reviewId") or item.get("outputReviewId"),
                "reviewUrl": item.get("reviewUrl") or item.get("outputReviewUrl"),
                "reviewOrigin": item.get("reviewOrigin"),
                "stars": item.get("stars") or item.get("outputStars"),
                "rating": item.get("rating") or item.get("placeRating") or item.get("outputPlaceRating"),
                "responseFromOwnerDate": item.get("responseFromOwnerDate") or item.get("ownerReplyPublishedAtIso"),
                "responseFromOwnerText": item.get("responseFromOwnerText") or item.get("ownerReplyText"),
                "reviewImageUrls": item.get("reviewImageUrls") or item.get("outputReviewImageUrls"),
                "originalLanguage": item.get("originalLanguage") or item.get("outputOriginalLanguage"),
                "translatedLanguage": item.get("translatedLanguage") or item.get("outputTranslatedLanguage"),
                "placeId": item.get("placeId") or item.get("outputPlaceId"),
                "placeLatitude": lat,
                "placeLongitude": lon,
                "address": item.get("address") or item.get("placeAddress") or item.get("outputPlaceAddress"),
                "categoryName": item.get("categoryName") or item.get("placeCategory") or item.get("outputPlaceCategory"),
                "categories": item.get("categories") or item.get("placeCategories") or item.get("outputPlaceCategories"),
                "title": title,
                "totalScore": item.get("totalScore") or item.get("placeRating") or item.get("outputPlaceRating"),
                "reviewsCount": item.get("reviewsCount"),
                "url": item.get("url") or item.get("placeUrl") or item.get("outputPlaceUrl"),
                "price": item.get("price"),
                "cid": item.get("cid") or item.get("outputCid"),
                "fid": item.get("fid") or item.get("outputFid"),
                "hotelStars": item.get("hotelStars"),
                "imageUrl": item.get("imageUrl"),
                "scrapedAt": item.get("scrapedAt") or item.get("outputScrapedAt"),
                "language": item.get("language"),
                "review_target_id": target.get("review_target_id", ""),
                "penginapan_id": target.get("penginapan_id", ""),
                "name_target": target_name,
                "property_type": target.get("property_type", ""),
                "review_scrape_priority": target.get("review_scrape_priority", ""),
                "google_maps_search_query": target.get("google_maps_search_query", ""),
                "google_maps_search_url": target.get("google_maps_search_url", ""),
                "target_match_method": match_method,
                "target_matched": bool(match_method),
                "has_text": bool(clean_text(item.get("text") or item.get("outputText") or item.get("textTranslated") or item.get("outputTextTranslated"))),
                "has_place_id": bool(item.get("placeId") or item.get("outputPlaceId")),
                "has_review_id": bool(item.get("reviewId") or item.get("outputReviewId")),
                "title_target_similarity": round(float(similarity), 4),
                "place_title_equals_target": normalize_key(title) == normalize_key(target_name) if target_name else False,
            }
            rows.append(row)

    if not rows:
        raise ValueError(f"Tidak ada record review yang bisa dibaca dari {RAW_DIR}")

    df = pd.DataFrame(rows)
    df["text"] = df["text"].fillna("")
    df["textTranslated"] = df["textTranslated"].fillna("")
    matched = df[df["target_matched"]].copy()
    unmatched = df[~df["target_matched"]].copy()

    dedupe_cols = ["reviewId", "penginapan_id"]
    if "reviewId" in matched.columns:
        matched["_review_dedupe_key"] = matched["reviewId"].fillna("").astype(str) + "|" + matched["penginapan_id"].fillna("").astype(str)
        fallback = (
            matched["title"].fillna("").astype(str)
            + "|"
            + matched["stars"].fillna("").astype(str)
            + "|"
            + matched["text"].fillna("").astype(str).str[:120]
        )
        matched["_review_dedupe_key"] = matched["_review_dedupe_key"].where(
            matched["reviewId"].fillna("").astype(str).str.strip() != "",
            fallback,
        )
        matched = matched.drop_duplicates(subset=["_review_dedupe_key"], keep="first").drop(columns=["_review_dedupe_key"])
    else:
        matched = matched.drop_duplicates()

    matched.to_csv(NORMALIZED_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    unmatched.to_csv(UNMATCHED_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_dir": str(RAW_DIR),
        "raw_files": [path.name for path in raw_files],
        "raw_file_count": len(raw_files),
        "raw_rows_read": int(len(df)),
        "matched_rows_before_dedupe": int(df["target_matched"].sum()),
        "matched_rows_after_dedupe": int(len(matched)),
        "unmatched_rows": int(len(unmatched)),
        "unique_review_targets_matched": int(matched["review_target_id"].nunique()) if len(matched) else 0,
        "unique_penginapan_matched": int(matched["penginapan_id"].nunique()) if len(matched) else 0,
        "rows_with_text": int((matched["text"].fillna("").astype(str).str.len() > 0).sum()),
        "target_total_final_ready": int(pd.read_csv(TARGET_PATHS[0], usecols=["review_target_id"]).shape[0])
        if TARGET_PATHS[0].exists()
        else None,
        "outputs": {
            "normalized": str(NORMALIZED_OUTPUT_PATH),
            "unmatched": str(UNMATCHED_OUTPUT_PATH),
        },
        "decision": (
            "Output ini hanya memakai raw review yang sudah ada lokal. "
            "Jika hasil full Apify belum masuk, coverage sentiment tetap terbatas."
        ),
    }
    SUMMARY_OUTPUT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    normalize_records()
