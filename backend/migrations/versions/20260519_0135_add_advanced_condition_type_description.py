"""Ajoute la description aux types de conditions avancees.

Revision ID: 20260519_0135
Revises: 20260519_0134
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0135"
down_revision: Union[str, Sequence[str], None] = "20260519_0134"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "astral_advanced_condition_types"


def _column_exists(table_name: str, column_name: str) -> bool:
    """Indique si une colonne existe dans la table cible."""
    return any(
        column["name"] == column_name
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    )


def upgrade() -> None:
    """Ajoute le champ explicatif requis par le brief initial."""
    if not _column_exists(TABLE, "description"):
        op.add_column(
            TABLE,
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
        )
    if op.get_bind().dialect.name == "sqlite":
        return
    if _column_exists(TABLE, "description"):
        op.alter_column(TABLE, "description", server_default=None)


def downgrade() -> None:
    """Retire le champ explicatif des types avances."""
    if _column_exists(TABLE, "description"):
        op.drop_column(TABLE, "description")
