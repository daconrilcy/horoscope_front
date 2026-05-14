"""Supprime la table legacy vide des profils d'interprétation de maisons.

Revision ID: 20260514_0101
Revises: 20260514_0100
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0101"
down_revision: Union[str, Sequence[str], None] = "20260514_0100"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_TABLE = "house_interpretation_profiles"
NEW_TABLE = "astral_house_interpretation_profiles"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _row_count(table_name: str) -> int:
    """Compte les lignes d'une table existante."""
    return int(op.get_bind().execute(sa.text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one())


def upgrade() -> None:
    """Élimine la table historique si le renommage a laissé une coquille vide."""
    if not _table_exists(OLD_TABLE):
        return
    if not _table_exists(NEW_TABLE):
        op.rename_table(OLD_TABLE, NEW_TABLE)
        return
    if _row_count(OLD_TABLE) != 0:
        raise RuntimeError(
            f"Cannot drop {OLD_TABLE}: legacy and canonical tables both exist and legacy has data"
        )
    op.drop_table(OLD_TABLE)


def downgrade() -> None:
    """Ne recrée pas la table legacy vide supprimée par cette migration de nettoyage."""
