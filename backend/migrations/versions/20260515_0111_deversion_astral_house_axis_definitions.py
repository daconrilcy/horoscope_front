"""Déversionne les définitions d'axes de maisons astrales.

Revision ID: 20260515_0111
Revises: 20260515_0110
Create Date: 2026-05-15
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0111"
down_revision: Union[str, Sequence[str], None] = "20260515_0110"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_house_axis_definitions"
SCOPE_CONSTRAINT = "uq_astral_house_axis_definitions_scope"
REFERENCE_INDEX = "ix_astral_house_axis_definitions_reference_version_id"


def _table_exists(table_name: str) -> bool:
    """Indique si la table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    """Indique si une colonne existe dans la table."""
    if not _table_exists(table_name):
        return False
    return column_name in {
        column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe sur la table."""
    if not _table_exists(table_name):
        return False
    return index_name in {
        index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def upgrade() -> None:
    """Supprime la dimension de version des axes de maisons."""
    if not _column_exists(TABLE_NAME, "reference_version_id"):
        return
    if _index_exists(TABLE_NAME, REFERENCE_INDEX):
        op.drop_index(REFERENCE_INDEX, table_name=TABLE_NAME)
    with op.batch_alter_table(TABLE_NAME, recreate="always") as batch_op:
        batch_op.drop_constraint(SCOPE_CONSTRAINT, type_="unique")
        batch_op.drop_column("reference_version_id")
        batch_op.create_unique_constraint(
            SCOPE_CONSTRAINT,
            ["astral_system_id", "key", "language_id"],
        )


def downgrade() -> None:
    """Restaure une colonne de version nullable pour retour arrière technique."""
    if not _table_exists(TABLE_NAME) or _column_exists(TABLE_NAME, "reference_version_id"):
        return
    with op.batch_alter_table(TABLE_NAME, recreate="always") as batch_op:
        batch_op.drop_constraint(SCOPE_CONSTRAINT, type_="unique")
        batch_op.add_column(sa.Column("reference_version_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_astral_house_axis_definitions_reference_version_id",
            "astral_reference_versions",
            ["reference_version_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_unique_constraint(
            SCOPE_CONSTRAINT,
            ["reference_version_id", "astral_system_id", "key", "language_id"],
        )
    if not _index_exists(TABLE_NAME, REFERENCE_INDEX):
        op.create_index(REFERENCE_INDEX, TABLE_NAME, ["reference_version_id"], unique=False)
