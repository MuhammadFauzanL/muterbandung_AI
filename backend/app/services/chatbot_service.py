import json
import os
import re
from copy import deepcopy

import requests

from app.services.llm_evidence_pack import build_llm_evidence_pack

# DAFTAR KEYWORD PENJAGA KONTEKS (Tourism-Related)
TOURISM_CONTEXT_KEYWORDS = {
    "wisata", "jalan-jalan", "liburan", "hotel", "penginapan", "villa", "guest house", 
    "makan", "kuliner", "cafe", "museum", "taman", "curug", "gunung", "alam", "dago", 
    "lembang", "bandung", "ciwidey", "tiket", "buka", "jarak", "rekomendasi", "cepot",
    "pijak", "muterbandung", "rute", "itinerary", "pagi", "siang", "malam"
}
GREETING_WORDS = {
    "halo", "hallo", "hello", "helo", "hai", "hi", "hey", "hei",
    "pagi", "siang", "sore", "malam", "punten", "permisi",
    "assalamualaikum", "salam",
}
GREETING_FILLER_WORDS = {
    "cepot", "kang", "teh", "a", "aa", "teteh", "admin", "min",
    "ai", "bandung", "muter", "muterbandung",
}


def _chat_tokens(text):
    raw_tokens = re.findall(r"[a-z0-9]+", _as_text(text).lower())
    return [_normalize_chat_token(token) for token in raw_tokens]


def _normalize_chat_token(token):
    token = re.sub(r"([a-z])\1{2,}", r"\1", _as_text(token).lower())
    if re.fullmatch(r"h+a+l+o+", token) or re.fullmatch(r"h+e+l+o+", token):
        return "halo"
    if re.fullmatch(r"h+a+i+", token):
        return "hai"
    if re.fullmatch(r"h+i+", token):
        return "hi"
    if re.fullmatch(r"h+e+y+", token):
        return "hey"
    return token


def _is_greeting_only(query):
    tokens = _chat_tokens(query)
    if not tokens:
        return False
    meaningful = [token for token in tokens if token not in GREETING_FILLER_WORDS]
    if not meaningful:
        return False
    return all(token in GREETING_WORDS for token in meaningful)

def _is_query_in_context(query):
    """Memeriksa apakah kueri user setidaknya mengandung satu kata kunci pariwisata."""
    if not query: return False
    q = _as_text(query).lower()
    # Izinkan sapaan pendek
    if len(q.split()) <= 2 and any(k in q for k in ["halo", "hi", "hai", "pagi", "siang", "sore", "malam"]):
        return True
    return any(keyword in q for keyword in TOURISM_CONTEXT_KEYWORDS)


def should_bypass_recommender(message):
    message = _as_text(message)
    if not message:
        return True
    return _is_greeting_only(message) or not _is_query_in_context(message)

from app.services.llm_guard import (
    OUTPUT_SCHEMA_VERSION,
    build_llm_prompt_guard,
    validate_llm_output,
)


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct"
ENABLE_ONLINE_LLM_VALUES = {"1", "true", "yes", "on"}


def _clean_env(value):
    if value is None:
        return ""
    return str(value).strip().strip('"').strip("'")


def _as_text(value, default=""):
    if value is None:
        return default
    text = str(value).strip()
    if text.lower() in {"", "none", "null", "nan"}:
        return default
    return text


def _candidate_summary(candidate):
    practical = candidate.get("practical_info") or {}
    media = candidate.get("media") or {}
    sentiment = candidate.get("sentiment") or {}
    return {
        "destination_id": candidate.get("destination_id"),
        "rank": candidate.get("rank"),
        "name": candidate.get("name"),
        "why": candidate.get("backend_reason")
        or "Cocok berdasarkan ranking backend dan filter yang aktif.",
        "price": practical.get("price") or "Tidak ada info",
        "opening_hours": practical.get("opening_hours") or {
            "weekday": "Tidak ada info",
            "weekend": "Tidak ada info",
        },
        "distance_label": practical.get("distance_label") or "",
        "sentiment_score": sentiment.get("score"),
        "adjusted_sentiment_score": sentiment.get("adjusted_score"),
        "sentiment_model_source": sentiment.get("model_source"),
        "review_confidence": sentiment.get("review_confidence"),
        "review_confidence_label": sentiment.get("review_confidence_label"),
        "media": {
            "available": bool(media.get("available")),
            "image_url": media.get("image_url") or "",
            "destination_url": media.get("destination_url") or "",
            "website": media.get("website") or "",
            "source": media.get("source") or "",
            "match_title": media.get("match_title") or "",
            "match_score": media.get("match_score"),
            "audit_status": media.get("audit_status") or "",
        },
        "realworld_flags": candidate.get("realworld_flags") or {},
        "limitations": candidate.get("limitations") or [],
    }


def _compact_recommendations(evidence_pack):
    recommendations = []
    for candidate in (evidence_pack.get("candidates") or []):
        practical = candidate.get("practical_info") or {}
        sentiment = candidate.get("sentiment") or {}
        recommendations.append(
            {
                "destination_id": candidate.get("destination_id"),
                "rank": candidate.get("rank"),
                "name": candidate.get("name"),
                "category": candidate.get("category"),
                "price": practical.get("price") or "Tidak ada info",
                "opening_hours": practical.get("opening_hours") or {},
                "distance_label": practical.get("distance_label") or "",
                "sentiment_score": sentiment.get("score"),
                "adjusted_sentiment_score": sentiment.get("adjusted_score"),
                "review_confidence_label": sentiment.get("review_confidence_label"),
                "limitations": candidate.get("limitations") or [],
            }
        )
    return recommendations


def _is_lodging_query(message):
    text = _as_text(message).lower()
    return any(
        keyword in text
        for keyword in (
            "hotel",
            "penginapan",
            "villa",
            "guest house",
            "kost",
            "hostel",
            "losmen",
            "staycation",
            "kamar",
        )
    )


def _build_lodging_recommendation_response(message, top_k=5):
    try:
        from app.services.penginapan_service import penginapan_service
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Penginapan service unavailable: {exc}",
            "recommendations": [],
        }

    lodgings = penginapan_service.search_penginapans(query=message, limit=top_k)
    recommendations = []
    for index, lodging in enumerate(lodgings, 1):
        coordinates = lodging.get("coordinates") or {}
        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")
        sentiment = lodging.get("ai_insight") or {}
        rating = lodging.get("google_rating") or 0
        confidence = min(max(float(rating or 0) / 5.0, 0.0), 1.0)
        recommendations.append({
            "location_id": f"PENG-{lodging.get('penginapan_id') or index}",
            "location_name": lodging.get("name") or f"Penginapan {index}",
            "category": "Penginapan",
            "subcategory": lodging.get("type") or "Penginapan",
            "rank": index,
            "final_score": round((float(rating or 0) / 5.0) * 100, 2),
            "label_taxonomy": {
                "primary_intent": "penginapan",
                "core_labels": ["penginapan"],
                "secondary_labels": [lodging.get("type") or "Penginapan"],
            },
            "multi_labels": ["penginapan", lodging.get("type") or "Penginapan"],
            "info_praktis": {
                "harga": lodging.get("price") or "Hubungi untuk harga",
                "jam_buka_weekday": "Tidak ada info",
                "jam_buka_weekend": "Tidak ada info",
                "estimasi_durasi": "Tidak ada info",
                "koordinat": [latitude, longitude] if latitude and longitude else [],
            },
            "media": {
                "image_url": lodging.get("image_url") or "",
                "destination_url": lodging.get("destination_url") or "",
                "website": lodging.get("website") or "",
                "source": "penginapan_dataset",
                "match_title": lodging.get("name") or "",
                "match_score": 1.0,
                "audit_status": "curated",
            },
            "media_image_url": lodging.get("image_url") or "",
            "media_destination_url": lodging.get("destination_url") or "",
            "media_website": lodging.get("website") or "",
            "media_source": "penginapan_dataset",
            "media_match_title": lodging.get("name") or "",
            "media_match_score": 1.0,
            "media_audit_status": "curated",
            "distance_km": lodging.get("distance_km"),
            "distance_label": (
                f"{lodging.get('distance_km'):.1f} km dari lokasi Anda"
                if lodging.get("distance_km") is not None
                else ""
            ),
            "score_breakdown": {
                "google_rating": rating,
                "confidence": confidence,
                "sentiment_score": sentiment.get("sentiment_score"),
                "adjusted_sentiment_score": sentiment.get("sentiment_score"),
                "sentiment_label": sentiment.get("sentiment_label"),
                "sentiment_available": sentiment.get("sentiment_score") is not None,
                "review_confidence": confidence,
                "review_confidence_label": "penginapan_dataset",
            },
            "sentiment_metadata": {
                "sentiment_score": sentiment.get("sentiment_score"),
                "adjusted_sentiment_score": sentiment.get("sentiment_score"),
                "sentiment_label": sentiment.get("sentiment_label"),
                "sentiment_model_source": "penginapan_dataset",
                "review_confidence": confidence,
                "review_confidence_label": "penginapan_dataset",
                "sentiment_available": sentiment.get("sentiment_score") is not None,
            },
            "realworld_flags": {
                "is_active_verified": True,
                "price_verified": lodging.get("price") not in ("", "Hubungi untuk harga"),
                "coordinate_verified": bool(latitude and longitude),
                "parking_verified": False,
                "wheelchair_accessible_verified": False,
                "toilet_verified": False,
                "mushola_verified": False,
                "pet_friendly_verified": False,
                "child_friendly_verified": False,
                "safety_verified": False,
                "open_24h_verified": False,
                "crowd_level": "unknown",
            },
            "alasan": (
                f"{lodging.get('name')} cocok sebagai opsi penginapan dari dataset penginapan MuterBandung, "
                f"dengan rating Google {rating} dan harga {lodging.get('price') or 'Hubungi untuk harga'}."
            ),
        })

    return {
        "status": "success",
        "query": message,
        "mode": "penginapan_support",
        "recommendations": recommendations,
    }


def _fallback_llm_output(evidence_pack, message):
    candidates = evidence_pack.get("candidates") or []
    selected = candidates[:3]
    selected_ids = [item.get("destination_id") for item in selected if item.get("destination_id")]
    names = [item.get("name") for item in selected if item.get("name")]

    if names:
        answer = (
            "Berdasarkan data MuterBandung yang tersedia, pilihan teratas untuk pertanyaan Anda adalah "
            f"{', '.join(names)}. Saya tetap memakai harga, jarak, rating, dan sentiment dari hasil ranking backend."
        )
    else:
        answer = (
            "Saya belum menemukan kandidat yang cukup kuat dari data MuterBandung untuk pertanyaan itu. "
            "Coba sebutkan area, budget, atau jenis wisata yang lebih spesifik."
        )

    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "answer": answer,
        "selected_destination_ids": selected_ids,
        "destination_summaries": [_candidate_summary(item) for item in selected],
        "warnings": ["llm_online_fallback_used"],
        "follow_up_question": "Mau saya persempit berdasarkan area, budget, atau jenis wisata?",
    }


def _coerce_llm_object(llm_output):
    if isinstance(llm_output, dict):
        return deepcopy(llm_output)
    return _extract_json_object(llm_output)


def _norm_lookup(value):
    return re.sub(r"[^a-z0-9]+", "", _as_text(value).lower())


def _ground_llm_output_to_evidence(llm_output, evidence_pack, use_llm_text=True):
    raw_text = _as_text(llm_output)
    parsed = _coerce_llm_object(llm_output)
    parsed_was_valid = isinstance(parsed, dict)
    if not parsed_was_valid:
        parsed = {}

    candidates = evidence_pack.get("candidates") or []
    candidate_by_id = {
        _as_text(candidate.get("destination_id")): candidate
        for candidate in candidates
        if _as_text(candidate.get("destination_id"))
    }
    candidate_id_by_name = {
        _norm_lookup(candidate.get("name")): destination_id
        for destination_id, candidate in candidate_by_id.items()
        if _norm_lookup(candidate.get("name"))
    }
    ranking_policy = evidence_pack.get("ranking_policy") or {}
    allowed_ids = [
        _as_text(item)
        for item in ranking_policy.get("allowed_destination_ids", [])
        if _as_text(item)
    ]
    if not allowed_ids:
        return None

    requested_ids = []

    def add_requested_candidate(value):
        value = _as_text(value)
        if not value:
            return
        value_lookup = _norm_lookup(value)
        destination_id = value if value in candidate_by_id else candidate_id_by_name.get(value_lookup)
        if not destination_id:
            for candidate_id, candidate in candidate_by_id.items():
                candidate_id_lookup = _norm_lookup(candidate_id)
                candidate_name_lookup = _norm_lookup(candidate.get("name"))
                if (
                    candidate_id_lookup
                    and candidate_id_lookup in value_lookup
                ) or (
                    candidate_name_lookup
                    and (candidate_name_lookup in value_lookup or value_lookup in candidate_name_lookup)
                ):
                    destination_id = candidate_id
                    break
        if destination_id and destination_id not in requested_ids:
            requested_ids.append(destination_id)

    for item in parsed.get("selected_destination_ids", []) or []:
        if isinstance(item, dict):
            for key in ("destination_id", "location_id", "id", "name", "title", "destination_name", "location_name"):
                add_requested_candidate(item.get(key))
        else:
            add_requested_candidate(item)

    candidate_lists = (
        parsed.get("destination_summaries"),
        parsed.get("recommendations"),
        parsed.get("destinations"),
        parsed.get("places"),
    )
    for candidate_list in candidate_lists:
        if isinstance(candidate_list, dict):
            candidate_list = list(candidate_list.values())
        if not isinstance(candidate_list, list):
            continue
        for summary in candidate_list:
            if isinstance(summary, dict):
                for key in ("destination_id", "location_id", "id", "name", "title", "destination_name", "location_name"):
                    add_requested_candidate(summary.get(key))
            else:
                add_requested_candidate(summary)

    answer_lookup = _norm_lookup(parsed.get("answer") or raw_text)
    if answer_lookup:
        for name_lookup, destination_id in candidate_id_by_name.items():
            if name_lookup and name_lookup in answer_lookup:
                add_requested_candidate(destination_id)

    if not requested_ids:
        if parsed_was_valid:
            return None
        requested_ids = list(allowed_ids)

    if not parsed_was_valid:
        for destination_id in allowed_ids:
            if destination_id not in requested_ids:
                requested_ids.append(destination_id)

    if ranking_policy.get("llm_may_rerank") is False:
        selected_ids = [item for item in allowed_ids if item in requested_ids]
    else:
        selected_ids = []
        for item in requested_ids:
            if item not in selected_ids and item in allowed_ids:
                selected_ids.append(item)
    if not selected_ids:
        return None

    why_by_id = {}
    for candidate_list in candidate_lists:
        if isinstance(candidate_list, dict):
            candidate_list = list(candidate_list.values())
        if not isinstance(candidate_list, list):
            continue
        for summary in candidate_list:
            if not isinstance(summary, dict):
                continue
            why = _as_text(summary.get("why") or summary.get("reason") or summary.get("alasan"))
            if not why:
                continue
            resolved_ids = []
            for key in ("destination_id", "location_id", "id", "name", "title", "destination_name", "location_name"):
                value = _as_text(summary.get(key))
                destination_id = value if value in candidate_by_id else candidate_id_by_name.get(_norm_lookup(value))
                if destination_id and destination_id not in resolved_ids:
                    resolved_ids.append(destination_id)
            for destination_id in resolved_ids:
                why_by_id[destination_id] = why

    grounded_summaries = []
    for destination_id in selected_ids:
        summary = _candidate_summary(candidate_by_id[destination_id])
        if use_llm_text and why_by_id.get(destination_id):
            summary["why"] = why_by_id[destination_id]
        grounded_summaries.append(summary)

    answer = _as_text(parsed.get("answer")) if use_llm_text else ""
    if not answer:
        names = [summary.get("name") for summary in grounded_summaries if summary.get("name")]
        answer = (
            "Siap, Cepot nemu beberapa pilihan yang paling relevan dari data MuterBandung: "
            f"{', '.join(names)}. Mau saya bantu persempit lagi berdasarkan budget, area, atau jam kunjungan?"
        )

    warnings = parsed.get("warnings") if isinstance(parsed.get("warnings"), list) else []
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "answer": answer,
        "selected_destination_ids": selected_ids,
        "destination_summaries": grounded_summaries,
        "warnings": warnings,
        "follow_up_question": parsed.get("follow_up_question"),
    }


def _summarize_llm_shape(llm_output):
    parsed = _coerce_llm_object(llm_output)
    if not isinstance(parsed, dict):
        return {"parsed": False}

    summaries = parsed.get("destination_summaries")
    if isinstance(summaries, dict):
        summaries = list(summaries.values())
    if not isinstance(summaries, list):
        summaries = []

    compact_summaries = []
    for summary in summaries[:5]:
        if isinstance(summary, dict):
            compact_summaries.append({
                "keys": sorted(summary.keys()),
                "destination_id": _as_text(summary.get("destination_id")),
                "name": _as_text(summary.get("name")),
                "title": _as_text(summary.get("title")),
            })
        else:
            compact_summaries.append({"value": _as_text(summary)})

    return {
        "parsed": True,
        "keys": sorted(parsed.keys()),
        "selected_destination_ids": parsed.get("selected_destination_ids"),
        "destination_summaries": compact_summaries,
    }


def _extract_json_object(text):
    text = _as_text(text)
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None



def _call_cloudflare_ai(message, evidence_pack, prompt_guard):
    account_id = _clean_env(os.getenv("CLOUDFLARE_ACCOUNT_ID"))
    api_token = _clean_env(os.getenv("CLOUDFLARE_API_TOKEN"))
    if not account_id or not api_token:
        return None, "Cloudflare credentials not configured."
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    system_msg = prompt_guard.get("system_prompt", "") + "\nKembalikan JSON valid saja sesuai output_contract."
    user_content = json.dumps({
        "user_message": message,
        "llm_evidence_pack": evidence_pack,
        "output_contract": prompt_guard.get("output_contract"),
    }, ensure_ascii=False)

    payload = {
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        if response.status_code == 200:
            result = response.json()
            result_payload = result.get("result", {})
            raw_content = result_payload.get("response", "")
            if not raw_content:
                choices = result_payload.get("choices") or []
                if choices:
                    raw_content = ((choices[0].get("message") or {}).get("content")) or ""
            if isinstance(raw_content, dict):
                raw_content = json.dumps(raw_content)
            return raw_content, None
        return None, f"Cloudflare returned {response.status_code}"
    except Exception as e:
        return None, str(e)

def _call_llm_with_failover(message, evidence_pack, prompt_guard):
    # Try Cloudflare first
    print("[LLM] Attempting Layer 1 (Cloudflare) for Chat/RAG...")
    output, error = _call_cloudflare_ai(message, evidence_pack, prompt_guard)
    
    if output:
        return output, None, "cloudflare"
        
    # Fallback to OpenRouter
    print(f"[LLM] Layer 1 Failed ({error}). Switching to Layer 2 (OpenRouter)...")
    output, error = _call_openrouter(message, evidence_pack, prompt_guard)
    return output, error, "openrouter"

def _call_openrouter(message, evidence_pack, prompt_guard):
    online_llm_enabled = _clean_env(os.getenv("MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM")).lower()
    if online_llm_enabled not in ENABLE_ONLINE_LLM_VALUES:
        return None, "Online chat LLM is disabled; using grounded local fallback."

    api_key = _clean_env(os.getenv("OPENROUTER_API_KEY"))
    if not api_key:
        return None, "OPENROUTER_API_KEY is not configured."

    model = _clean_env(os.getenv("OPENROUTER_MODEL")) or DEFAULT_OPENROUTER_MODEL
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": prompt_guard.get("system_prompt", "")
                + "\nKembalikan JSON valid saja sesuai output_contract.",
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_message": message,
                        "llm_evidence_pack": evidence_pack,
                        "output_contract": prompt_guard.get("output_contract"),
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:3000",
        "X-Title": "MuterBandung",
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=6,
        )
    except requests.RequestException as exc:
        return None, f"LLM request failed: {exc}"

    if response.status_code >= 400:
        return None, f"LLM returned HTTP {response.status_code}: {response.text[:300]}"

    try:
        data = response.json()
    except ValueError:
        return None, "LLM response is not valid JSON."

    choices = data.get("choices") or []
    if not choices:
        return None, "LLM response has no choices."
    content = ((choices[0].get("message") or {}).get("content")) or ""
    parsed = _extract_json_object(content)
    if not parsed:
        return None, "LLM content did not contain a valid JSON object."
    return parsed, None



def build_chat_response(message, engine, top_k=5, persona_context=None, behaviour_context=None):
    message = _as_text(message)
    if not message:
        return {
            "status": "error",
            "message": "message is required.",
            "errors": ["message is required."],
        }, 400

    if _is_greeting_only(message):
        return {
            "status": "success",
            "message": message,
            "answer": (
                "Halo! Cepot siap bantu. Mau cari wisata, penginapan, rute, atau itinerary "
                "di Bandung? Sebutkan area, budget, atau jenis tempat yang kamu mau."
            ),
            "recommendations": [],
            "llm_output": None,
            "llm_validation": {"valid": True, "errors": []},
            "metadata": {
                "llm_used": False,
                "fallback_used": False,
                "source": "greeting_guard",
                "greeting_only": True,
                "allowed_destination_ids": [],
            },
        }, 200
    
    # --- HARD CONTEXT GUARDRAIL ---
    if not _is_query_in_context(message):
        print(f"[SECURITY] Query out of context blocked: {message}")
        return {
            "status": "success",
            "message": message,
            "answer": "Aduh hapunten pisan A/Teteh, Cepot mah cuma ngartos soal wisata sareng penginapan di MuterBandung wae euy. Tanya anu sanesna yuk!",
            "recommendations": [],
            "llm_rag_used": False,
            "llm_rag_error": "Out of context query blocked by Backend Guardrail"
        }, 200
    # ------------------------------

    if _is_lodging_query(message):
        recommendation_response = _build_lodging_recommendation_response(message, top_k=top_k)
    else:
        recommendation_response = engine.recommend(
            query=message,
            top_k=top_k,
            explain=True,
            persona_context=persona_context,
            behaviour_context=behaviour_context,
        )
    evidence_pack = build_llm_evidence_pack(recommendation_response)
    prompt_guard = build_llm_prompt_guard(evidence_pack)

    llm_output, llm_error, parser_source = _call_llm_with_failover(message, evidence_pack, prompt_guard)
    # parser_source handled by failover
    fallback_used = False
    raw_llm_output = deepcopy(llm_output)

    if llm_output is None:
        llm_output = _fallback_llm_output(evidence_pack, message)
        parser_source = "deterministic_fallback"
        fallback_used = True

    validation = validate_llm_output(deepcopy(llm_output), evidence_pack)
    repair_used = False
    original_validation_errors = []
    if not validation.get("valid"):
        original_validation_errors = validation.get("errors", [])
        repaired_output = _ground_llm_output_to_evidence(llm_output, evidence_pack)
        if repaired_output is not None:
            repaired_validation = validate_llm_output(deepcopy(repaired_output), evidence_pack)
            if repaired_validation.get("valid"):
                llm_output = repaired_output
                validation = repaired_validation
                parser_source = f"{parser_source}_grounded_repair"
                repair_used = True
            else:
                safe_repaired_output = _ground_llm_output_to_evidence(
                    llm_output,
                    evidence_pack,
                    use_llm_text=False,
                )
                if safe_repaired_output is not None:
                    safe_repaired_validation = validate_llm_output(deepcopy(safe_repaired_output), evidence_pack)
                    if safe_repaired_validation.get("valid"):
                        llm_output = safe_repaired_output
                        validation = safe_repaired_validation
                        parser_source = f"{parser_source}_grounded_repair_safe"
                        repair_used = True

        if not validation.get("valid"):
            llm_output = _fallback_llm_output(evidence_pack, message)
            validation = validate_llm_output(deepcopy(llm_output), evidence_pack)
            parser_source = "deterministic_fallback_after_validation"
            fallback_used = True
            if not llm_error:
                llm_error = "LLM output failed validation."
        elif not llm_error and original_validation_errors:
            llm_error = "LLM output was grounded to evidence after validation errors: " + "; ".join(original_validation_errors[:3])

    sanitized = validation.get("sanitized_output") or llm_output

    return {
        "status": "success",
        "message": message,
        "answer": sanitized.get("answer", ""),
        "llm_output": sanitized,
        "llm_validation": validation,
        "recommendations": _compact_recommendations(evidence_pack),
        "metadata": {
            "llm_used": not fallback_used,
            "fallback_used": fallback_used,
            "source": parser_source,
            "llm_repair_used": repair_used,
            "llm_error": llm_error,
            "llm_validation_errors_before_repair": original_validation_errors[:5],
            "llm_shape": _summarize_llm_shape(raw_llm_output) if fallback_used else None,
            "allowed_destination_ids": evidence_pack.get("ranking_policy", {}).get("allowed_destination_ids", []),
        },
    }, 200

def build_rag_recommendation(message, recommendation_response):
    """
    Takes an existing recommendation_response (from engine.recommend)
    and uses LLM to augment the explanations (RAG).
    Returns the augmented recommendation_response.
    """
    message = _as_text(message)
    if not message:
        return recommendation_response

    evidence_pack = build_llm_evidence_pack(recommendation_response)
    prompt_guard = build_llm_prompt_guard(evidence_pack)

    llm_output, llm_error, parser_source = _call_llm_with_failover(message, evidence_pack, prompt_guard)
    print(f"[RAG] OpenRouter returned: {llm_output}")
    print(f"[RAG] OpenRouter error: {llm_error}")
    fallback_used = False

    if llm_output is None:
        llm_output = _fallback_llm_output(evidence_pack, message)
        fallback_used = True

    validation = validate_llm_output(deepcopy(llm_output), evidence_pack)
    print(f"[RAG] Validation result: {validation.get('valid')}, errors: {validation.get('errors')}")
    if not validation.get("valid"):
        llm_output = _fallback_llm_output(evidence_pack, message)
        validation = validate_llm_output(deepcopy(llm_output), evidence_pack)
        fallback_used = True
        if not llm_error:
            llm_error = "LLM output failed validation: " + str(validation.get("errors"))

    sanitized = validation.get("sanitized_output") or llm_output

    # Augment the original recommendations with LLM's 'why'
    summaries = {
        _as_text(summary.get("destination_id")): summary.get("why")
        for summary in sanitized.get("destination_summaries", [])
        if summary.get("destination_id") and summary.get("why")
    }

    if "recommendations" in recommendation_response:
        for rec in recommendation_response["recommendations"]:
            dest_id = str(rec.get("location_id", ""))
            if dest_id in summaries:
                rec["alasan"] = summaries[dest_id]

    recommendation_response["llm_rag_used"] = not fallback_used
    if fallback_used:
        recommendation_response["llm_rag_error"] = llm_error

    return recommendation_response

