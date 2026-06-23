# Commentaire global: migration de cache applicatif des thèmes natals Astral.
"""Create persisted Astral natal theme cache.

Revision ID: 20260623_0148
Revises: 20260622_0147
Create Date: 2026-06-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260623_0148"
down_revision = "20260622_0147"
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    """Retourne les tables visibles pour rendre la migration idempotente localement."""
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_columns(table_name: str, index_name: str) -> list[str] | None:
    """Retourne les colonnes d'un index existant."""
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return None
    for index in inspector.get_indexes(table_name):
        if index["name"] == index_name:
            return [str(column) for column in index["column_names"]]
    return None


def _column_names(table_name: str) -> set[str]:
    """Retourne les colonnes existantes d'une table."""
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {str(column["name"]) for column in inspector.get_columns(table_name)}


def _create_index_if_missing(
    index_name: str,
    table_name: str,
    columns: list[str],
    *,
    unique: bool = False,
) -> None:
    """Crée ou réaligne un index applicatif idempotent."""
    existing_columns = _index_columns(table_name, index_name)
    if existing_columns is None:
        op.create_index(index_name, table_name, columns, unique=unique)
        return
    if existing_columns != columns:
        op.drop_index(index_name, table_name=table_name)
        op.create_index(index_name, table_name, columns, unique=unique)


def upgrade() -> None:
    """Crée la table de stockage des thèmes natals Astral."""
    if "user_astral_natal_themes" not in _table_names():
        op.create_table(
            "user_astral_natal_themes",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("birth_profile_id", sa.Integer(), nullable=False),
            sa.Column("birth_fingerprint", sa.String(length=64), nullable=False),
            sa.Column("theme_level", sa.String(length=16), nullable=False),
            sa.Column("requested_product", sa.String(length=32), nullable=False),
            sa.Column("requested_plan", sa.String(length=16), nullable=False),
            sa.Column("service_code", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("run_id", sa.String(length=128), nullable=False),
            sa.Column("client_request_id", sa.String(length=128), nullable=False),
            sa.Column("response_payload", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["birth_profile_id"], ["user_birth_profiles.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    elif "birth_fingerprint" not in _column_names("user_astral_natal_themes"):
        op.add_column(
            "user_astral_natal_themes",
            sa.Column(
                "birth_fingerprint",
                sa.String(length=64),
                nullable=False,
                server_default="",
            ),
        )
    _create_index_if_missing(
        "ix_user_astral_natal_themes_birth_profile_id",
        "user_astral_natal_themes",
        ["birth_profile_id"],
    )
    _create_index_if_missing(
        "ix_user_astral_natal_themes_client_request",
        "user_astral_natal_themes",
        ["client_request_id"],
    )
    _create_index_if_missing(
        "ix_user_astral_natal_themes_reusable_lookup",
        "user_astral_natal_themes",
        [
            "user_id",
            "birth_profile_id",
            "theme_level",
            "birth_fingerprint",
            "status",
            "created_at",
        ],
    )
    _create_index_if_missing(
        "ix_user_astral_natal_themes_run_id",
        "user_astral_natal_themes",
        ["run_id"],
        unique=True,
    )
    _create_index_if_missing(
        "ix_user_astral_natal_themes_user_created",
        "user_astral_natal_themes",
        ["user_id", "created_at"],
    )
    _create_index_if_missing(
        "ix_user_astral_natal_themes_user_id",
        "user_astral_natal_themes",
        ["user_id"],
    )


def downgrade() -> None:
    """Supprime la table de stockage des thèmes natals Astral."""
    op.drop_index("ix_user_astral_natal_themes_user_id", table_name="user_astral_natal_themes")
    op.drop_index(
        "ix_user_astral_natal_themes_user_created",
        table_name="user_astral_natal_themes",
    )
    op.drop_index("ix_user_astral_natal_themes_run_id", table_name="user_astral_natal_themes")
    op.drop_index(
        "ix_user_astral_natal_themes_reusable_lookup",
        table_name="user_astral_natal_themes",
    )
    op.drop_index(
        "ix_user_astral_natal_themes_client_request",
        table_name="user_astral_natal_themes",
    )
    op.drop_index(
        "ix_user_astral_natal_themes_birth_profile_id",
        table_name="user_astral_natal_themes",
    )
    op.drop_table("user_astral_natal_themes")
