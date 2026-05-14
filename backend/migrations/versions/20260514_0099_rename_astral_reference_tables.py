"""Renomme les tables de référence astrologique avec le préfixe astral.

Revision ID: 20260514_0099
Revises: 20260514_0098
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0099"
down_revision: Union[str, Sequence[str], None] = "20260514_0098"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_RENAMES = (
    ("reference_versions", "astral_reference_versions"),
    ("aspects", "astral_aspects"),
    ("aspect_profiles", "astral_aspect_profiles"),
    ("planet_category_weights", "astral_planet_category_weights"),
)

INDEX_RENAMES = (
    (
        "ix_reference_versions_version",
        "ix_astral_reference_versions_version",
        "astral_reference_versions",
        ["version"],
    ),
    ("ix_aspects_code", "ix_astral_aspects_code", "astral_aspects", ["code"]),
    (
        "ix_aspect_profiles_reference_version_id",
        "ix_astral_aspect_profiles_reference_version_id",
        "astral_aspect_profiles",
        ["reference_version_id"],
    ),
    (
        "ix_aspect_profiles_aspect_id",
        "ix_astral_aspect_profiles_aspect_id",
        "astral_aspect_profiles",
        ["aspect_id"],
    ),
    (
        "ix_planet_category_weights_reference_version_id",
        "ix_astral_planet_category_weights_reference_version_id",
        "astral_planet_category_weights",
        ["reference_version_id"],
    ),
    (
        "ix_planet_category_weights_planet_id",
        "ix_astral_planet_category_weights_planet_id",
        "astral_planet_category_weights",
        ["planet_id"],
    ),
    (
        "ix_planet_category_weights_category_id",
        "ix_astral_planet_category_weights_category_id",
        "astral_planet_category_weights",
        ["category_id"],
    ),
)


def _table_exists(table_name: str) -> bool:
    """Indique si la table existe dans le schéma courant."""
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
    """Retourne la table propriétaire d'un index existant."""
    inspector = sa.inspect(op.get_bind())
    for table_name in inspector.get_table_names():
        if index_name in _index_names(table_name, inspector):
            return table_name
    return None


def _drop_index_if_exists(index_name: str) -> None:
    """Supprime un index uniquement s'il est présent."""
    table_name = _index_table(index_name)
    if table_name is not None:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    """Crée un index canonique sans doublonner l'existant."""
    if _table_exists(table_name) and _index_table(index_name) is None:
        op.create_index(index_name, table_name, columns, unique=False)


def _rename_tables(renames: tuple[tuple[str, str], ...]) -> None:
    """Renomme les tables en gardant la migration idempotente pour SQLite de test."""
    for old_table, new_table in renames:
        if _table_exists(old_table) and not _table_exists(new_table):
            op.rename_table(old_table, new_table)


def _rename_indexes(indexes: tuple[tuple[str, str, str, list[str]], ...]) -> None:
    """Recrée les index avec les noms alignés sur les tables renommées."""
    for old_index, new_index, table_name, columns in indexes:
        _drop_index_if_exists(old_index)
        _create_index_if_missing(new_index, table_name, columns)


def upgrade() -> None:
    """Applique les noms SQL canoniques des référentiels astraux."""
    _rename_tables(TABLE_RENAMES)
    _rename_indexes(INDEX_RENAMES)


def downgrade() -> None:
    """Restaure les noms historiques pour rollback Alembic."""
    for _old_index, new_index, _table_name, _columns in INDEX_RENAMES:
        _drop_index_if_exists(new_index)
    _rename_tables(
        tuple((new_table, old_table) for old_table, new_table in reversed(TABLE_RENAMES))
    )
    for old_index, _new_index, new_table_name, columns in INDEX_RENAMES:
        historical_table = next(
            old_table
            for old_table, renamed_table in TABLE_RENAMES
            if renamed_table == new_table_name
        )
        _create_index_if_missing(old_index, historical_table, columns)
