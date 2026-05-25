"""Etend les interpretations natales avec l'audit narratif v1.

Revision ID: 20260525_0139
Revises: 20260524_0138
Create Date: 2026-05-25
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_0139"
down_revision: Union[str, Sequence[str], None] = "20260524_0138"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "user_natal_interpretations"
ZERO_HASH = "0" * 64


def upgrade() -> None:
    """Ajoute les ancres persistantes requises par `narrative_answer_audit_v1`."""
    op.add_column(
        TABLE_NAME,
        sa.Column("answer_id", sa.String(length=96), nullable=False, server_default="legacy"),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column("answer_type", sa.String(length=16), nullable=False, server_default="basic"),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column("plan", sa.String(length=64), nullable=False, server_default="unknown"),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column(
            "projection_version",
            sa.String(length=64),
            nullable=False,
            server_default="legacy_unavailable",
        ),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column(
            "projection_hash",
            sa.String(length=64),
            nullable=False,
            server_default=ZERO_HASH,
        ),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column(
            "llm_input_version",
            sa.String(length=64),
            nullable=False,
            server_default="legacy_unavailable",
        ),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column("llm_input_hash", sa.String(length=64), nullable=False, server_default=ZERO_HASH),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column(
            "prompt_version",
            sa.String(length=64),
            nullable=False,
            server_default="legacy_unavailable",
        ),
    )
    op.add_column(TABLE_NAME, sa.Column("prompt_ref", sa.String(length=255), nullable=True))
    op.add_column(
        TABLE_NAME,
        sa.Column("prompt_snapshot_ref", sa.String(length=255), nullable=True),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column("provider", sa.String(length=32), nullable=False, server_default="unknown"),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column("model", sa.String(length=100), nullable=False, server_default="unknown"),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column(
            "grounding_status",
            sa.String(length=16),
            nullable=False,
            server_default="not_checked",
        ),
    )
    op.add_column(
        TABLE_NAME,
        sa.Column("evidence_refs", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.execute(
        sa.text(
            """
            UPDATE user_natal_interpretations
            SET answer_id = 'user_natal_interpretation:' || id,
                answer_type = CASE
                    WHEN lower(CAST(level AS VARCHAR)) = 'short' THEN 'basic'
                    ELSE 'premium'
                END,
                prompt_version = COALESCE(CAST(prompt_version_id AS VARCHAR), 'legacy_unavailable')
            """
        )
    )
    op.create_index(
        "ix_user_natal_interpretations_answer_id",
        TABLE_NAME,
        ["answer_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_natal_interpretations_audit_lookup",
        TABLE_NAME,
        ["user_id", "chart_id", "answer_type", "created_at"],
        unique=False,
    )
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.create_check_constraint(
            "ck_user_natal_interpretations_answer_type",
            "answer_type IN ('basic', 'premium', 'long', 'sensitive', 'free_short')",
        )
        batch_op.create_check_constraint(
            "ck_user_natal_interpretations_grounding_status",
            "grounding_status IN ('grounded', 'partial', 'ungrounded', 'rejected', 'not_checked')",
        )


def downgrade() -> None:
    """Retire les colonnes d'audit narratif v1."""
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.drop_constraint("ck_user_natal_interpretations_grounding_status", type_="check")
        batch_op.drop_constraint("ck_user_natal_interpretations_answer_type", type_="check")
    op.drop_index("ix_user_natal_interpretations_audit_lookup", table_name=TABLE_NAME)
    op.drop_index("ix_user_natal_interpretations_answer_id", table_name=TABLE_NAME)
    for column_name in (
        "evidence_refs",
        "grounding_status",
        "model",
        "provider",
        "prompt_snapshot_ref",
        "prompt_ref",
        "prompt_version",
        "llm_input_hash",
        "llm_input_version",
        "projection_hash",
        "projection_version",
        "plan",
        "answer_type",
        "answer_id",
    ):
        op.drop_column(TABLE_NAME, column_name)
