"""
Accommodation model – stores hotel/villa/guest house data.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class Accommodation(Base):
    """Accommodation record imported from the curated lodging dataset."""

    __tablename__ = "accommodations"

    __table_args__ = (
        Index(
            "ix_accommodations_active_type",
            "display_status",
            "is_active",
            "accommodation_type",
        ),
        Index(
            "ix_accommodations_active_rating",
            "display_status",
            "is_active",
            "avg_rating",
        ),
        Index(
            "ix_accommodations_coordinates",
            "latitude",
            "longitude",
        ),
    )

    # ── Identity ─────────────────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    external_id = Column(
        String(30),
        unique=True,
        index=True,
        nullable=False,
        comment="Original lodging ID from dataset (e.g. LODGE-00001)",
    )
    slug = Column(String(300), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)

    # ── Classification ───────────────────────────────────
    category = Column(String(100), index=True, nullable=True)
    accommodation_type = Column(String(100), index=True, nullable=True)
    description = Column(Text, nullable=True)
    facilities = Column(
        JSONB,
        nullable=True,
        comment='Facility labels parsed from description, e.g. ["Wi-Fi", "Parkir"]',
    )

    # ── Location ─────────────────────────────────────────
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    distance_from_center_km = Column(Float, nullable=True)
    coordinate_verified = Column(Boolean, nullable=True)

    # ── Price ────────────────────────────────────────────
    price_min = Column(Integer, nullable=True)
    price_max = Column(Integer, nullable=True)

    # ── Rating & Sentiment ───────────────────────────────
    avg_rating = Column(Float, nullable=True)
    total_reviews = Column(Integer, nullable=True)
    positive_reviews = Column(Integer, nullable=True)
    negative_reviews = Column(Integer, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    avg_sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(30), nullable=True)
    sentiment_available = Column(Boolean, nullable=True)

    # ── Media / External Links ───────────────────────────
    image_url = Column(Text, nullable=True)
    destination_url = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)
    media_source = Column(String(80), nullable=True)
    media_available = Column(Boolean, nullable=True)

    # ── Display Status ───────────────────────────────────
    display_status = Column(String(30), index=True, nullable=True)
    is_active = Column(Boolean, index=True, nullable=True)

    # ── Computed Scores ──────────────────────────────────
    quality_score = Column(
        Float,
        index=True,
        nullable=True,
        comment="Quality score calculated during accommodation import",
    )

    # ── Raw / Audit ──────────────────────────────────────
    source_payload = Column(JSONB, nullable=True)

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

    def __repr__(self) -> str:
        return f"<Accommodation {self.external_id}: {self.name}>"
