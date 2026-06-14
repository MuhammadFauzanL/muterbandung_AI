import json
import math
import re
import warnings
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
MODEL_PATH = ROOT / "Penginapan_Workspace" / "07_Models" / "model_sentimen_muterbandung.pkl"

PRIMARY_INPUT = CURATED_DIR / "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_2026-06-13.csv"
REVIEW_JSON_PATTERN = "dataset_Google-Maps-Reviews-Scraper_2026-06-12*.json"
DATE_TAG = "2026-06-13"

ACCEPTED_REVIEW_OUTPUT = CURATED_DIR / f"PENGINAPAN_REVIEW_COMPLETION_ACCEPTED_NORMALIZED_{DATE_TAG}.csv"
HELD_REVIEW_OUTPUT = CURATED_DIR / f"PENGINAPAN_REVIEW_COMPLETION_HELD_OR_NOISY_{DATE_TAG}.csv"
TARGET_AUDIT_OUTPUT = CURATED_DIR / f"PENGINAPAN_REVIEW_COMPLETION_PER_TARGET_AUDIT_{DATE_TAG}.csv"
SENTIMENT_INFERENCE_OUTPUT = CURATED_DIR / f"PENGINAPAN_REVIEW_SENTIMENT_INFERENCE_{DATE_TAG}_COMPLETION_ACCEPTED.csv"
SENTIMENT_AGGREGATED_OUTPUT = CURATED_DIR / f"PENGINAPAN_SENTIMENT_AGGREGATED_{DATE_TAG}_COMPLETION_ACCEPTED.csv"
PRICE_CANDIDATE_OUTPUT = CURATED_DIR / f"PENGINAPAN_PRICE_CANDIDATE_FROM_REVIEW_JSON_NEEDS_VERIFICATION_{DATE_TAG}.csv"
PRIMARY_OUTPUT = CURATED_DIR / f"PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_REVIEW_COMPLETED_{DATE_TAG}.csv"
QUEUE_OUTPUT = CURATED_DIR / f"PENGINAPAN_PRIMARY_DATA_COMPLETION_QUEUE_ORDERED_REVIEW_COMPLETED_{DATE_TAG}.csv"
P1_PRICE_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_P1_PRICE_MISSING_{DATE_TAG}.csv"
P1_CORE_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_P1_CORE_RATING_PRICE_MISSING_{DATE_TAG}.csv"
P1_RATING_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_P1_RATING_REVIEWS_MISSING_{DATE_TAG}.csv"
P2_SENTIMENT_OUTPUT = CURATED_DIR / f"PENGINAPAN_COMPLETION_REMAINING_P2_SENTIMENT_MISSING_{DATE_TAG}.csv"
SUMMARY_OUTPUT = CURATED_DIR / f"penginapan_primary_review_completion_summary_{DATE_TAG}.json"

SENTIMENT_SHRINKAGE_K = 50.0
TITLE_TARGET_ACCEPT_THRESHOLD = 0.75
TITLE_TARGET_STRICT_THRESHOLD = 0.90
NEAR_ALIAS_DISTANCE_KM = 0.05


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
        if value is None or value == "":
            return None
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def coerce_int(value):
    number = coerce_float(value)
    if number is None:
        return None
    return int(round(number))


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


def similarity(left, right):
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def parse_search_string(value):
    text = clean_text(value)
    match = re.search(r"(.+?)\s+(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\s*$", text)
    if not match:
        return text, None, None
    return clean_text(match.group(1)), float(match.group(2)), float(match.group(3))


def number_tokens(value):
    return set(re.findall(r"\b\d+\b", normalize_text(value)))


def extract_location(item):
    location = item.get("location")
    if isinstance(location, dict):
        return coerce_float(location.get("lat")), coerce_float(location.get("lng"))
    return (
        coerce_float(item.get("placeLatitude") or item.get("outputPlaceLatitude") or item.get("location/lat")),
        coerce_float(item.get("placeLongitude") or item.get("outputPlaceLongitude") or item.get("location/lng")),
    )


def read_json_records():
    json_files = sorted(ROOT.glob(REVIEW_JSON_PATTERN))
    rows = []
    for path in json_files:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, list):
            continue
        for item in data:
            if isinstance(item, dict):
                rows.append((path.name, item))
    return json_files, rows


def build_primary_lookup(primary):
    primary = primary.copy()
    primary["_name_norm"] = primary["name"].map(normalize_text)
    primary["_lat_round4"] = pd.to_numeric(primary["latitude"], errors="coerce").round(4)
    primary["_lon_round4"] = pd.to_numeric(primary["longitude"], errors="coerce").round(4)
    return primary


def match_primary(query_name, query_lat, query_lon, primary_lookup):
    if query_lat is not None and query_lon is not None:
        window = primary_lookup[
            (primary_lookup["_lat_round4"].sub(round(query_lat, 4)).abs() <= 0.002)
            & (primary_lookup["_lon_round4"].sub(round(query_lon, 4)).abs() <= 0.002)
        ].copy()
        if not window.empty:
            window["_query_distance_km"] = window.apply(
                lambda row: haversine_km(query_lat, query_lon, row["latitude"], row["longitude"]) or 9999.0,
                axis=1,
            )
            window["_query_name_similarity"] = window["name"].apply(lambda value: similarity(query_name, value))
            window = window.sort_values(["_query_distance_km", "_query_name_similarity"], ascending=[True, False])
            best = window.iloc[0]
            if best["_query_distance_km"] <= 2.0 and best["_query_name_similarity"] >= 0.35:
                return best

    query_key = normalize_text(query_name)
    exact = primary_lookup[primary_lookup["_name_norm"].eq(query_key)]
    if not exact.empty:
        return exact.iloc[0]
    return None


def normalize_reviews(primary):
    json_files, raw_items = read_json_records()
    primary_lookup = build_primary_lookup(primary)
    rows = []

    for source_file, item in raw_items:
        search_string = clean_text(item.get("searchString") or item.get("outputSearchQuery"))
        query_name, query_lat, query_lon = parse_search_string(search_string)
        target = match_primary(query_name, query_lat, query_lon, primary_lookup)
        place_lat, place_lon = extract_location(item)
        place_title = clean_text(item.get("title") or item.get("placeName") or item.get("outputPlaceName"))
        target_name = clean_text(target["name"]) if target is not None else ""
        target_id = clean_text(target["penginapan_id"]) if target is not None else ""
        country_code = clean_text(item.get("countryCode") or item.get("country"))
        target_distance_km = (
            haversine_km(target["latitude"], target["longitude"], place_lat, place_lon)
            if target is not None
            else None
        )
        title_similarity_target = similarity(place_title, target_name)
        title_similarity_query = similarity(place_title, query_name)
        title_similarity_best = max(title_similarity_target, title_similarity_query)

        has_target = bool(target_id)
        country_ok = country_code in {"", "ID"}
        distance_ok = target_distance_km is not None and target_distance_km <= 2.0
        target_numbers = number_tokens(target_name)
        title_numbers = number_tokens(place_title)
        number_mismatch_far = (
            target_numbers != title_numbers
            and bool(target_numbers or title_numbers)
            and target_distance_km is not None
            and target_distance_km > NEAR_ALIAS_DISTANCE_KM
        )
        # Query dari scraper bisa cocok dengan hasil Google, tetapi belum tentu
        # cocok dengan baris target yang terpilih dari dataset. Untuk apply ke
        # master, nama Google harus cukup dekat dengan nama target dataset.
        title_ok = (
            not number_mismatch_far
            and (
                title_similarity_target >= TITLE_TARGET_STRICT_THRESHOLD
                or (
                    title_similarity_target >= TITLE_TARGET_ACCEPT_THRESHOLD
                    and target_distance_km is not None
                    and target_distance_km <= NEAR_ALIAS_DISTANCE_KM
                )
            )
        )
        accepted = has_target and country_ok and distance_ok and title_ok

        if not has_target:
            match_status = "unmatched_to_primary"
        elif not country_ok:
            match_status = "held_non_id_country"
        elif not distance_ok:
            match_status = "held_far_place_location"
        elif not title_ok:
            match_status = "held_low_title_match"
        else:
            match_status = "accepted_exact_or_close"

        text = clean_text(item.get("text") or item.get("outputText"))
        text_translated = clean_text(item.get("textTranslated") or item.get("outputTextTranslated"))
        rows.append(
            {
                "source_raw_file": source_file,
                "penginapan_id": target_id,
                "name_target": target_name,
                "searchString": search_string,
                "query_name": query_name,
                "query_latitude": query_lat,
                "query_longitude": query_lon,
                "title": place_title,
                "countryCode": country_code,
                "city": item.get("city"),
                "categoryName": item.get("categoryName") or item.get("placeCategory") or item.get("outputPlaceCategory"),
                "placeLatitude": place_lat,
                "placeLongitude": place_lon,
                "target_place_distance_km": target_distance_km,
                "title_similarity_target": title_similarity_target,
                "title_similarity_query": title_similarity_query,
                "title_similarity_best": title_similarity_best,
                "match_status": match_status,
                "reviewId": item.get("reviewId") or item.get("outputReviewId"),
                "reviewUrl": item.get("reviewUrl") or item.get("outputReviewUrl"),
                "stars": item.get("stars") or item.get("outputStars"),
                "text": text,
                "textTranslated": text_translated,
                "cleaned_text_for_sentiment": clean_text(text or text_translated),
                "publishedAtDate": item.get("publishedAtDate") or item.get("publishedAtIso") or item.get("outputPublishedAtIso"),
                "totalScore": item.get("totalScore") or item.get("placeRating") or item.get("outputPlaceRating"),
                "reviewsCount": item.get("reviewsCount"),
                "price_raw_from_review_json": item.get("price"),
                "placeId": item.get("placeId") or item.get("outputPlaceId"),
                "url": item.get("url") or item.get("placeUrl") or item.get("outputPlaceUrl"),
            }
        )

    normalized = pd.DataFrame(rows)
    summary = {
        "raw_json_files": [str(path.relative_to(ROOT)) for path in json_files],
        "raw_review_rows": len(normalized),
        "match_status_counts": normalized["match_status"].value_counts().to_dict() if not normalized.empty else {},
    }
    return normalized, summary


def load_model():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = joblib.load(MODEL_PATH)
    return model, [str(item.message) for item in caught]


def run_sentiment(accepted):
    text_reviews = accepted[accepted["cleaned_text_for_sentiment"].fillna("").astype(str).str.len() > 0].copy()
    text_reviews = text_reviews.drop_duplicates(subset=["reviewId", "cleaned_text_for_sentiment"])
    if text_reviews.empty:
        return pd.DataFrame(), pd.DataFrame(), [], []

    model, model_warnings = load_model()
    texts = text_reviews["cleaned_text_for_sentiment"].tolist()
    predictions = model.predict(texts)
    probabilities = model.predict_proba(texts)
    classes = list(model.classes_ if hasattr(model, "classes_") else model.named_steps["svm"].classes_)
    proba = pd.DataFrame(probabilities, columns=[f"proba_{label.lower()}" for label in classes])

    text_reviews = text_reviews.reset_index(drop=True)
    text_reviews = pd.concat([text_reviews, proba], axis=1)
    text_reviews["hotel_sentiment_prediction"] = predictions

    negative_col = "proba_negatif"
    neutral_col = "proba_netral"
    positive_col = "proba_positif"
    if positive_col in text_reviews.columns and negative_col in text_reviews.columns:
        text_reviews["hotel_review_sentiment_score"] = (
            text_reviews[positive_col].fillna(0.0) - text_reviews[negative_col].fillna(0.0)
        )
    else:
        text_reviews["hotel_review_sentiment_score"] = text_reviews["hotel_sentiment_prediction"].map(
            {"Positif": 1.0, "Netral": 0.0, "Negatif": -1.0}
        ).fillna(0.0)

    available_proba_cols = [col for col in [negative_col, neutral_col, positive_col] if col in text_reviews.columns]
    text_reviews["hotel_review_sentiment_confidence"] = text_reviews[available_proba_cols].max(axis=1)
    aggregated = aggregate_sentiment(text_reviews)
    return text_reviews, aggregated, classes, model_warnings


def sentiment_label(score):
    if pd.isna(score):
        return "Belum tersedia"
    if score >= 0.20:
        return "Positif"
    if score <= -0.20:
        return "Negatif"
    return "Netral"


def confidence_label(value):
    if value >= 0.75:
        return "high_review_confidence"
    if value >= 0.50:
        return "medium_review_confidence"
    return "low_review_confidence"


def review_confidence(count, p95_count):
    count = max(0.0, float(count or 0.0))
    p95_count = max(1.0, float(p95_count or 1.0))
    return min(1.0, math.log1p(count) / math.log1p(p95_count))


def aggregate_sentiment(inference):
    global_average = float(inference["hotel_review_sentiment_score"].mean())
    grouped = (
        inference.groupby("penginapan_id")
        .agg(
            hotel_review_count_analyzed=("reviewId", "nunique"),
            hotel_sentiment_score=("hotel_review_sentiment_score", "mean"),
            hotel_sentiment_confidence_mean=("hotel_review_sentiment_confidence", "mean"),
            positive_review_count=("hotel_sentiment_prediction", lambda s: int((s == "Positif").sum())),
            neutral_review_count=("hotel_sentiment_prediction", lambda s: int((s == "Netral").sum())),
            negative_review_count=("hotel_sentiment_prediction", lambda s: int((s == "Negatif").sum())),
            review_target_count=("source_raw_file", "nunique"),
        )
        .reset_index()
    )
    p95_count = float(grouped["hotel_review_count_analyzed"].quantile(0.95)) if len(grouped) else 1.0
    if not math.isfinite(p95_count) or p95_count <= 0:
        p95_count = 1.0

    grouped["hotel_adjusted_sentiment_score"] = (
        (grouped["hotel_review_count_analyzed"] * grouped["hotel_sentiment_score"])
        + (SENTIMENT_SHRINKAGE_K * global_average)
    ) / (grouped["hotel_review_count_analyzed"] + SENTIMENT_SHRINKAGE_K)
    grouped["hotel_sentiment_label"] = grouped["hotel_sentiment_score"].apply(sentiment_label)
    grouped["hotel_adjusted_sentiment_label"] = grouped["hotel_adjusted_sentiment_score"].apply(sentiment_label)
    grouped["hotel_review_confidence"] = grouped["hotel_review_count_analyzed"].apply(
        lambda value: review_confidence(value, p95_count)
    )
    grouped["hotel_review_confidence_label"] = grouped["hotel_review_confidence"].apply(confidence_label)
    grouped["hotel_sentiment_model_source"] = "tfidf_svm_penginapan"
    grouped["hotel_sentiment_model_version"] = f"model_sentimen_muterbandung_{DATE_TAG}_completion_accepted"
    grouped["hotel_sentiment_prior_score"] = global_average
    grouped["hotel_sentiment_review_count_p95"] = p95_count
    return grouped


def first_valid_number(values, lower=None, upper=None):
    for value in values:
        number = coerce_float(value)
        if number is None:
            continue
        if lower is not None and number < lower:
            continue
        if upper is not None and number > upper:
            continue
        return number
    return None


def build_place_profile(accepted):
    if accepted.empty:
        return pd.DataFrame(columns=["penginapan_id"])
    profile_rows = []
    for penginapan_id, group in accepted.groupby("penginapan_id"):
        total_score = first_valid_number(group["totalScore"].tolist(), lower=0, upper=5)
        reviews_count = first_valid_number(group["reviewsCount"].tolist(), lower=0)
        price_values = [clean_text(v) for v in group["price_raw_from_review_json"].tolist() if clean_text(v)]
        profile_rows.append(
            {
                "penginapan_id": penginapan_id,
                "google_maps_totalScore_candidate": total_score,
                "google_maps_reviewsCount_candidate": reviews_count,
                "price_raw_from_review_json_candidates": "|".join(sorted(set(price_values)))[:500],
                "accepted_review_rows": int(len(group)),
                "accepted_review_text_rows": int(group["cleaned_text_for_sentiment"].fillna("").astype(str).str.len().gt(0).sum()),
                "google_maps_title_candidates": "|".join(sorted(set(group["title"].fillna("").astype(str))))[:500],
                "google_maps_url_candidate": clean_text(group["url"].dropna().astype(str).iloc[0]) if group["url"].notna().any() else "",
            }
        )
    return pd.DataFrame(profile_rows)


def is_missing_number(value):
    return coerce_float(value) is None


def is_missing_text(value):
    return normalize_text(value) in {"", "nan", "none", "null"}


def recompute_completion(row):
    missing_rating_reviews = is_missing_number(row.get("overall_rating")) or is_missing_number(row.get("reviews"))
    missing_price = is_missing_number(row.get("price_lowest"))
    missing_sentiment = is_missing_number(row.get("hotel_adjusted_sentiment_score")) or (coerce_int(row.get("hotel_review_count_analyzed")) or 0) <= 0
    missing_source = is_missing_text(row.get("link"))
    missing_amenities = is_missing_text(row.get("amenities"))
    missing_image = is_missing_text(row.get("primary_image_url"))

    flags = []
    if missing_rating_reviews:
        flags.append("missing_rating_reviews")
    if missing_price:
        flags.append("missing_price")
    if missing_sentiment:
        flags.append("missing_sentiment")
    if missing_source:
        flags.append("missing_source_link")
    if missing_amenities:
        flags.append("missing_amenities")
    if missing_image:
        flags.append("missing_image")

    if missing_rating_reviews and missing_price:
        priority = "P1_core_rating_price_missing"
        route = "scrape_place_rating_reviews_and_price"
        order = 2
    elif missing_price:
        priority = "P1_price_missing"
        route = "scrape_or_manual_price"
        order = 1
    elif missing_rating_reviews:
        priority = "P1_rating_reviews_missing"
        route = "scrape_place_rating_reviews"
        order = 3
    elif missing_sentiment:
        priority = "P2_sentiment_missing"
        route = "scrape_reviews_for_sentiment"
        order = 4
    elif missing_amenities or missing_image:
        priority = "P3_content_missing"
        route = "complete_amenities_or_image"
        order = 5
    elif missing_source:
        priority = "P3_source_link_missing"
        route = "fill_source_link_when_available"
        order = 6
    else:
        priority = "OK_complete_enough"
        route = "ready_for_baseline"
        order = 99

    score = 6 - sum(
        [
            missing_rating_reviews,
            missing_price,
            missing_sentiment,
            missing_source,
            missing_amenities,
            missing_image,
        ]
    )
    return pd.Series(
        {
            "completion_priority_order": order,
            "completion_priority_data_focus": priority,
            "completion_flags_data_focus": "|".join(flags),
            "completion_route_data_focus": route,
            "completion_score_data_focus": score,
        }
    )


def apply_completion(primary, accepted, aggregated):
    updated = primary.copy()
    profile = build_place_profile(accepted)
    profile_map = profile.set_index("penginapan_id").to_dict("index") if not profile.empty else {}
    agg_map = aggregated.set_index("penginapan_id").to_dict("index") if not aggregated.empty else {}

    updated["review_completion_rating_reviews_filled"] = False
    updated["review_completion_sentiment_filled"] = False
    updated["review_completion_price_candidate_available"] = False
    updated["review_completion_note"] = ""

    for idx, row in updated.iterrows():
        penginapan_id = row["penginapan_id"]
        notes = []

        if penginapan_id in profile_map:
            profile_row = profile_map[penginapan_id]
            rating_candidate = profile_row.get("google_maps_totalScore_candidate")
            reviews_candidate = profile_row.get("google_maps_reviewsCount_candidate")
            filled_rating_or_reviews = False

            if is_missing_number(row.get("overall_rating")) and rating_candidate is not None:
                updated.at[idx, "overall_rating"] = rating_candidate
                filled_rating_or_reviews = True
            if is_missing_number(row.get("reviews")) and reviews_candidate is not None:
                updated.at[idx, "reviews"] = reviews_candidate
                filled_rating_or_reviews = True
            if filled_rating_or_reviews:
                updated.at[idx, "review_completion_rating_reviews_filled"] = True
                notes.append("rating/reviews diisi dari Google Maps review JSON yang match")

            if profile_row.get("price_raw_from_review_json_candidates"):
                updated.at[idx, "review_completion_price_candidate_available"] = True
                notes.append("ada price raw di review JSON, ditahan untuk verifikasi")

        if penginapan_id in agg_map:
            agg_row = agg_map[penginapan_id]
            current_count = coerce_int(row.get("hotel_review_count_analyzed")) or 0
            current_score_missing = is_missing_number(row.get("hotel_adjusted_sentiment_score"))
            if current_count <= 0 or current_score_missing:
                updated.at[idx, "hotel_review_count_analyzed"] = int(agg_row["hotel_review_count_analyzed"])
                updated.at[idx, "hotel_adjusted_sentiment_score"] = round(float(agg_row["hotel_adjusted_sentiment_score"]), 6)
                updated.at[idx, "hotel_sentiment_label"] = agg_row["hotel_adjusted_sentiment_label"]
                updated.at[idx, "review_completion_sentiment_filled"] = True
                notes.append("sentiment diisi dari review valid dan model lokal")

        updated.at[idx, "review_completion_note"] = "; ".join(notes)

    completion = updated.apply(recompute_completion, axis=1)
    for col in completion.columns:
        updated[col] = completion[col]

    return updated, profile


def build_price_candidate(profile, primary):
    if profile.empty:
        return pd.DataFrame()
    merged = profile.merge(
        primary[
            [
                "penginapan_id",
                "name",
                "property_type_final_after_p3",
                "price_lowest",
                "price_display",
                "overall_rating",
                "reviews",
            ]
        ],
        on="penginapan_id",
        how="left",
    )
    candidates = merged[
        merged["price_raw_from_review_json_candidates"].fillna("").astype(str).str.len().gt(0)
        & merged["price_lowest"].isna()
    ].copy()
    candidates["price_candidate_decision"] = "needs_manual_or_google_hotels_verification"
    candidates["price_candidate_note"] = "Field price dari review JSON tidak di-apply otomatis karena format/currency raw."
    return candidates.sort_values(["property_type_final_after_p3", "name"])


def make_target_audit(normalized):
    if normalized.empty:
        return pd.DataFrame()
    grouped = (
        normalized.groupby(["searchString", "penginapan_id", "name_target", "match_status"], dropna=False)
        .agg(
            raw_review_rows=("reviewId", "count"),
            text_review_rows=("cleaned_text_for_sentiment", lambda s: int(s.fillna("").astype(str).str.len().gt(0).sum())),
            unique_review_ids=("reviewId", "nunique"),
            title_candidates=("title", lambda s: "|".join(sorted(set(clean_text(v) for v in s if clean_text(v))))[:500]),
            country_codes=("countryCode", lambda s: "|".join(sorted(set(clean_text(v) for v in s if clean_text(v))))),
            min_target_distance_km=("target_place_distance_km", "min"),
            max_title_similarity=("title_similarity_best", "max"),
            google_maps_rating_candidate=("totalScore", lambda s: first_valid_number(s.tolist(), lower=0, upper=5)),
            google_maps_reviews_count_candidate=("reviewsCount", lambda s: first_valid_number(s.tolist(), lower=0)),
        )
        .reset_index()
    )
    return grouped.sort_values(["match_status", "name_target", "searchString"])


def export_completion_queues(updated):
    queue = updated[updated["completion_priority_data_focus"].ne("OK_complete_enough")].copy()
    queue = queue.sort_values(
        ["completion_priority_order", "property_type_final_after_p3", "data_quality_score", "reviews", "name"],
        ascending=[True, True, False, False, True],
    )
    queue.to_csv(QUEUE_OUTPUT, index=False, encoding="utf-8-sig")
    queue[queue["completion_priority_data_focus"].eq("P1_price_missing")].to_csv(
        P1_PRICE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    queue[queue["completion_priority_data_focus"].eq("P1_core_rating_price_missing")].to_csv(
        P1_CORE_OUTPUT, index=False, encoding="utf-8-sig"
    )
    queue[queue["completion_priority_data_focus"].eq("P1_rating_reviews_missing")].to_csv(
        P1_RATING_OUTPUT, index=False, encoding="utf-8-sig"
    )
    queue[queue["completion_priority_data_focus"].eq("P2_sentiment_missing")].to_csv(
        P2_SENTIMENT_OUTPUT, index=False, encoding="utf-8-sig"
    )
    return queue


def main():
    primary = pd.read_csv(PRIMARY_INPUT)
    before_priority_counts = primary["completion_priority_data_focus"].value_counts(dropna=False).to_dict()
    before_flag_counts = {
        "missing_rating_reviews": int(primary["completion_flags_data_focus"].fillna("").str.contains("missing_rating_reviews").sum()),
        "missing_price": int(primary["completion_flags_data_focus"].fillna("").str.contains("missing_price").sum()),
        "missing_sentiment": int(primary["completion_flags_data_focus"].fillna("").str.contains("missing_sentiment").sum()),
    }

    normalized, normalize_summary = normalize_reviews(primary)
    accepted = normalized[normalized["match_status"].eq("accepted_exact_or_close")].copy()
    held = normalized[~normalized["match_status"].eq("accepted_exact_or_close")].copy()
    accepted = accepted.drop_duplicates(subset=["reviewId", "cleaned_text_for_sentiment", "penginapan_id"])
    held = held.drop_duplicates(subset=["reviewId", "cleaned_text_for_sentiment", "searchString", "title"])

    inference, aggregated, classes, model_warnings = run_sentiment(accepted)
    updated, profile = apply_completion(primary, accepted, aggregated)
    price_candidates = build_price_candidate(profile, primary)
    target_audit = make_target_audit(normalized)

    accepted.to_csv(ACCEPTED_REVIEW_OUTPUT, index=False, encoding="utf-8-sig")
    held.to_csv(HELD_REVIEW_OUTPUT, index=False, encoding="utf-8-sig")
    target_audit.to_csv(TARGET_AUDIT_OUTPUT, index=False, encoding="utf-8-sig")
    inference.to_csv(SENTIMENT_INFERENCE_OUTPUT, index=False, encoding="utf-8-sig")
    aggregated.to_csv(SENTIMENT_AGGREGATED_OUTPUT, index=False, encoding="utf-8-sig")
    price_candidates.to_csv(PRICE_CANDIDATE_OUTPUT, index=False, encoding="utf-8-sig")
    updated.to_csv(PRIMARY_OUTPUT, index=False, encoding="utf-8-sig")
    queue = export_completion_queues(updated)

    after_priority_counts = updated["completion_priority_data_focus"].value_counts(dropna=False).to_dict()
    after_flag_counts = {
        "missing_rating_reviews": int(updated["completion_flags_data_focus"].fillna("").str.contains("missing_rating_reviews").sum()),
        "missing_price": int(updated["completion_flags_data_focus"].fillna("").str.contains("missing_price").sum()),
        "missing_sentiment": int(updated["completion_flags_data_focus"].fillna("").str.contains("missing_sentiment").sum()),
    }

    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_primary": str(PRIMARY_INPUT.relative_to(ROOT)),
        "model_path": str(MODEL_PATH.relative_to(ROOT)),
        "review_json_pattern": REVIEW_JSON_PATTERN,
        "primary_rows": int(len(primary)),
        "normalize_summary": normalize_summary,
        "accepted_review_rows": int(len(accepted)),
        "accepted_review_targets": int(accepted["penginapan_id"].nunique()) if not accepted.empty else 0,
        "held_or_noisy_review_rows": int(len(held)),
        "held_or_noisy_target_groups": int(held["searchString"].nunique()) if not held.empty else 0,
        "sentiment_inference_rows": int(len(inference)),
        "sentiment_aggregated_targets": int(len(aggregated)),
        "rating_reviews_filled_rows": int(updated["review_completion_rating_reviews_filled"].sum()),
        "sentiment_filled_rows": int(updated["review_completion_sentiment_filled"].sum()),
        "price_candidates_from_review_json_not_applied": int(len(price_candidates)),
        "before_priority_counts": before_priority_counts,
        "after_priority_counts": after_priority_counts,
        "before_flag_counts": before_flag_counts,
        "after_flag_counts": after_flag_counts,
        "remaining_p1_p2_queue_count": int(
            updated["completion_priority_data_focus"].isin(
                [
                    "P1_price_missing",
                    "P1_core_rating_price_missing",
                    "P1_rating_reviews_missing",
                    "P2_sentiment_missing",
                ]
            ).sum()
        ),
        "remaining_total_queue_count": int(len(queue)),
        "sentiment_classes": classes,
        "model_load_warnings": model_warnings,
        "match_status_counts": Counter(normalized["match_status"]).most_common(),
        "outputs": {
            "primary_review_completed": str(PRIMARY_OUTPUT.relative_to(ROOT)),
            "completion_queue_review_completed": str(QUEUE_OUTPUT.relative_to(ROOT)),
            "accepted_reviews": str(ACCEPTED_REVIEW_OUTPUT.relative_to(ROOT)),
            "held_or_noisy_reviews": str(HELD_REVIEW_OUTPUT.relative_to(ROOT)),
            "per_target_audit": str(TARGET_AUDIT_OUTPUT.relative_to(ROOT)),
            "sentiment_inference": str(SENTIMENT_INFERENCE_OUTPUT.relative_to(ROOT)),
            "sentiment_aggregated": str(SENTIMENT_AGGREGATED_OUTPUT.relative_to(ROOT)),
            "price_candidates_needs_verification": str(PRICE_CANDIDATE_OUTPUT.relative_to(ROOT)),
            "remaining_p1_price": str(P1_PRICE_OUTPUT.relative_to(ROOT)),
            "remaining_p1_core": str(P1_CORE_OUTPUT.relative_to(ROOT)),
            "remaining_p1_rating": str(P1_RATING_OUTPUT.relative_to(ROOT)),
            "remaining_p2_sentiment": str(P2_SENTIMENT_OUTPUT.relative_to(ROOT)),
        },
        "decision_notes": [
            "Review dipakai hanya jika match ke primary penginapan, country ID, jarak <= 2 km, dan nama sangat mirip; alias sedang hanya diterima bila jaraknya <= 50 meter.",
            "Rating/reviews diisi dari totalScore/reviewsCount Google Maps hanya untuk baris yang masih kosong.",
            "Sentiment diisi dari review text accepted menggunakan model lokal.",
            "Price raw dari review JSON tidak di-apply otomatis karena currency/arti field belum cukup aman.",
        ],
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
