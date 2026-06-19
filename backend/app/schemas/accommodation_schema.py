"""
Pydantic response schemas for accommodation endpoints.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
    )


class AccommodationCardResponse(_CamelModel):
    """Lightweight accommodation data for list/card views."""

    id: str = Field(..., description="External ID, e.g. LODGE-00001")
    slug: str
    name: str
    type: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_label: str = "Harga belum tersedia"
    location: str = "Bandung Raya"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None
    facilities: list[str] = []
    maps_url: Optional[str] = None
    booking_url: Optional[str] = None
    score: Optional[float] = None
    score_reason: Optional[str] = None


class AccommodationFilterOption(_CamelModel):
    label: str
    value: str
    count: int


class AccommodationFilterMetadata(_CamelModel):
    types: list[AccommodationFilterOption]
    price_options: list[str]
    rating_options: list[float]
    facility_options: list[str]
    sort_options: list[str]
