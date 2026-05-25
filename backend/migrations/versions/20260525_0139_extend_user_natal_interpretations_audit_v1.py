"""Etend les interpretations natales avec l'audit narratif v1.

Revision ID: 20260525_0139
Revises: 20260524_0138
Create Date: 2026-05-25
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_0139"
down_revision: Union[str, Sequence[str], None] = "20260524_0138"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "user_natal_interpretations"
ZERO_HASH = "0" * 64


def _inspector() -> sa.Inspector:
    """Retourne l'inspecteur SQLAlchemy du bind Alembic courant."""
    return sa.inspect(op.get_bind())


def _has_table() -> bool:
    """Indique si la table historique des interpretations existe deja."""
    return _inspector().has_table(TABLE_NAME)


def _column_names() -> set[str]:
    """Liste les colonnes presentes sur la table cible."""
    if not _has_table():
        return set()
    return {str(column["name"]) for column in _inspector().get_columns(TABLE_NAME)}


def _index_names() -> set[str]:
    """Liste les index presents sur la table cible."""
    if not _has_table():
        return set()
    return {str(index["name"]) for index in _inspector().get_indexes(TABLE_NAME)}


def _check_constraint_names() -> set[str]:
    """Liste les contraintes CHECK nommees presentes sur la table cible."""
    if not _has_table():
        return set()
    return {
        str(check["name"])
        for check in _inspector().get_check_constraints(TABLE_NAME)
        if check["name"] is not None
    }


def _add_column_if_missing(existing_columns: set[str], column: sa.Column) -> None:
    """Ajoute une colonne uniquement si une base SQLite partielle ne l'a pas deja."""
    if column.name in existing_columns:
        return
    op.add_column(TABLE_NAME, column)
    existing_columns.add(str(column.name))


def _drop_column_if_present(existing_columns: set[str], column_name: str) -> None:
    """Retire une colonne uniquement lorsqu'elle existe encore."""
    if column_name not in existing_columns:
        return
    op.drop_column(TABLE_NAME, column_name)
    existing_columns.remove(column_name)


def upgrade() -> None:
    """Ajoute les ancres persistantes requises par `narrative_answer_audit_v1`."""
    if not _has_table():
        return

    existing_columns = _column_names()
    _add_column_if_missing(
        existing_columns,
        sa.Column("answer_id", sa.String(length=96), nullable=False, server_default="legacy"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("answer_type", sa.String(length=16), nullable=False, server_default="basic"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("plan", sa.String(length=64), nullable=False, server_default="unknown"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "projection_version",
            sa.String(length=64),
            nullable=False,
            server_default="legacy_unavailable",
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "projection_hash",
            sa.String(length=64),
            nullable=False,
            server_default=ZERO_HASH,
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "llm_input_version",
            sa.String(length=64),
            nullable=False,
            server_default="legacy_unavailable",
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("llm_input_hash", sa.String(length=64), nullable=False, server_default=ZERO_HASH),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "prompt_version",
            sa.String(length=64),
            nullable=False,
            server_default="legacy_unavailable",
        ),
    )
    _add_column_if_missing(
        existing_columns, sa.Column("prompt_ref", sa.String(length=255), nullable=True)
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("prompt_snapshot_ref", sa.String(length=255), nullable=True),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("provider", sa.String(length=32), nullable=False, server_default="unknown"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("model", sa.String(length=100), nullable=False, server_default="unknown"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "grounding_status",
            sa.String(length=16),
            nullable=False,
            server_default="not_checked",
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("evidence_refs", sa.JSON(), nullable=False, server_default="[]"),
    )
    update_assignments: list[str] = []
    if {"answer_id", "id"} <= existing_columns:
        update_assignments.append(
            """
            answer_id = CASE
                WHEN answer_id = 'legacy' THEN 'user_natal_interpretation:' || id
                ELSE answer_id
            END
            """
        )
    if {"answer_type", "level"} <= existing_columns:
        update_assignments.append(
            """
            answer_type = CASE
                WHEN answer_type <> 'basic' THEN answer_type
                WHEN lower(CAST(level AS VARCHAR)) = 'short' THEN answer_type
                ELSE 'premium'
            END
            """
        )
    if {"prompt_version", "prompt_version_id"} <= existing_columns:
        update_assignments.append(
            """
            prompt_version = CASE
                WHEN prompt_version = 'legacy_unavailable'
                    THEN COALESCE(CAST(prompt_version_id AS VARCHAR), 'legacy_unavailable')
                ELSE prompt_version
            END
            """
        )
    if update_assignments:
        op.execute(sa.text(f"UPDATE {TABLE_NAME} SET {', '.join(update_assignments)}"))

    indexes = _index_names()
    if "ix_user_natal_interpretations_answer_id" not in indexes and "answer_id" in existing_columns:
        op.create_index(
            "ix_user_natal_interpretations_answer_id",
            TABLE_NAME,
            ["answer_id"],
            unique=False,
        )
    if (
        "ix_user_natal_interpretations_audit_lookup" not in indexes
        and {"user_id", "chart_id", "answer_type", "created_at"} <= existing_columns
    ):
        op.create_index(
            "ix_user_natal_interpretations_audit_lookup",
            TABLE_NAME,
            ["user_id", "chart_id", "answer_type", "created_at"],
            unique=False,
        )

    checks = _check_constraint_names()
    missing_answer_type_check = (
        "ck_user_natal_interpretations_answer_type" not in checks
        and "answer_type" in existing_columns
    )
    missing_grounding_status_check = (
        "ck_user_natal_interpretations_grounding_status" not in checks
        and "grounding_status" in existing_columns
    )
    if missing_answer_type_check or missing_grounding_status_check:
        with op.batch_alter_table(TABLE_NAME) as batch_op:
            if missing_answer_type_check:
                batch_op.create_check_constraint(
                    "ck_user_natal_interpretations_answer_type",
                    "answer_type IN ('basic', 'premium', 'long', 'sensitive', 'free_short')",
                )
            if missing_grounding_status_check:
                batch_op.create_check_constraint(
                    "ck_user_natal_interpretations_grounding_status",
                    (
                        "grounding_status IN "
                        "('grounded', 'partial', 'ungrounded', 'rejected', 'not_checked')"
                    ),
                )


def downgrade() -> None:
    """Retire les colonnes d'audit narratif v1."""
    if not _has_table():
        return

    checks = _check_constraint_names()
    if {
        "ck_user_natal_interpretations_grounding_status",
        "ck_user_natal_interpretations_answer_type",
    } & checks:
        with op.batch_alter_table(TABLE_NAME) as batch_op:
            if "ck_user_natal_interpretations_grounding_status" in checks:
                batch_op.drop_constraint(
                    "ck_user_natal_interpretations_grounding_status", type_="check"
                )
            if "ck_user_natal_interpretations_answer_type" in checks:
                batch_op.drop_constraint("ck_user_natal_interpretations_answer_type", type_="check")

    indexes = _index_names()
    if "ix_user_natal_interpretations_audit_lookup" in indexes:
        op.drop_index("ix_user_natal_interpretations_audit_lookup", table_name=TABLE_NAME)
    if "ix_user_natal_interpretations_answer_id" in indexes:
        op.drop_index("ix_user_natal_interpretations_answer_id", table_name=TABLE_NAME)

    existing_columns = _column_names()
    for column_name in (
        "evidence_refs",
        "grounding_status",
        "model",
        "provider",
        "prompt_snapshot_ref",
        "prompt_ref",
        "prompt_version",
        "llm_input_hash",
        "llm_input_version",
        "projection_hash",
        "projection_version",
        "plan",
        "answer_type",
        "answer_id",
    ):
        _drop_column_if_present(existing_columns, column_name)
