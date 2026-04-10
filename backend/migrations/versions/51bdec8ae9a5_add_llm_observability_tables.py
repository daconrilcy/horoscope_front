"""add_llm_observability_tables

Revision ID: 51bdec8ae9a5
Revises: 20260406_0067
Create Date: 2026-04-07 23:55:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "51bdec8ae9a5"
down_revision: Union[str, Sequence[str], None] = "20260406_0067"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "llm_call_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("use_case", sa.String(length=100), nullable=False),
        sa.Column("assembly_id", sa.UUID(), nullable=True),
        sa.Column("feature", sa.String(length=64), nullable=True),
        sa.Column("subfeature", sa.String(length=64), nullable=True),
        sa.Column("plan", sa.String(length=64), nullable=True),
        sa.Column("template_source", sa.String(length=32), nullable=True),
        sa.Column("prompt_version_id", sa.UUID(), nullable=True),
        sa.Column("persona_id", sa.UUID(), nullable=True),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("cost_usd_estimated", sa.Float(), nullable=False),
        sa.Column("validation_status", sa.String(length=20), nullable=False),
        sa.Column("repair_attempted", sa.Boolean(), nullable=False),
        sa.Column("fallback_triggered", sa.Boolean(), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=False),
        sa.Column("trace_id", sa.String(length=100), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("environment", sa.String(length=20), nullable=False),
        sa.Column("evidence_warnings_count", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assembly_id"],
            ["llm_assembly_configs.id"],
        ),
        sa.ForeignKeyConstraint(
            ["persona_id"],
            ["llm_personas.id"],
        ),
        sa.ForeignKeyConstraint(
            ["prompt_version_id"],
            ["llm_prompt_versions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_llm_call_logs_request_id"), ["request_id"], unique=False
        )
        batch_op.create_index(
            "ix_llm_call_logs_prompt_v_timestamp", ["prompt_version_id", "timestamp"], unique=False
        )
        batch_op.create_index(
            "ix_llm_call_logs_status_timestamp", ["validation_status", "timestamp"], unique=False
        )
        batch_op.create_index(
            "ix_llm_call_logs_use_case_timestamp", ["use_case", "timestamp"], unique=False
        )

    op.create_table(
        "llm_replay_snapshots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("call_log_id", sa.UUID(), nullable=False),
        sa.Column("input_enc", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["call_log_id"], ["llm_call_logs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("call_log_id"),
    )


def downgrade() -> None:
    op.drop_table("llm_replay_snapshots")
    op.drop_table("llm_call_logs")
