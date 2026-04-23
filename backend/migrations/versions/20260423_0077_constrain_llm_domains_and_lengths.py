"""Contraint les domaines LLM stables et harmonise les longueurs.

Revision ID: 20260423_0077
Revises: 20260423_0076
Create Date: 2026-04-23 16:23:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0077"
down_revision: Union[str, Sequence[str], None] = "20260423_0076"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    """Indique si la table existe dans la base cible."""
    return sa.inspect(op.get_bind()).has_table(table_name)


def _check_names(table_name: str) -> set[str]:
    """Retourne les noms de contraintes CHECK deja presentes."""
    return {
        str(check["name"])
        for check in sa.inspect(op.get_bind()).get_check_constraints(table_name)
        if check.get("name")
    }


def _create_check_if_missing(
    batch_op,
    existing_checks: set[str],
    name: str,
    condition: str,
) -> None:
    """Ajoute une contrainte CHECK seulement si elle n existe pas deja."""
    if name not in existing_checks:
        batch_op.create_check_constraint(name, condition)


def upgrade() -> None:
    """Applique les domaines fermes et aligne les tailles des champs partages."""
    if _has_table("llm_execution_profiles"):
        checks = _check_names("llm_execution_profiles")
        with op.batch_alter_table("llm_execution_profiles") as batch_op:
            batch_op.alter_column(
                "provider",
                existing_type=sa.String(length=50),
                type_=sa.String(length=32),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "feature",
                existing_type=sa.String(length=100),
                type_=sa.String(length=64),
                existing_nullable=True,
            )
            batch_op.alter_column(
                "subfeature",
                existing_type=sa.String(length=100),
                type_=sa.String(length=64),
                existing_nullable=True,
            )
            batch_op.alter_column(
                "plan",
                existing_type=sa.String(length=50),
                type_=sa.String(length=64),
                existing_nullable=True,
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_execution_profiles_reasoning_profile",
                "reasoning_profile IN ('off', 'light', 'medium', 'deep')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_execution_profiles_verbosity_profile",
                "verbosity_profile IN ('concise', 'balanced', 'detailed')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_execution_profiles_output_mode",
                "output_mode IN ('free_text', 'structured_json')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_execution_profiles_tool_mode",
                "tool_mode IN ('none', 'optional', 'required')",
            )

    if _has_table("llm_assembly_configs"):
        checks = _check_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            batch_op.alter_column(
                "locale",
                existing_type=sa.String(length=16),
                type_=sa.String(length=32),
                existing_nullable=True,
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_assembly_configs_interaction_mode",
                "interaction_mode IN ('structured', 'chat')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_assembly_configs_user_question_policy",
                "user_question_policy IN ('none', 'optional', 'required')",
            )

    if _has_table("llm_sample_payloads"):
        with op.batch_alter_table("llm_sample_payloads") as batch_op:
            batch_op.alter_column(
                "locale",
                existing_type=sa.String(length=16),
                type_=sa.String(length=32),
                existing_nullable=False,
            )

    if _has_table("llm_call_logs"):
        with op.batch_alter_table("llm_call_logs") as batch_op:
            batch_op.alter_column(
                "model",
                existing_type=sa.String(length=50),
                type_=sa.String(length=100),
                existing_nullable=False,
            )

    if _has_table("llm_canonical_consumption_aggregates"):
        checks = _check_names("llm_canonical_consumption_aggregates")
        with op.batch_alter_table("llm_canonical_consumption_aggregates") as batch_op:
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_canonical_consumption_granularity",
                "granularity IN ('day', 'month')",
            )


def downgrade() -> None:
    """Retire les contraintes ajoutees et restaure les anciennes longueurs."""
    if _has_table("llm_canonical_consumption_aggregates"):
        checks = _check_names("llm_canonical_consumption_aggregates")
        with op.batch_alter_table("llm_canonical_consumption_aggregates") as batch_op:
            if "ck_llm_canonical_consumption_granularity" in checks:
                batch_op.drop_constraint("ck_llm_canonical_consumption_granularity", type_="check")

    if _has_table("llm_call_logs"):
        with op.batch_alter_table("llm_call_logs") as batch_op:
            batch_op.alter_column(
                "model",
                existing_type=sa.String(length=100),
                type_=sa.String(length=50),
                existing_nullable=False,
            )

    if _has_table("llm_sample_payloads"):
        with op.batch_alter_table("llm_sample_payloads") as batch_op:
            batch_op.alter_column(
                "locale",
                existing_type=sa.String(length=32),
                type_=sa.String(length=16),
                existing_nullable=False,
            )

    if _has_table("llm_assembly_configs"):
        checks = _check_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            if "ck_llm_assembly_configs_interaction_mode" in checks:
                batch_op.drop_constraint("ck_llm_assembly_configs_interaction_mode", type_="check")
            if "ck_llm_assembly_configs_user_question_policy" in checks:
                batch_op.drop_constraint(
                    "ck_llm_assembly_configs_user_question_policy", type_="check"
                )
            batch_op.alter_column(
                "locale",
                existing_type=sa.String(length=32),
                type_=sa.String(length=16),
                existing_nullable=True,
            )

    if _has_table("llm_execution_profiles"):
        checks = _check_names("llm_execution_profiles")
        with op.batch_alter_table("llm_execution_profiles") as batch_op:
            for name in (
                "ck_llm_execution_profiles_reasoning_profile",
                "ck_llm_execution_profiles_verbosity_profile",
                "ck_llm_execution_profiles_output_mode",
                "ck_llm_execution_profiles_tool_mode",
            ):
                if name in checks:
                    batch_op.drop_constraint(name, type_="check")
            batch_op.alter_column(
                "plan",
                existing_type=sa.String(length=64),
                type_=sa.String(length=50),
                existing_nullable=True,
            )
            batch_op.alter_column(
                "subfeature",
                existing_type=sa.String(length=64),
                type_=sa.String(length=100),
                existing_nullable=True,
            )
            batch_op.alter_column(
                "feature",
                existing_type=sa.String(length=64),
                type_=sa.String(length=100),
                existing_nullable=True,
            )
            batch_op.alter_column(
                "provider",
                existing_type=sa.String(length=32),
                type_=sa.String(length=50),
                existing_nullable=False,
            )
