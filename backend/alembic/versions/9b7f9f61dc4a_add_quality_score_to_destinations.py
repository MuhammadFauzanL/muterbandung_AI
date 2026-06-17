"""add quality score to destinations

Revision ID: 9b7f9f61dc4a
Revises: e805abd6f11b
Create Date: 2026-06-18 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b7f9f61dc4a"
down_revision: Union[str, None] = "e805abd6f11b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "destinations",
        sa.Column(
            "quality_score",
            sa.Float(),
            nullable=True,
            comment="Quality-oriented ranking score for recommendations",
        ),
    )
    op.create_index(
        op.f("ix_destinations_quality_score"),
        "destinations",
        ["quality_score"],
        unique=False,
    )
    op.create_index(
        "ix_destinations_active_quality",
        "destinations",
        ["curation_action", "display_status", "quality_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_destinations_active_quality", table_name="destinations")
    op.drop_index(op.f("ix_destinations_quality_score"), table_name="destinations")
    op.drop_column("destinations", "quality_score")
