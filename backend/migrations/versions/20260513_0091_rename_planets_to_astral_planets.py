"""Renomme le vocabulaire SQL des planetes astrologiques.

Revision ID: 20260513_0091
Revises: 20260513_0090
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0091"
down_revision: Union[str, Sequence[str], None] = "20260513_0090"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_TABLE_NAME = "planets"
NEW_TABLE_NAME = "astral_planets"
OLD_INDEX_NAME = "ix_planets_code"
NEW_INDEX_NAME = "ix_astral_planets_code"


def _table_exists(table_name: str) -> bool:
    """Vérifie la présence d'une table pour rendre le renommage idempotent."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_table(index_name: str) -> str | None:
    """Retourne la table propriétaire d'un index si elle existe."""
    inspector = sa.inspect(op.get_bind())
    for table_name in inspector.get_table_names():
        indexes = {index["name"] for index in inspector.get_indexes(table_name)}
        if index_name in indexes:
            return table_name
    return None


def _drop_index_if_exists(index_name: str) -> None:
    """Supprime un index uniquement s'il existe dans le schéma courant."""
    table_name = _index_table(index_name)
    if table_name is not None:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    """Crée un index attendu sans dupliquer un index déjà présent."""
    if _index_table(index_name) is None:
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    """Renomme la table stable des planètes sans modifier ses données."""
    if _table_exists(OLD_TABLE_NAME) and not _table_exists(NEW_TABLE_NAME):
        op.rename_table(OLD_TABLE_NAME, NEW_TABLE_NAME)
    _drop_index_if_exists(OLD_INDEX_NAME)
    _create_index_if_missing(NEW_INDEX_NAME, NEW_TABLE_NAME, ["code"])


def downgrade() -> None:
    """Restaure le nom historique de la table stable des planètes."""
    _drop_index_if_exists(NEW_INDEX_NAME)
    if _table_exists(NEW_TABLE_NAME) and not _table_exists(OLD_TABLE_NAME):
        op.rename_table(NEW_TABLE_NAME, OLD_TABLE_NAME)
    _create_index_if_missing(OLD_INDEX_NAME, OLD_TABLE_NAME, ["code"])
