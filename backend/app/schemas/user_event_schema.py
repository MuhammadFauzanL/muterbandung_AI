"""
Pydantic schemas for user event tracking.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


ALLOWED_EVENT_TYPES = (
    "search",
    "filter_apply",
    "view_detail",
    "favorite_add",
    "favorite_remove",
    "planner_add",
)


class TrackEventRequest(BaseModel):
    """Payload sent by the frontend to record an interaction event."""

    event_type: Literal[
        "search",
        "filter_apply",
        "view_detail",
        "favorite_add",
        "favorite_remove",
        "planner_add",
    ] = Field(..., description="Type of user interaction")
    destination_id: Optional[str] = Field(
        None,
        description="External destination ID (LOC-xxx). Null for search/filter events.",
    )
    metadata: Optional[dict] = Field(
        None,
        description="Extra context: search query, filter values, etc.",
    )
