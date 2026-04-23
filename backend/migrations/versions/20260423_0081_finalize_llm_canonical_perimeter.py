"""Finalise le perimetre canonique des modeles LLM.

Revision ID: 20260423_0081
Revises: 20260423_0080
Create Date: 2026-04-23 23:35:00
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0081"
down_revision: Union[str, Sequence[str], None] = "20260423_0080"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CALL_LOG_OPERATIONAL_COLUMNS = (
    "pipeline_kind",
    "execution_path_kind",
    "fallback_kind",
    "requested_provider",
    "resolved_provider",
    "executed_provider",
    "context_quality",
    "context_compensation_status",
    "max_output_tokens_source",
    "max_output_tokens_final",
    "executed_provider_mode",
    "attempt_count",
    "provider_error_code",
    "runtime_error_code",
    "breaker_state",
    "breaker_scope",
    "active_snapshot_id",
    "active_snapshot_version",
    "manifest_entry_id",
)


def _has_table(table_name: str) -> bool:
    """Indique si une table existe deja."""
    return sa.inspect(op.get_bind()).has_table(table_name)


def _column_names(table_name: str) -> set[str]:
    """Retourne les colonnes existantes d une table."""
    return {str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    """Retourne les index existants d une table."""
    return {str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _check_names(table_name: str) -> set[str]:
    """Retourne les contraintes CHECK existantes d une table."""
    return {
        str(check["name"])
        for check in sa.inspect(op.get_bind()).get_check_constraints(table_name)
        if check.get("name")
    }


def upgrade() -> None:
    """Ajoute la FK canonique de schema et supprime les duplications de logs."""
    if _has_table("llm_assembly_configs"):
        columns = _column_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            if "output_schema_id" not in columns:
                batch_op.add_column(sa.Column("output_schema_id", sa.UUID(), nullable=True))

        columns = _column_names("llm_assembly_configs")
        if {"output_contract_ref", "output_schema_id"} <= columns and _has_table(
            "llm_output_schemas"
        ):
            op.execute(
                sa.text(
                    """
                    UPDATE llm_assembly_configs
                    SET output_schema_id = (
                        CASE
                            WHEN output_contract_ref IS NULL
                                 OR trim(output_contract_ref) = ''
                            THEN NULL
                            WHEN EXISTS (
                                SELECT 1
                                FROM llm_output_schemas schema_direct
                                WHERE CAST(schema_direct.id AS TEXT) =
                                    llm_assembly_configs.output_contract_ref
                            ) THEN output_contract_ref
                            ELSE (
                                SELECT CAST(schema_named.id AS TEXT)
                                FROM llm_output_schemas schema_named
                                WHERE schema_named.name = llm_assembly_configs.output_contract_ref
                                ORDER BY schema_named.version DESC
                                LIMIT 1
                            )
                        END
                    )
                    WHERE output_schema_id IS NULL
                    """
                )
            )

        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            try:
                batch_op.create_foreign_key(
                    "fk_llm_assembly_configs_output_schema_id",
                    "llm_output_schemas",
                    ["output_schema_id"],
                    ["id"],
                    ondelete="SET NULL",
                )
            except ValueError:
                pass
            if "output_contract_ref" in columns:
                batch_op.drop_column("output_contract_ref")

    if _has_table("llm_call_logs"):
        columns = _column_names("llm_call_logs")
        indexes = _index_names("llm_call_logs")
        checks = _check_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            if "ix_llm_call_logs_active_snapshot_version" in indexes:
                batch_op.drop_index("ix_llm_call_logs_active_snapshot_version")
            if "ix_llm_call_logs_executed_provider_timestamp" in indexes:
                batch_op.drop_index("ix_llm_call_logs_executed_provider_timestamp")
            if "ck_llm_call_logs_pipeline_kind" in checks:
                batch_op.drop_constraint("ck_llm_call_logs_pipeline_kind", type_="check")
            if "ck_llm_call_logs_breaker_state" in checks:
                batch_op.drop_constraint("ck_llm_call_logs_breaker_state", type_="check")
            for column_name in _CALL_LOG_OPERATIONAL_COLUMNS:
                if column_name in columns:
                    batch_op.drop_column(column_name)

    if _has_table("llm_personas"):
        op.execute(
            sa.text(
                """
                UPDATE llm_personas
                SET tone = 'warm'
                WHERE tone = 'calm'
                """
            )
        )
        checks = _check_names("llm_personas")
        with op.batch_alter_table("llm_personas") as batch_op:
            if "ck_llm_personas_tone" not in checks:
                batch_op.create_check_constraint(
                    "ck_llm_personas_tone",
                    "tone IN ('warm', 'direct', 'mystical', 'rational')",
                )
            if "ck_llm_personas_verbosity" not in checks:
                batch_op.create_check_constraint(
                    "ck_llm_personas_verbosity",
                    "verbosity IN ('short', 'medium', 'long')",
                )


def downgrade() -> None:
    """Restaure les surfaces legacy si la migration doit etre annulee."""
    if _has_table("llm_assembly_configs"):
        columns = _column_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            if "output_contract_ref" not in columns:
                batch_op.add_column(
                    sa.Column("output_contract_ref", sa.String(length=64), nullable=True)
                )

        columns = _column_names("llm_assembly_configs")
        if {"output_contract_ref", "output_schema_id"} <= columns:
            op.execute(
                sa.text(
                    """
                    UPDATE llm_assembly_configs
                    SET output_contract_ref = CAST(output_schema_id AS TEXT)
                    WHERE output_schema_id IS NOT NULL
                    """
                )
            )

        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            try:
                batch_op.drop_constraint(
                    "fk_llm_assembly_configs_output_schema_id",
                    type_="foreignkey",
                )
            except ValueError:
                pass
            if "output_schema_id" in columns:
                batch_op.drop_column("output_schema_id")

    if _has_table("llm_call_logs"):
        columns = _column_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            for column_name, column in (
                ("pipeline_kind", sa.String(length=32)),
                ("execution_path_kind", sa.String(length=40)),
                ("fallback_kind", sa.String(length=40)),
                ("requested_provider", sa.String(length=32)),
                ("resolved_provider", sa.String(length=32)),
                ("executed_provider", sa.String(length=32)),
                ("context_quality", sa.String(length=32)),
                ("context_compensation_status", sa.String(length=32)),
                ("max_output_tokens_source", sa.String(length=32)),
                ("max_output_tokens_final", sa.Integer()),
                ("executed_provider_mode", sa.String(length=32)),
                ("attempt_count", sa.Integer()),
                ("provider_error_code", sa.String(length=80)),
                ("runtime_error_code", sa.String(length=80)),
                ("breaker_state", sa.String(length=20)),
                ("breaker_scope", sa.String(length=100)),
                ("active_snapshot_id", sa.UUID()),
                ("active_snapshot_version", sa.String(length=64)),
                ("manifest_entry_id", sa.String(length=100)),
            ):
                if column_name not in columns:
                    batch_op.add_column(sa.Column(column_name, column, nullable=True))

        if _has_table("llm_call_log_operational_metadata"):
            op.execute(
                sa.text(
                    """
                    UPDATE llm_call_logs
                    SET
                        pipeline_kind = metadata.pipeline_kind,
                        execution_path_kind = metadata.execution_path_kind,
                        fallback_kind = metadata.fallback_kind,
                        requested_provider = metadata.requested_provider,
                        resolved_provider = metadata.resolved_provider,
                        executed_provider = metadata.executed_provider,
                        context_quality = metadata.context_quality,
                        context_compensation_status = metadata.context_compensation_status,
                        max_output_tokens_source = metadata.max_output_tokens_source,
                        max_output_tokens_final = metadata.max_output_tokens_final,
                        executed_provider_mode = metadata.executed_provider_mode,
                        attempt_count = metadata.attempt_count,
                        provider_error_code = metadata.provider_error_code,
                        runtime_error_code = metadata.runtime_error_code,
                        breaker_state = metadata.breaker_state,
                        breaker_scope = metadata.breaker_scope,
                        active_snapshot_id = metadata.active_snapshot_id,
                        active_snapshot_version = metadata.active_snapshot_version,
                        manifest_entry_id = metadata.manifest_entry_id
                    FROM llm_call_log_operational_metadata metadata
                    WHERE metadata.call_log_id = llm_call_logs.id
                    """
                )
            )

        with op.batch_alter_table("llm_call_logs") as batch_op:
            batch_op.create_check_constraint(
                "ck_llm_call_logs_pipeline_kind",
                "pipeline_kind IN ('nominal', 'nominal_canonical', 'transitional_governance')",
            )
            batch_op.create_check_constraint(
                "ck_llm_call_logs_breaker_state",
                "breaker_state IN ('closed', 'open', 'half_open')",
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

    if _has_table("llm_personas"):
        checks = _check_names("llm_personas")
        with op.batch_alter_table("llm_personas") as batch_op:
            if "ck_llm_personas_tone" in checks:
                batch_op.drop_constraint("ck_llm_personas_tone", type_="check")
            if "ck_llm_personas_verbosity" in checks:
                batch_op.drop_constraint("ck_llm_personas_verbosity", type_="check")
