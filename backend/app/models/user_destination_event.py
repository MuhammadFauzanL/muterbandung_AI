"""
UserDestinationEvent model – lightweight interaction tracking for
behavioral personalization.

Event types:
  - search: user performed a text search
  - filter_apply: user applied explore filters
  - view_detail: user opened a destination detail page
  - favorite_add: user added a destination to favorites
  - favorite_remove: user removed a destination from favorites
  - planner_add: user added a destination to planner
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserDestinationEvent(Base):
    """Single interaction event between a user and a destination."""

    __tablename__ = "user_destination_events"
    __table_args__ = (
        Index("ix_ude_user_type", "user_id", "event_type"),
        Index("ix_ude_user_created", "user_id", "created_at"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    destination_id = Column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=True,  # null for search / filter_apply events
    )
    event_type = Column(
        String(30),
        nullable=False,
    )
    event_metadata = Column(
        JSONB,
        nullable=True,  # search query, filter values, etc.
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="events")
    destination = relationship("Destination")

    def __repr__(self) -> str:
        return (
            f"<UserDestinationEvent type={self.event_type} "
            f"user={self.user_id} dest={self.destination_id}>"
        )
