"""Réconcilie les colonnes d'ordre des référentiels de dignités.

Revision ID: 20260519_0129
Revises: 20260519_0128
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0129"
down_revision: Union[str, Sequence[str], None] = "20260519_0128"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOOKUP_TABLES_WITH_SORT_ORDER = (
    "astral_dignity_functional_effects",
    "astral_dignity_intensity_effects",
    "astral_essential_dignity_categories",
    "astral_essential_dignity_expression_tendencies",
    "astral_accidental_dignity_categories",
    "astral_accidental_dignity_expression_tendencies",
    "astral_accidental_dignity_condition_schemas",
    "astral_term_system_code",
    "astral_decan_system_code",
    "astral_sect",
    "astral_ruler_assignments_role",
    "astral_planet_motion_states",
    "astral_speed_relations",
    "astral_heliacal_conditions",
    "astral_horizon_positions",
    "astral_sign_genders",
    "astral_planet_natures",
    "astral_condition_operators",
)


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe déjà dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    """Indique si une colonne existe déjà dans une table."""
    if not _table_exists(table_name):
        return False
    return column_name in {
        str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def upgrade() -> None:
    """Ajoute `sort_order` aux bases ayant appliqué une première version de 0128."""
    for table_name in LOOKUP_TABLES_WITH_SORT_ORDER:
        if _table_exists(table_name) and not _column_exists(table_name, "sort_order"):
            op.add_column(
                table_name,
                sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            )


def downgrade() -> None:
    """Retire les colonnes de réconciliation quand le dialecte le permet."""
    for table_name in reversed(LOOKUP_TABLES_WITH_SORT_ORDER):
        if _table_exists(table_name) and _column_exists(table_name, "sort_order"):
            op.drop_column(table_name, "sort_order")
