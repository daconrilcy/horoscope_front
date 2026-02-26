"""make user_birth_profiles.birth_time nullable

Revision ID: 20260225_0022
Revises: 20260221_0021
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260225_0022"
down_revision: Union[str, Sequence[str], None] = "20260221_0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user_birth_profiles") as batch_op:
        batch_op.alter_column(
            "birth_time",
            existing_type=sa.String(length=8),
            nullable=True,
        )


def downgrade() -> None:
    # Use a valid fallback time before restoring NOT NULL constraint.
    op.execute("UPDATE user_birth_profiles SET birth_time = '00:00' WHERE birth_time IS NULL")
    with op.batch_alter_table("user_birth_profiles") as batch_op:
        batch_op.alter_column(
            "birth_time",
            existing_type=sa.String(length=8),
            nullable=False,
        )
