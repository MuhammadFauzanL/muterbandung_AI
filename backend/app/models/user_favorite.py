"""
UserFavorite model – stores permanent favorite destinations per user.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserFavorite(Base):
    """A destination that a user has explicitly favorited (hearted)."""

    __tablename__ = "user_favorites"
    __table_args__ = (
        Index(
            "ix_user_favorites_user_dest",
            "user_id",
            "destination_id",
            unique=True,
        ),
        Index("ix_user_favorites_user_id", "user_id"),
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
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="favorites")
    destination = relationship("Destination")

    def __repr__(self) -> str:
        return f"<UserFavorite user={self.user_id} dest={self.destination_id}>"
