"""Ajoute les index d exploitation des journaux LLM.

Revision ID: 20260423_0075
Revises: 20260423_0074
Create Date: 2026-04-23 00:00:00
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0075"
down_revision: Union[str, Sequence[str], None] = "20260423_0074"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute les index alignes sur les requetes d exploitation LLM."""
    with op.batch_alter_table("llm_call_logs") as batch_op:
        batch_op.create_index("ix_llm_call_logs_timestamp", ["timestamp"], unique=False)
        batch_op.create_index("ix_llm_call_logs_trace_id", ["trace_id"], unique=False)
        batch_op.create_index(
            "ix_llm_call_logs_scope_timestamp",
            ["feature", "subfeature", "plan", "timestamp"],
            unique=False,
        )
        batch_op.create_index(
            "ix_llm_call_logs_active_snapshot_version",
            ["active_snapshot_version"],
            unique=False,
        )
        batch_op.create_index(
            "ix_llm_call_logs_executed_provider_timestamp",
            ["executed_provider", "timestamp"],
            unique=False,
        )


def downgrade() -> None:
    """Retire les index d exploitation ajoutes sur les journaux LLM."""
    with op.batch_alter_table("llm_call_logs") as batch_op:
        batch_op.drop_index("ix_llm_call_logs_executed_provider_timestamp")
        batch_op.drop_index("ix_llm_call_logs_active_snapshot_version")
        batch_op.drop_index("ix_llm_call_logs_scope_timestamp")
        batch_op.drop_index("ix_llm_call_logs_trace_id")
        batch_op.drop_index("ix_llm_call_logs_timestamp")
