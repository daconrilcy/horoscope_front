"""Renomme le provider legacy des logs LLM pour lever l ambiguite.

Revision ID: 20260423_0080
Revises: 20260423_0079
Create Date: 2026-04-23 17:05:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0080"
down_revision: Union[str, Sequence[str], None] = "20260423_0079"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    """Indique si la table cible existe dans la base."""
    return sa.inspect(op.get_bind()).has_table(table_name)


def _check_names(table_name: str) -> set[str]:
    """Retourne les contraintes CHECK deja presentes pour une table."""
    return {
        str(check["name"])
        for check in sa.inspect(op.get_bind()).get_check_constraints(table_name)
        if check.get("name")
    }


def _column_names(table_name: str) -> set[str]:
    """Retourne les colonnes deja presentes pour une table."""
    return {
        str(column["name"])
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
        if column.get("name")
    }


def upgrade() -> None:
    """Renomme `provider` en `provider_compat` sur les logs LLM."""
    if not _has_table("llm_call_logs"):
        return

    columns = _column_names("llm_call_logs")
    if "provider_compat" in columns:
        return
    if "provider" not in columns:
        return

    checks = _check_names("llm_call_logs")
    with op.batch_alter_table("llm_call_logs") as batch_op:
        if "ck_llm_call_logs_provider" in checks:
            batch_op.drop_constraint("ck_llm_call_logs_provider", type_="check")
        batch_op.alter_column(
            "provider",
            new_column_name="provider_compat",
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )
        batch_op.create_check_constraint(
            "ck_llm_call_logs_provider",
            "provider_compat IN ('openai', 'anthropic')",
        )


def downgrade() -> None:
    """Restaure le nom `provider` sur les logs LLM."""
    if not _has_table("llm_call_logs"):
        return

    columns = _column_names("llm_call_logs")
    if "provider" in columns:
        return
    if "provider_compat" not in columns:
        return

    checks = _check_names("llm_call_logs")
    with op.batch_alter_table("llm_call_logs") as batch_op:
        if "ck_llm_call_logs_provider" in checks:
            batch_op.drop_constraint("ck_llm_call_logs_provider", type_="check")
        batch_op.alter_column(
            "provider_compat",
            new_column_name="provider",
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )
        batch_op.create_check_constraint(
            "ck_llm_call_logs_provider",
            "provider IN ('openai', 'anthropic')",
        )
