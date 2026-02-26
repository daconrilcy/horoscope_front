"""add optional location fields to user_birth_profiles

Revision ID: 20260225_0023
Revises: 20260225_0022
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260225_0023"
down_revision: Union[str, Sequence[str], None] = "20260225_0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_birth_profiles",
        sa.Column("birth_city", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "user_birth_profiles",
        sa.Column("birth_country", sa.String(length=100), nullable=True),
    )
    op.add_column("user_birth_profiles", sa.Column("birth_lat", sa.Float(), nullable=True))
    op.add_column("user_birth_profiles", sa.Column("birth_lon", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_birth_profiles", "birth_lon")
    op.drop_column("user_birth_profiles", "birth_lat")
    op.drop_column("user_birth_profiles", "birth_country")
    op.drop_column("user_birth_profiles", "birth_city")
