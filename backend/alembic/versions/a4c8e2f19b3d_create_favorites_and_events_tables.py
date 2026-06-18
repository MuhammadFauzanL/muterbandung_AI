"""create user_favorites and user_destination_events tables

Revision ID: a4c8e2f19b3d
Revises: 31b7d82e6a10
Create Date: 2026-06-18 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "a4c8e2f19b3d"
down_revision: Union[str, None] = "31b7d82e6a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user_favorites ──
    op.create_table(
        "user_favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "destination_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["destination_id"], ["destinations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_favorites_user_dest",
        "user_favorites",
        ["user_id", "destination_id"],
        unique=True,
    )
    op.create_index(
        "ix_user_favorites_user_id",
        "user_favorites",
        ["user_id"],
    )

    # ── user_destination_events ──
    op.create_table(
        "user_destination_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "destination_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column(
            "event_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["destination_id"], ["destinations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ude_user_type",
        "user_destination_events",
        ["user_id", "event_type"],
    )
    op.create_index(
        "ix_ude_user_created",
        "user_destination_events",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_ude_user_created", table_name="user_destination_events")
    op.drop_index("ix_ude_user_type", table_name="user_destination_events")
    op.drop_table("user_destination_events")

    op.drop_index("ix_user_favorites_user_id", table_name="user_favorites")
    op.drop_index("ix_user_favorites_user_dest", table_name="user_favorites")
    op.drop_table("user_favorites")
