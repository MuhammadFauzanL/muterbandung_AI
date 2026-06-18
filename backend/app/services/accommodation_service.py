"""
Accommodation service – filtering, nearest search, and ranking helpers.
"""

from __future__ import annotations

import math
from typing import Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.accommodation import Accommodation
from app.models.destination import Destination
from app.schemas.accommodation_schema import AccommodationCardResponse


EARTH_RADIUS_KM = 6371.0088
DEFAULT_RADIUS_KM = 10.0


def _active_accommodations_query(db: Session):
    return db.query(Accommodation).filter(
        Accommodation.display_status == "active_candidate",
        Accommodation.is_active.is_(True),
        Accommodation.latitude.isnot(None),
        Accommodation.longitude.isnot(None),
    )


def _distance_expression(user_lat: float, user_lng: float):
    """Build a Haversine SQL expression in kilometers."""
    lat_1 = func.radians(user_lat)
    lng_1 = func.radians(user_lng)
    lat_2 = func.radians(Accommodation.latitude)
    lng_2 = func.radians(Accommodation.longitude)
    cosine_distance = (
        func.sin(lat_1) * func.sin(lat_2)
        + func.cos(lat_1) * func.cos(lat_2) * func.cos(lng_2 - lng_1)
    )
    clamped = func.least(1.0, func.greatest(-1.0, cosine_distance))
    return EARTH_RADIUS_KM * func.acos(clamped)


def calculate_distance_km(
    accommodation: Accommodation,
    user_lat: Optional[float],
    user_lng: Optional[float],
) -> Optional[float]:
    """Calculate Haversine distance in Python for response payloads."""
    if (
        user_lat is None
        or user_lng is None
        or accommodation.latitude is None
        or accommodation.longitude is None
    ):
        return None

    lat_1 = math.radians(user_lat)
    lng_1 = math.radians(user_lng)
    lat_2 = math.radians(accommodation.latitude)
    lng_2 = math.radians(accommodation.longitude)
    delta_lat = lat_2 - lat_1
    delta_lng = lng_2 - lng_1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_1) * math.cos(lat_2) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(EARTH_RADIUS_KM * c, 2)


def _normalize_rating(value: Optional[float]) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(100.0, value * 20.0))


def _normalize_reviews(value: Optional[int]) -> float:
    if not value:
        return 0.0
    return max(0.0, min(100.0, math.log1p(value) / math.log1p(10000) * 100))


def _data_completeness_score(accommodation: Accommodation) -> float:
    checks = [
        accommodation.price_min is not None,
        bool(accommodation.image_url),
        bool(accommodation.destination_url or accommodation.website_url),
        accommodation.avg_rating is not None,
        accommodation.total_reviews is not None,
        bool(accommodation.description),
    ]
    return round(sum(1 for item in checks if item) / len(checks) * 100, 2)


def _format_price_label(
    price_min: Optional[int],
    price_max: Optional[int],
) -> str:
    if price_min is None and price_max is None:
        return "Harga belum tersedia"
    if price_min is not None and price_max is not None and price_min != price_max:
        return f"Rp {price_min:,.0f} - Rp {price_max:,.0f}/malam".replace(",", ".")
    price = price_min if price_min is not None else price_max
    return f"Mulai Rp {price:,.0f}/malam".replace(",", ".")


def _location_label(accommodation: Accommodation) -> str:
    parts = [
        part
        for part in [accommodation.district, accommodation.city]
        if part and part.lower() != "unknown"
    ]
    return ", ".join(parts) if parts else "Bandung Raya"


def _maps_url(accommodation: Accommodation) -> str:
    if accommodation.latitude is None or accommodation.longitude is None:
        return f"https://www.google.com/maps/search/?api=1&query={accommodation.name}"
    return (
        "https://www.google.com/maps/search/?api=1"
        f"&query={accommodation.latitude},{accommodation.longitude}"
    )


def _score_reason(
    sort: str,
    distance_km: Optional[float],
    accommodation: Accommodation,
) -> str:
    if distance_km is not None:
        if sort == "nearest":
            return f"Berjarak sekitar {distance_km:.2f} km dari destinasi yang dipilih."
        return (
            f"Dipilih karena dekat ({distance_km:.2f} km), "
            "rating, ulasan, dan kelengkapan data penginapan."
        )
    if accommodation.avg_rating is not None:
        return "Direkomendasikan dari rating, ulasan, dan kelengkapan data penginapan."
    return "Direkomendasikan dari kelengkapan data penginapan yang tersedia."


def _rank_score(
    accommodation: Accommodation,
    *,
    distance_km: Optional[float],
    radius_km: Optional[float],
) -> float:
    rating_score = _normalize_rating(accommodation.avg_rating)
    review_score = _normalize_reviews(accommodation.total_reviews)
    completeness_score = _data_completeness_score(accommodation)

    if distance_km is None:
        return round(
            0.55 * rating_score
            + 0.25 * review_score
            + 0.20 * completeness_score,
            2,
        )

    radius = max(radius_km or DEFAULT_RADIUS_KM, 1.0)
    distance_score = max(0.0, 100.0 - (distance_km / radius) * 100.0)
    return round(
        0.55 * distance_score
        + 0.25 * rating_score
        + 0.10 * review_score
        + 0.10 * completeness_score,
        2,
    )


def _build_card(
    accommodation: Accommodation,
    *,
    distance_km: Optional[float],
    sort: str,
    score: Optional[float] = None,
) -> dict:
    return AccommodationCardResponse(
        id=accommodation.external_id,
        slug=accommodation.slug,
        name=accommodation.name,
        type=accommodation.accommodation_type,
        category=accommodation.category,
        image_url=accommodation.image_url,
        rating=accommodation.avg_rating,
        review_count=accommodation.total_reviews,
        price_label=_format_price_label(
            accommodation.price_min,
            accommodation.price_max,
        ),
        location=_location_label(accommodation),
        distance_km=distance_km,
        facilities=accommodation.facilities or [],
        maps_url=_maps_url(accommodation),
        booking_url=accommodation.destination_url or accommodation.website_url,
        score=score,
        score_reason=_score_reason(sort, distance_km, accommodation),
    ).model_dump(by_alias=True)


def get_accommodations(
    db: Session,
    *,
    page: int = 1,
    limit: int = 12,
    search: Optional[str] = None,
    accommodation_type: Optional[str] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    facilities: Optional[list[str]] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    sort: str = "recommended",
) -> tuple[list[dict], int]:
    """Return paginated, filtered accommodation cards."""
    has_origin = user_lat is not None and user_lng is not None
    distance_expr = _distance_expression(user_lat, user_lng) if has_origin else None

    query = _active_accommodations_query(db)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Accommodation.name.ilike(pattern),
                Accommodation.accommodation_type.ilike(pattern),
                Accommodation.description.ilike(pattern),
                Accommodation.city.ilike(pattern),
                Accommodation.district.ilike(pattern),
            )
        )

    if accommodation_type:
        query = query.filter(Accommodation.accommodation_type == accommodation_type)

    if max_price is not None:
        query = query.filter(
            or_(
                Accommodation.price_min.is_(None),
                Accommodation.price_min <= max_price,
            )
        )

    if min_rating is not None:
        query = query.filter(Accommodation.avg_rating >= min_rating)

    for facility in facilities or []:
        query = query.filter(Accommodation.facilities.contains([facility]))

    if radius_km is not None and distance_expr is not None:
        query = query.filter(distance_expr <= radius_km)

    total = query.count()

    if sort in {"recommended", "nearest"} and has_origin:
        rows = query.all()
        ranked: list[tuple[float, float, Accommodation]] = []
        for accommodation in rows:
            distance_km = calculate_distance_km(accommodation, user_lat, user_lng)
            score = _rank_score(
                accommodation,
                distance_km=distance_km,
                radius_km=radius_km,
            )
            distance_value = distance_km if distance_km is not None else 999999
            ranked.append((score, distance_value, accommodation))

        if sort == "nearest":
            ranked.sort(
                key=lambda item: (
                    item[1],
                    -(item[2].avg_rating or 0),
                    -(item[2].total_reviews or 0),
                )
            )
        else:
            ranked.sort(
                key=lambda item: (
                    item[0],
                    -(item[1]),
                    item[2].avg_rating or 0,
                    item[2].total_reviews or 0,
                ),
                reverse=True,
            )

        offset = (page - 1) * limit
        page_rows = ranked[offset : offset + limit]
        return [
            _build_card(
                accommodation,
                distance_km=round(distance_km, 2),
                sort=sort,
                score=score,
            )
            for score, distance_km, accommodation in page_rows
        ], total

    sort_map = {
        "recommended": [
            Accommodation.quality_score.desc().nullslast(),
            Accommodation.avg_rating.desc().nullslast(),
            Accommodation.total_reviews.desc().nullslast(),
        ],
        "rating": [
            Accommodation.avg_rating.desc().nullslast(),
            Accommodation.total_reviews.desc().nullslast(),
        ],
        "reviews": [
            Accommodation.total_reviews.desc().nullslast(),
            Accommodation.avg_rating.desc().nullslast(),
        ],
        "price_low": [Accommodation.price_min.asc().nullslast()],
        "price_high": [Accommodation.price_min.desc().nullslast()],
    }
    effective_sort = sort if sort in sort_map else "recommended"
    query = query.order_by(*sort_map[effective_sort])
    rows = query.offset((page - 1) * limit).limit(limit).all()

    return [
        _build_card(
            accommodation,
            distance_km=calculate_distance_km(accommodation, user_lat, user_lng),
            sort=effective_sort,
            score=_rank_score(
                accommodation,
                distance_km=calculate_distance_km(accommodation, user_lat, user_lng),
                radius_km=radius_km,
            ),
        )
        for accommodation in rows
    ], total


def get_nearby_accommodations_for_destination(
    db: Session,
    *,
    destination_slug: str,
    page: int = 1,
    limit: int = 5,
    radius_km: float = DEFAULT_RADIUS_KM,
    accommodation_type: Optional[str] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    facilities: Optional[list[str]] = None,
    sort: str = "recommended",
) -> tuple[list[dict], int]:
    """Return nearby accommodations for a selected destination."""
    destination = (
        db.query(Destination)
        .filter(Destination.slug == destination_slug)
        .first()
    )
    if destination is None:
        raise NotFoundException(message=f"Destination {destination_slug} not found")
    if destination.latitude is None or destination.longitude is None:
        return [], 0

    return get_accommodations(
        db,
        page=page,
        limit=limit,
        accommodation_type=accommodation_type,
        max_price=max_price,
        min_rating=min_rating,
        facilities=facilities,
        user_lat=destination.latitude,
        user_lng=destination.longitude,
        radius_km=radius_km,
        sort=sort,
    )


def get_accommodation_filters(db: Session) -> dict:
    """Return dynamic filter metadata for accommodation UI."""
    type_rows = (
        _active_accommodations_query(db)
        .with_entities(
            Accommodation.accommodation_type,
            func.count(Accommodation.id),
        )
        .filter(Accommodation.accommodation_type.isnot(None))
        .group_by(Accommodation.accommodation_type)
        .order_by(func.count(Accommodation.id).desc())
        .all()
    )

    facilities: set[str] = set()
    rows = _active_accommodations_query(db).with_entities(
        Accommodation.facilities,
    ).all()
    for (items,) in rows:
        if isinstance(items, list):
            facilities.update(str(item) for item in items if item)

    return {
        "types": [
            {"label": value, "value": value, "count": count}
            for value, count in type_rows
        ],
        "priceOptions": ["under_250000", "under_500000", "under_1000000"],
        "ratingOptions": [3, 4, 4.5],
        "facilityOptions": sorted(facilities),
        "sortOptions": ["recommended", "nearest", "rating", "reviews", "price_low"],
    }
