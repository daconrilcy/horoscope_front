"""Separe les metadonnees operationnelles des logs LLM.

Revision ID: 20260423_0078
Revises: 20260423_0077
Create Date: 2026-04-23 16:23:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0078"
down_revision: Union[str, Sequence[str], None] = "20260423_0077"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cree la couche operationnelle one-to-one et la renseigne depuis les logs."""
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("llm_call_log_operational_metadata"):
        return

    op.create_table(
        "llm_call_log_operational_metadata",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("call_log_id", sa.UUID(), nullable=False),
        sa.Column("pipeline_kind", sa.String(length=32), nullable=True),
        sa.Column("execution_path_kind", sa.String(length=40), nullable=True),
        sa.Column("fallback_kind", sa.String(length=40), nullable=True),
        sa.Column("requested_provider", sa.String(length=32), nullable=True),
        sa.Column("resolved_provider", sa.String(length=32), nullable=True),
        sa.Column("executed_provider", sa.String(length=32), nullable=True),
        sa.Column("context_quality", sa.String(length=32), nullable=True),
        sa.Column("context_compensation_status", sa.String(length=32), nullable=True),
        sa.Column("max_output_tokens_source", sa.String(length=32), nullable=True),
        sa.Column("max_output_tokens_final", sa.Integer(), nullable=True),
        sa.Column("executed_provider_mode", sa.String(length=32), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=True),
        sa.Column("provider_error_code", sa.String(length=50), nullable=True),
        sa.Column("runtime_error_code", sa.String(length=80), nullable=True),
        sa.Column("breaker_state", sa.String(length=20), nullable=True),
        sa.Column("breaker_scope", sa.String(length=100), nullable=True),
        sa.Column("active_snapshot_id", sa.UUID(), nullable=True),
        sa.Column("active_snapshot_version", sa.String(length=64), nullable=True),
        sa.Column("manifest_entry_id", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["call_log_id"], ["llm_call_logs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("call_log_id", name="uq_llm_call_log_operational_metadata_call_log"),
    )
    op.create_index(
        "ix_llm_call_log_operational_metadata_provider",
        "llm_call_log_operational_metadata",
        ["executed_provider", "pipeline_kind"],
        unique=False,
    )
    op.create_index(
        "ix_llm_call_log_operational_metadata_snapshot",
        "llm_call_log_operational_metadata",
        ["active_snapshot_version"],
        unique=False,
    )

    if inspector.has_table("llm_call_logs"):
        op.execute(
            sa.text(
                """
                INSERT INTO llm_call_log_operational_metadata (
                    id,
                    call_log_id,
                    pipeline_kind,
                    execution_path_kind,
                    fallback_kind,
                    requested_provider,
                    resolved_provider,
                    executed_provider,
                    context_quality,
                    context_compensation_status,
                    max_output_tokens_source,
                    max_output_tokens_final,
                    executed_provider_mode,
                    attempt_count,
                    provider_error_code,
                    runtime_error_code,
                    breaker_state,
                    breaker_scope,
                    active_snapshot_id,
                    active_snapshot_version,
                    manifest_entry_id
                )
                SELECT
                    lower(hex(randomblob(16))),
                    id,
                    pipeline_kind,
                    execution_path_kind,
                    fallback_kind,
                    requested_provider,
                    resolved_provider,
                    executed_provider,
                    context_quality,
                    context_compensation_status,
                    max_output_tokens_source,
                    max_output_tokens_final,
                    executed_provider_mode,
                    attempt_count,
                    provider_error_code,
                    runtime_error_code,
                    breaker_state,
                    breaker_scope,
                    active_snapshot_id,
                    active_snapshot_version,
                    manifest_entry_id
                FROM llm_call_logs
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM llm_call_log_operational_metadata metadata
                    WHERE metadata.call_log_id = llm_call_logs.id
                )
                """
            )
        )


def downgrade() -> None:
    """Supprime la couche operationnelle materialisee."""
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("llm_call_log_operational_metadata"):
        return

    op.drop_index(
        "ix_llm_call_log_operational_metadata_snapshot",
        table_name="llm_call_log_operational_metadata",
    )
    op.drop_index(
        "ix_llm_call_log_operational_metadata_provider",
        table_name="llm_call_log_operational_metadata",
    )
    op.drop_table("llm_call_log_operational_metadata")
