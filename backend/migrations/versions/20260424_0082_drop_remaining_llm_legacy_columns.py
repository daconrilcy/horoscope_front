"""Supprime les colonnes legacy LLM restantes.

Revision ID: 20260424_0082
Revises: 20260423_0081
Create Date: 2026-04-24 10:45:00
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260424_0082"
down_revision: Union[str, Sequence[str], None] = "20260423_0081"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    """Indique si une table existe deja."""
    return sa.inspect(op.get_bind()).has_table(table_name)


def _column_names(table_name: str) -> set[str]:
    """Retourne les colonnes existantes d une table."""
    return {str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _check_names(table_name: str) -> set[str]:
    """Retourne les contraintes CHECK presentes pour une table."""
    return {
        str(check["name"])
        for check in sa.inspect(op.get_bind()).get_check_constraints(table_name)
        if check.get("name")
    }


def _ensure_use_case_legacy_archive_table() -> None:
    """Cree la table d archive des champs legacy de use case si necessaire."""
    if _has_table("llm_use_case_config_legacy_archives"):
        return

    op.create_table(
        "llm_use_case_config_legacy_archives",
        sa.Column("use_case_key", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("output_schema_id", sa.String(length=64), nullable=True),
        sa.Column("allowed_persona_ids", sa.JSON(), nullable=True),
        sa.Column("input_schema", sa.JSON(), nullable=True),
        sa.Column("interaction_mode", sa.String(length=32), nullable=True),
        sa.Column("user_question_policy", sa.String(length=32), nullable=True),
        sa.Column("persona_strategy", sa.String(length=32), nullable=True),
        sa.Column("safety_profile", sa.String(length=64), nullable=True),
        sa.Column("fallback_use_case_key", sa.String(length=64), nullable=True),
        sa.Column(
            "archived_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def _archive_legacy_use_case_configs() -> None:
    """Archive explicitement les champs legacy de use case avant leur suppression."""
    if not _has_table("llm_use_case_configs"):
        return

    columns = _column_names("llm_use_case_configs")
    expected_columns = (
        "output_schema_id",
        "allowed_persona_ids",
        "input_schema",
        "interaction_mode",
        "user_question_policy",
        "persona_strategy",
        "safety_profile",
        "fallback_use_case_key",
    )
    if not {"key", *expected_columns} <= columns:
        return

    _ensure_use_case_legacy_archive_table()
    op.execute(
        sa.text(
            """
            INSERT INTO llm_use_case_config_legacy_archives (
                use_case_key,
                output_schema_id,
                allowed_persona_ids,
                input_schema,
                interaction_mode,
                user_question_policy,
                persona_strategy,
                safety_profile,
                fallback_use_case_key
            )
            SELECT
                key,
                output_schema_id,
                allowed_persona_ids,
                input_schema,
                interaction_mode,
                user_question_policy,
                persona_strategy,
                safety_profile,
                fallback_use_case_key
            FROM llm_use_case_configs
            WHERE NOT EXISTS (
                SELECT 1
                FROM llm_use_case_config_legacy_archives AS archive
                WHERE archive.use_case_key = llm_use_case_configs.key
            )
            """
        )
    )


def _assert_columns_are_empty(
    table_name: str,
    column_names: Sequence[str],
    *,
    empty_predicates: dict[str, str] | None = None,
) -> None:
    """Bloque la suppression si des colonnes legacy contiennent encore des donnees."""
    empty_predicates = empty_predicates or {}
    existing_columns = [column_name for column_name in column_names if column_name in _column_names(table_name)]
    if not existing_columns:
        return

    violation_clauses = []
    for column_name in existing_columns:
        empty_predicate = empty_predicates.get(column_name)
        if empty_predicate is None:
            violation_clauses.append(f"{column_name} IS NOT NULL")
        else:
            violation_clauses.append(f"NOT ({empty_predicate})")

    where_clause = " OR ".join(violation_clauses)
    query = sa.text(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}")
    row_count = int(op.get_bind().execute(query).scalar() or 0)
    if row_count > 0:
        raise RuntimeError(
            f"Cannot drop legacy columns from {table_name}: {row_count} rows still carry data in "
            f"{', '.join(existing_columns)}."
        )


def _assert_provider_compat_is_migrated() -> None:
    """Verifie que `provider_compat` a bien ete reporte dans les metadonnees canoniques."""
    if not _has_table("llm_call_logs") or "provider_compat" not in _column_names("llm_call_logs"):
        return
    if not _has_table("llm_call_log_operational_metadata"):
        raise RuntimeError(
            "Cannot drop llm_call_logs.provider_compat: operational metadata table is missing."
        )

    query = sa.text(
        """
        SELECT COUNT(*)
        FROM llm_call_logs AS logs
        LEFT JOIN llm_call_log_operational_metadata AS meta
            ON meta.call_log_id = logs.id
        WHERE logs.provider_compat IS NOT NULL
          AND (
              meta.executed_provider IS NULL
              OR meta.executed_provider != logs.provider_compat
          )
        """
    )
    row_count = int(op.get_bind().execute(query).scalar() or 0)
    if row_count > 0:
        raise RuntimeError(
            "Cannot drop llm_call_logs.provider_compat: some rows are not mirrored into "
            "llm_call_log_operational_metadata.executed_provider."
        )


def upgrade() -> None:
    """Supprime les residus legacy des assemblies, prompts, use cases et logs."""
    if _has_table("llm_assembly_configs"):
        _assert_columns_are_empty(
            "llm_assembly_configs",
            (
                "execution_config",
                "interaction_mode",
                "user_question_policy",
                "input_schema",
                "fallback_use_case",
                "output_contract_ref",
            ),
        )
        columns = _column_names("llm_assembly_configs")
        checks = _check_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            if (
                "interaction_mode" in columns
                and "ck_llm_assembly_configs_interaction_mode" in checks
            ):
                batch_op.drop_constraint(
                    "ck_llm_assembly_configs_interaction_mode",
                    type_="check",
                )
            if (
                "user_question_policy" in columns
                and "ck_llm_assembly_configs_user_question_policy" in checks
            ):
                batch_op.drop_constraint(
                    "ck_llm_assembly_configs_user_question_policy",
                    type_="check",
                )
            for column_name in (
                "execution_config",
                "interaction_mode",
                "user_question_policy",
                "input_schema",
                "fallback_use_case",
                "output_contract_ref",
            ):
                if column_name in columns:
                    batch_op.drop_column(column_name)

    if _has_table("llm_prompt_versions"):
        _assert_columns_are_empty(
            "llm_prompt_versions",
            ("model", "temperature", "max_output_tokens", "reasoning_effort", "verbosity"),
        )
        columns = _column_names("llm_prompt_versions")
        with op.batch_alter_table("llm_prompt_versions") as batch_op:
            for column_name in (
                "model",
                "temperature",
                "max_output_tokens",
                "reasoning_effort",
                "verbosity",
            ):
                if column_name in columns:
                    batch_op.drop_column(column_name)

    if _has_table("llm_use_case_configs"):
        _archive_legacy_use_case_configs()
        columns = _column_names("llm_use_case_configs")
        with op.batch_alter_table("llm_use_case_configs") as batch_op:
            for column_name in (
                "input_schema",
                "output_schema_id",
                "persona_strategy",
                "interaction_mode",
                "user_question_policy",
                "safety_profile",
                "fallback_use_case_key",
                "allowed_persona_ids",
            ):
                if column_name in columns:
                    batch_op.drop_column(column_name)

    if _has_table("llm_call_logs"):
        _assert_provider_compat_is_migrated()
        columns = _column_names("llm_call_logs")
        checks = _check_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            if "provider_compat" in columns and "ck_llm_call_logs_provider" in checks:
                batch_op.drop_constraint("ck_llm_call_logs_provider", type_="check")
                batch_op.drop_column("provider_compat")


def downgrade() -> None:
    """Restaure les colonnes legacy si un rollback complet est requis."""
    if _has_table("llm_assembly_configs"):
        columns = _column_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            if "execution_config" not in columns:
                batch_op.add_column(sa.Column("execution_config", sa.JSON(), nullable=True))
            if "interaction_mode" not in columns:
                batch_op.add_column(
                    sa.Column("interaction_mode", sa.String(length=32), nullable=True)
                )
                batch_op.create_check_constraint(
                    "ck_llm_assembly_configs_interaction_mode",
                    "interaction_mode IN ('structured', 'chat')",
                )
            if "user_question_policy" not in columns:
                batch_op.add_column(
                    sa.Column("user_question_policy", sa.String(length=32), nullable=True)
                )
                batch_op.create_check_constraint(
                    "ck_llm_assembly_configs_user_question_policy",
                    "user_question_policy IN ('none', 'optional', 'required')",
                )
            if "input_schema" not in columns:
                batch_op.add_column(sa.Column("input_schema", sa.JSON(), nullable=True))
            if "fallback_use_case" not in columns:
                batch_op.add_column(
                    sa.Column("fallback_use_case", sa.String(length=64), nullable=True)
                )
            if "output_contract_ref" not in columns:
                batch_op.add_column(
                    sa.Column("output_contract_ref", sa.String(length=64), nullable=True)
                )

    if _has_table("llm_prompt_versions"):
        columns = _column_names("llm_prompt_versions")
        with op.batch_alter_table("llm_prompt_versions") as batch_op:
            if "model" not in columns:
                batch_op.add_column(sa.Column("model", sa.String(length=100), nullable=True))
            if "temperature" not in columns:
                batch_op.add_column(sa.Column("temperature", sa.Float(), nullable=True))
            if "max_output_tokens" not in columns:
                batch_op.add_column(sa.Column("max_output_tokens", sa.Integer(), nullable=True))
            if "reasoning_effort" not in columns:
                batch_op.add_column(
                    sa.Column("reasoning_effort", sa.String(length=32), nullable=True)
                )
            if "verbosity" not in columns:
                batch_op.add_column(sa.Column("verbosity", sa.String(length=32), nullable=True))

    if _has_table("llm_use_case_configs"):
        columns = _column_names("llm_use_case_configs")
        with op.batch_alter_table("llm_use_case_configs") as batch_op:
            if "input_schema" not in columns:
                batch_op.add_column(sa.Column("input_schema", sa.JSON(), nullable=True))
            if "output_schema_id" not in columns:
                batch_op.add_column(
                    sa.Column("output_schema_id", sa.String(length=64), nullable=True)
                )
            if "persona_strategy" not in columns:
                batch_op.add_column(
                    sa.Column("persona_strategy", sa.String(length=32), nullable=True)
                )
            if "interaction_mode" not in columns:
                batch_op.add_column(
                    sa.Column("interaction_mode", sa.String(length=32), nullable=True)
                )
            if "user_question_policy" not in columns:
                batch_op.add_column(
                    sa.Column("user_question_policy", sa.String(length=32), nullable=True)
                )
            if "safety_profile" not in columns:
                batch_op.add_column(
                    sa.Column("safety_profile", sa.String(length=64), nullable=True)
                )
            if "fallback_use_case_key" not in columns:
                batch_op.add_column(
                    sa.Column("fallback_use_case_key", sa.String(length=64), nullable=True)
                )
            if "allowed_persona_ids" not in columns:
                batch_op.add_column(sa.Column("allowed_persona_ids", sa.JSON(), nullable=True))
        if _has_table("llm_use_case_config_legacy_archives"):
            op.execute(
                sa.text(
                    """
                    UPDATE llm_use_case_configs
                    SET
                        output_schema_id = archive.output_schema_id,
                        allowed_persona_ids = archive.allowed_persona_ids,
                        input_schema = archive.input_schema,
                        interaction_mode = archive.interaction_mode,
                        user_question_policy = archive.user_question_policy,
                        persona_strategy = archive.persona_strategy,
                        safety_profile = archive.safety_profile,
                        fallback_use_case_key = archive.fallback_use_case_key
                    FROM llm_use_case_config_legacy_archives AS archive
                    WHERE archive.use_case_key = llm_use_case_configs.key
                    """
                )
            )

    if _has_table("llm_call_logs"):
        columns = _column_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            if "provider_compat" not in columns:
                batch_op.add_column(
                    sa.Column("provider_compat", sa.String(length=32), nullable=True)
                )
        if _has_table("llm_call_log_operational_metadata"):
            op.execute(
                sa.text(
                    """
                    UPDATE llm_call_logs
                    SET provider_compat = (
                        SELECT metadata.executed_provider
                        FROM llm_call_log_operational_metadata AS metadata
                        WHERE metadata.call_log_id = llm_call_logs.id
                    )
                    WHERE provider_compat IS NULL
                      AND EXISTS (
                          SELECT 1
                          FROM llm_call_log_operational_metadata AS metadata
                          WHERE metadata.call_log_id = llm_call_logs.id
                            AND metadata.executed_provider IS NOT NULL
                      )
                    """
                )
            )
        columns = _column_names("llm_call_logs")
        checks = _check_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            if "provider_compat" in columns and "ck_llm_call_logs_provider" not in checks:
                batch_op.create_check_constraint(
                    "ck_llm_call_logs_provider",
                    "provider_compat IN ('openai', 'anthropic')",
                )

    if _has_table("llm_use_case_config_legacy_archives"):
        op.drop_table("llm_use_case_config_legacy_archives")
