"""
DestinationFacility model – stores verified facility flags for a destination.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DestinationFacility(Base):
    """Facility availability flags for a destination."""

    __tablename__ = "destination_facilities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    destination_id = Column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    parking_available = Column(Boolean, nullable=True)
    wheelchair_accessible = Column(Boolean, nullable=True)
    toilet_available = Column(Boolean, nullable=True)
    mushola_available = Column(Boolean, nullable=True)
    pet_friendly = Column(Boolean, nullable=True)
    open_24h = Column(Boolean, nullable=True)
    child_friendly = Column(Boolean, nullable=True)
    night_available = Column(Boolean, nullable=True)
    indoor_available = Column(Boolean, nullable=True)
    safety_verified = Column(Boolean, nullable=True)

    # ── Timestamps ───────────────────────────────────────
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

    # ── Relationship ─────────────────────────────────────
    destination = relationship(
        "Destination",
        back_populates="facilities",
    )

    def __repr__(self) -> str:
        return f"<DestinationFacility destination_id={self.destination_id}>"
