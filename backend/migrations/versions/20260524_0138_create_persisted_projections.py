"""Cree la table canonique des projections persistées.

Revision ID: 20260524_0138
Revises: 20260523_0137
Create Date: 2026-05-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260524_0138"
down_revision: Union[str, Sequence[str], None] = "20260523_0137"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la persistance versionnée des projections internes."""
    op.create_table(
        "persisted_projections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chart_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("projection_type", sa.String(length=96), nullable=False),
        sa.Column("projection_version", sa.String(length=64), nullable=False),
        sa.Column("projection_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("source_versions", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_persisted_projection_identity",
        "persisted_projections",
        ["projection_type", "projection_version", "projection_hash"],
        unique=False,
    )
    op.create_index(
        "ix_persisted_projection_scope",
        "persisted_projections",
        ["projection_type", "projection_version", "user_id"],
        unique=False,
    )
    for column_name in (
        "chart_id",
        "generated_at",
        "projection_hash",
        "projection_type",
        "projection_version",
        "source",
        "user_id",
    ):
        op.create_index(
            op.f(f"ix_persisted_projections_{column_name}"),
            "persisted_projections",
            [column_name],
            unique=False,
        )


def downgrade() -> None:
    """Supprime la table des projections persistées."""
    for column_name in (
        "user_id",
        "source",
        "projection_version",
        "projection_type",
        "projection_hash",
        "generated_at",
        "chart_id",
    ):
        op.drop_index(
            op.f(f"ix_persisted_projections_{column_name}"), table_name="persisted_projections"
        )
    op.drop_index("ix_persisted_projection_scope", table_name="persisted_projections")
    op.drop_index("ix_persisted_projection_identity", table_name="persisted_projections")
    op.drop_table("persisted_projections")
