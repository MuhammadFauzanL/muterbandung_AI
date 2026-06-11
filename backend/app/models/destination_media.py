"""
DestinationMedia model – stores image, maps URL, and website for a destination.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DestinationMedia(Base):
    """Media assets (image, maps link, website) for a destination."""

    __tablename__ = "destination_media"

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

    media_available = Column(Boolean, nullable=True)
    image_url = Column(Text, nullable=True)
    maps_url = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)
    media_source = Column(String(100), nullable=True)
    place_id = Column(String(100), nullable=True)
    media_audit_status = Column(
        String(20), nullable=True,
        comment="accepted / manual_accepted / missing / rejected / pending",
    )

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
        back_populates="media",
    )

    def __repr__(self) -> str:
        return f"<DestinationMedia destination_id={self.destination_id}>"
