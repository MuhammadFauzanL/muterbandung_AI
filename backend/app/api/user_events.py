"""
User event tracking endpoints.

- POST /me/events — fire-and-forget interaction event recording
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.schemas.user_event_schema import TrackEventRequest
from app.services.user_event_service import track_event
from app.utils.response import success_response

router = APIRouter(prefix="/me")


@router.post("/events")
def record_event(
    body: TrackEventRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a user interaction event for behavioral profiling."""
    track_event(
        db,
        current_user.id,
        event_type=body.event_type,
        destination_external_id=body.destination_id,
        metadata=body.metadata,
    )
    return success_response(
        message="Event recorded",
        status_code=201,
    )
