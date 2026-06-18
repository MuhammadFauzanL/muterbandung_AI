"""
User favorites endpoints.

- GET    /me/favorites                    — list favorited destinations
- POST   /me/favorites/{destination_id}   — add to favorites
- DELETE /me/favorites/{destination_id}   — remove from favorites
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.services.user_event_service import track_event
from app.services.user_favorite_service import (
    add_favorite,
    get_user_favorites,
    remove_favorite,
)
from app.utils.response import paginated_response, success_response

router = APIRouter(prefix="/me/favorites")


@router.get("")
def list_favorites(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return paginated list of user's favorited destinations."""
    items, total = get_user_favorites(
        db, current_user.id, page=page, limit=limit,
    )
    return paginated_response(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message="User favorites retrieved successfully",
    )


@router.post("/{destination_id}")
def add_to_favorites(
    destination_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a destination to user favorites (idempotent)."""
    favorite = add_favorite(db, current_user.id, destination_id)
    if favorite is None:
        return JSONResponse(
            status_code=404,
            content={
                "statusCode": 404,
                "message": f"Destination {destination_id} not found",
            },
        )

    # Also record as event for behavioral profiling
    track_event(
        db,
        current_user.id,
        "favorite_add",
        destination_external_id=destination_id,
    )

    return success_response(
        data={"destinationId": destination_id},
        message="Destination added to favorites",
        status_code=201,
    )


@router.delete("/{destination_id}")
def remove_from_favorites(
    destination_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a destination from user favorites."""
    deleted = remove_favorite(db, current_user.id, destination_id)

    if deleted:
        # Record removal event
        track_event(
            db,
            current_user.id,
            "favorite_remove",
            destination_external_id=destination_id,
        )

    return success_response(
        message="Destination removed from favorites",
        status_code=200,
    )
