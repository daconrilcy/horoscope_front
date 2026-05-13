"""add astral dignity type

Revision ID: 20260513_0088
Revises: 20260513_0087
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0088"
down_revision: Union[str, Sequence[str], None] = "20260513_0087"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DIGNITY_TYPE_ROWS = (
    {"code": "domicile", "name": "Domicile"},
    {"code": "detriment", "name": "Detriment"},
    {"code": "exaltation", "name": "Exaltation"},
    {"code": "fall", "name": "Fall"},
)


def upgrade() -> None:
    """Crée le référentiel stable des types de dignités astrologiques."""
    op.create_table(
        "astral_dignity_type",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        op.f("ix_astral_dignity_type_code"),
        "astral_dignity_type",
        ["code"],
        unique=False,
    )
    op.bulk_insert(
        sa.table(
            "astral_dignity_type",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        list(DIGNITY_TYPE_ROWS),
    )


def downgrade() -> None:
    """Supprime le référentiel des types de dignités astrologiques."""
    op.drop_index(op.f("ix_astral_dignity_type_code"), table_name="astral_dignity_type")
    op.drop_table("astral_dignity_type")
