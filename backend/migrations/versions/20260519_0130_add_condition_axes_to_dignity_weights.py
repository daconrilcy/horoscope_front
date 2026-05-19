"""Ajoute les axes conditionnels aux poids de dignites.

Revision ID: 20260519_0130
Revises: 20260519_0129
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0130"
down_revision: Union[str, Sequence[str], None] = "20260519_0129"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCORE_WEIGHT_TABLES = (
    "astral_essential_dignity_score_weights",
    "astral_accidental_dignity_score_weights",
)
CONDITION_AXIS_COLUMNS = (
    "visibility_weight",
    "stability_weight",
    "coherence_weight",
    "support_weight",
    "constraint_weight",
)


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base migree."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    """Indique si une colonne est deja presente."""
    if not _table_exists(table_name):
        return False
    return column_name in {
        str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def upgrade() -> None:
    """Ajoute des axes neutres compatibles avec les seeds existants."""
    for table_name in SCORE_WEIGHT_TABLES:
        if not _table_exists(table_name):
            continue
        for column_name in CONDITION_AXIS_COLUMNS:
            if not _column_exists(table_name, column_name):
                op.add_column(
                    table_name,
                    sa.Column(column_name, sa.Float(), nullable=False, server_default="0.0"),
                )


def downgrade() -> None:
    """Retire les axes conditionnels des poids de dignites."""
    for table_name in reversed(SCORE_WEIGHT_TABLES):
        if not _table_exists(table_name):
            continue
        for column_name in reversed(CONDITION_AXIS_COLUMNS):
            if _column_exists(table_name, column_name):
                op.drop_column(table_name, column_name)
