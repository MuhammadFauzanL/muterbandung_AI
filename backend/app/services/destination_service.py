"""
Service layer for Destination queries and response building.

All database queries and response transformations live here.
The router layer delegates to these functions and wraps results
with the standard response helpers.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from sqlalchemy import func, or_
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


def _apply_sort(query, sort: str):
    """Apply sorting to a destination query."""
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


def build_destination_card(dest: Destination) -> dict:
    """Build a card dict from a Destination ORM instance."""
    image_url = None
    if dest.media:
        image_url = dest.media.image_url

    tourism_zone = dest.tourism_zone or "Bandung Raya"

    return DestinationCardResponse(
        id=dest.external_id,
        slug=dest.slug,
        name=dest.name,
        category=dest.category,
        image_url=image_url,
        rating=dest.avg_rating,
        price_label=format_price_label(
            dest.price_min, dest.price_max, dest.price_type,
        ),
        location=tourism_zone,
        tourism_zone=dest.tourism_zone,
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
        .options(joinedload(Destination.media))
    )
    query = _apply_sort(query, "popular")
    destinations = query.limit(limit).all()
    return [build_destination_card(d) for d in destinations]


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
    category: Optional[str] = None,
    tourism_zone: Optional[str] = None,
    price_type: Optional[str] = None,
    child_friendly: Optional[bool] = None,
    indoor: Optional[bool] = None,
    sort: str = "popular",
) -> tuple[list[dict], int]:
    """
    Return paginated, filtered destination cards.
    Returns (items, total_count).
    """
    query = _active_with_media_query(db).options(
        joinedload(Destination.media),
    )

    # ── Filters ──
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Destination.name.ilike(pattern),
                Destination.category.ilike(pattern),
                Destination.subcategory.ilike(pattern),
                Destination.description.ilike(pattern),
                Destination.tourism_zone.ilike(pattern),
            )
        )
    if category:
        query = query.filter(Destination.category == category)
    if tourism_zone:
        query = query.filter(Destination.tourism_zone == tourism_zone)
    if price_type:
        query = query.filter(Destination.price_type == price_type)
    if child_friendly is not None:
        query = query.join(Destination.facilities).filter(
            DestinationFacility.child_friendly == child_friendly,
        )
    if indoor is not None:
        # Avoid double join if child_friendly already joined
        if child_friendly is None:
            query = query.join(Destination.facilities)
        query = query.filter(
            DestinationFacility.indoor_available == indoor,
        )

    # ── Count (before pagination) ──
    total = query.count()

    # ── Sort & paginate ──
    query = _apply_sort(query, sort)
    offset = (page - 1) * limit
    destinations = query.offset(offset).limit(limit).all()

    return [build_destination_card(d) for d in destinations], total


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
