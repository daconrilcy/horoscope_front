"""Relie les profils d'interprétation de maisons aux systèmes astraux.

Revision ID: 20260514_0098
Revises: 20260514_0097
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0098"
down_revision: Union[str, Sequence[str], None] = "20260514_0097"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_house_interpretation_profiles"
OLD_UNIQUE_NAME = "uq_house_interpretation_profiles_version_house_language_tradition"
NEW_UNIQUE_NAME = "uq_astral_house_interpretation_profiles_version_house_language_system"
SYSTEM_FK_NAME = "fk_astral_house_interpretation_profiles_astral_system_id"
SYSTEM_INDEX_NAME = "ix_astral_house_interpretation_profiles_astral_system_id"


def _table_columns(table_name: str) -> set[str]:
    """Retourne les colonnes connues d'une table migrée."""
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _unique_constraint_names(table_name: str) -> set[str]:
    """Retourne les noms de contraintes uniques disponibles pour batch Alembic."""
    return {
        constraint["name"]
        for constraint in sa.inspect(op.get_bind()).get_unique_constraints(table_name)
        if constraint["name"]
    }


def _index_names(table_name: str) -> set[str]:
    """Retourne les index existants d'une table."""
    return {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
        if index["name"]
    }


def upgrade() -> None:
    """Remplace la tradition texte par une référence à `astral_systems`."""
    columns = _table_columns(TABLE_NAME)
    if "astral_system_id" not in columns:
        op.add_column(TABLE_NAME, sa.Column("astral_system_id", sa.Integer(), nullable=True))
    if "tradition" in columns:
        op.execute(
            sa.text(
                f"""
                UPDATE {TABLE_NAME}
                SET astral_system_id = (
                    SELECT astral_systems.id
                    FROM astral_systems
                    WHERE astral_systems.name = {TABLE_NAME}.tradition
                )
                WHERE astral_system_id IS NULL
                """
            )
        )
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        unique_names = _unique_constraint_names(TABLE_NAME)
        if OLD_UNIQUE_NAME in unique_names:
            batch_op.drop_constraint(OLD_UNIQUE_NAME, type_="unique")
        if NEW_UNIQUE_NAME not in unique_names:
            batch_op.create_unique_constraint(
                NEW_UNIQUE_NAME,
                ["reference_version_id", "house_id", "language", "astral_system_id"],
            )
        batch_op.create_foreign_key(
            SYSTEM_FK_NAME,
            "astral_systems",
            ["astral_system_id"],
            ["id"],
        )
        batch_op.alter_column("astral_system_id", existing_type=sa.Integer(), nullable=False)
        if "tradition" in columns:
            batch_op.drop_column("tradition")
    if SYSTEM_INDEX_NAME not in _index_names(TABLE_NAME):
        op.create_index(SYSTEM_INDEX_NAME, TABLE_NAME, ["astral_system_id"], unique=False)


def downgrade() -> None:
    """Restaure la colonne texte historique `tradition`."""
    columns = _table_columns(TABLE_NAME)
    if "tradition" not in columns:
        op.add_column(TABLE_NAME, sa.Column("tradition", sa.String(length=32), nullable=True))
    op.execute(
        sa.text(
            f"""
            UPDATE {TABLE_NAME}
            SET tradition = (
                SELECT astral_systems.name
                FROM astral_systems
                WHERE astral_systems.id = {TABLE_NAME}.astral_system_id
            )
            WHERE tradition IS NULL
            """
        )
    )
    if SYSTEM_INDEX_NAME in _index_names(TABLE_NAME):
        op.drop_index(SYSTEM_INDEX_NAME, table_name=TABLE_NAME)
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        unique_names = _unique_constraint_names(TABLE_NAME)
        if NEW_UNIQUE_NAME in unique_names:
            batch_op.drop_constraint(NEW_UNIQUE_NAME, type_="unique")
        batch_op.drop_constraint(SYSTEM_FK_NAME, type_="foreignkey")
        if OLD_UNIQUE_NAME not in unique_names:
            batch_op.create_unique_constraint(
                OLD_UNIQUE_NAME,
                ["reference_version_id", "house_id", "language", "tradition"],
            )
        batch_op.alter_column("tradition", existing_type=sa.String(length=32), nullable=False)
        if "astral_system_id" in columns:
            batch_op.drop_column("astral_system_id")
