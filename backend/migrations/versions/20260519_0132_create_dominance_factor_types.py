"""Cree le referentiel des facteurs de dominance planetaire.

Revision ID: 20260519_0132
Revises: 20260519_0131
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0132"
down_revision: Union[str, Sequence[str], None] = "20260519_0131"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_dominance_factor_types"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base migree."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    """Ajoute la table versionnee des facteurs de dominance."""
    if _table_exists(TABLE_NAME):
        return
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("default_weight", sa.Float(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "default_weight >= 0",
            name="ck_astral_dominance_factor_types_weight",
        ),
        sa.ForeignKeyConstraint(
            ["reference_version_id"],
            ["astral_reference_versions.id"],
        ),
        sa.UniqueConstraint(
            "reference_version_id",
            "code",
            name="uq_astral_dominance_factor_types_scope",
        ),
    )
    op.create_index("ix_astral_dominance_factor_types_code", TABLE_NAME, ["code"])
    op.create_index("ix_astral_dominance_factor_types_category", TABLE_NAME, ["category"])
    op.create_index(
        "ix_astral_dominance_factor_types_reference_version_id",
        TABLE_NAME,
        ["reference_version_id"],
    )


def downgrade() -> None:
    """Supprime la table des facteurs de dominance."""
    if _table_exists(TABLE_NAME):
        op.drop_table(TABLE_NAME)
