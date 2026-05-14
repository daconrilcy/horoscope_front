"""Renomme la table des profils planetaires de prediction quotidienne.

Revision ID: 20260513_0089
Revises: 20260513_0088
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0089"
down_revision: Union[str, Sequence[str], None] = "20260513_0088"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_TABLE_NAME = "planet_profiles"
NEW_TABLE_NAME = "astral_prediction_daily_planet_profiles"

OLD_INDEX_NAMES = (
    "ix_planet_profiles_planet_id",
    "ix_planet_profiles_reference_version_id",
)
NEW_INDEX_SPECS = (
    ("ix_astral_prediction_daily_planet_profiles_planet_id", ["planet_id"]),
    (
        "ix_astral_prediction_daily_planet_profiles_reference_version_id",
        ["reference_version_id"],
    ),
)


def _table_exists(table_name: str) -> bool:
    """Vérifie la présence d'une table pour reprendre une migration interrompue."""
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
    """Crée un index attendu sans dupliquer un index déjà présent."""
    if _index_table(index_name) is None:
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    """Renomme la table sans modifier les profils existants."""
    if _table_exists(OLD_TABLE_NAME) and not _table_exists(NEW_TABLE_NAME):
        op.rename_table(OLD_TABLE_NAME, NEW_TABLE_NAME)
    for index_name in OLD_INDEX_NAMES:
        _drop_index_if_exists(index_name)
    for index_name, columns in NEW_INDEX_SPECS:
        _create_index_if_missing(index_name, NEW_TABLE_NAME, columns)


def downgrade() -> None:
    """Restaure le nom historique de la table pour rollback."""
    for index_name, _columns in NEW_INDEX_SPECS:
        _drop_index_if_exists(index_name)
    if _table_exists(NEW_TABLE_NAME) and not _table_exists(OLD_TABLE_NAME):
        op.rename_table(NEW_TABLE_NAME, OLD_TABLE_NAME)
    _create_index_if_missing("ix_planet_profiles_planet_id", OLD_TABLE_NAME, ["planet_id"])
    _create_index_if_missing(
        "ix_planet_profiles_reference_version_id",
        OLD_TABLE_NAME,
        ["reference_version_id"],
    )
