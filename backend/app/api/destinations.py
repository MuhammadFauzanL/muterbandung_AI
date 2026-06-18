"""
Destination API endpoints (public, read-only).

Routes:
- GET /destination-categories/highlights — homepage category section
- GET /destinations/popular              — homepage popular cards
- GET /destinations                      — paginated list with filters
- GET /destinations/{slug}               — single destination detail
"""

from __future__ import annotations

from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_optional_current_user

from app.database import get_db
from app.services.destination_service import (
    get_destination_filters,
    get_destination_by_slug,
    get_destinations,
    get_highlighted_categories,
    get_popular_destinations,
)
from app.utils.response import error_response, paginated_response, success_response

router = APIRouter()


# =========================================================================
# GET /destination-categories/highlights
# =========================================================================


@router.get("/destination-categories/highlights")
def highlighted_categories(
    limit: int = Query(8, ge=1, le=20, description="Max categories to return"),
    db: Session = Depends(get_db),
):
    """
    Highlighted destination categories for the homepage.

    Returns top categories sorted by destination count,
    each with a sample image and description.
    """
    data = get_highlighted_categories(db, limit=limit)
    return success_response(
        data=data,
        message="Highlighted destination categories retrieved successfully",
    )


# =========================================================================
# GET /destinations/popular
# =========================================================================


@router.get("/destinations/popular")
def popular_destinations(
    limit: int = Query(8, ge=1, le=50, description="Number of popular destinations"),
    db: Session = Depends(get_db),
):
    """
    Top popular destinations for the homepage section.

    Returns lightweight card data sorted by popularity score.
    Only active destinations with verified media are included.
    """
    data = get_popular_destinations(db, limit=limit)
    return success_response(
        data=data,
        message="Popular destinations retrieved successfully",
    )


# =========================================================================
# GET /destinations
# =========================================================================

_ALLOWED_SORTS = {
    "popular",
    "quality",
    "rating",
    "reviews",
    "newest",
    "price_low",
    "price_high",
    "nearest",
    "personal",
}


@router.get("/destinations")
def list_destinations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=50, description="Items per page"),
    search: Optional[str] = Query(None, min_length=1, max_length=200, description="Search query"),
    intent: Optional[str] = Query(None, description="Filter by AI primary intent"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tourism_zone: Optional[str] = Query(
        None, alias="tourismZone", description="Filter by tourism zone",
    ),
    price_type: Optional[str] = Query(
        None, alias="priceType", description="Filter by price type",
    ),
    free_only: Optional[bool] = Query(
        None, alias="freeOnly", description="Filter free destinations",
    ),
    max_price: Optional[int] = Query(
        None, ge=0, alias="maxPrice", description="Maximum starting price",
    ),
    min_rating: Optional[float] = Query(
        None, ge=0, le=5, alias="minRating", description="Minimum rating",
    ),
    child_friendly: Optional[bool] = Query(
        None, alias="childFriendly", description="Filter child-friendly destinations",
    ),
    indoor: Optional[bool] = Query(None, description="Filter indoor destinations"),
    open_now: Optional[bool] = Query(
        None, alias="openNow", description="Filter destinations open at planned time",
    ),
    day_type: Optional[str] = Query(
        None, alias="dayType", description="weekday or weekend",
    ),
    planned_time: Optional[str] = Query(
        None, alias="plannedTime", pattern=r"^\d{2}:\d{2}$",
        description="Planned visit time in HH:mm",
    ),
    user_lat: Optional[float] = Query(
        None, ge=-90, le=90, alias="userLat", description="User latitude",
    ),
    user_lng: Optional[float] = Query(
        None, ge=-180, le=180, alias="userLng", description="User longitude",
    ),
    radius_km: Optional[float] = Query(
        None, ge=0, alias="radiusKm", description="Radius filter in kilometers",
    ),
    sort: str = Query("popular", description="Sort order"),
    current_user=Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Paginated destination list with search, filters, and sorting.

    **Allowed sorts:** popular, quality, rating, reviews, newest,
    price_low, price_high, nearest, personal
    """
    # Validate sort
    if sort not in _ALLOWED_SORTS:
        sort = "popular"

    data, total = get_destinations(
        db,
        page=page,
        limit=limit,
        search=search,
        intent=intent,
        category=category,
        tourism_zone=tourism_zone,
        price_type=price_type,
        free_only=free_only,
        max_price=max_price,
        min_rating=min_rating,
        child_friendly=child_friendly,
        indoor=indoor,
        open_now=open_now,
        day_type=day_type,
        planned_time=planned_time,
        user_lat=user_lat,
        user_lng=user_lng,
        radius_km=radius_km,
        sort=sort,
        user_id=current_user.id if current_user else None,
    )

    return paginated_response(
        data=data,
        page=page,
        limit=limit,
        total=total,
        message="Destinations retrieved successfully",
    )


# =========================================================================
# GET /destinations/filters
# =========================================================================


@router.get("/destinations/filters")
def destination_filters(
    db: Session = Depends(get_db),
):
    """Dynamic filter metadata for Explore UI."""
    data = get_destination_filters(db)
    return success_response(
        data=data,
        message="Destination filters retrieved successfully",
    )


# =========================================================================
# GET /destinations/{slug}
# =========================================================================


@router.get("/destinations/{slug}")
def destination_detail(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Full destination detail by slug.

    Returns complete data including rating, ticket, opening hours,
    location, AI recommendation, facilities, and review summary.
    """
    data = get_destination_by_slug(db, slug)
    if data is None:
        return error_response(
            message="Destination not found",
            status_code=404,
            errors=[{"detail": f"No active destination with slug '{slug}'"}],
        )
    return success_response(
        data=data,
        message="Destination retrieved successfully",
    )
