import math
import os
import re
from datetime import datetime, timezone

import numpy as np
import pandas as pd


DEFAULT_PENGINAPAN_DATASET_PATH = os.getenv(
    "MUTERBANDUNG_PENGINAPAN_DATASET_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Penginapan_Workspace",
        "02_Curated",
        "PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_2026-06-10_DRIVE_FULL_REVIEW.csv",
    ),
)

DISTANCE_SCORE_SCALE_KM = 5.0
BANDUNG_CENTER_LAT = -6.9175
BANDUNG_CENTER_LON = 107.6191

RANKING_WEIGHTS = {
    "distance": 0.30,
    "rating": 0.15,
    "sentiment": 0.13,
    "price": 0.10,
    "data_quality": 0.05,
    "review_confidence": 0.05,
}

PROPERTY_TYPE_PRIORITY = {
    "hotel": 1.00,
    "guest_house": 1.00,
    "villa": 0.97,
    "vacation_rental": 0.94,
    "apartment": 0.82,
}

APARTMENT_INTENT_KEYWORDS = {
    "apartment",
    "apartemen",
    "studio",
    "1br",
    "2br",
    "3br",
    "one bedroom",
    "two bedroom",
    "three bedroom",
    "long stay",
    "bulanan",
    "mingguan",
}

PROPERTY_TYPE_ALIASES = {
    "hotel": {"hotel", "penginapan", "menginap", "formal"},
    "guest_house": {"guest house", "guesthouse", "homestay", "syariah"},
    "villa": {"villa", "vila", "rombongan", "keluarga besar"},
    "apartment": APARTMENT_INTENT_KEYWORDS,
    "vacation_rental": {"vacation rental", "rumah", "sewa rumah"},
}


def _clean_text(value):
    return str(value or "").strip()


def _norm(value):
    text = _clean_text(value).lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _coerce_float(value, default=None):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _haversine_km(lat1, lon1, lat2, lon2):
    lat1 = _coerce_float(lat1)
    lon1 = _coerce_float(lon1)
    lat2 = _coerce_float(lat2)
    lon2 = _coerce_float(lon2)
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


def _distance_score(distance_km):
    if pd.isna(distance_km):
        return 0.0
    return 1.0 / (1.0 + max(0.0, float(distance_km)) / DISTANCE_SCORE_SCALE_KM)


def _normalize_score(value, min_value, max_value, default=0.0):
    value = _coerce_float(value)
    if value is None:
        return default
    if max_value <= min_value:
        return default
    return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))


class PenginapanRecommender:
    def __init__(self, dataset_path=DEFAULT_PENGINAPAN_DATASET_PATH):
        self.dataset_path = dataset_path
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(dataset_path)
        self.df = pd.read_csv(dataset_path)
        self.df["__search_text"] = self.df.apply(self._build_search_text, axis=1)
        prices = pd.to_numeric(self.df.get("price_lowest"), errors="coerce")
        positive_prices = prices[prices > 0]
        if len(positive_prices):
            self.price_p10 = float(positive_prices.quantile(0.10))
            self.price_p90 = float(positive_prices.quantile(0.90))
        else:
            self.price_p10 = 0.0
            self.price_p90 = 1.0

    def _build_search_text(self, row):
        values = [
            row.get("name"),
            row.get("property_type"),
            row.get("raw_type"),
            row.get("amenities"),
            row.get("nearby_place_names"),
            row.get("region_bucket"),
        ]
        return _norm(" ".join(_clean_text(value) for value in values))

    def _detect_property_types(self, query):
        query_text = _norm(query)
        detected = []
        for property_type, aliases in PROPERTY_TYPE_ALIASES.items():
            if any(alias in query_text for alias in aliases):
                detected.append(property_type)
        return detected

    def _query_score(self, row, query, detected_property_types):
        if not query:
            return 0.0
        query_text = _norm(query)
        score = 0.0
        property_type = _clean_text(row.get("property_type"))
        if property_type and property_type in detected_property_types:
            score += 0.45
        tokens = [token for token in re.split(r"[^a-z0-9]+", query_text) if len(token) >= 4]
        if tokens:
            matched = sum(1 for token in tokens if token in row.get("__search_text", ""))
            score += min(0.45, matched / max(1, len(tokens)) * 0.45)
        if "murah" in query_text or "budget" in query_text:
            price = _coerce_float(row.get("price_lowest"))
            if price is not None and price > 0:
                score += 0.10 * (1.0 - _normalize_score(price, self.price_p10, self.price_p90, default=0.5))
        return max(0.0, min(1.0, score))

    def _price_score(self, price):
        price = _coerce_float(price)
        if price is None or price <= 0:
            return 0.4
        return 1.0 - _normalize_score(price, self.price_p10, self.price_p90, default=0.5)

    def _apartment_requested(self, query, selected_property_types):
        query_text = _norm(query)
        selected = {str(item).strip().lower() for item in selected_property_types or []}
        return "apartment" in selected or any(keyword in query_text for keyword in APARTMENT_INTENT_KEYWORDS)

    def _property_type_priority_score(self, property_type, apartment_requested=False):
        property_type = _clean_text(property_type)
        if property_type == "apartment" and apartment_requested:
            return 1.0
        return PROPERTY_TYPE_PRIORITY.get(property_type, 0.92)

    def recommend(
        self,
        query=None,
        property_types=None,
        max_price=None,
        min_rating=None,
        user_lat=None,
        user_lon=None,
        max_distance_km=None,
        sort_by="balanced",
        top_k=5,
    ):
        query = _clean_text(query)
        detected_property_types = self._detect_property_types(query)
        selected_property_types = property_types or detected_property_types
        apartment_requested = self._apartment_requested(query, selected_property_types)

        candidates = self.df.copy()
        if selected_property_types:
            normalized_types = {str(item).strip() for item in selected_property_types if str(item).strip()}
            candidates = candidates[candidates["property_type"].isin(normalized_types)].copy()

        if max_price is not None:
            price_series = pd.to_numeric(candidates.get("price_lowest"), errors="coerce")
            candidates = candidates[price_series.isna() | (price_series <= float(max_price))].copy()

        if min_rating is not None:
            rating_series = pd.to_numeric(candidates.get("overall_rating"), errors="coerce").fillna(0.0)
            candidates = candidates[rating_series >= float(min_rating)].copy()

        has_user_location = user_lat is not None and user_lon is not None
        lat = _coerce_float(user_lat, BANDUNG_CENTER_LAT)
        lon = _coerce_float(user_lon, BANDUNG_CENTER_LON)
        candidates["distance_km"] = candidates.apply(
            lambda row: _haversine_km(lat, lon, row.get("latitude"), row.get("longitude")),
            axis=1,
        )
        if max_distance_km is not None and has_user_location:
            candidates = candidates[
                candidates["distance_km"].isna() | (candidates["distance_km"] <= float(max_distance_km))
            ].copy()

        if candidates.empty:
            return {
                "status": "ok",
                "entity_type": "penginapan",
                "query": query,
                "total_results": 0,
                "recommendations": [],
                "metadata": self._metadata(),
            }

        candidates["distance_score"] = candidates["distance_km"].apply(_distance_score)
        candidates["rating_score"] = (
            pd.to_numeric(candidates.get("overall_rating"), errors="coerce").fillna(0.0).clip(0, 5) / 5.0
        )
        candidates["sentiment_score_normalized"] = (
            pd.to_numeric(candidates.get("hotel_adjusted_sentiment_score"), errors="coerce").fillna(0.0).clip(-1, 1)
            + 1.0
        ) / 2.0
        candidates["review_confidence_score"] = pd.to_numeric(
            candidates.get("hotel_review_confidence"), errors="coerce"
        ).fillna(0.0).clip(0, 1)
        candidates["data_quality_score_normalized"] = pd.to_numeric(
            candidates.get("data_quality_score"), errors="coerce"
        ).fillna(0.0).clip(0, 1)
        candidates["price_score"] = candidates.get("price_lowest", pd.Series(index=candidates.index)).apply(self._price_score)
        candidates["query_score"] = candidates.apply(
            lambda row: self._query_score(row, query, detected_property_types), axis=1
        )
        candidates["property_type_priority_score"] = candidates["property_type"].apply(
            lambda value: self._property_type_priority_score(value, apartment_requested)
        )

        dist_weight = RANKING_WEIGHTS["distance"] if has_user_location else 0.0
        query_weight = 0.22 if has_user_location else (0.22 + RANKING_WEIGHTS["distance"])

        candidates["hotel_recommendation_score_raw"] = (
            dist_weight * candidates["distance_score"]
            + RANKING_WEIGHTS["rating"] * candidates["rating_score"]
            + RANKING_WEIGHTS["sentiment"] * candidates["sentiment_score_normalized"]
            + RANKING_WEIGHTS["price"] * candidates["price_score"]
            + RANKING_WEIGHTS["data_quality"] * candidates["data_quality_score_normalized"]
            + RANKING_WEIGHTS["review_confidence"] * candidates["review_confidence_score"]
            + query_weight * candidates["query_score"]
        ) * 100.0
        candidates["hotel_recommendation_score"] = (
            candidates["hotel_recommendation_score_raw"] * candidates["property_type_priority_score"]
        )

        if sort_by == "nearest":
            candidates = candidates.sort_values(["distance_km", "hotel_recommendation_score"], ascending=[True, False])
        else:
            candidates = candidates.sort_values("hotel_recommendation_score", ascending=False)

        rows = candidates.head(int(top_k)).reset_index(drop=True)
        recommendations = []
        for rank, (_, row) in enumerate(rows.iterrows(), start=1):
            distance_km = _coerce_float(row.get("distance_km"))
            score_breakdown = {
                "distance_score": round(float(row.get("distance_score", 0.0)), 4),
                "rating_score": round(float(row.get("rating_score", 0.0)), 4),
                "sentiment_score": round(float(row.get("sentiment_score_normalized", 0.0)), 4),
                "price_score": round(float(row.get("price_score", 0.0)), 4),
                "data_quality_score": round(float(row.get("data_quality_score_normalized", 0.0)), 4),
                "review_confidence_score": round(float(row.get("review_confidence_score", 0.0)), 4),
                "query_score": round(float(row.get("query_score", 0.0)), 4),
                "property_type_priority_score": round(float(row.get("property_type_priority_score", 0.0)), 4),
                "weights": RANKING_WEIGHTS,
            }
            recommendations.append({
                "rank": rank,
                "entity_type": "penginapan",
                "penginapan_id": row.get("penginapan_id"),
                "name": row.get("name"),
                "property_type": row.get("property_type"),
                "latitude": _coerce_float(row.get("latitude")),
                "longitude": _coerce_float(row.get("longitude")),
                "distance_km": round(distance_km, 2) if distance_km is not None else None,
                "distance_label": f"{distance_km:.1f} km dari titik acuan" if distance_km is not None else None,
                "overall_rating": _coerce_float(row.get("overall_rating")),
                "reviews": int(_coerce_float(row.get("reviews"), 0) or 0),
                "price_lowest": _coerce_float(row.get("price_lowest")),
                "price_display": row.get("price_display"),
                "primary_image_url": row.get("primary_image_url"),
                "link": row.get("link"),
                "hotel_sentiment_available": bool(row.get("hotel_sentiment_available", False)),
                "hotel_adjusted_sentiment_score": _coerce_float(row.get("hotel_adjusted_sentiment_score")),
                "hotel_adjusted_sentiment_label": row.get("hotel_adjusted_sentiment_label"),
                "hotel_review_count_analyzed": int(_coerce_float(row.get("hotel_review_count_analyzed"), 0) or 0),
                "hotel_review_confidence_label": row.get("hotel_review_confidence_label"),
                "final_score": round(float(row.get("hotel_recommendation_score", 0.0)), 2),
                "score_breakdown": score_breakdown,
                "note": self._build_note(row),
            })

        return {
            "status": "ok",
            "entity_type": "penginapan",
            "query": query,
            "total_results": int(len(candidates)),
            "recommendations": recommendations,
            "metadata": self._metadata(),
        }

    def _build_note(self, row):
        distance_km = _coerce_float(row.get("distance_km"))
        parts = []
        if distance_km is not None:
            parts.append(f"Jarak menjadi faktor ranking utama, sekitar {distance_km:.1f} km dari titik acuan.")
        rating = _coerce_float(row.get("overall_rating"))
        if rating is not None and rating > 0:
            parts.append(f"Rating {rating:.1f}/5.")
        if bool(row.get("hotel_sentiment_available", False)):
            label = row.get("hotel_adjusted_sentiment_label") or "tersedia"
            count = int(_coerce_float(row.get("hotel_review_count_analyzed"), 0) or 0)
            parts.append(f"Sentiment review hotel {label.lower()} dari {count} review teks batch awal.")
        else:
            parts.append("Sentiment review hotel belum tersedia untuk item ini.")
        return " ".join(parts)

    def _metadata(self):
        return {
            "dataset_path": self.dataset_path,
            "data_version": f"{os.path.basename(self.dataset_path)}:{int(os.path.getmtime(self.dataset_path))}",
            "ranking_mode": "distance_weighted_baseline",
            "distance_weight": RANKING_WEIGHTS["distance"],
            "apartment_default_priority": PROPERTY_TYPE_PRIORITY["apartment"],
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
