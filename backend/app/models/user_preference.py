"""
UserPreference model - stores onboarding preference choices for personalization.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserPreference(Base):
    """Preference profile selected by a registered user during onboarding."""

    __tablename__ = "user_preferences"
    __table_args__ = (
        Index("ix_user_preferences_user_id", "user_id", unique=True),
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
    favorite_place_types = Column(JSONB, nullable=False, default=list)
    favorite_activities = Column(JSONB, nullable=False, default=list)
    visitor_target = Column(JSONB, nullable=True)
    preferred_atmospheres = Column(JSONB, nullable=False, default=list)
    free_only = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="preference")

    def __repr__(self) -> str:
        return f"<UserPreference user_id={self.user_id}>"
