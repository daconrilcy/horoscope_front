"""Cree le referentiel des signaux de condition planetaire.

Revision ID: 20260519_0131
Revises: 20260519_0130
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0131"
down_revision: Union[str, Sequence[str], None] = "20260519_0130"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_planet_condition_signal_profiles"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base migree."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    """Ajoute la table versionnee des signaux conditionnels."""
    if _table_exists(TABLE_NAME):
        return
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("condition_axis", sa.String(length=64), nullable=False),
        sa.Column("level_min", sa.Float(), nullable=False),
        sa.Column("level_max", sa.Float(), nullable=False),
        sa.Column("signal_code", sa.String(length=96), nullable=False),
        sa.Column("signal_label", sa.String(length=128), nullable=False),
        sa.Column("signal_level", sa.String(length=64), nullable=False),
        sa.Column("interpretation_use", sa.String(length=128), nullable=False),
        sa.Column("priority_weight", sa.Float(), nullable=False),
        sa.Column("prompt_hint", sa.String(length=160), nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "level_min <= level_max",
            name="ck_astral_planet_condition_signal_profiles_range",
        ),
        sa.ForeignKeyConstraint(
            ["reference_version_id"],
            ["astral_reference_versions.id"],
        ),
        sa.UniqueConstraint(
            "reference_version_id",
            "condition_axis",
            "signal_code",
            "signal_level",
            name="uq_astral_planet_condition_signal_profiles_scope",
        ),
    )
    op.create_index(
        "ix_astral_planet_condition_signal_profiles_condition_axis",
        TABLE_NAME,
        ["condition_axis"],
    )
    op.create_index(
        "ix_astral_planet_condition_signal_profiles_signal_code",
        TABLE_NAME,
        ["signal_code"],
    )
    op.create_index(
        "ix_astral_planet_condition_signal_profiles_reference_version_id",
        TABLE_NAME,
        ["reference_version_id"],
    )


def downgrade() -> None:
    """Supprime la table des signaux conditionnels."""
    if _table_exists(TABLE_NAME):
        op.drop_table(TABLE_NAME)
