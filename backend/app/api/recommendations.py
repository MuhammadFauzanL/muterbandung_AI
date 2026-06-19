"""
Recommendation endpoints.

- GET /recommendations/destinations — guest or personalized destination cards
"""

from __future__ import annotations

from typing import Any, Dict

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.security import get_optional_current_user
from app.database import get_db
from app.services.recommendation_service import get_recommended_destinations
from app.services.user_preference_service import get_user_preference
from app.utils.response import error_response, paginated_response, success_response

router = APIRouter(prefix="/recommendations")
_ai_recommender = None


def _get_ai_recommender():
    global _ai_recommender
    if _ai_recommender is None:
        from app.services.recommender import MuterBandungRecommender

        _ai_recommender = MuterBandungRecommender()
    return _ai_recommender


def _safe_int(value: Any, default: int, minimum: int = 1, maximum: int = 50) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _context_payload(payload: Dict[str, Any], key: str):
    value = payload.get(key)
    if isinstance(value, dict):
        return value
    return {}


def _build_persona_context(payload: Dict[str, Any]):
    provided = payload.get("persona_context")
    if isinstance(provided, dict):
        return provided

    persona_payload = _context_payload(payload, "persona_payload") or _context_payload(payload, "persona")
    if not persona_payload:
        return None
    if "persona" in persona_payload or "persona_id" in persona_payload:
        return persona_payload

    from app.services.persona_service import persona_service

    return persona_service.determine_home_persona(persona_payload)


def _build_behaviour_context(payload: Dict[str, Any]):
    provided = payload.get("behaviour_context") or payload.get("behavior_context")
    if isinstance(provided, dict):
        return provided

    behaviour_payload = (
        _context_payload(payload, "behaviour_payload")
        or _context_payload(payload, "behavior_payload")
        or _context_payload(payload, "behaviour")
        or _context_payload(payload, "behavior")
    )
    if not behaviour_payload:
        return None
    if "next_category_predictions" in behaviour_payload:
        return behaviour_payload

    from app.services.behaviour_service import behaviour_service

    return behaviour_service.predict_next_category(behaviour_payload)


@router.get("/destinations")
def recommended_destinations(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    current_user=Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Return destination recommendations for guest or logged-in users."""
    preference = None
    user_id = None
    if current_user is not None:
        user_id = current_user.id
        preference = get_user_preference(db, current_user.id)

    items, total = get_recommended_destinations(
        db,
        page=page,
        limit=limit,
        preference=preference,
        user_id=user_id,
    )

    message = (
        "Personalized recommendations retrieved successfully"
        if preference is not None
        else "Default recommendations retrieved successfully"
    )
    return paginated_response(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message=message,
    )


@router.post("/ai-planner")
def ai_planner_recommend(payload: Dict[str, Any] | None = Body(default=None)):
    """Return AI Planner recommendations with evidence-ready score_breakdown."""
    payload = payload or {}
    filters = payload.get("filters") if isinstance(payload.get("filters"), dict) else {}
    query = payload.get("query") or filters.get("search") or ""
    top_k = _safe_int(payload.get("top_k") or payload.get("limit") or filters.get("limit"), 5)

    engine = _get_ai_recommender()
    result = engine.recommend(
        query=query,
        categories=filters.get("categories") or filters.get("category"),
        max_price=filters.get("max_price") or filters.get("maxPrice"),
        min_rating=filters.get("min_rating") or filters.get("minRating"),
        free_only=bool(filters.get("free_only") or filters.get("freeOnly", False)),
        open_now=bool(filters.get("open_now") or filters.get("openNow", False)),
        day_type=filters.get("day_type") or filters.get("dayType"),
        open_at_hour=filters.get("open_at_hour") or filters.get("plannedTime"),
        user_lat=filters.get("user_lat") or filters.get("userLat"),
        user_lon=filters.get("user_lon") or filters.get("userLon") or filters.get("userLng"),
        max_distance_km=filters.get("max_distance_km") or filters.get("radiusKm"),
        sort_by=filters.get("sort") or payload.get("sort_by") or "balanced",
        top_k=top_k,
        explain=True,
        persona_context=_build_persona_context(payload),
        behaviour_context=_build_behaviour_context(payload),
    )
    return success_response(data=result, message="AI Planner recommendations retrieved successfully")


@router.post("/cepot-chat")
def cepot_chat(payload: Dict[str, Any] | None = Body(default=None)):
    """Return Cepot chat answer grounded by backend recommendation evidence."""
    payload = payload or {}
    message = str(payload.get("message") or payload.get("query") or "").strip()
    if not message:
        return JSONResponse(
            status_code=400,
            content=error_response(
                message="message is required.",
                status_code=400,
                errors=["message is required."],
            ),
        )
    top_k = _safe_int(payload.get("top_k") or payload.get("limit"), 5)

    from app.services.chatbot_service import build_chat_response, should_bypass_recommender

    engine = None if should_bypass_recommender(message) else _get_ai_recommender()

    response, _status = build_chat_response(
        message,
        engine,
        top_k=top_k,
        persona_context=_build_persona_context(payload),
        behaviour_context=_build_behaviour_context(payload),
    )
    if _status >= 400:
        return JSONResponse(
            status_code=_status,
            content=error_response(
                message=response.get("message", "Cepot request failed"),
                status_code=_status,
                errors=response.get("errors", []),
            ),
        )
    return success_response(data=response, message="Cepot response generated successfully")

