import copy
import json
import re


PROMPT_GUARD_SCHEMA_VERSION = "muterbandung.llm_prompt_guard.v1"
OUTPUT_SCHEMA_VERSION = "muterbandung.llm_output.v1"

TOP_LEVEL_REQUIRED_FIELDS = {
    "answer",
    "selected_destination_ids",
    "destination_summaries",
    "warnings",
}

SUMMARY_REQUIRED_FIELDS = {
    "destination_id",
    "rank",
    "name",
    "why",
    "price",
    "opening_hours",
    "distance_label",
    "media",
    "limitations",
}

SUMMARY_ALLOWED_FIELDS = SUMMARY_REQUIRED_FIELDS | {
    "sentiment_score",
    "adjusted_sentiment_score",
    "sentiment_model_source",
    "review_confidence",
    "review_confidence_label",
    "personalization_boost",
    "persona_score",
    "persona_source",
    "behaviour_score",
    "behaviour_model_source",
    "realworld_flags",
}

MEDIA_ALLOWED_FIELDS = {
    "available",
    "image_url",
    "destination_url",
    "website",
    "source",
    "match_title",
    "match_score",
    "audit_status",
}

PRICE_PATTERN = re.compile(
    r"\bRp\.?\s*\d[\d.,]*(?:\s*(?:-|sampai|hingga)\s*Rp?\.?\s*\d[\d.,]*)?",
    re.IGNORECASE,
)
DISTANCE_PATTERN = re.compile(r"\b\d+(?:[.,]\d+)?\s*km\b", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s\]\)\}\",]+", re.IGNORECASE)
RATING_PATTERN = re.compile(r"\b[1-5](?:[.,]\d{1,2})?\s*(?:/5|bintang)\b", re.IGNORECASE)

FACILITY_POSITIVE_PATTERNS = {
    "parking_verified": [
        r"\b(ada|tersedia|punya|memiliki|dilengkapi|menyediakan)\b.{0,40}\bparkir\b",
        r"\bparkir\b.{0,25}\b(ada|tersedia|luas|aman)\b",
    ],
    "toilet_verified": [
        r"\b(ada|tersedia|punya|memiliki|dilengkapi|menyediakan)\b.{0,40}\b(toilet|wc)\b",
        r"\b(toilet|wc)\b.{0,25}\b(ada|tersedia|bersih)\b",
    ],
    "mushola_verified": [
        r"\b(ada|tersedia|punya|memiliki|dilengkapi|menyediakan)\b.{0,40}\b(mushola|musala)\b",
        r"\b(mushola|musala)\b.{0,25}\b(ada|tersedia)\b",
    ],
    "wheelchair_accessible_verified": [
        r"\b(akses|ramah|fasilitas)\b.{0,35}\b(kursi roda|disabilitas|difabel)\b",
    ],
    "pet_friendly_verified": [
        r"\b(pet friendly|boleh bawa hewan|ramah hewan)\b",
    ],
    "open_24h_verified": [
        r"\b(buka|operasional)\b.{0,15}\b24\s*jam\b",
        r"\b24\s*jam\b.{0,20}\b(buka|operasional)\b",
    ],
}


def _as_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _norm(value):
    return re.sub(r"\s+", " ", _as_text(value).lower()).strip()


def _normalize_compact(value):
    return re.sub(r"\s+", "", _as_text(value).lower())


def _candidate_map(evidence_pack):
    candidates = evidence_pack.get("candidates") or []
    return {
        _as_text(candidate.get("destination_id")): candidate
        for candidate in candidates
        if _as_text(candidate.get("destination_id"))
    }


def _allowed_ids(evidence_pack):
    ranking_policy = evidence_pack.get("ranking_policy") or {}
    ids = ranking_policy.get("allowed_destination_ids") or []
    return [_as_text(item) for item in ids if _as_text(item)]


def _iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _all_output_text(parsed_output):
    return "\n".join(_iter_strings(parsed_output))


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _same_float(left, right, tolerance=0.0001):
    left_num = _safe_float(left)
    right_num = _safe_float(right)
    if left_num is None or right_num is None:
        return False
    return abs(left_num - right_num) <= tolerance


def _extract_allowed_urls(candidates):
    urls = set()
    for candidate in candidates:
        media = candidate.get("media") or {}
        for key in ("image_url", "destination_url", "website"):
            url = _as_text(media.get(key))
            if url:
                urls.add(url.rstrip(".,;"))
    return urls


def _extract_allowed_prices(candidates):
    prices = []
    for candidate in candidates:
        practical = candidate.get("practical_info") or {}
        price = _as_text(practical.get("price"))
        if price:
            prices.append(_normalize_compact(price))
    return prices


def _extract_allowed_distances(candidates):
    distances = []
    for candidate in candidates:
        practical = candidate.get("practical_info") or {}
        label = _as_text(practical.get("distance_label"))
        if label:
            distances.append(_normalize_compact(label))
    return distances


def _extract_allowed_ratings(candidates):
    ratings = []
    for candidate in candidates:
        score_signals = candidate.get("score_signals") or {}
        rating = score_signals.get("google_rating")
        if rating is not None:
            ratings.append(str(rating).replace(".", ","))
            ratings.append(str(rating).replace(",", "."))
    return ratings


def _parse_output(llm_output):
    if isinstance(llm_output, dict):
        return copy.deepcopy(llm_output), None
    if isinstance(llm_output, str):
        try:
            parsed = json.loads(llm_output)
        except ValueError as exc:
            return None, f"LLM output is not valid JSON: {exc}"
        if not isinstance(parsed, dict):
            return None, "LLM output JSON must be an object."
        return parsed, None
    return None, "llm_output must be a JSON string or object."


def _validate_media(summary, candidate, errors, path):
    media = summary.get("media")
    expected = candidate.get("media") or {}
    if not isinstance(media, dict):
        errors.append(f"{path}.media must be an object.")
        return

    unknown_fields = sorted(set(media) - MEDIA_ALLOWED_FIELDS)
    if unknown_fields:
        errors.append(f"{path}.media contains unsupported fields: {unknown_fields}.")

    if media.get("available") != expected.get("available"):
        errors.append(f"{path}.media.available must match evidence.")

    for key in ("image_url", "destination_url", "website", "source", "match_title", "audit_status"):
        actual = _as_text(media.get(key))
        expected_value = _as_text(expected.get(key))
        if actual != expected_value:
            errors.append(f"{path}.media.{key} must match evidence exactly.")

    if "match_score" in media or "match_score" in expected:
        if not _same_float(media.get("match_score"), expected.get("match_score")):
            errors.append(f"{path}.media.match_score must match evidence.")

    if expected.get("available") is not True:
        for key in ("image_url", "destination_url", "website"):
            if _as_text(media.get(key)):
                errors.append(f"{path}.media.{key} is not allowed because media.available is false.")


def _validate_summary(summary, candidate, errors, warnings, index):
    path = f"destination_summaries[{index}]"
    if not isinstance(summary, dict):
        errors.append(f"{path} must be an object.")
        return

    missing = sorted(SUMMARY_REQUIRED_FIELDS - set(summary))
    if missing:
        errors.append(f"{path} is missing required fields: {missing}.")

    unknown_fields = sorted(set(summary) - SUMMARY_ALLOWED_FIELDS)
    if unknown_fields:
        errors.append(f"{path} contains unsupported fields: {unknown_fields}.")

    if _as_text(summary.get("destination_id")) != _as_text(candidate.get("destination_id")):
        errors.append(f"{path}.destination_id must match selected_destination_ids order.")

    if _as_text(summary.get("name")) != _as_text(candidate.get("name")):
        errors.append(f"{path}.name must match evidence exactly.")

    practical = candidate.get("practical_info") or {}
    if _as_text(summary.get("price")) != _as_text(practical.get("price")):
        errors.append(f"{path}.price must match evidence exactly.")

    if _as_text(summary.get("distance_label")) != _as_text(practical.get("distance_label")):
        errors.append(f"{path}.distance_label must match evidence exactly.")

    opening = summary.get("opening_hours")
    expected_opening = practical.get("opening_hours") or {}
    if not isinstance(opening, dict):
        errors.append(f"{path}.opening_hours must be an object.")
    else:
        for key in ("weekday", "weekend"):
            if _as_text(opening.get(key)) != _as_text(expected_opening.get(key)):
                errors.append(f"{path}.opening_hours.{key} must match evidence exactly.")

    if "sentiment_score" in summary:
        expected_score = (candidate.get("sentiment") or {}).get("score")
        if not _same_float(summary.get("sentiment_score"), expected_score):
            errors.append(f"{path}.sentiment_score must match evidence.")

    if "adjusted_sentiment_score" in summary:
        expected_adjusted = (candidate.get("sentiment") or {}).get("adjusted_score")
        if not _same_float(summary.get("adjusted_sentiment_score"), expected_adjusted):
            errors.append(f"{path}.adjusted_sentiment_score must match evidence.")

    if "sentiment_model_source" in summary:
        expected_source = _as_text((candidate.get("sentiment") or {}).get("model_source"))
        if _as_text(summary.get("sentiment_model_source")) != expected_source:
            errors.append(f"{path}.sentiment_model_source must match evidence.")

    if "review_confidence" in summary:
        expected_confidence = (candidate.get("sentiment") or {}).get("review_confidence")
        if not _same_float(summary.get("review_confidence"), expected_confidence):
            errors.append(f"{path}.review_confidence must match evidence.")

    if "review_confidence_label" in summary:
        expected_label = _as_text((candidate.get("sentiment") or {}).get("review_confidence_label"))
        if _as_text(summary.get("review_confidence_label")) != expected_label:
            errors.append(f"{path}.review_confidence_label must match evidence.")

    score_signals = candidate.get("score_signals") or {}
    numeric_score_fields = ("personalization_boost", "persona_score", "behaviour_score")
    for field in numeric_score_fields:
        if field in summary and not _same_float(summary.get(field), score_signals.get(field)):
            errors.append(f"{path}.{field} must match evidence.")

    text_score_fields = ("persona_source", "behaviour_model_source")
    for field in text_score_fields:
        if field in summary and _as_text(summary.get(field)) != _as_text(score_signals.get(field)):
            errors.append(f"{path}.{field} must match evidence.")

    if "realworld_flags" in summary:
        flags = summary.get("realworld_flags")
        expected_flags = candidate.get("realworld_flags") or {}
        if not isinstance(flags, dict):
            errors.append(f"{path}.realworld_flags must be an object.")
        else:
            for key, value in flags.items():
                if key not in expected_flags:
                    errors.append(f"{path}.realworld_flags.{key} is not present in evidence.")
                elif value != expected_flags.get(key):
                    errors.append(f"{path}.realworld_flags.{key} must match evidence.")

    _validate_media(summary, candidate, errors, path)

    limitations = summary.get("limitations")
    if limitations is not None:
        expected_limitations = candidate.get("limitations") or []
        if not isinstance(limitations, list):
            errors.append(f"{path}.limitations must be a list.")
        else:
            for limitation in limitations:
                if limitation not in expected_limitations:
                    warnings.append(f"{path}.limitations contains text not copied from evidence: {limitation}")


def _validate_fact_claims(parsed_output, candidates, selected_candidates, errors):
    text = _all_output_text(parsed_output)
    normalized_text = _norm(text)

    allowed_urls = _extract_allowed_urls(candidates)
    for url in URL_PATTERN.findall(text):
        cleaned = url.rstrip(".,;")
        if cleaned not in allowed_urls:
            errors.append(f"Output contains URL not present in evidence: {cleaned}")

    allowed_prices = _extract_allowed_prices(candidates)
    for price in PRICE_PATTERN.findall(text):
        normalized_price = _normalize_compact(price)
        if not any(normalized_price in allowed for allowed in allowed_prices):
            errors.append(f"Output contains price not present in evidence: {price}")

    allowed_distances = _extract_allowed_distances(candidates)
    for distance in DISTANCE_PATTERN.findall(text):
        normalized_distance = _normalize_compact(distance)
        if not any(normalized_distance in allowed for allowed in allowed_distances):
            errors.append(f"Output contains distance not present in evidence: {distance}")

    allowed_ratings = _extract_allowed_ratings(candidates)
    for rating in RATING_PATTERN.findall(text):
        normalized_rating = rating.lower().replace(" ", "")
        if not any(allowed in normalized_rating for allowed in allowed_ratings):
            errors.append(f"Output contains rating not present in evidence: {rating}")

    candidates_for_facilities = selected_candidates or candidates
    for flag_name, patterns in FACILITY_POSITIVE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                if not candidates_for_facilities:
                    errors.append(f"Output claims {flag_name}, but no candidate evidence is selected.")
                    break
                if not all((candidate.get("realworld_flags") or {}).get(flag_name) is True for candidate in candidates_for_facilities):
                    errors.append(f"Output claims {flag_name}, but not all selected candidates verify it.")
                    break


def _sanitize_output(parsed_output):
    sanitized = {
        "schema_version": _as_text(parsed_output.get("schema_version") or OUTPUT_SCHEMA_VERSION),
        "answer": _as_text(parsed_output.get("answer")),
        "selected_destination_ids": [
            _as_text(item)
            for item in (parsed_output.get("selected_destination_ids") or [])
            if _as_text(item)
        ],
        "destination_summaries": [],
        "warnings": parsed_output.get("warnings") if isinstance(parsed_output.get("warnings"), list) else [],
        "follow_up_question": parsed_output.get("follow_up_question"),
    }
    for summary in parsed_output.get("destination_summaries") or []:
        if isinstance(summary, dict):
            sanitized["destination_summaries"].append({
                key: copy.deepcopy(summary.get(key))
                for key in SUMMARY_ALLOWED_FIELDS
                if key in summary
            })
    return sanitized


def build_llm_prompt_guard(evidence_pack):
    """Return prompt and output contract that keep an LLM tied to evidence."""
    allowed_destination_ids = _allowed_ids(evidence_pack)
    candidates = evidence_pack.get("candidates") or []
    allowed_names = [_as_text(candidate.get("name")) for candidate in candidates if _as_text(candidate.get("name"))]

    system_prompt = (
        "Anda adalah Cepot, asisten virtual lokal MuterBandung yang ramah, informatif, dan suka bergaya asyik (seperti guide lokal Sunda). "
        "Jawab HANYA berdasarkan llm_evidence_pack yang diberikan. "
        "Jangan membuat destinasi, harga, jarak, jam buka, rating, atau fasilitas baru. "
        "BATASAN KONTEKS MUTLAK: Anda adalah sistem khusus MuterBandung. Anda dilarang menjawab apa pun di luar pariwisata, penginapan, dan bantuan sistem. "
        "Jika user bertanya hal lain (resep, coding, politik, dll), Anda WAJIB memberikan jawaban penolakan di field 'answer' dan mengosongkan list 'selected_destination_ids'. "
        "JANGAN memaksakan data dari evidence_pack jika pertanyaannya tidak relevan. "
        "Contoh penolakan: 'Aduh hapunten pisan A/Teteh, Cepot mah cuma ngartos soal wisata sareng penginapan di MuterBandung wae euy. Tanya anu sanesna yuk!'. "
        "Tugas Anda: tulis deskripsi singkat (field 'why') untuk tiap tempat yang menjelaskan *kenapa* tempat itu cocok dengan query user. "
        "Gunakan bahasa natural, santai tapi profesional, dan JANGAN KAKU. Boleh pakai kata sapaan ringan (misal: 'Tempat ini pas banget buat kamu...', atau 'Cocok nih buat...'). "
        "Tulis maksimal 3-4 kalimat per destinasi. "
        "PASTIKAN semua JSON field dikembalikan dalam format yang diminta dan Anda BOLEH mengatur ulang urutan (rerank) destinasi sesuai pemahaman Anda tentang relevansinya."
    )

    example_shape = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "selected_destination_ids": ["LOC-123", "LOC-456"],
        "destination_summaries": [
            {
                "destination_id": "LOC-123",
                "rank": 1,
                "name": "Kawah Putih Ciwidey",
                "why": "Kawah Putih Ciwidey ini pas banget buat kamu yang lagi cari wisata alam dengan pemandangan magis. Banyak pengunjung yang terkesan dengan pesonanya (sentimen 89%), dan tempat ini juga punya rating tinggi lho!",
                "price": "Rp 28.000 (Per Orang)",
                "opening_hours": {
                    "weekday": "07:00 - 17:00",
                    "weekend": "07:00 - 17:00"
                },
                "distance_label": "35 km",
                "sentiment_score": 0.89,
                "adjusted_sentiment_score": 0.88,
                "sentiment_model_source": "tfidf_linearsvc",
                "review_confidence_label": "high_review_confidence",
                "media": {
                    "available": True,
                    "image_url": "https://example.com/kawah_putih.jpg",
                    "destination_url": "https://maps.google.com/?q=Kawah+Putih",
                    "website": "https://kawahputih.com",
                    "source": "google_maps_extractor"
                },
                "realworld_flags": {
                    "is_active_verified": True,
                    "price_verified": True,
                    "coordinate_verified": True,
                    "night_verified": False,
                    "indoor_verified": False,
                    "child_friendly_verified": True,
                    "parking_verified": True,
                    "wheelchair_accessible_verified": False,
                    "toilet_verified": True,
                    "mushola_verified": True,
                    "pet_friendly_verified": False,
                    "safety_verified": True,
                    "open_24h_verified": False,
                    "crowd_level": "unknown"
                },
                "limitations": [
                    "Harga bersifat estimasi/kurasi dan dapat berubah."
                ]
            }
        ],
        "warnings": [],
        "follow_up_question": "Mau cari tempat makan sekalian di dekat sana?"
    }

    return {
        "schema_version": PROMPT_GUARD_SCHEMA_VERSION,
        "language": "id",
        "system_prompt": system_prompt,
        "rules": [
            "Use only facts present in llm_evidence_pack.",
            "Do not create destinations outside allowed_destination_ids.",
            "Do not rerank candidates while llm_may_rerank is false.",
            "Copy prices, distances, opening hours, sentiment metadata, adjusted sentiment, personalization signals, media URLs, and flags exactly from evidence.",
            "Do not output image_url, destination_url, or website unless candidate.media.available is true.",
            "If a facility flag is false or missing, describe it as not verified instead of available.",
        ],
        "output_schema_version": OUTPUT_SCHEMA_VERSION,
        "allowed_destination_ids": allowed_destination_ids,
        "allowed_destination_names": allowed_names,
        "output_contract": {
            "format": "json_object",
            "required_top_level_fields": sorted(TOP_LEVEL_REQUIRED_FIELDS),
            "required_destination_summary_fields": sorted(SUMMARY_REQUIRED_FIELDS),
            "media_policy": "Media URLs may only be copied from candidate.media when media.available is true.",
            "example_shape": example_shape
        },
    }


def validate_llm_output(llm_output, evidence_pack):
    """Validate LLM JSON output against an evidence pack."""
    errors = []
    warnings = []

    if not isinstance(evidence_pack, dict):
        return {
            "valid": False,
            "errors": ["evidence_pack must be an object."],
            "warnings": [],
            "sanitized_output": None,
        }

    parsed_output, parse_error = _parse_output(llm_output)
    if parse_error:
        return {
            "valid": False,
            "errors": [parse_error],
            "warnings": [],
            "sanitized_output": None,
        }

    candidate_by_id = _candidate_map(evidence_pack)
    allowed_destination_ids = _allowed_ids(evidence_pack)
    candidates = [candidate_by_id[item] for item in allowed_destination_ids if item in candidate_by_id]
    ranking_policy = evidence_pack.get("ranking_policy") or {}

    missing_top_fields = sorted(TOP_LEVEL_REQUIRED_FIELDS - set(parsed_output))
    if missing_top_fields:
        errors.append(f"Output is missing required top-level fields: {missing_top_fields}.")

    if parsed_output.get("schema_version") and parsed_output.get("schema_version") != OUTPUT_SCHEMA_VERSION:
        errors.append(f"Unexpected output schema_version: {parsed_output.get('schema_version')}.")

    selected_ids = parsed_output.get("selected_destination_ids")
    if not isinstance(selected_ids, list):
        errors.append("selected_destination_ids must be a list.")
        selected_ids = []
    else:
        selected_ids = [_as_text(item) for item in selected_ids]

    if candidates and not selected_ids:
        errors.append("selected_destination_ids cannot be empty when evidence candidates are available.")

    if len(selected_ids) != len(set(selected_ids)):
        errors.append("selected_destination_ids contains duplicate ids.")

    unknown_ids = [item for item in selected_ids if item not in allowed_destination_ids]
    if unknown_ids:
        errors.append(f"selected_destination_ids contains ids not allowed by evidence: {unknown_ids}.")

    if ranking_policy.get("llm_may_rerank") is False:
        expected_prefix = allowed_destination_ids[:len(selected_ids)]
        if selected_ids != expected_prefix:
            errors.append("selected_destination_ids must preserve backend rank order and use the top-ranked prefix.")

    summaries = parsed_output.get("destination_summaries")
    if not isinstance(summaries, list):
        errors.append("destination_summaries must be a list.")
        summaries = []

    summary_ids = [
        _as_text(summary.get("destination_id"))
        for summary in summaries
        if isinstance(summary, dict)
    ]
    if summary_ids != selected_ids:
        errors.append("destination_summaries ids must exactly match selected_destination_ids.")

    selected_candidates = []
    for index, summary in enumerate(summaries):
        candidate_id = _as_text(summary.get("destination_id")) if isinstance(summary, dict) else ""
        candidate = candidate_by_id.get(candidate_id)
        if not candidate:
            errors.append(f"destination_summaries[{index}].destination_id is not in evidence.")
            continue
        selected_candidates.append(candidate)
        _validate_summary(summary, candidate, errors, warnings, index)

    if not isinstance(parsed_output.get("warnings", []), list):
        errors.append("warnings must be a list.")

    _validate_fact_claims(parsed_output, candidates, selected_candidates, errors)

    sanitized = _sanitize_output(parsed_output)
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "sanitized_output": sanitized if not errors else None,
    }
