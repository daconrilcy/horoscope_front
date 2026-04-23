"""Harmonise les termes de l agregat de consommation LLM.

Revision ID: 20260423_0076
Revises: 20260423_0075
Create Date: 2026-04-23 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0076"
down_revision: Union[str, Sequence[str], None] = "20260423_0075"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_canonical_consumption_table() -> None:
    """Cree le read model avec les noms harmonises pour les bases neuves."""
    op.create_table(
        "llm_canonical_consumption_aggregates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("granularity", sa.String(length=16), nullable=False),
        sa.Column("period_start_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("subscription_plan", sa.String(length=64), nullable=False),
        sa.Column("feature", sa.String(length=64), nullable=False),
        sa.Column("subfeature", sa.String(length=64), nullable=True),
        sa.Column("locale", sa.String(length=32), nullable=False),
        sa.Column("executed_provider", sa.String(length=32), nullable=False),
        sa.Column("active_snapshot_version", sa.String(length=64), nullable=False),
        sa.Column("is_legacy_residual", sa.Boolean(), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_usd_estimated_microusd", sa.Integer(), nullable=False),
        sa.Column("call_count", sa.Integer(), nullable=False),
        sa.Column("latency_p50_ms", sa.Integer(), nullable=False),
        sa.Column("latency_p95_ms", sa.Integer(), nullable=False),
        sa.Column("error_rate_bps", sa.Integer(), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "granularity",
            "period_start_utc",
            "user_id",
            "subscription_plan",
            "feature",
            "subfeature",
            "locale",
            "executed_provider",
            "active_snapshot_version",
            "is_legacy_residual",
            name="uq_llm_canonical_consumption_dims",
        ),
    )
    op.create_index(
        "ix_llm_canonical_consumption_period",
        "llm_canonical_consumption_aggregates",
        ["granularity", "period_start_utc"],
        unique=False,
    )
    op.create_index(
        "ix_llm_canonical_consumption_feature",
        "llm_canonical_consumption_aggregates",
        ["feature", "subfeature"],
        unique=False,
    )


def _ensure_call_log_operational_columns() -> None:
    """Ajoute les colonnes ORM-only encore absentes des bases Alembic neuves."""
    if not sa.inspect(op.get_bind()).has_table("llm_call_logs"):
        return
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("llm_call_logs")}
    missing_columns = {
        "executed_provider_mode": sa.Column(
            "executed_provider_mode", sa.String(length=32), nullable=True
        ),
        "attempt_count": sa.Column("attempt_count", sa.Integer(), nullable=True),
        "provider_error_code": sa.Column(
            "provider_error_code", sa.String(length=50), nullable=True
        ),
        "breaker_state": sa.Column("breaker_state", sa.String(length=20), nullable=True),
        "breaker_scope": sa.Column("breaker_scope", sa.String(length=100), nullable=True),
    }
    with op.batch_alter_table("llm_call_logs") as batch_op:
        for column_name, column in missing_columns.items():
            if column_name not in columns:
                batch_op.add_column(column)


def upgrade() -> None:
    """Supprime le scope duplique et aligne les noms tokens/cout sur les logs."""
    _ensure_call_log_operational_columns()
    if not sa.inspect(op.get_bind()).has_table("llm_canonical_consumption_aggregates"):
        _create_canonical_consumption_table()
        return

    with op.batch_alter_table("llm_canonical_consumption_aggregates") as batch_op:
        columns = {
            column["name"]
            for column in sa.inspect(op.get_bind()).get_columns(
                "llm_canonical_consumption_aggregates"
            )
        }
        if "taxonomy_scope" in columns:
            batch_op.drop_column("taxonomy_scope")
        if "input_tokens" in columns:
            batch_op.alter_column(
                "input_tokens",
                new_column_name="tokens_in",
                existing_type=sa.Integer(),
                existing_nullable=False,
            )
        if "output_tokens" in columns:
            batch_op.alter_column(
                "output_tokens",
                new_column_name="tokens_out",
                existing_type=sa.Integer(),
                existing_nullable=False,
            )
        if "estimated_cost_microusd" in columns:
            batch_op.alter_column(
                "estimated_cost_microusd",
                new_column_name="cost_usd_estimated_microusd",
                existing_type=sa.Integer(),
                existing_nullable=False,
            )


def downgrade() -> None:
    """Restaure les anciens noms de projection pour retour arriere."""
    with op.batch_alter_table("llm_canonical_consumption_aggregates") as batch_op:
        batch_op.add_column(
            sa.Column(
                "taxonomy_scope",
                sa.String(length=32),
                nullable=False,
                server_default="nominal",
            )
        )
        batch_op.alter_column(
            "tokens_in",
            new_column_name="input_tokens",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
    op.execute(
        sa.text(
            """
            UPDATE llm_canonical_consumption_aggregates
            SET taxonomy_scope = CASE
                WHEN is_legacy_residual THEN 'legacy_residual'
                ELSE 'nominal'
            END
            """
        )
    )
    with op.batch_alter_table("llm_canonical_consumption_aggregates") as batch_op:
        batch_op.alter_column(
            "taxonomy_scope",
            server_default=None,
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "tokens_out",
            new_column_name="output_tokens",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "cost_usd_estimated_microusd",
            new_column_name="estimated_cost_microusd",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
