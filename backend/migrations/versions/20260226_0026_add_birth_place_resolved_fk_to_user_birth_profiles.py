"""add birth_place_resolved_id foreign key to user_birth_profiles

Revision ID: 20260226_0026
Revises: 20260226_0025
Create Date: 2026-02-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260226_0026"
down_revision: Union[str, Sequence[str], None] = "20260226_0025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user_birth_profiles", schema=None) as batch_op:
        batch_op.add_column(sa.Column("birth_place_resolved_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            "ix_user_birth_profiles_birth_place_resolved_id",
            ["birth_place_resolved_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            "fk_user_birth_profiles_birth_place_resolved_id",
            "geo_place_resolved",
            ["birth_place_resolved_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("user_birth_profiles", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_user_birth_profiles_birth_place_resolved_id",
            type_="foreignkey",
        )
        batch_op.drop_index("ix_user_birth_profiles_birth_place_resolved_id")
        batch_op.drop_column("birth_place_resolved_id")
