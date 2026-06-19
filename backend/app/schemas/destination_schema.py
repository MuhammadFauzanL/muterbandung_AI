"""
Pydantic response schemas for Destination endpoints.

All response fields use camelCase aliases for frontend (Next.js) compatibility.
Internal database models remain snake_case.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Shared config ────────────────────────────────────────

def _to_camel(name: str) -> str:
    """Convert snake_case to camelCase for JSON serialization."""
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class _CamelModel(BaseModel):
    """Base model with camelCase alias generation."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
    )


# =========================================================================
# Card response (popular list, search results)
# =========================================================================


class DestinationCardResponse(_CamelModel):
    """Lightweight destination data for list/card views."""

    id: str = Field(..., description="External ID (e.g. LOC-002)")
    slug: str
    name: str
    category: Optional[str] = None
    primary_intent: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    price_label: str = "Harga belum tersedia"
    location: str = "Bandung Raya"
    tourism_zone: Optional[str] = None
    opening_hours_label: Optional[str] = None
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    score: Optional[float] = None
    score_reason: Optional[str] = None
    score_breakdown: Optional[Dict[str, Any]] = None
    is_favorite: bool = False


# =========================================================================
# Detail response — nested sub-schemas
# =========================================================================


class DestinationRatingResponse(_CamelModel):
    """Rating block for destination detail."""

    value: Optional[float] = None
    total_reviews: Optional[int] = None
    label: str = "Belum ada rating"


class DestinationTicketResponse(_CamelModel):
    """Ticket / price block for destination detail."""

    price_min: Optional[int] = None
    price_max: Optional[int] = None
    price_type: Optional[str] = None
    label: str = "Harga belum tersedia"


class DestinationOpeningHoursResponse(_CamelModel):
    """Opening hours block for destination detail."""

    regular: Optional[str] = None
    weekday: Optional[str] = None
    weekend: Optional[str] = None


class DestinationLocationResponse(_CamelModel):
    """Location / map block for destination detail."""

    label: str = "Bandung Raya"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maps_url: Optional[str] = None


class DestinationAIRecommendationResponse(_CamelModel):
    """AI-generated recommendation block (template-based, not LLM runtime)."""

    title: str = "Mengapa Cepot AI Merekomendasikan Ini?"
    reason: str
    tags: list[str] = []


class DestinationFacilityResponse(_CamelModel):
    """Single facility item."""

    key: str
    label: str
    available: bool


class DestinationReviewSummaryResponse(_CamelModel):
    """Review / sentiment summary block."""

    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    positive_reviews: Optional[int] = None
    negative_reviews: Optional[int] = None
    total_reviews: Optional[int] = None


# =========================================================================
# Full detail response
# =========================================================================


class DestinationDetailResponse(_CamelModel):
    """Complete destination detail for the detail page."""

    id: str = Field(..., description="External ID (e.g. LOC-002)")
    slug: str
    name: str
    category: Optional[str] = None
    tourism_zone: Optional[str] = None
    description: Optional[str] = None
    hero_image_url: Optional[str] = None
    gallery: list[str] = Field(default_factory=list)
    rating: DestinationRatingResponse
    ticket: DestinationTicketResponse
    opening_hours: DestinationOpeningHoursResponse
    location: DestinationLocationResponse
    ai_recommendation: DestinationAIRecommendationResponse
    facilities: list[DestinationFacilityResponse] = []
    review_summary: DestinationReviewSummaryResponse


# =========================================================================
# Category highlight response
# =========================================================================


class DestinationCategoryHighlightResponse(_CamelModel):
    """Category highlight item for homepage."""

    name: str
    slug: str
    description: str
    image_url: Optional[str] = None
    total_destinations: int = 0
