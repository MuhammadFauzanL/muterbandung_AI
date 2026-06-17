"""
Destination model – stores core destination/tourism data.
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
from sqlalchemy.orm import relationship

from app.database import Base


class Destination(Base):
    """Core destination record imported from the curated CSV dataset."""

    __tablename__ = "destinations"

    __table_args__ = (
        Index(
            "ix_destinations_active_popular",
            "curation_action",
            "display_status",
            "popular_score",
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
        String(20), unique=True, index=True, nullable=False,
        comment="Original ID from dataset (e.g. LOC-001)",
    )
    slug = Column(
        String(300), unique=True, index=True, nullable=False,
        comment="URL-friendly identifier generated from name",
    )
    name = Column(String(255), index=True, nullable=False)

    # ── Classification ───────────────────────────────────
    category = Column(String(100), index=True, nullable=True)
    subcategory = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    tourism_zone = Column(
        String(100), index=True, nullable=True,
        comment="Short location label (e.g. Lembang, Ciwidey, Bandung Kota)",
    )
    synthetic_tags = Column(
        JSONB, nullable=True,
        comment='JSON array of tags, e.g. ["Belanja","Indoor","Kuliner"]',
    )
    crowd_level = Column(String(20), nullable=True)

    # ── Location ─────────────────────────────────────────
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_from_center_km = Column(
        Float, nullable=True,
        comment="Distance from Alun-Alun Bandung in km",
    )
    coordinate_verified = Column(Boolean, nullable=True)

    # ── Price ────────────────────────────────────────────
    price_min = Column(Integer, nullable=True)
    price_max = Column(Integer, nullable=True)
    price_type = Column(String(50), nullable=True)

    # ── Opening Hours ────────────────────────────────────
    opening_time = Column(String(10), nullable=True)
    closing_time = Column(String(10), nullable=True)
    weekday_opening_time = Column(String(10), nullable=True)
    weekday_closing_time = Column(String(10), nullable=True)
    weekend_opening_time = Column(String(10), nullable=True)
    weekend_closing_time = Column(String(10), nullable=True)

    # ── Duration ─────────────────────────────────────────
    estimated_duration_minutes = Column(Integer, nullable=True)

    # ── Rating & Sentiment ───────────────────────────────
    avg_rating = Column(Float, nullable=True)
    total_reviews = Column(Integer, nullable=True)
    positive_reviews = Column(Integer, nullable=True)
    negative_reviews = Column(Integer, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    avg_sentiment_score = Column(
        Float, nullable=True,
        comment="Fallback when sentiment_score is null",
    )
    sentiment_label = Column(String(20), nullable=True)
    sentiment_available = Column(Boolean, nullable=True)

    # ── Display Status ───────────────────────────────────
    curation_action = Column(
        String(20), index=True, nullable=True,
        comment="keep / remove",
    )
    display_status = Column(
        String(30), index=True, nullable=True,
        comment="active_candidate / exclude_scope / temporarily_hidden",
    )
    is_active = Column(
        Boolean, nullable=True,
        comment="From is_active_verified; not a mandatory MVP filter",
    )

    # ── Computed / Future ────────────────────────────────
    popular_score = Column(
        Float, index=True, nullable=True,
        comment="Calculated during CSV import (Phase 3)",
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

    # ── Relationships (one-to-one) ───────────────────────
    media = relationship(
        "DestinationMedia",
        back_populates="destination",
        uselist=False,
        cascade="all, delete-orphan",
    )
    labels = relationship(
        "DestinationLabel",
        back_populates="destination",
        uselist=False,
        cascade="all, delete-orphan",
    )
    facilities = relationship(
        "DestinationFacility",
        back_populates="destination",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Destination {self.external_id}: {self.name}>"
