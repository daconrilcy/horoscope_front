"""Fusionne les heads Alembic LLM et entitlement mutation.

Revision ID: 20260425_0083
Revises: 20260424_0082, 20260425_0067
Create Date: 2026-04-25 16:15:00
"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "20260425_0083"
down_revision: Union[str, Sequence[str], None] = ("20260424_0082", "20260425_0067")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ne modifie pas le schéma, unifie uniquement la lignée Alembic."""


def downgrade() -> None:
    """Ne modifie pas le schéma, rouvre simplement les deux branches parentes."""
