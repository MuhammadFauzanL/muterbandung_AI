"""create destination gallery images table

Revision ID: c2d4e6f8a9b1
Revises: b7a1c9d3e4f2
Create Date: 2026-06-18 20:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c2d4e6f8a9b1"
down_revision: Union[str, None] = "b7a1c9d3e4f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "destination_gallery_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("destination_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("source_image_url", sa.Text(), nullable=True),
        sa.Column("media_public_id", sa.String(length=255), nullable=True),
        sa.Column("match_confidence", sa.String(length=50), nullable=True),
        sa.Column("matched_title", sa.String(length=255), nullable=True),
        sa.Column("upload_status", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["destination_id"],
            ["destinations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_destination_gallery_images_destination_sort",
        "destination_gallery_images",
        ["destination_id", "sort_order"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_destination_gallery_images_destination_sort",
        table_name="destination_gallery_images",
    )
    op.drop_table("destination_gallery_images")
