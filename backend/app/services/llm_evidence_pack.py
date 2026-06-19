import math
import re


EVIDENCE_PACK_SCHEMA_VERSION = "muterbandung.llm_evidence_pack.v1"

FACILITY_VERIFICATION_FLAGS = (
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
    "child_friendly_verified",
)


def _is_nan(value):
    try:
        return isinstance(value, float) and math.isnan(value)
    except TypeError:
        return False


def _clean_value(value):
    """Return JSON-safe evidence values without NaN/inf leakage."""
    if value is None or _is_nan(value):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {
            str(key): _clean_value(item)
            for key, item in value.items()
            if _clean_value(item) is not None
        }
    if isinstance(value, (list, tuple, set)):
        return [_clean_value(item) for item in value if _clean_value(item) is not None]
    return value


def _as_text(value, default=""):
    value = _clean_value(value)
    if value is None:
        return default
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return default
    return text


def _as_url(value):
    text = _as_text(value)
    if re.match(r"^https?://", text, flags=re.IGNORECASE):
        return text
    return ""


def _first_url(*values):
    for value in values:
        url = _as_url(value)
        if url:
            return url
    return ""


def _as_list(value):
    value = _clean_value(value)
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item not in (None, "")]
    return [value]


def _round_number(value, digits=4):
    value = _clean_value(value)
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return round(parsed, digits)


def _slugify(value):
    text = _as_text(value, "unknown").lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def _destination_id(item):
    explicit_id = _as_text(item.get("location_id"))
    if explicit_id:
        return explicit_id
    rank = item.get("rank") or "x"
    return f"rank_{rank}_{_slugify(item.get('location_name'))}"


def _build_media(item):
    media = item.get("media") or {}
    if not isinstance(media, dict):
        media = {}

    image_url = _first_url(
        item.get("media_image_url"),
        item.get("image_url"),
        item.get("imageUrl"),
        media.get("image_url"),
        media.get("imageUrl"),
    )
    destination_url = _first_url(
        item.get("media_destination_url"),
        item.get("destination_url"),
        item.get("google_maps_url"),
        item.get("location_url"),
        item.get("url"),
        media.get("destination_url"),
        media.get("google_maps_url"),
        media.get("location_url"),
        media.get("url"),
    )
    website = _first_url(
        item.get("media_website"),
        item.get("website"),
        item.get("official_website"),
        media.get("website"),
        media.get("official_website"),
    )
    available = bool(image_url or destination_url or website)
    source = _as_text(media.get("source") or item.get("media_source"))
    if not source:
        source = "curated_dataset" if available else "not_available_in_curated_dataset"

    return {
        "available": available,
        "image_url": image_url,
        "destination_url": destination_url,
        "website": website,
        "source": source,
        "match_title": _as_text(media.get("match_title") or item.get("media_match_title")),
        "match_score": _round_number(media.get("match_score") or item.get("media_match_score"), 4),
        "audit_status": _as_text(media.get("audit_status") or item.get("media_audit_status")),
    }


def _has_any_true_flag(flags, flag_names):
    return any(flags.get(name) is True for name in flag_names)


def _candidate_labels(item):
    taxonomy = item.get("label_taxonomy") or {}
    labels = []
    labels.extend(_as_list(item.get("multi_labels")))
    labels.extend(_as_list(taxonomy.get("core_labels")))
    labels.extend(_as_list(taxonomy.get("secondary_labels")))
    primary_intent = _as_text(taxonomy.get("primary_intent"))
    if primary_intent:
        labels.append(primary_intent)
    return {str(label).strip().lower() for label in labels if _as_text(label)}


def _hour_text_is_incomplete(value):
    text = _as_text(value).strip().lower()
    return (
        not text
        or text in {"tutup", "n/a", "na", "-"}
        or "tidak ada info" in text
    )


def _candidate_limitations(item):
    limitations = [
        "Harga bersifat estimasi/kurasi dan dapat berubah.",
        "Jam buka perlu dicek ulang sebelum berangkat.",
    ]
    if item.get("distance_km") is None:
        limitations.append("Jarak tidak dihitung karena lokasi user tidak tersedia atau tidak digunakan.")

    sentiment = item.get("sentiment_metadata") or {}
    score_breakdown = item.get("score_breakdown") or {}
    sentiment_available = sentiment.get("sentiment_available")
    if sentiment_available is None:
        sentiment_available = score_breakdown.get("sentiment_available")
    if sentiment_available is False:
        limitations.append("Sentiment ulasan belum tersedia untuk destinasi ini.")

    media = _build_media(item)
    if not media.get("available"):
        limitations.append("Media/gambar belum tersedia atau belum terverifikasi untuk destinasi ini.")

    info = item.get("info_praktis") or {}
    if _hour_text_is_incomplete(info.get("jam_buka_weekday")) or _hour_text_is_incomplete(info.get("jam_buka_weekend")):
        limitations.append("Jam buka belum lengkap untuk sebagian hari.")

    flags = item.get("realworld_flags") or {}
    labels = _candidate_labels(item)
    if flags.get("is_active_verified") is not True:
        limitations.append("Status aktif destinasi belum terverifikasi penuh.")
    if flags.get("price_verified") is not True:
        limitations.append("Harga belum terverifikasi penuh.")
    if flags.get("coordinate_verified") is False:
        limitations.append("Koordinat destinasi belum terverifikasi penuh.")
    if flags.get("safety_verified") is False:
        limitations.append("Data keamanan belum terverifikasi sebagai aman untuk semua konteks.")
    if not _has_any_true_flag(flags, FACILITY_VERIFICATION_FLAGS):
        limitations.append("Detail fasilitas belum terverifikasi; jangan menyebut fasilitas spesifik kecuali flag terkait bernilai true.")
    if "malam" in labels and flags.get("night_verified") is not True:
        limitations.append("Kelayakan kunjungan malam belum terverifikasi penuh.")
    if "indoor" in labels and flags.get("indoor_verified") is not True:
        limitations.append("Status indoor belum terverifikasi penuh.")
    if ({"keluarga", "ramah anak"} & labels) and flags.get("child_friendly_verified") is not True:
        limitations.append("Klaim ramah anak belum terverifikasi penuh.")
    return limitations


def _build_candidate(item):
    taxonomy = item.get("label_taxonomy") or {}
    info = item.get("info_praktis") or {}
    score_breakdown = item.get("score_breakdown") or {}
    sentiment = item.get("sentiment_metadata") or {}
    flags = item.get("realworld_flags") or {}

    sentiment_score = sentiment.get("sentiment_score")
    if sentiment_score is None:
        sentiment_score = score_breakdown.get("sentiment_score")
    adjusted_sentiment_score = sentiment.get("adjusted_sentiment_score")
    if adjusted_sentiment_score is None:
        adjusted_sentiment_score = score_breakdown.get("adjusted_sentiment_score")
    sentiment_used_for_ranking = score_breakdown.get("sentiment_used_for_ranking")
    if sentiment_used_for_ranking is None:
        sentiment_used_for_ranking = adjusted_sentiment_score if adjusted_sentiment_score is not None else sentiment_score
    review_confidence = sentiment.get("review_confidence")
    if review_confidence is None:
        review_confidence = score_breakdown.get("review_confidence", score_breakdown.get("confidence"))
    review_confidence_label = sentiment.get("review_confidence_label") or score_breakdown.get("review_confidence_label")

    candidate = {
        "destination_id": _destination_id(item),
        "rank": item.get("rank"),
        "name": _as_text(item.get("location_name")),
        "category": _as_text(item.get("category")),
        "primary_intent": _as_text(taxonomy.get("primary_intent")),
        "core_labels": _as_list(taxonomy.get("core_labels")),
        "secondary_labels": _as_list(taxonomy.get("secondary_labels")),
        "multi_labels": _as_list(item.get("multi_labels")),
        "final_score": _round_number(item.get("final_score"), 2),
        "practical_info": {
            "price": _as_text(info.get("harga"), "Tidak ada info"),
            "opening_hours": {
                "weekday": _as_text(info.get("jam_buka_weekday"), "Tidak ada info"),
                "weekend": _as_text(info.get("jam_buka_weekend"), "Tidak ada info"),
            },
            "duration": _as_text(info.get("estimasi_durasi"), "Tidak ada info"),
            "coordinates": _clean_value(info.get("koordinat")) or [],
            "distance_km": _round_number(item.get("distance_km"), 2),
            "distance_label": _as_text(item.get("distance_label")),
        },
        "media": _build_media(item),
        "sentiment": {
            "score": _round_number(sentiment_score, 4),
            "adjusted_score": _round_number(adjusted_sentiment_score, 4),
            "used_for_ranking": _round_number(sentiment_used_for_ranking, 4),
            "label": _as_text(sentiment.get("sentiment_label") or score_breakdown.get("sentiment_label")),
            "model_source": _as_text(sentiment.get("sentiment_model_source") or score_breakdown.get("sentiment_model_source")),
            "model_version": _as_text(sentiment.get("sentiment_model_version") or score_breakdown.get("sentiment_model_version")),
            "available": bool(sentiment.get("sentiment_available", score_breakdown.get("sentiment_available", False))),
            "review_count": int(score_breakdown.get("sentiment_review_count") or sentiment.get("sentiment_review_count") or 0),
            "review_confidence": _round_number(review_confidence, 4),
            "review_confidence_label": _as_text(review_confidence_label),
        },
        "realworld_flags": _clean_value(flags) or {},
        "score_signals": {
            "similarity": _round_number(score_breakdown.get("similarity"), 4),
            "google_rating": _round_number(score_breakdown.get("google_rating"), 2),
            "confidence": _round_number(score_breakdown.get("confidence"), 4),
            "review_confidence": _round_number(review_confidence, 4),
            "review_confidence_label": _as_text(review_confidence_label),
            "sentiment_used_for_ranking": _round_number(sentiment_used_for_ranking, 4),
            "matched_intents": _as_list(score_breakdown.get("matched_intents")),
            "penalized_intents": _as_list(score_breakdown.get("penalized_intents")),
            "distance_score": _round_number(score_breakdown.get("distance_score"), 4),
            "ranking_mode": _as_text(score_breakdown.get("ranking_mode")),
            "personalization_boost": _round_number(score_breakdown.get("personalization_boost"), 4),
            "personalization_applied": bool(score_breakdown.get("personalization_applied", False)),
            "persona_score": _round_number(score_breakdown.get("persona_score"), 4),
            "persona_boost": _round_number(score_breakdown.get("persona_boost"), 4),
            "persona_applied": bool(score_breakdown.get("persona_applied", False)),
            "persona_model_used": bool(score_breakdown.get("persona_model_used", False)),
            "persona_id": _as_text(score_breakdown.get("persona_id")),
            "persona_source": _as_text(score_breakdown.get("persona_source")),
            "persona_confidence": _round_number(score_breakdown.get("persona_confidence"), 4),
            "persona_matched_labels": _as_list(score_breakdown.get("persona_matched_labels")),
            "behaviour_score": _round_number(score_breakdown.get("behaviour_score"), 4),
            "behaviour_boost": _round_number(score_breakdown.get("behaviour_boost"), 4),
            "behaviour_applied": bool(score_breakdown.get("behaviour_applied", False)),
            "behaviour_model_used": bool(score_breakdown.get("behaviour_model_used", False)),
            "behaviour_model_source": _as_text(score_breakdown.get("behaviour_model_source")),
            "behaviour_fallback_used": bool(score_breakdown.get("behaviour_fallback_used", False)),
            "behaviour_matched_categories": _as_list(score_breakdown.get("behaviour_matched_categories")),
        },
        "limitations": _candidate_limitations(item),
    }
    return _clean_value(candidate)


def build_llm_evidence_pack(recommendation_response, max_candidates=5):
    """Build compact, auditable evidence for an LLM explanation layer."""
    recommendations = recommendation_response.get("recommendations") or []
    candidates = [_build_candidate(item) for item in recommendations[:max_candidates]]
    allowed_ids = [candidate["destination_id"] for candidate in candidates]

    return {
        "schema_version": EVIDENCE_PACK_SCHEMA_VERSION,
        "purpose": "Evidence for LLM explanation layer. Ranking remains controlled by backend.",
        "query": recommendation_response.get("query"),
        "backend_status": recommendation_response.get("status"),
        "ranking_policy": {
            "source": "deterministic_backend",
            "llm_may_explain": True,
            "llm_may_rerank": True,
            "llm_may_create_destinations": False,
            "allowed_destination_ids": allowed_ids,
        },
        "input_context": {
            "ai_intents": _clean_value(recommendation_response.get("ai_intents")) or {},
            "personalization": _clean_value(recommendation_response.get("personalization")) or {},
            "manual_filters": _clean_value(recommendation_response.get("manual_filters")) or {},
            "implicit_filters": _clean_value(recommendation_response.get("implicit_filters")) or {},
            "location_context": _clean_value(recommendation_response.get("location_context")) or {},
            "fallback": _clean_value(recommendation_response.get("fallback")) or {},
            "no_strong_match": _clean_value(recommendation_response.get("no_strong_match")) or {},
        },
        "source_fields": {
            "category": "Dataset curated",
            "labels": "Rule-based taxonomy plus manual review",
            "price": "Curated estimate from tourism metadata",
            "opening_hours": "Curated/scraped opening-hour metadata",
            "distance": "Backend-calculated distance only when user location or landmark is available",
            "sentiment": "Raw review sentiment plus Bayesian-adjusted sentiment and p95-capped review confidence",
            "media": "Curated media/link metadata only when present; otherwise unavailable",
            "realworld_flags": "Curated verification flags and audit overrides",
        },
        "global_limitations": [
            "LLM must only discuss destinations listed in allowed_destination_ids.",
            "LLM must not invent destinations, prices, distances, opening hours, ratings, or facilities.",
            "LLM must not invent image URLs, destination URLs, or websites.",
            "Image and destination URLs may be shown only when candidate.media.available is true.",
            "Prices and opening hours can change and should be rechecked before visiting.",
            "A false facility flag can mean unavailable or not verified in the dataset.",
            "Candidate limitations must be reflected in any user-facing explanation.",
            "Active sentiment source is tfidf_linearsvc, not IndoBERT.",
        ],
        "candidates": candidates,
    }
