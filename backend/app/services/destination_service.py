"""
Service layer for Destination queries and response building.

All database queries and response transformations live here.
The router layer delegates to these functions and wraps results
with the standard response helpers.
"""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Optional

from sqlalchemy import and_, func, literal, or_
from sqlalchemy.orm import Session, joinedload

from app.models.destination import Destination
from app.models.destination_facility import DestinationFacility
from app.models.destination_label import DestinationLabel
from app.models.destination_media import DestinationMedia
from app.schemas.destination_schema import (
    DestinationAIRecommendationResponse,
    DestinationCardResponse,
    DestinationCategoryHighlightResponse,
    DestinationDetailResponse,
    DestinationFacilityResponse,
    DestinationLocationResponse,
    DestinationOpeningHoursResponse,
    DestinationRatingResponse,
    DestinationReviewSummaryResponse,
    DestinationTicketResponse,
)


# =========================================================================
# Reusable query helpers
# =========================================================================

EARTH_RADIUS_KM = 6371.0


def _active_base_query(db: Session):
    """
    Return a base query filtered to active destinations only.

    Active = curation_action=keep, display_status=active_candidate,
             coordinate_verified=True
    """
    return (
        db.query(Destination)
        .filter(
            Destination.curation_action == "keep",
            Destination.display_status == "active_candidate",
            Destination.coordinate_verified.is_(True),
        )
    )


def _active_with_media_query(db: Session):
    """Active destinations that also have verified media (for card views)."""
    return (
        _active_base_query(db)
        .join(Destination.media)
        .filter(DestinationMedia.media_available.is_(True))
    )


def _eager_load_all():
    """Eager-load options for all child relationships."""
    return [
        joinedload(Destination.media),
        joinedload(Destination.labels),
        joinedload(Destination.facilities),
    ]


def _apply_sort(query, sort: str, distance_expr=None):
    """Apply sorting to a destination query."""
    if sort == "nearest" and distance_expr is not None:
        return query.order_by(
            distance_expr.asc().nullslast(),
            Destination.quality_score.desc().nullslast(),
            Destination.avg_rating.desc().nullslast(),
        )

    sort_map = {
        "popular": [
            Destination.popular_score.desc().nullslast(),
            Destination.total_reviews.desc().nullslast(),
            Destination.avg_rating.desc().nullslast(),
        ],
        "quality": [
            Destination.quality_score.desc().nullslast(),
            Destination.avg_rating.desc().nullslast(),
            Destination.total_reviews.desc().nullslast(),
        ],
        "rating": [
            Destination.avg_rating.desc().nullslast(),
            Destination.total_reviews.desc().nullslast(),
        ],
        "reviews": [
            Destination.total_reviews.desc().nullslast(),
        ],
        "newest": [
            Destination.created_at.desc(),
        ],
        "price_low": [
            Destination.price_min.asc().nullslast(),
        ],
        "price_high": [
            Destination.price_max.desc().nullslast(),
        ],
    }
    order_clauses = sort_map.get(sort, sort_map["popular"])
    return query.order_by(*order_clauses)


def _distance_expression(user_lat: float, user_lng: float):
    """
    Build a Haversine SQL expression in kilometers.

    PostGIS is intentionally avoided for the MVP so this works with the
    existing latitude/longitude columns.
    """
    lat_1 = func.radians(user_lat)
    lng_1 = func.radians(user_lng)
    lat_2 = func.radians(Destination.latitude)
    lng_2 = func.radians(Destination.longitude)
    cosine_distance = (
        func.sin(lat_1) * func.sin(lat_2)
        + func.cos(lat_1) * func.cos(lat_2) * func.cos(lng_2 - lng_1)
    )
    clamped = func.least(1.0, func.greatest(-1.0, cosine_distance))
    return EARTH_RADIUS_KM * func.acos(clamped)


def calculate_distance_km(
    dest: Destination,
    user_lat: Optional[float],
    user_lng: Optional[float],
) -> Optional[float]:
    """Calculate Haversine distance in Python for response payloads."""
    if (
        user_lat is None
        or user_lng is None
        or dest.latitude is None
        or dest.longitude is None
    ):
        return None

    lat_1 = math.radians(user_lat)
    lng_1 = math.radians(user_lng)
    lat_2 = math.radians(dest.latitude)
    lng_2 = math.radians(dest.longitude)
    delta_lat = lat_2 - lat_1
    delta_lng = lng_2 - lng_1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_1) * math.cos(lat_2) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(EARTH_RADIUS_KM * c, 2)


# =========================================================================
# Format helpers
# =========================================================================


def format_price_label(
    price_min: Optional[int],
    price_max: Optional[int],
    price_type: Optional[str],
) -> str:
    """Build a human-readable price label."""
    if price_type and price_type.lower() == "gratis":
        return "Gratis"
    if price_min is None and price_max is None:
        return "Harga belum tersedia"
    if price_min == 0 and price_max == 0:
        return "Gratis"
    if price_min is not None and price_max is not None:
        if price_min == price_max:
            return f"Rp {price_min:,}".replace(",", ".")
        return (
            f"Rp {price_min:,} - Rp {price_max:,}".replace(",", ".")
        )
    if price_min is not None:
        return f"Mulai Rp {price_min:,}".replace(",", ".")
    return f"Rp {price_max:,}".replace(",", ".")


def format_opening_hours(dest: Destination) -> DestinationOpeningHoursResponse:
    """Build opening hours response from destination fields."""
    regular = None
    weekday = None
    weekend = None

    # Check open_24h via facilities
    if dest.facilities and dest.facilities.open_24h:
        regular = "Buka 24 Jam"
        weekday = "Buka 24 Jam"
        weekend = "Buka 24 Jam"
        return DestinationOpeningHoursResponse(
            regular=regular, weekday=weekday, weekend=weekend,
        )

    if dest.opening_time and dest.closing_time:
        regular = f"{dest.opening_time} - {dest.closing_time}"
    if dest.weekday_opening_time and dest.weekday_closing_time:
        weekday = f"{dest.weekday_opening_time} - {dest.weekday_closing_time}"
    if dest.weekend_opening_time and dest.weekend_closing_time:
        weekend = f"{dest.weekend_opening_time} - {dest.weekend_closing_time}"

    return DestinationOpeningHoursResponse(
        regular=regular, weekday=weekday, weekend=weekend,
    )


def format_opening_hours_label(
    dest: Destination,
    day_type: Optional[str] = None,
) -> Optional[str]:
    """Return the best compact opening-hours label for list cards."""
    if dest.facilities and dest.facilities.open_24h:
        return "Buka 24 Jam"

    if day_type == "weekday" and dest.weekday_opening_time and dest.weekday_closing_time:
        return f"{dest.weekday_opening_time} - {dest.weekday_closing_time}"
    if day_type == "weekend" and dest.weekend_opening_time and dest.weekend_closing_time:
        return f"{dest.weekend_opening_time} - {dest.weekend_closing_time}"
    if dest.opening_time and dest.closing_time:
        return f"{dest.opening_time} - {dest.closing_time}"
    if dest.weekday_opening_time and dest.weekday_closing_time:
        return f"{dest.weekday_opening_time} - {dest.weekday_closing_time}"
    if dest.weekend_opening_time and dest.weekend_closing_time:
        return f"{dest.weekend_opening_time} - {dest.weekend_closing_time}"
    return None


def _opening_columns(day_type: Optional[str]):
    """Pick opening-hour columns based on planned visit day."""
    if day_type == "weekday":
        return (
            func.coalesce(Destination.weekday_opening_time, Destination.opening_time),
            func.coalesce(Destination.weekday_closing_time, Destination.closing_time),
        )
    if day_type == "weekend":
        return (
            func.coalesce(Destination.weekend_opening_time, Destination.opening_time),
            func.coalesce(Destination.weekend_closing_time, Destination.closing_time),
        )
    return Destination.opening_time, Destination.closing_time


def _open_at_time_filter(day_type: Optional[str], planned_time: str):
    """Build a SQL filter for destinations open at a planned HH:mm time."""
    open_col, close_col = _opening_columns(day_type)
    time_value = literal(planned_time)
    return or_(
        DestinationFacility.open_24h.is_(True),
        and_(
            open_col.isnot(None),
            close_col.isnot(None),
            or_(
                and_(
                    close_col >= open_col,
                    open_col <= time_value,
                    close_col >= time_value,
                ),
                and_(
                    close_col < open_col,
                    or_(open_col <= time_value, close_col >= time_value),
                ),
            ),
        ),
    )


def build_ai_recommendation(
    dest: Destination,
) -> DestinationAIRecommendationResponse:
    """Build a template-based AI recommendation (no LLM runtime)."""
    labels = dest.labels
    if not labels or not labels.primary_intent:
        return DestinationAIRecommendationResponse(
            reason=(
                "Destinasi ini direkomendasikan berdasarkan informasi "
                "kategori, rating, dan data ulasan yang tersedia."
            ),
            tags=[],
        )

    # Collect up to 5 tags from core + secondary
    all_tags: list[str] = []
    if labels.core_labels:
        all_tags.extend(labels.core_labels)
    if labels.secondary_labels:
        all_tags.extend(labels.secondary_labels)
    tags = all_tags[:5]

    intent = labels.primary_intent
    if tags:
        tag_str = ", ".join(tags[:-1]) + f", dan {tags[-1]}" if len(tags) > 1 else tags[0]
        reason = (
            f"Destinasi ini cocok untuk kamu yang mencari wisata {intent} "
            f"dengan karakter {tag_str}. "
            f"Rating dan sentimen ulasan membantu menunjukkan bahwa "
            f"destinasi ini layak dipertimbangkan."
        )
    else:
        reason = (
            f"Destinasi ini cocok untuk kamu yang mencari wisata {intent}. "
            f"Rating dan sentimen ulasan membantu menunjukkan bahwa "
            f"destinasi ini layak dipertimbangkan."
        )

    return DestinationAIRecommendationResponse(
        reason=reason, tags=tags,
    )


# Facility mapping: DB field → (key, label)
_FACILITY_MAP: list[tuple[str, str, str]] = [
    ("parking_available", "parking", "Parkir"),
    ("wheelchair_accessible", "wheelchair", "Akses Difabel"),
    ("toilet_available", "toilet", "Toilet"),
    ("mushola_available", "mushola", "Mushola"),
    ("pet_friendly", "petFriendly", "Pet Friendly"),
    ("open_24h", "open24h", "Buka 24 Jam"),
    ("child_friendly", "childFriendly", "Ramah Anak"),
    ("night_available", "nightVisit", "Kunjungan Malam"),
    ("indoor_available", "indoor", "Indoor"),
    ("safety_verified", "safety", "Keamanan"),
]


def build_facilities(
    facilities: Optional[DestinationFacility],
) -> list[DestinationFacilityResponse]:
    """Convert boolean facility fields to a list of facility items.
    Null values are skipped (not shown to frontend).
    """
    if facilities is None:
        return []
    result: list[DestinationFacilityResponse] = []
    for db_field, key, label in _FACILITY_MAP:
        value = getattr(facilities, db_field, None)
        if value is not None:
            result.append(
                DestinationFacilityResponse(key=key, label=label, available=value)
            )
    return result


def slugify_category(name: str) -> str:
    """Generate a URL-safe slug from a category name."""
    slug = unicodedata.normalize("NFKD", name)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "other"


# Category description templates
_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "Wisata Alam": "Temukan destinasi wisata alam terbaik untuk healing, spot foto, dan udara segar.",
    "Rekreasi Keluarga": "Nikmati wahana seru dan destinasi ramah anak untuk liburan keluarga.",
    "Taman Kota": "Jelajahi taman kota dan ruang publik untuk bersantai di tengah Bandung.",
    "Tempat Belajar": "Kunjungi museum, galeri, dan pusat edukasi untuk menambah wawasan.",
    "Tempat Camping": "Temukan spot camping terbaik dengan pemandangan alam Bandung.",
    "Tempat Belanja": "Belanja oleh-oleh, fashion, dan kuliner khas Bandung.",
    "Tempat Kuliner": "Cicipi kuliner terbaik Bandung dari street food hingga fine dining.",
    "Tempat Sejarah": "Jelajahi bangunan bersejarah dan situs warisan budaya Bandung.",
    "Wisata Satwa": "Nikmati interaksi dengan satwa di kebun binatang dan taman satwa.",
    "Tempat Seni": "Apresiasi seni dan kreativitas di galeri, studio, dan art space.",
    "Tempat Ibadah": "Kunjungi masjid, gereja, dan tempat ibadah berarsitektur indah.",
    "Wisata Petualangan": "Rasakan adrenalin dengan aktivitas outdoor dan petualangan.",
    "Wahana Air": "Nikmati wisata air dari waterpark hingga arung jeram.",
    "Penginapan Wisata": "Temukan penginapan unik dengan pemandangan alam.",
    "Desa Wisata": "Rasakan suasana pedesaan dan budaya lokal khas Bandung.",
    "Tempat Budaya": "Jelajahi pusat kebudayaan dan tradisi Sunda.",
    "Rekreasi Alam": "Nikmati rekreasi di alam terbuka dengan udara segar pegunungan.",
}


# =========================================================================
# Response builders
# =========================================================================


def build_score_reason(dest: Destination, sort: str) -> str:
    """Explain why a destination appears in a recommendation list."""
    if sort == "popular":
        return "Populer berdasarkan jumlah ulasan, rating, dan skor popularitas."
    if sort == "nearest":
        return "Diurutkan berdasarkan jarak terdekat dari lokasi yang kamu izinkan."
    if sort == "rating":
        return "Diurutkan berdasarkan rating tertinggi dari data ulasan."
    if sort == "reviews":
        return "Diurutkan berdasarkan jumlah ulasan terbanyak."
    return (
        "Direkomendasikan dari rating, ulasan, sentimen, label, "
        "dan kelengkapan data."
    )


def build_score_value(dest: Destination, sort: str) -> Optional[float]:
    """Return the ranking score most relevant to the current sort."""
    if sort == "popular":
        return dest.popular_score
    if sort in {"quality", "nearest"}:
        return dest.quality_score
    if sort == "rating":
        return dest.avg_rating
    if sort == "reviews":
        return float(dest.total_reviews) if dest.total_reviews is not None else None
    return dest.quality_score


def build_destination_card(
    dest: Destination,
    *,
    day_type: Optional[str] = None,
    distance_km: Optional[float] = None,
    sort: str = "quality",
) -> dict:
    """Build a card dict from a Destination ORM instance."""
    image_url = None
    if dest.media:
        image_url = dest.media.image_url

    tourism_zone = dest.tourism_zone or "Bandung Raya"
    primary_intent = dest.labels.primary_intent if dest.labels else None

    return DestinationCardResponse(
        id=dest.external_id,
        slug=dest.slug,
        name=dest.name,
        category=dest.category,
        primary_intent=primary_intent,
        image_url=image_url,
        rating=dest.avg_rating,
        price_label=format_price_label(
            dest.price_min, dest.price_max, dest.price_type,
        ),
        location=tourism_zone,
        tourism_zone=dest.tourism_zone,
        opening_hours_label=format_opening_hours_label(dest, day_type),
        duration_minutes=dest.estimated_duration_minutes,
        distance_km=distance_km,
        score=build_score_value(dest, sort),
        score_reason=build_score_reason(dest, sort),
        is_favorite=False,
    ).model_dump(by_alias=True)


def build_destination_detail(dest: Destination) -> dict:
    """Build the full detail dict from a Destination ORM instance."""
    tourism_zone = dest.tourism_zone or "Bandung Raya"
    hero_image = dest.media.image_url if dest.media else None
    maps_url = dest.media.maps_url if dest.media else None

    # Rating
    rating_label = "Belum ada rating"
    if dest.avg_rating is not None:
        rating_label = f"{dest.avg_rating} / 5.0"

    rating = DestinationRatingResponse(
        value=dest.avg_rating,
        total_reviews=dest.total_reviews,
        label=rating_label,
    )

    # Ticket
    ticket = DestinationTicketResponse(
        price_min=dest.price_min,
        price_max=dest.price_max,
        price_type=dest.price_type,
        label=format_price_label(dest.price_min, dest.price_max, dest.price_type),
    )

    # Opening hours
    opening_hours = format_opening_hours(dest)

    # Location
    location = DestinationLocationResponse(
        label=tourism_zone,
        latitude=dest.latitude,
        longitude=dest.longitude,
        maps_url=maps_url,
    )

    # AI recommendation
    ai_recommendation = build_ai_recommendation(dest)

    # Facilities
    facilities = build_facilities(dest.facilities)

    # Review summary
    review_summary = DestinationReviewSummaryResponse(
        sentiment_label=dest.sentiment_label,
        sentiment_score=dest.sentiment_score,
        positive_reviews=dest.positive_reviews,
        negative_reviews=dest.negative_reviews,
        total_reviews=dest.total_reviews,
    )

    return DestinationDetailResponse(
        id=dest.external_id,
        slug=dest.slug,
        name=dest.name,
        category=dest.category,
        tourism_zone=dest.tourism_zone,
        description=dest.description,
        hero_image_url=hero_image,
        rating=rating,
        ticket=ticket,
        opening_hours=opening_hours,
        location=location,
        ai_recommendation=ai_recommendation,
        facilities=facilities,
        review_summary=review_summary,
    ).model_dump(by_alias=True)


# =========================================================================
# Service functions (called by router)
# =========================================================================


def get_popular_destinations(db: Session, limit: int = 8) -> list[dict]:
    """Return top popular active destinations for homepage cards."""
    query = (
        _active_with_media_query(db)
        .options(
            joinedload(Destination.media),
            joinedload(Destination.labels),
            joinedload(Destination.facilities),
        )
    )
    query = _apply_sort(query, "popular")
    destinations = query.limit(limit).all()
    return [build_destination_card(d, sort="popular") for d in destinations]


def get_destination_by_slug(db: Session, slug: str) -> Optional[dict]:
    """Return full detail for a single destination, or None if not found."""
    dest = (
        _active_base_query(db)
        .options(*_eager_load_all())
        .filter(Destination.slug == slug)
        .first()
    )
    if not dest:
        return None
    return build_destination_detail(dest)


def get_destinations(
    db: Session,
    *,
    page: int = 1,
    limit: int = 12,
    search: Optional[str] = None,
    intent: Optional[str] = None,
    category: Optional[str] = None,
    tourism_zone: Optional[str] = None,
    price_type: Optional[str] = None,
    free_only: Optional[bool] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    child_friendly: Optional[bool] = None,
    indoor: Optional[bool] = None,
    open_now: Optional[bool] = None,
    day_type: Optional[str] = None,
    planned_time: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    sort: str = "popular",
) -> tuple[list[dict], int]:
    """
    Return paginated, filtered destination cards.
    Returns (items, total_count).
    """
    has_user_location = user_lat is not None and user_lng is not None
    distance_expr = (
        _distance_expression(user_lat, user_lng) if has_user_location else None
    )
    effective_sort = sort
    if sort == "nearest" and distance_expr is None:
        effective_sort = "quality"

    query = _active_with_media_query(db).options(
        joinedload(Destination.media),
        joinedload(Destination.labels),
        joinedload(Destination.facilities),
    )

    joined_labels = False
    joined_facilities = False

    # ── Filters ──
    if search:
        pattern = f"%{search}%"
        query = query.outerjoin(Destination.labels)
        joined_labels = True
        query = query.filter(
            or_(
                Destination.name.ilike(pattern),
                Destination.category.ilike(pattern),
                Destination.subcategory.ilike(pattern),
                Destination.description.ilike(pattern),
                Destination.tourism_zone.ilike(pattern),
                DestinationLabel.primary_intent.ilike(pattern),
            )
        )
    if intent:
        if not joined_labels:
            query = query.join(Destination.labels)
            joined_labels = True
        query = query.filter(DestinationLabel.primary_intent == intent)
    if category:
        query = query.filter(Destination.category == category)
    if tourism_zone:
        query = query.filter(Destination.tourism_zone == tourism_zone)
    if price_type:
        query = query.filter(Destination.price_type == price_type)
    if free_only is True:
        query = query.filter(
            or_(
                func.lower(Destination.price_type) == "gratis",
                and_(Destination.price_min == 0, Destination.price_max == 0),
            )
        )
    if max_price is not None:
        query = query.filter(Destination.price_min <= max_price)
    if min_rating is not None:
        query = query.filter(Destination.avg_rating >= min_rating)
    if child_friendly is not None:
        query = query.join(Destination.facilities)
        joined_facilities = True
        query = query.filter(
            DestinationFacility.child_friendly == child_friendly,
        )
    if indoor is not None:
        if not joined_facilities:
            query = query.join(Destination.facilities)
            joined_facilities = True
        query = query.filter(
            DestinationFacility.indoor_available == indoor,
        )
    if open_now is True and planned_time:
        if not joined_facilities:
            query = query.outerjoin(Destination.facilities)
            joined_facilities = True
        query = query.filter(_open_at_time_filter(day_type, planned_time))
    if radius_km is not None and distance_expr is not None:
        query = query.filter(distance_expr <= radius_km)

    # ── Count (before pagination) ──
    total = query.count()

    # ── Sort & paginate ──
    query = _apply_sort(query, effective_sort, distance_expr)
    offset = (page - 1) * limit
    destinations = query.offset(offset).limit(limit).all()

    return [
        build_destination_card(
            d,
            day_type=day_type,
            distance_km=calculate_distance_km(d, user_lat, user_lng),
            sort=effective_sort,
        )
        for d in destinations
    ], total


def get_destination_filters(db: Session) -> dict:
    """Return dynamic filter options for Explore UI."""
    intent_rows = (
        _active_with_media_query(db)
        .join(Destination.labels)
        .with_entities(
            DestinationLabel.primary_intent.label("value"),
            func.count(Destination.id).label("total"),
        )
        .filter(DestinationLabel.primary_intent.isnot(None))
        .group_by(DestinationLabel.primary_intent)
        .order_by(func.count(Destination.id).desc(), DestinationLabel.primary_intent.asc())
        .all()
    )

    category_rows = (
        _active_with_media_query(db)
        .with_entities(
            Destination.category.label("value"),
            func.count(Destination.id).label("total"),
        )
        .filter(Destination.category.isnot(None))
        .group_by(Destination.category)
        .order_by(func.count(Destination.id).desc(), Destination.category.asc())
        .all()
    )

    return {
        "intents": [
            {"label": value, "value": value, "count": total}
            for value, total in intent_rows
            if value
        ],
        "categories": [
            {"label": value, "value": value, "count": total}
            for value, total in category_rows
            if value
        ],
        "budgetOptions": ["free", "under_50000", "under_100000"],
        "ratingOptions": [3, 4, 4.5],
        "sortOptions": ["quality", "popular", "rating", "nearest"],
    }


def get_highlighted_categories(
    db: Session, limit: int = 8,
) -> list[dict]:
    """
    Return top destination categories with count and sample image.
    Uses a subquery to pick one image per category.
    """
    # Query: group active destinations by category
    results = (
        _active_with_media_query(db)
        .with_entities(
            Destination.category,
            func.count(Destination.id).label("total"),
            func.min(DestinationMedia.image_url).label("sample_image"),
        )
        .group_by(Destination.category)
        .order_by(func.count(Destination.id).desc())
        .limit(limit)
        .all()
    )

    categories: list[dict] = []
    for cat_name, total, sample_image in results:
        if not cat_name:
            continue
        desc = _CATEGORY_DESCRIPTIONS.get(
            cat_name,
            f"Jelajahi destinasi {cat_name.lower()} terbaik di Bandung.",
        )
        item = DestinationCategoryHighlightResponse(
            name=cat_name,
            slug=slugify_category(cat_name),
            description=desc,
            image_url=sample_image,
            total_destinations=total,
        )
        categories.append(item.model_dump(by_alias=True))

    return categories
