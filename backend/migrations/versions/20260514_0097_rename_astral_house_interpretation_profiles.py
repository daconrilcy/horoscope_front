"""Renomme la table éditoriale des profils d'interprétation des maisons.

Revision ID: 20260514_0097
Revises: 20260514_0096
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0097"
down_revision: Union[str, Sequence[str], None] = "20260514_0096"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_TABLE = "house_interpretation_profiles"
NEW_TABLE = "astral_house_interpretation_profiles"

OLD_INDEX_NAMES = (
    "ix_house_interpretation_profiles_reference_version_id",
    "ix_house_interpretation_profiles_house_id",
)
NEW_INDEX_SPECS = (
    (
        "ix_astral_house_interpretation_profiles_reference_version_id",
        NEW_TABLE,
        ["reference_version_id"],
    ),
    (
        "ix_astral_house_interpretation_profiles_house_id",
        NEW_TABLE,
        ["house_id"],
    ),
)


def _table_exists(table_name: str) -> bool:
    """Vérifie si une table existe dans le schéma courant."""
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
    """Supprime un index uniquement s'il existe."""
    table_name = _index_table(index_name)
    if table_name is not None:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    """Crée un index canonique sans dupliquer un index existant."""
    if _index_table(index_name) is None:
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    """Renomme la table éditoriale et ses index canoniques."""
    if _table_exists(OLD_TABLE) and not _table_exists(NEW_TABLE):
        op.rename_table(OLD_TABLE, NEW_TABLE)
    for index_name in OLD_INDEX_NAMES:
        _drop_index_if_exists(index_name)
    for index_name, table_name, columns in NEW_INDEX_SPECS:
        _create_index_if_missing(index_name, table_name, columns)


def downgrade() -> None:
    """Restaure le nom historique de la table éditoriale pour rollback."""
    for index_name, _table_name, _columns in NEW_INDEX_SPECS:
        _drop_index_if_exists(index_name)
    if _table_exists(NEW_TABLE) and not _table_exists(OLD_TABLE):
        op.rename_table(NEW_TABLE, OLD_TABLE)
    _create_index_if_missing(
        "ix_house_interpretation_profiles_reference_version_id",
        OLD_TABLE,
        ["reference_version_id"],
    )
    _create_index_if_missing(
        "ix_house_interpretation_profiles_house_id",
        OLD_TABLE,
        ["house_id"],
    )
