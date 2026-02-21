"""add feature flags table

Revision ID: 20260221_0021
Revises: 20260220_0020
Create Date: 2026-02-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260221_0021"
down_revision: Union[str, Sequence[str], None] = "20260220_0020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind: sa.engine.Connection, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(bind: sa.engine.Connection, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)


def upgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "feature_flags"):
        op.create_table(
            "feature_flags",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("target_roles_csv", sa.String(length=255), nullable=True),
            sa.Column("target_user_ids_csv", sa.String(length=1024), nullable=True),
            sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("key", name="uq_feature_flags_key"),
        )

    if not _index_exists(bind, "feature_flags", "ix_feature_flags_key"):
        op.create_index("ix_feature_flags_key", "feature_flags", ["key"], unique=True)
    if not _index_exists(bind, "feature_flags", "ix_feature_flags_updated_by_user_id"):
        op.create_index(
            "ix_feature_flags_updated_by_user_id",
            "feature_flags",
            ["updated_by_user_id"],
            unique=False,
        )
    if not _index_exists(bind, "feature_flags", "ix_feature_flags_created_at"):
        op.create_index(
            "ix_feature_flags_created_at", "feature_flags", ["created_at"], unique=False
        )
    if not _index_exists(bind, "feature_flags", "ix_feature_flags_updated_at"):
        op.create_index(
            "ix_feature_flags_updated_at", "feature_flags", ["updated_at"], unique=False
        )


def downgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "feature_flags"):
        return

    for index_name in (
        "ix_feature_flags_updated_at",
        "ix_feature_flags_created_at",
        "ix_feature_flags_updated_by_user_id",
        "ix_feature_flags_key",
    ):
        if _index_exists(bind, "feature_flags", index_name):
            op.drop_index(index_name, table_name="feature_flags")
    op.drop_table("feature_flags")
