"""Supprime le reliquat de pondération astrologique locale.

Revision ID: 20260622_0146
Revises: 20260622_0145
Create Date: 2026-06-22
"""

from __future__ import annotations

from alembic import op

revision = "20260622_0146"
down_revision = "20260622_0145"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Supprime la table locale sans modèle applicatif."""
    op.drop_table("point_category_weights", if_exists=True)


def downgrade() -> None:
    """La purge des tables locales est irréversible."""
    raise RuntimeError("Cannot downgrade local astrology table purge")
