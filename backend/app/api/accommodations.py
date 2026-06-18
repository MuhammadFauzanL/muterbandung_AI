"""
Accommodation endpoints.

- GET /accommodations
- GET /accommodations/filters
- GET /destinations/{slug}/nearby-accommodations
"""

from __future__ import annotations

from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.accommodation_service import (
    get_accommodation_filters,
    get_accommodations,
    get_nearby_accommodations_for_destination,
)
from app.utils.response import paginated_response, success_response

router = APIRouter()

_ALLOWED_SORTS = {
    "recommended",
    "nearest",
    "rating",
    "reviews",
    "price_low",
    "price_high",
}


def _parse_facilities(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@router.get("/accommodations")
def list_accommodations(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    search: Optional[str] = Query(None, min_length=1, max_length=200),
    type: Optional[str] = Query(None, description="Hotel, Villa, Guest_House, etc."),
    max_price: Optional[int] = Query(None, ge=0, alias="maxPrice"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, alias="minRating"),
    facilities: Optional[str] = Query(
        None,
        description="Comma-separated facility labels",
    ),
    user_lat: Optional[float] = Query(None, ge=-90, le=90, alias="userLat"),
    user_lng: Optional[float] = Query(None, ge=-180, le=180, alias="userLng"),
    radius_km: Optional[float] = Query(None, ge=0, alias="radiusKm"),
    sort: str = Query("recommended"),
    db: Session = Depends(get_db),
):
    """Paginated accommodation list with filters and optional location ranking."""
    if sort not in _ALLOWED_SORTS:
        sort = "recommended"

    items, total = get_accommodations(
        db,
        page=page,
        limit=limit,
        search=search,
        accommodation_type=type,
        max_price=max_price,
        min_rating=min_rating,
        facilities=_parse_facilities(facilities),
        user_lat=user_lat,
        user_lng=user_lng,
        radius_km=radius_km,
        sort=sort,
    )

    return paginated_response(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message="Accommodations retrieved successfully",
    )


@router.get("/accommodations/filters")
def accommodation_filters(db: Session = Depends(get_db)):
    """Return dynamic accommodation filter metadata."""
    return success_response(
        data=get_accommodation_filters(db),
        message="Accommodation filters retrieved successfully",
    )


@router.get("/destinations/{slug}/nearby-accommodations")
def nearby_accommodations(
    slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=20),
    radius_km: float = Query(10, ge=0, alias="radiusKm"),
    type: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None, ge=0, alias="maxPrice"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, alias="minRating"),
    facilities: Optional[str] = Query(None),
    sort: str = Query("recommended"),
    db: Session = Depends(get_db),
):
    """Return accommodations near a selected destination slug."""
    if sort not in _ALLOWED_SORTS:
        sort = "recommended"

    items, total = get_nearby_accommodations_for_destination(
        db,
        destination_slug=slug,
        page=page,
        limit=limit,
        radius_km=radius_km,
        accommodation_type=type,
        max_price=max_price,
        min_rating=min_rating,
        facilities=_parse_facilities(facilities),
        sort=sort,
    )

    return paginated_response(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message="Nearby accommodations retrieved successfully",
    )
