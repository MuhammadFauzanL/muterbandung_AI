"""
DestinationLabel model – stores AI-generated labels and confidence scores.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DestinationLabel(Base):
    """AI labels (intents, core/secondary/avoid labels) for a destination."""

    __tablename__ = "destination_labels"

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

    primary_intent = Column(
        String(100), nullable=True,
        comment="Main intent from AI labeling (e.g. Alam, Belanja)",
    )
    core_labels = Column(
        JSONB, nullable=True,
        comment='JSON array, e.g. ["Belanja","Indoor","Gratis"]',
    )
    secondary_labels = Column(
        JSONB, nullable=True,
        comment='JSON array of secondary labels',
    )
    avoid_labels = Column(
        JSONB, nullable=True,
        comment='JSON array of labels to avoid',
    )
    label_confidence = Column(Float, nullable=True)
    label_source = Column(
        String(50), nullable=True,
        comment="auto_rule_v1 / manual_browser_review_v1",
    )
    label_scores = Column(
        JSONB, nullable=True,
        comment='Per-label scores, e.g. {"Alam": 8.8, "Belanja": -2.0}',
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
        back_populates="labels",
    )

    def __repr__(self) -> str:
        return f"<DestinationLabel destination_id={self.destination_id}>"
