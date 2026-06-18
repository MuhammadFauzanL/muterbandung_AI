"""create accommodations table

Revision ID: b7a1c9d3e4f2
Revises: a4c8e2f19b3d
Create Date: 2026-06-18 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b7a1c9d3e4f2"
down_revision: Union[str, None] = "a4c8e2f19b3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accommodations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=30), nullable=False),
        sa.Column("slug", sa.String(length=300), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("accommodation_type", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "facilities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("distance_from_center_km", sa.Float(), nullable=True),
        sa.Column("coordinate_verified", sa.Boolean(), nullable=True),
        sa.Column("price_min", sa.Integer(), nullable=True),
        sa.Column("price_max", sa.Integer(), nullable=True),
        sa.Column("avg_rating", sa.Float(), nullable=True),
        sa.Column("total_reviews", sa.Integer(), nullable=True),
        sa.Column("positive_reviews", sa.Integer(), nullable=True),
        sa.Column("negative_reviews", sa.Integer(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("avg_sentiment_score", sa.Float(), nullable=True),
        sa.Column("sentiment_label", sa.String(length=30), nullable=True),
        sa.Column("sentiment_available", sa.Boolean(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("destination_url", sa.Text(), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("media_source", sa.String(length=80), nullable=True),
        sa.Column("media_available", sa.Boolean(), nullable=True),
        sa.Column("display_status", sa.String(length=30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column(
            "source_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_accommodations_external_id"),
        "accommodations",
        ["external_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_accommodations_slug"),
        "accommodations",
        ["slug"],
        unique=True,
    )
    op.create_index(
        op.f("ix_accommodations_name"),
        "accommodations",
        ["name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_accommodations_category"),
        "accommodations",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_accommodations_accommodation_type"),
        "accommodations",
        ["accommodation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_accommodations_display_status"),
        "accommodations",
        ["display_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_accommodations_is_active"),
        "accommodations",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_accommodations_quality_score"),
        "accommodations",
        ["quality_score"],
        unique=False,
    )
    op.create_index(
        "ix_accommodations_active_type",
        "accommodations",
        ["display_status", "is_active", "accommodation_type"],
        unique=False,
    )
    op.create_index(
        "ix_accommodations_active_rating",
        "accommodations",
        ["display_status", "is_active", "avg_rating"],
        unique=False,
    )
    op.create_index(
        "ix_accommodations_coordinates",
        "accommodations",
        ["latitude", "longitude"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_accommodations_coordinates", table_name="accommodations")
    op.drop_index("ix_accommodations_active_rating", table_name="accommodations")
    op.drop_index("ix_accommodations_active_type", table_name="accommodations")
    op.drop_index(op.f("ix_accommodations_quality_score"), table_name="accommodations")
    op.drop_index(op.f("ix_accommodations_is_active"), table_name="accommodations")
    op.drop_index(op.f("ix_accommodations_display_status"), table_name="accommodations")
    op.drop_index(
        op.f("ix_accommodations_accommodation_type"),
        table_name="accommodations",
    )
    op.drop_index(op.f("ix_accommodations_category"), table_name="accommodations")
    op.drop_index(op.f("ix_accommodations_name"), table_name="accommodations")
    op.drop_index(op.f("ix_accommodations_slug"), table_name="accommodations")
    op.drop_index(op.f("ix_accommodations_external_id"), table_name="accommodations")
    op.drop_table("accommodations")
