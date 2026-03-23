"""add provider_type to astrologer_profiles

Revision ID: 20260323_0905
Revises: f44760fae191
Create Date: 2026-03-23 09:05:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260323_0905"
down_revision = "f44760fae191"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("astrologer_profiles")}

    if "provider_type" not in column_names:
        op.add_column(
            "astrologer_profiles",
            sa.Column(
                "provider_type",
                sa.String(length=16),
                nullable=False,
                server_default="ia",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("astrologer_profiles")}

    if "provider_type" in column_names:
        op.drop_column("astrologer_profiles", "provider_type")
