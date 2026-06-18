"""
Service layer for user favorites.

Handles CRUD operations on the user_favorites table and provides
helper functions for injecting is_favorite into destination cards.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.user_favorite import UserFavorite
from app.services.destination_service import (
    _active_with_media_query,
    build_destination_card,
)


def get_favorite_destination_ids(
    db: Session,
    user_id: UUID,
) -> set[UUID]:
    """Return a set of internal destination UUIDs favorited by this user."""
    rows = (
        db.query(UserFavorite.destination_id)
        .filter(UserFavorite.user_id == user_id)
        .all()
    )
    return {row[0] for row in rows}


def get_favorite_external_ids(
    db: Session,
    user_id: UUID,
) -> set[str]:
    """Return a set of external destination IDs (LOC-xxx) favorited by this user."""
    rows = (
        db.query(Destination.external_id)
        .join(UserFavorite, UserFavorite.destination_id == Destination.id)
        .filter(UserFavorite.user_id == user_id)
        .all()
    )
    return {row[0] for row in rows}


def is_favorite(
    db: Session,
    user_id: UUID,
    destination_internal_id: UUID,
) -> bool:
    """Check if a specific destination is favorited by this user."""
    return (
        db.query(UserFavorite.id)
        .filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.destination_id == destination_internal_id,
            )
        )
        .first()
        is not None
    )


def add_favorite(
    db: Session,
    user_id: UUID,
    destination_external_id: str,
) -> Optional[UserFavorite]:
    """Add a destination to user favorites (idempotent).

    Returns the UserFavorite row, or None if the destination does not exist.
    """
    dest = (
        db.query(Destination)
        .filter(Destination.external_id == destination_external_id)
        .first()
    )
    if dest is None:
        return None

    existing = (
        db.query(UserFavorite)
        .filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.destination_id == dest.id,
            )
        )
        .first()
    )
    if existing:
        return existing

    favorite = UserFavorite(user_id=user_id, destination_id=dest.id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(
    db: Session,
    user_id: UUID,
    destination_external_id: str,
) -> bool:
    """Remove a destination from user favorites.

    Returns True if a row was deleted, False if nothing existed.
    """
    dest = (
        db.query(Destination)
        .filter(Destination.external_id == destination_external_id)
        .first()
    )
    if dest is None:
        return False

    deleted = (
        db.query(UserFavorite)
        .filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.destination_id == dest.id,
            )
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted > 0


def get_user_favorites(
    db: Session,
    user_id: UUID,
    *,
    page: int = 1,
    limit: int = 12,
) -> tuple[list[dict], int]:
    """Return paginated destination cards for a user's favorites."""
    from sqlalchemy.orm import joinedload

    base = (
        _active_with_media_query(db)
        .join(
            UserFavorite,
            and_(
                UserFavorite.destination_id == Destination.id,
                UserFavorite.user_id == user_id,
            ),
        )
        .options(
            joinedload(Destination.media),
            joinedload(Destination.labels),
            joinedload(Destination.facilities),
        )
    )

    total = base.count()

    destinations = (
        base.order_by(UserFavorite.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    cards: list[dict] = []
    for dest in destinations:
        card = build_destination_card(dest, sort="quality")
        card["isFavorite"] = True
        cards.append(card)

    return cards, total
