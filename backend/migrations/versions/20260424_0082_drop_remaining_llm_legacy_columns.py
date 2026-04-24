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


def upgrade() -> None:
    """Supprime les residus legacy des assemblies, prompts, use cases et logs."""
    if _has_table("llm_assembly_configs"):
        columns = _column_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            if "interaction_mode" in columns:
                try:
                    batch_op.drop_constraint(
                        "ck_llm_assembly_configs_interaction_mode",
                        type_="check",
                    )
                except ValueError:
                    pass
            if "user_question_policy" in columns:
                try:
                    batch_op.drop_constraint(
                        "ck_llm_assembly_configs_user_question_policy",
                        type_="check",
                    )
                except ValueError:
                    pass
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
        columns = _column_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            if "provider_compat" in columns:
                try:
                    batch_op.drop_constraint("ck_llm_call_logs_provider", type_="check")
                except ValueError:
                    pass
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
            if "user_question_policy" not in columns:
                batch_op.add_column(
                    sa.Column("user_question_policy", sa.String(length=32), nullable=True)
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

    if _has_table("llm_call_logs"):
        columns = _column_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            if "provider_compat" not in columns:
                batch_op.add_column(
                    sa.Column("provider_compat", sa.String(length=32), nullable=True)
                )
