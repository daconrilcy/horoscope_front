"""add current location to user_birth_profiles

Revision ID: 20260307_0031
Revises: 7fc050e24744
Create Date: 2026-03-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260307_0031"
down_revision: Union[str, Sequence[str], None] = "7fc050e24744"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_birth_profiles",
        sa.Column("geolocation_consent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("current_city", sa.String(255), nullable=True),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("current_country", sa.String(100), nullable=True),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("current_lat", sa.Float(), nullable=True),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("current_lon", sa.Float(), nullable=True),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("current_location_display", sa.String(255), nullable=True),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("current_timezone", sa.String(64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_birth_profiles", "current_timezone")
    op.drop_column("user_birth_profiles", "current_location_display")
    op.drop_column("user_birth_profiles", "current_lon")
    op.drop_column("user_birth_profiles", "current_lat")
    op.drop_column("user_birth_profiles", "current_country")
    op.drop_column("user_birth_profiles", "current_city")
    op.drop_column("user_birth_profiles", "geolocation_consent")
