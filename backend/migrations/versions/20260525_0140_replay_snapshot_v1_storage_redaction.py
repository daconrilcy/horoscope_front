"""Ajoute les champs internes approuves pour replay_snapshot_v1.

Revision ID: 20260525_0140
Revises: 20260525_0139
Create Date: 2026-05-25
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_0140"
down_revision: Union[str, Sequence[str], None] = "20260525_0139"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "llm_replay_snapshots"
SNAPSHOT_TYPE = "replay_snapshot_v1"
REDACTION_STATE = "encrypted_isolated_redacted_metadata_v1"
ZERO_HASH = "0" * 64


def _inspector() -> sa.Inspector:
    """Retourne l'inspecteur SQLAlchemy du bind Alembic courant."""
    return sa.inspect(op.get_bind())


def _has_table() -> bool:
    """Indique si la table canonique de snapshots existe deja."""
    return _inspector().has_table(TABLE_NAME)


def _column_names() -> set[str]:
    """Liste les colonnes presentes dans la table de snapshots."""
    if not _has_table():
        return set()
    return {str(column["name"]) for column in _inspector().get_columns(TABLE_NAME)}


def _add_column_if_missing(existing_columns: set[str], column: sa.Column) -> None:
    """Ajoute une colonne uniquement si elle manque encore."""
    if column.name in existing_columns:
        return
    op.add_column(TABLE_NAME, column)
    existing_columns.add(str(column.name))


def _drop_column_if_present(existing_columns: set[str], column_name: str) -> None:
    """Supprime une colonne uniquement lorsqu'elle existe."""
    if column_name not in existing_columns:
        return
    op.drop_column(TABLE_NAME, column_name)
    existing_columns.remove(column_name)


def _refresh_existing_retention() -> None:
    """Recalcule la retention des lignes existantes sur 30 jours."""
    dialect_name = op.get_bind().dialect.name
    if dialect_name == "sqlite":
        op.execute(
            sa.text(
                "UPDATE llm_replay_snapshots "
                "SET expires_at = datetime(created_at, '+30 days') "
                "WHERE created_at IS NOT NULL"
            )
        )
        return

    op.execute(
        sa.text(
            "UPDATE llm_replay_snapshots "
            "SET expires_at = created_at + INTERVAL '30 days' "
            "WHERE created_at IS NOT NULL"
        )
    )


def upgrade() -> None:
    """Etend le stockage replay existant avec les metadonnees approuvees."""
    if not _has_table():
        return

    existing_columns = _column_names()
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "snapshot_type",
            sa.String(length=64),
            nullable=False,
            server_default=SNAPSHOT_TYPE,
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("input_ref", sa.JSON(), nullable=False, server_default="{}"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("input_hash", sa.String(length=64), nullable=False, server_default=ZERO_HASH),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("version_identity", sa.JSON(), nullable=False, server_default="{}"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("provenance", sa.JSON(), nullable=False, server_default="{}"),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column(
            "redaction_state",
            sa.String(length=64),
            nullable=False,
            server_default=REDACTION_STATE,
        ),
    )
    _add_column_if_missing(
        existing_columns,
        sa.Column("payload_enc", sa.LargeBinary(), nullable=True),
    )
    _refresh_existing_retention()


def downgrade() -> None:
    """Retire les champs internes de replay_snapshot_v1."""
    if not _has_table():
        return

    existing_columns = _column_names()
    for column_name in (
        "payload_enc",
        "redaction_state",
        "provenance",
        "version_identity",
        "input_hash",
        "input_ref",
        "created_at",
        "snapshot_type",
    ):
        _drop_column_if_present(existing_columns, column_name)
