"""
Service layer for storing and retrieving user onboarding preferences.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference
from app.schemas.user_preference_schema import UserPreferenceUpsertRequest


def _unique(values: list[str]) -> list[str]:
    """Preserve order while removing duplicate preference values."""
    return list(dict.fromkeys(values))


def get_user_preference(db: Session, user_id) -> Optional[UserPreference]:
    """Return the preference profile for a user, if one exists."""
    return (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )


def upsert_user_preference(
    db: Session,
    *,
    user_id,
    payload: UserPreferenceUpsertRequest,
) -> UserPreference:
    """Create or update the current user's preference profile."""
    preference = get_user_preference(db, user_id)
    if preference is None:
        preference = UserPreference(user_id=user_id)
        db.add(preference)

    preference.favorite_place_types = _unique(payload.favorite_place_types)
    preference.favorite_activities = _unique(payload.favorite_activities)
    preference.visitor_target = payload.visitor_target
    preference.preferred_atmospheres = _unique(payload.preferred_atmospheres)
    preference.free_only = payload.free_only

    db.commit()
    db.refresh(preference)
    return preference
