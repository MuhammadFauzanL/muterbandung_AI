"""
User preference endpoints.

- GET /me/preferences  — retrieve current user's onboarding preferences
- PUT /me/preferences  — create/update current user's onboarding preferences
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.schemas.user_preference_schema import (
    UserPreferenceResponse,
    UserPreferenceUpsertRequest,
)
from app.services.user_preference_service import (
    get_user_preference,
    upsert_user_preference,
)
from app.utils.response import success_response

router = APIRouter()


@router.get("/me/preferences")
def get_my_preferences(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return preferences for the currently authenticated user."""
    preference = get_user_preference(db, current_user.id)
    if preference is None:
        return success_response(
            data=None,
            message="User preferences not set",
        )

    data = UserPreferenceResponse.from_entity(preference)
    return success_response(
        data=data.model_dump(mode="json"),
        message="User preferences retrieved successfully",
    )


@router.put("/me/preferences")
def put_my_preferences(
    payload: UserPreferenceUpsertRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update preferences for the currently authenticated user."""
    preference = upsert_user_preference(
        db,
        user_id=current_user.id,
        payload=payload,
    )
    data = UserPreferenceResponse.from_entity(preference)
    return success_response(
        data=data.model_dump(mode="json"),
        message="User preferences saved successfully",
    )
