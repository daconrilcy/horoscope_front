"""Renomme les tables SQL des maisons astrales.

Revision ID: 20260513_0094
Revises: 20260513_0093
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0094"
down_revision: Union[str, Sequence[str], None] = "20260513_0093"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_RENAMES = (
    ("houses", "astral_houses"),
    ("house_profiles", "astral_prediction_daily_house_profiles"),
    ("house_category_weights", "astral_house_category_weights"),
)

OLD_INDEX_NAMES = (
    "ix_house_profiles_house_id",
    "ix_house_profiles_reference_version_id",
    "ix_house_category_weights_category_id",
    "ix_house_category_weights_house_id",
    "ix_house_category_weights_reference_version_id",
)

NEW_INDEX_SPECS = (
    (
        "ix_astral_prediction_daily_house_profiles_house_id",
        "astral_prediction_daily_house_profiles",
        ["house_id"],
    ),
    (
        "ix_astral_prediction_daily_house_profiles_reference_version_id",
        "astral_prediction_daily_house_profiles",
        ["reference_version_id"],
    ),
    (
        "ix_astral_house_category_weights_category_id",
        "astral_house_category_weights",
        ["category_id"],
    ),
    (
        "ix_astral_house_category_weights_house_id",
        "astral_house_category_weights",
        ["house_id"],
    ),
    (
        "ix_astral_house_category_weights_reference_version_id",
        "astral_house_category_weights",
        ["reference_version_id"],
    ),
)


def _table_exists(table_name: str) -> bool:
    """Vérifie la présence d'une table pour rendre le renommage reprenable."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_names(table_name: str, inspector: sa.Inspector) -> set[str]:
    """Retourne les noms d'index sans refléter les index d'expression SQLite."""
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        rows = bind.execute(
            sa.text(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'index' AND tbl_name = :table_name
                """
            ),
            {"table_name": table_name},
        )
        return {str(row.name) for row in rows if row.name}
    return {str(index["name"]) for index in inspector.get_indexes(table_name)}


def _index_table(index_name: str) -> str | None:
    """Retourne la table propriétaire d'un index si elle existe."""
    inspector = sa.inspect(op.get_bind())
    for table_name in inspector.get_table_names():
        if index_name in _index_names(table_name, inspector):
            return table_name
    return None


def _drop_index_if_exists(index_name: str) -> None:
    """Supprime un index uniquement s'il est présent dans le schéma courant."""
    table_name = _index_table(index_name)
    if table_name is not None:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    """Crée un index canonique sans dupliquer un index déjà présent."""
    if _index_table(index_name) is None:
        op.create_index(index_name, table_name, columns, unique=False)


def _rename_table_if_needed(old_name: str, new_name: str) -> None:
    """Renomme une table si l'ancien nom existe encore et que le nouveau est absent."""
    if _table_exists(old_name) and not _table_exists(new_name):
        op.rename_table(old_name, new_name)


def upgrade() -> None:
    """Renomme les tables maison sans modifier les données métier."""
    for old_name, new_name in TABLE_RENAMES:
        _rename_table_if_needed(old_name, new_name)
    for index_name in OLD_INDEX_NAMES:
        _drop_index_if_exists(index_name)
    for index_name, table_name, columns in NEW_INDEX_SPECS:
        _create_index_if_missing(index_name, table_name, columns)


def downgrade() -> None:
    """Restaure les noms historiques des tables maison pour rollback."""
    for index_name, _table_name, _columns in NEW_INDEX_SPECS:
        _drop_index_if_exists(index_name)
    for old_name, new_name in reversed(TABLE_RENAMES):
        if _table_exists(new_name) and not _table_exists(old_name):
            op.rename_table(new_name, old_name)
    _create_index_if_missing("ix_house_profiles_house_id", "house_profiles", ["house_id"])
    _create_index_if_missing(
        "ix_house_profiles_reference_version_id",
        "house_profiles",
        ["reference_version_id"],
    )
    _create_index_if_missing(
        "ix_house_category_weights_category_id",
        "house_category_weights",
        ["category_id"],
    )
    _create_index_if_missing(
        "ix_house_category_weights_house_id",
        "house_category_weights",
        ["house_id"],
    )
    _create_index_if_missing(
        "ix_house_category_weights_reference_version_id",
        "house_category_weights",
        ["reference_version_id"],
    )
