"""
Recommendation endpoints.

- GET /recommendations/destinations — guest or personalized destination cards
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_optional_current_user
from app.database import get_db
from app.services.recommendation_service import get_recommended_destinations
from app.services.user_preference_service import get_user_preference
from app.utils.response import paginated_response

router = APIRouter(prefix="/recommendations")


@router.get("/destinations")
def recommended_destinations(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    current_user=Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Return destination recommendations for guest or logged-in users."""
    preference = None
    user_id = None
    if current_user is not None:
        user_id = current_user.id
        preference = get_user_preference(db, current_user.id)

    items, total = get_recommended_destinations(
        db,
        page=page,
        limit=limit,
        preference=preference,
        user_id=user_id,
    )

    message = (
        "Personalized recommendations retrieved successfully"
        if preference is not None
        else "Default recommendations retrieved successfully"
    )
    return paginated_response(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message=message,
    )

