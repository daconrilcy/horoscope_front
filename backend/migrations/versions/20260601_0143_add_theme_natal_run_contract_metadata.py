"""Ajoute les metadonnees contractuelles aux runs theme natal.

Revision ID: 20260601_0143
Revises: 20260601_0142
Create Date: 2026-06-01 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0143"
down_revision: Union[str, Sequence[str], None] = "20260601_0142"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute les champs techniques requis par les preuves de runtime."""
    op.add_column(
        "llm_generation_runs",
        sa.Column("generation_contract_key", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "llm_generation_runs",
        sa.Column("generation_contract_hash", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "llm_generation_runs",
        sa.Column("generation_contract_snapshot_id", sa.String(length=220), nullable=True),
    )
    op.add_column(
        "llm_generation_runs",
        sa.Column("provider_mode", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    """Retire uniquement les champs ajoutes par cette revision."""
    op.drop_column("llm_generation_runs", "provider_mode")
    op.drop_column("llm_generation_runs", "generation_contract_snapshot_id")
    op.drop_column("llm_generation_runs", "generation_contract_hash")
    op.drop_column("llm_generation_runs", "generation_contract_key")
