"""Corrige le nom SQL des familles d'aspects astraux.

Revision ID: 20260514_0103
Revises: 20260514_0102
Create Date: 2026-05-14
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0103"
down_revision: Union[str, Sequence[str], None] = "20260514_0102"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    """Renomme la table fautive sans toucher aux données seedées."""
    if _table_exists("astal_aspect_families") and not _table_exists("astral_aspect_families"):
        op.rename_table("astal_aspect_families", "astral_aspect_families")


def downgrade() -> None:
    """Laisse la migration précédente gérer la suppression de la table."""
    # Renommer ici casserait le downgrade complet: 0102 supprime la table corrigée.
    return
