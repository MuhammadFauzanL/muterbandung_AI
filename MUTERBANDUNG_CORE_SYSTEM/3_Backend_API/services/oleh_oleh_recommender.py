import csv
import math
import os
import re
from datetime import datetime


DEFAULT_OLEH_OLEH_DATASET_PATH = os.getenv(
    "MUTERBANDUNG_OLEH_OLEH_DATASET_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "ai_workspace",
        "OlehOleh_Workspace",
        "03_Curated",
        "OLEH_OLEH_BASELINE_UI_ENRICHED_WITH_MANUAL_PRODUCT_PRICE_2026-06-10.csv",
    ),
)

MAX_DISTANCE_SCORE_KM = 20.0

QUERY_CATEGORY_KEYWORDS = {
    "kue_bolu_pastry": [
        "kue", "bolu", "brownies", "brownis", "pastry", "roti", "donat",
        "cheese", "cheesecake", "kukus", "balok", "manis",
    ],
    "snack_keripik": [
        "snack", "cemilan", "camilan", "keripik", "kripik", "kering",
        "grosir", "tahan perjalanan",
    ],
    "tahu_tempe": ["tahu", "tempe", "tahu susu"],
    "olahan_susu": ["susu", "yoghurt", "yogurt", "fresh milk"],
    "souvenir_non_makanan": [
        "souvenir", "suvenir", "kaos", "cendera mata", "cenderamata",
        "non makanan",
    ],
    "haji_umroh_kurma": ["haji", "umroh", "umrah", "kurma", "zamzam"],
}

CATEGORY_ALIASES = {
    "kue": "kue_bolu_pastry",
    "bolu": "kue_bolu_pastry",
    "brownies": "kue_bolu_pastry",
    "pastry": "kue_bolu_pastry",
    "snack": "snack_keripik",
    "cemilan": "snack_keripik",
    "camilan": "snack_keripik",
    "keripik": "snack_keripik",
    "tahu": "tahu_tempe",
    "tempe": "tahu_tempe",
    "susu": "olahan_susu",
    "souvenir": "souvenir_non_makanan",
    "suvenir": "souvenir_non_makanan",
    "haji": "haji_umroh_kurma",
    "umroh": "haji_umroh_kurma",
    "kurma": "haji_umroh_kurma",
}


def _coerce_float(value, default=None):
    if value is None or value == "":
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(parsed):
        return default
    return parsed


def _coerce_int(value, default=0):
    if value is None or value == "":
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _coerce_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _normalize_text(value):
    value = str(value or "").lower()
    value = re.sub(r"[^a-z0-9\u00c0-\u024f\u1e00-\u1eff\s-]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _query_has_any(query_text, keywords):
    return any(keyword in query_text for keyword in keywords)


def _extract_query_price_limit(query_text):
    if not query_text:
        return None
    match = re.search(r"(?:di bawah|dibawah|maks(?:imal)?|max|under)\s*(\d+)\s*(?:ribu|rb|k)?", query_text)
    if not match:
        match = re.search(r"(\d+)\s*(?:ribu|rb|k)", query_text)
    if not match:
        return None
    value = int(match.group(1))
    return value * 1000 if value < 1000 else value


def _is_product_specific_query(query_text):
    product_terms = [
        "donat", "brownies", "brownis", "almond", "crispy", "kue balok",
        "bolu susu", "bolu kukus", "cheesecake", "cheese tart", "keripik tempe",
        "tahu susu", "susu murni", "yoghurt", "kurma", "kaos",
    ]
    return _query_has_any(query_text, product_terms)


def _haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class OlehOlehRecommender:
    """Small baseline recommender for MuterBandung oleh-oleh entities."""

    def __init__(self, dataset_path=DEFAULT_OLEH_OLEH_DATASET_PATH):
        self.dataset_path = dataset_path
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset oleh-oleh tidak ditemukan: {dataset_path}")
        with open(dataset_path, newline="", encoding="utf-8-sig") as handle:
            self.rows = list(csv.DictReader(handle))
        self.generated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        self.category_counts = self._category_counts(
            [row for row in self.rows if _coerce_bool(row.get("main_recommendation_eligible"))]
        )

    def _category_counts(self, rows):
        counts = {}
        for row in rows:
            category = row.get("manual_category") or "unknown"
            counts[category] = counts.get(category, 0) + 1
        return counts

    def _detect_query_categories(self, query, explicit_categories=None):
        categories = set()
        for item in explicit_categories or []:
            normalized = _normalize_text(item).replace(" ", "_")
            if normalized in QUERY_CATEGORY_KEYWORDS:
                categories.add(normalized)
            elif normalized in CATEGORY_ALIASES:
                categories.add(CATEGORY_ALIASES[normalized])

        query_text = _normalize_text(query)
        for category, keywords in QUERY_CATEGORY_KEYWORDS.items():
            if any(keyword in query_text for keyword in keywords):
                categories.add(category)
        if "tahu susu" in query_text:
            categories.discard("olahan_susu")
            categories.add("tahu_tempe")
        if any(phrase in query_text for phrase in ["bolu susu", "brownies susu", "donat susu"]):
            categories.discard("olahan_susu")
            categories.add("kue_bolu_pastry")
        return sorted(categories)

    def _query_keyword_score(self, row, query_text, detected_categories):
        if not query_text:
            return 0.0
        row_blob = _normalize_text(
            " ".join(
                [
                    row.get("name", ""),
                    row.get("manual_category_label", ""),
                    row.get("manual_subtype", ""),
                    row.get("produk_utama", ""),
                    row.get("cocok_untuk", ""),
                    row.get("best_use_case", ""),
                    row.get("google_category", ""),
                    row.get("google_categories", ""),
                ]
            )
        )
        product_blob = _normalize_text(
            " ".join(
                [
                    row.get("name", ""),
                    row.get("produk_utama", ""),
                    row.get("manual_subtype", ""),
                    row.get("best_use_case", ""),
                ]
            )
        )
        score = 0.0
        category = row.get("manual_category")
        if category in detected_categories:
            score += 50.0

        query_terms = [term for term in query_text.split() if len(term) >= 3]
        if query_terms:
            matched = sum(1 for term in query_terms if term in row_blob)
            score += min(30.0, (matched / len(query_terms)) * 30.0)

        product_boosts = {
            "donat": "donat",
            "brownies": "brownies",
            "brownis": "brownies",
            "almond": "almond",
            "crispy": "crispy",
            "balok": "balok",
            "bolu susu": "bolu susu",
            "bolu kukus": "bolu kukus",
            "cheesecake": "cheesecake",
            "cheese": "cheese",
        }
        for query_phrase, row_phrase in product_boosts.items():
            if query_phrase in query_text and row_phrase in product_blob:
                score += 28.0
        if "bolu susu" in query_text and "bolu" in product_blob and "susu" in product_blob:
            score += 18.0

        product_must_match = {
            "donat": ["donat"],
            "brownies": ["brownies", "brownis"],
            "brownis": ["brownies", "brownis"],
            "almond": ["almond"],
            "crispy": ["crispy"],
            "balok": ["balok"],
            "bolu susu": ["bolu", "susu"],
            "keripik tempe": ["keripik", "tempe"],
        }
        for query_phrase, required_terms in product_must_match.items():
            if query_phrase in query_text and not all(term in product_blob for term in required_terms):
                score -= 42.0

        if _query_has_any(query_text, ["murah", "grosir", "hemat", "budget", "di bawah", "dibawah"]):
            price_min = _coerce_float(row.get("price_min_idr"))
            if price_min is not None:
                if price_min <= 25_000:
                    score += 25.0
                elif price_min <= 50_000:
                    score += 18.0
                elif price_min <= 100_000:
                    score += 8.0
            score += min(10.0, _coerce_float(row.get("price_signal_score"), 0.0) * 0.10)

        if _query_has_any(query_text, ["keluarga", "anak", "rombongan", "hantaran", "buah tangan"]):
            score += min(10.0, _coerce_float(row.get("product_aspect_score"), 0.0) * 0.08)
            score += min(8.0, _coerce_float(row.get("service_aspect_signal_score"), 0.0) * 0.05)
            if any(term in row_blob for term in ["keluarga", "rombongan", "buah tangan", "hantaran"]):
                score += 10.0

        if _query_has_any(query_text, ["tahan", "perjalanan", "dibawa", "luar kota", "bus", "mobil"]):
            score += min(16.0, _coerce_float(row.get("packaging_score"), 0.0) * 0.16)
            durability = row.get("daya_tahan_produk_class") or row.get("travel_durability")
            if durability in {"tinggi", "high"}:
                score += 24.0
            elif durability in {"rendah", "low"}:
                score -= 16.0

        if _query_has_any(query_text, ["fresh", "segar", "langsung dimakan", "langsung makan", "makanan basah"]):
            durability = row.get("daya_tahan_produk_class") or row.get("travel_durability")
            if durability in {"rendah", "low"}:
                score += 20.0
            elif durability in {"tinggi", "high"}:
                score -= 8.0

        return max(0.0, min(100.0, score))

    def _distance_payload(self, row, user_lat, user_lon):
        lat = _coerce_float(row.get("latitude"))
        lon = _coerce_float(row.get("longitude"))
        if lat is None or lon is None or user_lat is None or user_lon is None:
            return None, None, "Jarak belum dihitung"
        distance = _haversine_km(user_lat, user_lon, lat, lon)
        distance_score = max(0.0, 100.0 * (1.0 - min(distance, MAX_DISTANCE_SCORE_KM) / MAX_DISTANCE_SCORE_KM))
        return distance, distance_score, f"{distance:.1f} km"

    def _warnings_for_row(self, row):
        warnings = []
        category = row.get("manual_category")
        if self.category_counts.get(category, 0) < 2:
            warnings.append("category_coverage_low")
        if _coerce_int(row.get("text_reviews"), 0) < 12:
            warnings.append("review_text_low")
        if row.get("manual_recommendation_status") == "active_low_rank":
            warnings.append("manual_low_rank")
        if not _coerce_bool(row.get("opening_hours_available")):
            warnings.append("opening_hours_unavailable")
        if _coerce_float(row.get("price_min_idr")) is None:
            warnings.append("price_range_unavailable")
        if row.get("price_confidence") == "medium":
            warnings.append("price_estimate_medium_confidence")
        return warnings

    def recommend(
        self,
        query=None,
        categories=None,
        user_lat=None,
        user_lon=None,
        max_distance_km=None,
        sort_by="balanced",
        top_k=5,
        include_non_main=False,
        max_price=None,
    ):
        query_text = _normalize_text(query)
        detected_categories = self._detect_query_categories(query_text, categories)
        product_specific_query = _is_product_specific_query(query_text)
        query_price_limit = _extract_query_price_limit(query_text)
        effective_max_price = _coerce_float(max_price, query_price_limit)
        has_location = user_lat is not None and user_lon is not None
        user_lat = _coerce_float(user_lat)
        user_lon = _coerce_float(user_lon)
        top_k = max(1, min(int(top_k or 5), 20))

        candidates = []
        for row in self.rows:
            eligible = _coerce_bool(row.get("main_recommendation_eligible"))
            if not include_non_main and not eligible:
                continue
            if detected_categories and row.get("manual_category") not in detected_categories:
                continue

            distance_km, distance_score, distance_label = self._distance_payload(row, user_lat, user_lon)
            if max_distance_km is not None and distance_km is not None and distance_km > float(max_distance_km):
                continue
            price_min = _coerce_float(row.get("price_min_idr"))
            if effective_max_price is not None and price_min is not None and price_min > effective_max_price:
                continue

            base_score = _coerce_float(row.get("final_oleh_oleh_recommendation_score"), 0.0)
            query_score = self._query_keyword_score(row, query_text, detected_categories)
            if has_location and distance_score is not None:
                if sort_by == "nearest":
                    combined = (base_score * 0.35) + (query_score * 0.15) + (distance_score * 0.50)
                elif product_specific_query:
                    combined = (base_score * 0.45) + (query_score * 0.35) + (distance_score * 0.20)
                else:
                    combined = (base_score * 0.60) + (query_score * 0.20) + (distance_score * 0.20)
            elif product_specific_query:
                combined = (base_score * 0.50) + (query_score * 0.50)
            else:
                combined = (base_score * 0.78) + (query_score * 0.22)

            manual_status = row.get("manual_recommendation_status") or "active"
            manual_sort_group = 1 if manual_status == "active_low_rank" else 0
            item = {
                "entity_type": "oleh_oleh",
                "oleh_oleh_id": row.get("oleh_oleh_id"),
                "name": row.get("name"),
                "category": row.get("manual_category"),
                "category_label": row.get("manual_category_label"),
                "manual_subtype": row.get("manual_subtype"),
                "produk_utama": row.get("produk_utama"),
                "cocok_untuk": row.get("cocok_untuk"),
                "best_use_case": row.get("best_use_case"),
                "manual_recommendation_status": manual_status,
                "manual_recommendation_note": row.get("manual_recommendation_note"),
                "main_recommendation_eligible": eligible,
                "score": round(max(0.0, min(100.0, combined)), 2),
                "base_score": round(base_score, 2),
                "query_score": round(query_score, 2),
                "distance_km": None if distance_km is None else round(distance_km, 3),
                "distance_label": distance_label,
                "rating": _coerce_float(row.get("rating")),
                "review_count": _coerce_int(row.get("source_reviews_count"), 0),
                "text_reviews": _coerce_int(row.get("text_reviews"), 0),
                "address": row.get("address"),
                "latitude": _coerce_float(row.get("latitude")),
                "longitude": _coerce_float(row.get("longitude")),
                "opening_hours": row.get("opening_hours"),
                "opening_hours_available": _coerce_bool(row.get("opening_hours_available")),
                "price_range": row.get("price_range_label"),
                "price_min_idr": _coerce_int(row.get("price_min_idr"), None),
                "price_max_idr": _coerce_int(row.get("price_max_idr"), None),
                "price_bucket": row.get("price_bucket"),
                "price_confidence": row.get("price_confidence"),
                "price_range_available": price_min is not None,
                "daya_tahan_produk": row.get("daya_tahan_produk_label"),
                "daya_tahan_produk_class": row.get("daya_tahan_produk_class"),
                "image_url": row.get("image_url"),
                "image_available": _coerce_bool(row.get("image_available")),
                "url": row.get("url"),
                "website": row.get("website"),
                "phone": row.get("phone"),
                "warnings": self._warnings_for_row(row),
                "score_breakdown": {
                    "rating_score": _coerce_float(row.get("rating_score"), 0.0),
                    "review_confidence_score": _coerce_float(row.get("review_confidence_score"), 0.0),
                    "product_aspect_score": _coerce_float(row.get("product_aspect_score"), 0.0),
                    "taste_score": _coerce_float(row.get("taste_score"), 0.0),
                    "price_signal_score": _coerce_float(row.get("price_signal_score"), 0.0),
                    "service_aspect_signal_score": _coerce_float(row.get("service_aspect_signal_score"), 0.0),
                    "packaging_score": _coerce_float(row.get("packaging_score"), 0.0),
                    "distance_score": None if distance_score is None else round(distance_score, 2),
                },
            }
            item["_manual_sort_group"] = manual_sort_group
            candidates.append(item)

        if sort_by == "nearest" and has_location:
            candidates.sort(key=lambda item: (item["distance_km"] is None, item["distance_km"] or 9999, -item["score"]))
        else:
            candidates.sort(key=lambda item: (item["_manual_sort_group"], -item["score"]))

        recommendations = []
        for index, item in enumerate(candidates[:top_k], start=1):
            item.pop("_manual_sort_group", None)
            item["rank"] = index
            recommendations.append(item)

        return {
            "status": "success",
            "query": query,
            "detected_categories": detected_categories,
            "total_candidates": len(self.rows),
            "eligible_candidates": sum(1 for row in self.rows if _coerce_bool(row.get("main_recommendation_eligible"))),
            "after_filtering": len(candidates),
            "sort_by": sort_by,
            "location_context": {
                "enabled": has_location,
                "user_lat": user_lat,
                "user_lon": user_lon,
                "max_distance_km": max_distance_km,
            },
            "price_context": {
                "enabled": effective_max_price is not None,
                "max_price": effective_max_price,
                "source": "query_or_payload" if effective_max_price is not None else None,
                "note": "Harga adalah estimasi manual, bukan harga resmi real-time.",
            },
            "query_context": {
                "product_specific_query": product_specific_query,
            },
            "coverage_warnings": {
                "thin_categories": [
                    category for category, count in self.category_counts.items() if count < 2
                ],
                "note": "Kategori tipis tetap boleh dipakai, tetapi jangan diklaim lengkap.",
            },
            "service_score_note": (
                "service_aspect_signal_score adalah sinyal topik dari review, "
                "bukan sentiment pelayanan final."
            ),
            "recommendations": recommendations,
        }
