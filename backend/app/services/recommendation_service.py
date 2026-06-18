"""
Personalized destination recommendation service.

V1 combines existing destination quality scoring with explicit onboarding
preferences. Behavioral events (search/favorite/planner) can be layered later.
"""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.destination import Destination
from app.models.user_preference import UserPreference
from app.services.destination_service import (
    _active_with_media_query,
    build_destination_card,
    get_destinations,
)


PREFERENCE_MATCHES: dict[str, dict[str, list[str]]] = {
    "nature": {
        "intents": ["Alam"],
        "labels": ["Alam"],
        "categories": ["Wisata Alam", "Rekreasi Alam"],
    },
    "culinary": {
        "intents": ["Kuliner"],
        "labels": ["Kuliner"],
        "categories": ["Tempat Kuliner"],
    },
    "shopping": {
        "intents": ["Belanja"],
        "labels": ["Belanja", "Indoor"],
        "categories": ["Tempat Belanja"],
    },
    "history": {
        "intents": ["Sejarah"],
        "labels": ["Sejarah", "Edukasi"],
        "categories": ["Tempat Sejarah"],
    },
    "culture": {
        "intents": ["Budaya"],
        "labels": ["Budaya"],
        "categories": ["Tempat Budaya", "Tempat Seni", "Desa Wisata"],
    },
    "wildlife": {
        "intents": [],
        "labels": ["Satwa", "Ramah Anak", "Keluarga"],
        "categories": ["Wisata Satwa"],
    },
    "religion": {
        "intents": ["Religi"],
        "labels": ["Religi", "Santai/Healing"],
        "categories": ["Tempat Ibadah"],
    },
    "education": {
        "intents": ["Edukasi"],
        "labels": ["Edukasi"],
        "categories": ["Tempat Belajar"],
    },
    "family": {
        "intents": ["Keluarga"],
        "labels": ["Keluarga", "Ramah Anak"],
        "categories": ["Rekreasi Keluarga", "Wahana Air"],
    },
    "healing": {
        "intents": ["Santai/Healing"],
        "labels": ["Santai/Healing", "Alam"],
        "categories": ["Taman Kota", "Wisata Alam"],
    },
    "photo_spot": {
        "intents": [],
        "labels": ["Spot Foto"],
        "categories": [],
    },
    "adventure": {
        "intents": ["Petualangan"],
        "labels": ["Petualangan", "Outdoor"],
        "categories": ["Wisata Petualangan", "Tempat Camping"],
    },
    "indoor": {
        "intents": [],
        "labels": ["Indoor"],
        "categories": ["Tempat Belanja", "Tempat Belajar"],
    },
    "outdoor": {
        "intents": [],
        "labels": ["Outdoor", "Alam"],
        "categories": ["Wisata Alam", "Taman Kota", "Tempat Camping"],
    },
    "night": {
        "intents": [],
        "labels": ["Malam"],
        "categories": ["Tempat Kuliner", "Taman Kota"],
    },
    "child_friendly": {
        "intents": ["Keluarga"],
        "labels": ["Ramah Anak", "Keluarga"],
        "categories": ["Rekreasi Keluarga", "Wisata Satwa"],
    },
}


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str):
        return [value]
    return []


def _normalize_score(value: Optional[float], fallback: float = 0.0) -> float:
    if value is None:
        return fallback
    if value <= 5:
        return max(0.0, min(100.0, value * 20))
    return max(0.0, min(100.0, value))


def _selected_values(preference: UserPreference) -> list[str]:
    selected: list[str] = []
    selected.extend(_as_list(preference.favorite_place_types))
    selected.extend(_as_list(preference.favorite_activities))
    selected.extend(_as_list(preference.preferred_atmospheres))
    if preference.visitor_target:
        selected.append(str(preference.visitor_target))
    return list(dict.fromkeys(selected))


def _label_set(dest: Destination) -> set[str]:
    labels = dest.labels
    values: set[str] = set()
    if labels:
        if labels.primary_intent:
            values.add(labels.primary_intent)
        values.update(_as_list(labels.core_labels))
        values.update(_as_list(labels.secondary_labels))
    return values


def _matches_any(values: Iterable[str], candidates: Iterable[str]) -> bool:
    return bool(set(values).intersection(candidates))


def _preference_match_score(
    dest: Destination,
    preference: UserPreference,
) -> tuple[float, list[str]]:
    labels = dest.labels
    facilities = dest.facilities
    selected = _selected_values(preference)
    destination_labels = _label_set(dest)
    matched_labels: list[str] = []
    score = 0.0

    for value in selected:
        mapping = PREFERENCE_MATCHES.get(value)
        if not mapping:
            continue

        intent_match = bool(
            labels
            and labels.primary_intent
            and labels.primary_intent in mapping["intents"]
        )
        label_match = _matches_any(destination_labels, mapping["labels"])
        category_match = bool(
            dest.category and dest.category in mapping["categories"]
        )

        if intent_match:
            score += 22
        if label_match:
            score += 18
        if category_match:
            score += 12

        if intent_match or label_match or category_match:
            matched_labels.extend(mapping["intents"] or mapping["labels"])

    if preference.free_only:
        if dest.price_type and dest.price_type.lower() == "gratis":
            score += 25
            matched_labels.append("Gratis")
        elif dest.price_min == 0 and dest.price_max == 0:
            score += 25
            matched_labels.append("Gratis")

    if preference.visitor_target == "child_friendly":
        if facilities and facilities.child_friendly:
            score += 22
            matched_labels.append("Ramah Anak")

    if "indoor" in selected and facilities and facilities.indoor_available:
        score += 18
        matched_labels.append("Indoor")

    if "night" in selected and facilities and facilities.night_available:
        score += 18
        matched_labels.append("Malam")

    return min(score, 100.0), list(dict.fromkeys(matched_labels))


def _personal_score(
    dest: Destination,
    preference: UserPreference,
) -> tuple[float, list[str]]:
    quality_fallback = _normalize_score(dest.avg_rating)
    quality_score = _normalize_score(dest.quality_score, quality_fallback)
    popularity_score = _normalize_score(dest.popular_score)
    match_score, matched_labels = _preference_match_score(dest, preference)
    final_score = (
        0.60 * quality_score
        + 0.30 * match_score
        + 0.10 * popularity_score
    )
    return round(final_score, 2), matched_labels


def _personal_reason(matched_labels: list[str]) -> str:
    if not matched_labels:
        return (
            "Direkomendasikan dari kualitas destinasi dan preferensi wisata "
            "yang kamu pilih."
        )
    visible = matched_labels[:3]
    if len(visible) == 1:
        labels = visible[0]
    elif len(visible) == 2:
        labels = f"{visible[0]} dan {visible[1]}"
    else:
        labels = f"{visible[0]}, {visible[1]}, dan {visible[2]}"
    return f"Cocok karena kamu memilih preferensi {labels}."


def get_recommended_destinations(
    db: Session,
    *,
    page: int,
    limit: int,
    preference: Optional[UserPreference] = None,
) -> tuple[list[dict], int]:
    """Return guest quality recommendations or personalized recommendations."""
    if preference is None:
        return get_destinations(
            db,
            page=page,
            limit=limit,
            sort="quality",
        )

    query = _active_with_media_query(db).options(
        joinedload(Destination.media),
        joinedload(Destination.labels),
        joinedload(Destination.facilities),
    )

    if preference.free_only:
        query = query.filter(
            or_(
                func.lower(Destination.price_type) == "gratis",
                and_(Destination.price_min == 0, Destination.price_max == 0),
            )
        )

    destinations = query.all()
    ranked: list[tuple[float, list[str], Destination]] = []
    for destination in destinations:
        score, matched_labels = _personal_score(destination, preference)
        ranked.append((score, matched_labels, destination))

    ranked.sort(
        key=lambda item: (
            item[0],
            item[2].quality_score or 0,
            item[2].avg_rating or 0,
            item[2].total_reviews or 0,
        ),
        reverse=True,
    )

    total = len(ranked)
    offset = (page - 1) * limit
    page_items = ranked[offset: offset + limit]

    cards: list[dict] = []
    for score, matched_labels, destination in page_items:
        card = build_destination_card(destination, sort="quality")
        card["score"] = score
        card["scoreReason"] = _personal_reason(matched_labels)
        cards.append(card)

    return cards, total
