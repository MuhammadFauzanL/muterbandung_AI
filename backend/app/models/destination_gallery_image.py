"""
DestinationGalleryImage model – stores multiple gallery images per destination.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DestinationGalleryImage(Base):
    """Gallery image imported from the curated wisata_image.csv dataset."""

    __tablename__ = "destination_gallery_images"

    __table_args__ = (
        Index(
            "ix_destination_gallery_images_destination_sort",
            "destination_id",
            "sort_order",
            unique=True,
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    destination_id = Column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order = Column(Integer, nullable=False)
    image_url = Column(Text, nullable=False)
    source_image_url = Column(Text, nullable=True)
    media_public_id = Column(String(255), nullable=True)
    match_confidence = Column(String(50), nullable=True)
    matched_title = Column(String(255), nullable=True)
    upload_status = Column(String(50), nullable=True)

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

    destination = relationship(
        "Destination",
        back_populates="gallery_images",
    )

    def __repr__(self) -> str:
        return (
            f"<DestinationGalleryImage destination_id={self.destination_id} "
            f"sort_order={self.sort_order}>"
        )
