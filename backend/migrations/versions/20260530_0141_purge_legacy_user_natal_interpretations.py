# Commentaire global: revision de compatibilite sans purge des interpretations natales.
"""Conserve la chaine Alembic sans effacer l'historique utilisateur."""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "20260530_0141"
down_revision: Union[str, Sequence[str], None] = "20260525_0140"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Preserve les lectures existantes, gerees par le message de regeneration."""


def downgrade() -> None:
    """Ne modifie aucune donnee utilisateur."""
