import json
import math
import os
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
CURATED_DIR = WORKSPACE / "02_Curated"
MODEL_PATH = WORKSPACE / "07_Models" / "model_sentimen_muterbandung.pkl"

DATE_TAG = os.getenv("PENGINAPAN_SENTIMENT_DATE_TAG", "2026-06-10")
SENTIMENT_SHRINKAGE_K = 50.0
DISTANCE_SCORE_SCALE_KM = 5.0
BANDUNG_CENTER_LAT = -6.9175
BANDUNG_CENTER_LON = 107.6191

REVIEW_INPUT_PATH = Path(
    os.getenv(
        "PENGINAPAN_REVIEW_INPUT_PATH",
        str(CURATED_DIR / "PENGINAPAN_COMPASS_REVIEW_TEST_BATCH_30_RAW_NORMALIZED_2026-06-06.csv"),
    )
)
PARENT_MASTER_PATH = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_2026-06-05.csv"
RELATIONS_PATH = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_RELATIONS_FINAL_2026-06-05.csv"

INFERENCE_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_REVIEW_SENTIMENT_INFERENCE_{DATE_TAG}.csv"
AGGREGATED_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_SENTIMENT_AGGREGATED_{DATE_TAG}.csv"
PARENT_WITH_SENTIMENT_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_{DATE_TAG}.csv"
BASELINE_SAMPLE_OUTPUT_PATH = CURATED_DIR / f"PENGINAPAN_DISTANCE_WEIGHTED_BASELINE_SAMPLE_{DATE_TAG}.csv"
SUMMARY_OUTPUT_PATH = CURATED_DIR / f"penginapan_sentiment_baseline_summary_{DATE_TAG}.json"


def clean_text(value):
    text = str(value or "")
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def coerce_float(value, default=None):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = coerce_float(lat1)
    lon1 = coerce_float(lon1)
    lat2 = coerce_float(lat2)
    lon2 = coerce_float(lon2)
    if None in (lat1, lon1, lat2, lon2):
        return np.nan
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


def distance_score(distance_km):
    if pd.isna(distance_km):
        return 0.0
    return 1.0 / (1.0 + max(0.0, float(distance_km)) / DISTANCE_SCORE_SCALE_KM)


def review_confidence(count, p95_count):
    count = max(0.0, float(count or 0.0))
    p95_count = max(1.0, float(p95_count or 1.0))
    return min(1.0, math.log1p(count) / math.log1p(p95_count))


def confidence_label(value):
    if value >= 0.75:
        return "high_review_confidence"
    if value >= 0.50:
        return "medium_review_confidence"
    return "low_review_confidence"


def sentiment_label(score):
    if score >= 0.20:
        return "Positif"
    if score <= -0.20:
        return "Negatif"
    return "Netral"


def normalize_score(value, min_value, max_value, default=0.0):
    value = coerce_float(value)
    if value is None:
        return default
    if max_value <= min_value:
        return default
    return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = joblib.load(MODEL_PATH)
    warning_messages = [str(item.message) for item in caught]
    return model, warning_messages


def build_parent_lookup():
    if not RELATIONS_PATH.exists():
        return {}
    relations = pd.read_csv(RELATIONS_PATH)
    if relations.empty:
        return {}
    final_relations = relations[
        relations.get("is_final_relation", False).astype(bool)
        & relations.get("manual_decision", "").astype(str).str.lower().eq("accept")
    ].copy()
    return dict(zip(final_relations["child_penginapan_id"], final_relations["parent_penginapan_id"]))


def choose_review_text(df):
    text = df.get("text", pd.Series("", index=df.index)).fillna("").astype(str)
    translated = df.get("textTranslated", pd.Series("", index=df.index)).fillna("").astype(str)
    combined = text.where(text.str.strip() != "", translated)
    return combined.apply(clean_text)


def run_sentiment_inference(model):
    reviews = pd.read_csv(REVIEW_INPUT_PATH)
    parent_lookup = build_parent_lookup()
    reviews["cleaned_text_for_sentiment"] = choose_review_text(reviews)
    text_reviews = reviews[reviews["cleaned_text_for_sentiment"].str.len() > 0].copy()
    text_reviews = text_reviews.drop_duplicates(subset=["reviewId", "cleaned_text_for_sentiment"])

    if text_reviews.empty:
        raise ValueError("No text review rows available for hotel sentiment inference.")

    predictions = model.predict(text_reviews["cleaned_text_for_sentiment"].tolist())
    probabilities = model.predict_proba(text_reviews["cleaned_text_for_sentiment"].tolist())
    classes = list(model.classes_ if hasattr(model, "classes_") else model.named_steps["svm"].classes_)
    probability_frame = pd.DataFrame(probabilities, columns=[f"proba_{label.lower()}" for label in classes])

    text_reviews = text_reviews.reset_index(drop=True)
    text_reviews = pd.concat([text_reviews, probability_frame], axis=1)
    text_reviews["hotel_sentiment_prediction"] = predictions

    negative_col = "proba_negatif" if "proba_negatif" in text_reviews.columns else None
    positive_col = "proba_positif" if "proba_positif" in text_reviews.columns else None
    neutral_col = "proba_netral" if "proba_netral" in text_reviews.columns else None

    text_reviews["hotel_review_sentiment_score"] = (
        text_reviews[positive_col].fillna(0.0) - text_reviews[negative_col].fillna(0.0)
        if positive_col and negative_col
        else text_reviews["hotel_sentiment_prediction"].map({"Positif": 1.0, "Netral": 0.0, "Negatif": -1.0}).fillna(0.0)
    )
    text_reviews["hotel_review_sentiment_confidence"] = text_reviews[
        [col for col in [negative_col, neutral_col, positive_col] if col]
    ].max(axis=1)
    text_reviews["parent_penginapan_id"] = text_reviews["penginapan_id"].map(parent_lookup).fillna(text_reviews["penginapan_id"])

    keep_cols = [
        "review_target_id",
        "penginapan_id",
        "parent_penginapan_id",
        "name_target",
        "title",
        "reviewId",
        "stars",
        "cleaned_text_for_sentiment",
        "hotel_sentiment_prediction",
        "hotel_review_sentiment_score",
        "hotel_review_sentiment_confidence",
    ]
    for col in ["proba_negatif", "proba_netral", "proba_positif"]:
        if col in text_reviews.columns:
            keep_cols.append(col)
    return text_reviews[keep_cols].copy(), classes


def aggregate_sentiment(inference):
    global_average = float(inference["hotel_review_sentiment_score"].mean())
    grouped = (
        inference.groupby("parent_penginapan_id")
        .agg(
            hotel_review_count_analyzed=("reviewId", "nunique"),
            hotel_sentiment_score=("hotel_review_sentiment_score", "mean"),
            hotel_sentiment_confidence_mean=("hotel_review_sentiment_confidence", "mean"),
            positive_review_count=("hotel_sentiment_prediction", lambda s: int((s == "Positif").sum())),
            neutral_review_count=("hotel_sentiment_prediction", lambda s: int((s == "Netral").sum())),
            negative_review_count=("hotel_sentiment_prediction", lambda s: int((s == "Negatif").sum())),
            review_target_count=("review_target_id", "nunique"),
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
    grouped["hotel_sentiment_model_version"] = f"model_sentimen_muterbandung_{DATE_TAG}"
    grouped["hotel_sentiment_prior_score"] = global_average
    grouped["hotel_sentiment_review_count_p95"] = p95_count
    return grouped, global_average, p95_count


def merge_parent_master(aggregated):
    parent = pd.read_csv(PARENT_MASTER_PATH)
    merged = parent.merge(
        aggregated,
        left_on="penginapan_id",
        right_on="parent_penginapan_id",
        how="left",
    )

    merged["hotel_review_count_analyzed"] = merged["hotel_review_count_analyzed"].fillna(0).astype(int)
    for col in [
        "hotel_sentiment_score",
        "hotel_adjusted_sentiment_score",
        "hotel_sentiment_confidence_mean",
        "hotel_review_confidence",
    ]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")
    merged["hotel_sentiment_available"] = merged["hotel_review_count_analyzed"] > 0
    merged["hotel_sentiment_label"] = merged["hotel_sentiment_label"].fillna("Belum tersedia")
    merged["hotel_adjusted_sentiment_label"] = merged["hotel_adjusted_sentiment_label"].fillna("Belum tersedia")
    merged["hotel_review_confidence_label"] = merged["hotel_review_confidence_label"].fillna("missing_review_confidence")
    merged["hotel_sentiment_model_source"] = merged["hotel_sentiment_model_source"].fillna("unavailable")
    merged["hotel_sentiment_model_version"] = merged["hotel_sentiment_model_version"].fillna("")
    return merged


def build_distance_weighted_sample(parent_with_sentiment):
    sample = parent_with_sentiment.copy()
    sample["distance_km_reference"] = sample.apply(
        lambda row: haversine_km(BANDUNG_CENTER_LAT, BANDUNG_CENTER_LON, row.get("latitude"), row.get("longitude")),
        axis=1,
    )
    sample["hotel_distance_score"] = sample["distance_km_reference"].apply(distance_score)
    sample["hotel_rating_score"] = pd.to_numeric(sample.get("overall_rating"), errors="coerce").fillna(0.0).clip(0, 5) / 5.0
    sample["hotel_sentiment_ranking_score"] = (
        pd.to_numeric(sample.get("hotel_adjusted_sentiment_score"), errors="coerce").fillna(0.0).clip(-1, 1) + 1.0
    ) / 2.0
    sample["hotel_review_confidence_score"] = pd.to_numeric(
        sample.get("hotel_review_confidence"), errors="coerce"
    ).fillna(0.0).clip(0, 1)
    sample["hotel_data_quality_score"] = pd.to_numeric(sample.get("data_quality_score"), errors="coerce").fillna(0.0).clip(0, 1)

    prices = pd.to_numeric(sample.get("price_lowest"), errors="coerce")
    positive_prices = prices[prices > 0]
    if len(positive_prices):
        p10 = float(positive_prices.quantile(0.10))
        p90 = float(positive_prices.quantile(0.90))
    else:
        p10, p90 = 0.0, 1.0
    sample["hotel_price_score"] = prices.apply(
        lambda value: 1.0 - normalize_score(value, p10, p90, default=0.5)
        if pd.notna(value) and value > 0
        else 0.4
    )

    weights = {
        "distance": 0.45,
        "rating": 0.18,
        "sentiment": 0.16,
        "price": 0.09,
        "data_quality": 0.07,
        "review_confidence": 0.05,
    }
    sample["hotel_recommendation_score"] = (
        weights["distance"] * sample["hotel_distance_score"]
        + weights["rating"] * sample["hotel_rating_score"]
        + weights["sentiment"] * sample["hotel_sentiment_ranking_score"]
        + weights["price"] * sample["hotel_price_score"]
        + weights["data_quality"] * sample["hotel_data_quality_score"]
        + weights["review_confidence"] * sample["hotel_review_confidence_score"]
    ) * 100.0

    output_cols = [
        "penginapan_id",
        "name",
        "property_type",
        "latitude",
        "longitude",
        "distance_km_reference",
        "hotel_recommendation_score",
        "hotel_distance_score",
        "hotel_rating_score",
        "hotel_sentiment_ranking_score",
        "hotel_price_score",
        "hotel_data_quality_score",
        "hotel_review_confidence_score",
        "overall_rating",
        "reviews",
        "price_lowest",
        "hotel_review_count_analyzed",
        "hotel_adjusted_sentiment_score",
        "hotel_adjusted_sentiment_label",
        "hotel_review_confidence_label",
    ]
    return (
        sample.sort_values("hotel_recommendation_score", ascending=False)
        [output_cols]
        .head(100)
        .reset_index(drop=True)
    )


def main():
    model, model_warnings = load_model()
    inference, classes = run_sentiment_inference(model)
    aggregated, global_average, p95_count = aggregate_sentiment(inference)
    parent_with_sentiment = merge_parent_master(aggregated)
    baseline_sample = build_distance_weighted_sample(parent_with_sentiment)

    inference.to_csv(INFERENCE_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    aggregated.to_csv(AGGREGATED_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    parent_with_sentiment.to_csv(PARENT_WITH_SENTIMENT_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    baseline_sample.to_csv(BASELINE_SAMPLE_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_path": str(MODEL_PATH),
        "review_input_path": str(REVIEW_INPUT_PATH),
        "parent_master_path": str(PARENT_MASTER_PATH),
        "sentiment_classes": classes,
        "model_warning_count": len(model_warnings),
        "model_warnings": model_warnings[:5],
        "review_rows_input": int(len(pd.read_csv(REVIEW_INPUT_PATH, usecols=["reviewId"]))),
        "review_rows_with_text_inference": int(len(inference)),
        "parent_hotels_with_sentiment": int(aggregated["parent_penginapan_id"].nunique()),
        "parent_master_rows": int(len(parent_with_sentiment)),
        "parent_master_with_sentiment_rows": int(parent_with_sentiment["hotel_sentiment_available"].sum()),
        "sentiment_global_average": round(float(global_average), 6),
        "sentiment_review_count_p95": round(float(p95_count), 2),
        "distance_weighted_baseline": {
            "reference_point": {
                "name": "Bandung Center",
                "latitude": BANDUNG_CENTER_LAT,
                "longitude": BANDUNG_CENTER_LON,
            },
            "distance_score_scale_km": DISTANCE_SCORE_SCALE_KM,
            "weights": {
                "distance": 0.45,
                "rating": 0.18,
                "sentiment": 0.16,
                "price": 0.09,
                "data_quality": 0.07,
                "review_confidence": 0.05,
            },
        },
        "outputs": {
            "inference": str(INFERENCE_OUTPUT_PATH),
            "aggregated": str(AGGREGATED_OUTPUT_PATH),
            "parent_with_sentiment": str(PARENT_WITH_SENTIMENT_OUTPUT_PATH),
            "baseline_sample": str(BASELINE_SAMPLE_OUTPUT_PATH),
        },
        "decision": (
            "Distance is intentionally the largest baseline ranking weight for hotel. "
            "Sentiment is included only where scraped review text exists."
        ),
    }
    SUMMARY_OUTPUT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
