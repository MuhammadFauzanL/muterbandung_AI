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
}


def _chat_tokens(text):
    raw_tokens = re.findall(r"[a-z0-9]+", _as_text(text).lower())
    return [re.sub(r"([a-z])\1{2,}", r"\1", token) for token in raw_tokens]


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
            raw_content = result.get("result", {}).get("response", "")
            if isinstance(raw_content, dict): raw_content = json.dumps(raw_content)
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

    if llm_output is None:
        llm_output = _fallback_llm_output(evidence_pack, message)
        parser_source = "deterministic_fallback"
        fallback_used = True

    validation = validate_llm_output(deepcopy(llm_output), evidence_pack)
    if not validation.get("valid"):
        llm_output = _fallback_llm_output(evidence_pack, message)
        validation = validate_llm_output(deepcopy(llm_output), evidence_pack)
        parser_source = "deterministic_fallback_after_validation"
        fallback_used = True
        if not llm_error:
            llm_error = "LLM output failed validation."

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
            "llm_error": llm_error,
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

