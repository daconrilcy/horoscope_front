"""Finalise les domaines fermes LLM et remplace les flags assembly.

Revision ID: 20260423_0079
Revises: 20260423_0078
Create Date: 2026-04-23 16:23:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0079"
down_revision: Union[str, Sequence[str], None] = "20260423_0078"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    """Indique si la table existe dans la base cible."""
    return sa.inspect(op.get_bind()).has_table(table_name)


def _check_names(table_name: str) -> set[str]:
    """Retourne les noms des contraintes CHECK deja presentes."""
    return {
        str(check["name"])
        for check in sa.inspect(op.get_bind()).get_check_constraints(table_name)
        if check.get("name")
    }


def _create_check_if_missing(
    batch_op, existing_checks: set[str], name: str, condition: str
) -> None:
    """Ajoute une contrainte CHECK si elle est absente."""
    if name not in existing_checks:
        batch_op.create_check_constraint(name, condition)


def upgrade() -> None:
    """Ajoute les contraintes fermes manquantes et remplace les booléens assembly."""
    if _has_table("llm_execution_profiles"):
        checks = _check_names("llm_execution_profiles")
        with op.batch_alter_table("llm_execution_profiles") as batch_op:
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_execution_profiles_provider",
                "provider IN ('openai', 'anthropic')",
            )

    if _has_table("llm_call_logs"):
        checks = _check_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_call_logs_provider",
                "provider IN ('openai', 'anthropic')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_call_logs_environment",
                (
                    "environment IN "
                    "('development', 'dev', 'staging', 'production', 'prod', "
                    "'test', 'testing', 'local')"
                ),
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_call_logs_pipeline_kind",
                "pipeline_kind IN ('nominal', 'nominal_canonical', 'transitional_governance')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_call_logs_breaker_state",
                "breaker_state IN ('closed', 'open', 'half_open')",
            )

    if _has_table("llm_call_log_operational_metadata"):
        checks = _check_names("llm_call_log_operational_metadata")
        with op.batch_alter_table("llm_call_log_operational_metadata") as batch_op:
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_call_log_operational_metadata_pipeline_kind",
                "pipeline_kind IN ('nominal', 'nominal_canonical', 'transitional_governance')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_call_log_operational_metadata_breaker_state",
                "breaker_state IN ('closed', 'open', 'half_open')",
            )

    if _has_table("llm_assembly_configs"):
        checks = _check_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "feature_template_state",
                    sa.String(length=16),
                    nullable=False,
                    server_default="enabled",
                )
            )
            batch_op.add_column(
                sa.Column(
                    "subfeature_template_state",
                    sa.String(length=16),
                    nullable=False,
                    server_default="absent",
                )
            )
            batch_op.add_column(
                sa.Column(
                    "persona_state",
                    sa.String(length=16),
                    nullable=False,
                    server_default="inherited",
                )
            )
            batch_op.add_column(
                sa.Column(
                    "plan_rules_state",
                    sa.String(length=16),
                    nullable=False,
                    server_default="absent",
                )
            )

        op.execute(
            sa.text(
                """
                UPDATE llm_assembly_configs
                SET feature_template_state = CASE
                        WHEN feature_enabled = 0 THEN 'disabled'
                        ELSE 'enabled'
                    END,
                    subfeature_template_state = CASE
                        WHEN subfeature_enabled = 0 THEN 'disabled'
                        WHEN subfeature_template_ref IS NOT NULL THEN 'enabled'
                        WHEN subfeature IS NOT NULL THEN 'inherited'
                        ELSE 'absent'
                    END,
                    persona_state = CASE
                        WHEN persona_enabled = 0 THEN 'disabled'
                        WHEN persona_ref IS NOT NULL THEN 'enabled'
                        ELSE 'inherited'
                    END,
                    plan_rules_state = CASE
                        WHEN plan_rules_enabled = 0 THEN 'disabled'
                        WHEN plan_rules_ref IS NOT NULL THEN 'enabled'
                        WHEN plan IS NOT NULL THEN 'inherited'
                        ELSE 'absent'
                    END
                """
            )
        )

        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            batch_op.drop_column("feature_enabled")
            batch_op.drop_column("subfeature_enabled")
            batch_op.drop_column("persona_enabled")
            batch_op.drop_column("plan_rules_enabled")
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_assembly_configs_feature_template_state",
                "feature_template_state IN ('absent', 'inherited', 'enabled', 'disabled')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_assembly_configs_subfeature_template_state",
                "subfeature_template_state IN ('absent', 'inherited', 'enabled', 'disabled')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_assembly_configs_persona_state",
                "persona_state IN ('absent', 'inherited', 'enabled', 'disabled')",
            )
            _create_check_if_missing(
                batch_op,
                checks,
                "ck_llm_assembly_configs_plan_rules_state",
                "plan_rules_state IN ('absent', 'inherited', 'enabled', 'disabled')",
            )
            batch_op.alter_column(
                "feature_template_state",
                server_default=None,
                existing_type=sa.String(length=16),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "subfeature_template_state",
                server_default=None,
                existing_type=sa.String(length=16),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "persona_state",
                server_default=None,
                existing_type=sa.String(length=16),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "plan_rules_state",
                server_default=None,
                existing_type=sa.String(length=16),
                existing_nullable=False,
            )


def downgrade() -> None:
    """Restaure les booléens assembly et retire les contraintes ajoutees."""
    if _has_table("llm_assembly_configs"):
        checks = _check_names("llm_assembly_configs")
        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            batch_op.add_column(
                sa.Column("feature_enabled", sa.Boolean(), nullable=False, server_default=sa.true())
            )
            batch_op.add_column(
                sa.Column(
                    "subfeature_enabled", sa.Boolean(), nullable=False, server_default=sa.true()
                )
            )
            batch_op.add_column(
                sa.Column("persona_enabled", sa.Boolean(), nullable=False, server_default=sa.true())
            )
            batch_op.add_column(
                sa.Column(
                    "plan_rules_enabled", sa.Boolean(), nullable=False, server_default=sa.true()
                )
            )

        op.execute(
            sa.text(
                """
                UPDATE llm_assembly_configs
                SET feature_enabled = CASE
                        WHEN feature_template_state = 'disabled' THEN 0
                        ELSE 1
                    END,
                    subfeature_enabled = CASE
                        WHEN subfeature_template_state = 'disabled' THEN 0
                        ELSE 1
                    END,
                    persona_enabled = CASE
                        WHEN persona_state = 'disabled' THEN 0
                        ELSE 1
                    END,
                    plan_rules_enabled = CASE
                        WHEN plan_rules_state = 'disabled' THEN 0
                        ELSE 1
                    END
                """
            )
        )

        with op.batch_alter_table("llm_assembly_configs") as batch_op:
            for name in (
                "ck_llm_assembly_configs_feature_template_state",
                "ck_llm_assembly_configs_subfeature_template_state",
                "ck_llm_assembly_configs_persona_state",
                "ck_llm_assembly_configs_plan_rules_state",
            ):
                if name in checks:
                    batch_op.drop_constraint(name, type_="check")
            batch_op.drop_column("feature_template_state")
            batch_op.drop_column("subfeature_template_state")
            batch_op.drop_column("persona_state")
            batch_op.drop_column("plan_rules_state")
            batch_op.alter_column(
                "feature_enabled",
                server_default=None,
                existing_type=sa.Boolean(),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "subfeature_enabled",
                server_default=None,
                existing_type=sa.Boolean(),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "persona_enabled",
                server_default=None,
                existing_type=sa.Boolean(),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "plan_rules_enabled",
                server_default=None,
                existing_type=sa.Boolean(),
                existing_nullable=False,
            )

    if _has_table("llm_call_log_operational_metadata"):
        checks = _check_names("llm_call_log_operational_metadata")
        with op.batch_alter_table("llm_call_log_operational_metadata") as batch_op:
            for name in (
                "ck_llm_call_log_operational_metadata_pipeline_kind",
                "ck_llm_call_log_operational_metadata_breaker_state",
            ):
                if name in checks:
                    batch_op.drop_constraint(name, type_="check")

    if _has_table("llm_call_logs"):
        checks = _check_names("llm_call_logs")
        with op.batch_alter_table("llm_call_logs") as batch_op:
            for name in (
                "ck_llm_call_logs_provider",
                "ck_llm_call_logs_environment",
                "ck_llm_call_logs_pipeline_kind",
                "ck_llm_call_logs_breaker_state",
            ):
                if name in checks:
                    batch_op.drop_constraint(name, type_="check")

    if _has_table("llm_execution_profiles"):
        checks = _check_names("llm_execution_profiles")
        with op.batch_alter_table("llm_execution_profiles") as batch_op:
            if "ck_llm_execution_profiles_provider" in checks:
                batch_op.drop_constraint("ck_llm_execution_profiles_provider", type_="check")
