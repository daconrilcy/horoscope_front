# Commentaire global: migration corrective de l'empreinte natale Astral.
"""Add Astral natal birth fingerprint to already migrated databases.

Revision ID: 20260623_0149
Revises: 20260623_0148
Create Date: 2026-06-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260623_0149"
down_revision = "20260623_0148"
branch_labels = None
depends_on = None

TABLE_NAME = "user_astral_natal_themes"
LOOKUP_INDEX_NAME = "ix_user_astral_natal_themes_reusable_lookup"
LOOKUP_INDEX_COLUMNS = [
    "user_id",
    "birth_profile_id",
    "theme_level",
    "birth_fingerprint",
    "status",
    "created_at",
]


def _table_exists() -> bool:
    """Indique si la table de cache natal existe déjà."""
    return TABLE_NAME in sa.inspect(op.get_bind()).get_table_names()


def _column_names() -> set[str]:
    """Retourne les colonnes actuelles de la table de cache natal."""
    if not _table_exists():
        return set()
    return {str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(TABLE_NAME)}


def _index_columns(index_name: str) -> list[str] | None:
    """Retourne les colonnes d'un index existant."""
    if not _table_exists():
        return None
    for index in sa.inspect(op.get_bind()).get_indexes(TABLE_NAME):
        if index["name"] == index_name:
            return [str(column) for column in index["column_names"]]
    return None


def _recreate_lookup_index() -> None:
    """Recrée l'index de lookup avec l'empreinte de naissance."""
    existing_columns = _index_columns(LOOKUP_INDEX_NAME)
    if existing_columns is not None:
        op.drop_index(LOOKUP_INDEX_NAME, table_name=TABLE_NAME)
    op.create_index(LOOKUP_INDEX_NAME, TABLE_NAME, LOOKUP_INDEX_COLUMNS)


def upgrade() -> None:
    """Ajoute l'empreinte natale aux bases déjà passées par la révision 0148."""
    if not _table_exists():
        return
    if "birth_fingerprint" not in _column_names():
        op.add_column(
            TABLE_NAME,
            sa.Column(
                "birth_fingerprint",
                sa.String(length=64),
                nullable=False,
                server_default="",
            ),
        )
    if _index_columns(LOOKUP_INDEX_NAME) != LOOKUP_INDEX_COLUMNS:
        _recreate_lookup_index()


def downgrade() -> None:
    """Retire l'empreinte natale corrective."""
    if not _table_exists():
        return
    if _index_columns(LOOKUP_INDEX_NAME) == LOOKUP_INDEX_COLUMNS:
        op.drop_index(LOOKUP_INDEX_NAME, table_name=TABLE_NAME)
        op.create_index(
            LOOKUP_INDEX_NAME,
            TABLE_NAME,
            ["user_id", "birth_profile_id", "theme_level", "status", "created_at"],
        )
    if "birth_fingerprint" in _column_names():
        op.drop_column(TABLE_NAME, "birth_fingerprint")
