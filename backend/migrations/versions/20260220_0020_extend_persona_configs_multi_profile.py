"""extend persona configs for multi-profile support

Revision ID: 20260220_0020
Revises: 20260220_0019
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0020"
down_revision: Union[str, Sequence[str], None] = "20260220_0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind: sa.engine.Connection, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind: sa.engine.Connection, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def _index_exists(bind: sa.engine.Connection, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)


def upgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "persona_configs"):
        op.create_table(
            "persona_configs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("version", sa.Integer(), nullable=False),
            sa.Column("profile_code", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("tone", sa.String(length=32), nullable=False),
            sa.Column("prudence_level", sa.String(length=32), nullable=False),
            sa.Column("scope_policy", sa.String(length=32), nullable=False),
            sa.Column("response_style", sa.String(length=32), nullable=False),
            sa.Column("fallback_policy", sa.String(length=32), nullable=False),
            sa.Column("status", sa.String(length=16), nullable=False),
            sa.Column("rollback_from_id", sa.Integer(), nullable=True),
            sa.Column("created_by_user_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_persona_configs_version", "persona_configs", ["version"], unique=False)
        op.create_index(
            "ix_persona_configs_profile_code", "persona_configs", ["profile_code"], unique=False
        )
        op.create_index("ix_persona_configs_status", "persona_configs", ["status"], unique=False)
        op.create_index(
            "uq_persona_configs_single_active",
            "persona_configs",
            ["status"],
            unique=True,
            sqlite_where=sa.text("status = 'active'"),
            postgresql_where=sa.text("status = 'active'"),
        )
        return

    if not _column_exists(bind, "persona_configs", "profile_code"):
        op.add_column(
            "persona_configs",
            sa.Column(
                "profile_code",
                sa.String(length=64),
                nullable=False,
                server_default="legacy-default",
            ),
        )
    if not _column_exists(bind, "persona_configs", "display_name"):
        op.add_column(
            "persona_configs",
            sa.Column(
                "display_name",
                sa.String(length=128),
                nullable=False,
                server_default="Astrologue Principal",
            ),
        )
    if not _column_exists(bind, "persona_configs", "fallback_policy"):
        op.add_column(
            "persona_configs",
            sa.Column(
                "fallback_policy",
                sa.String(length=32),
                nullable=False,
                server_default="safe_fallback",
            ),
        )
    if not _index_exists(bind, "persona_configs", "ix_persona_configs_profile_code"):
        op.create_index(
            "ix_persona_configs_profile_code",
            "persona_configs",
            ["profile_code"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "persona_configs"):
        return
    if _index_exists(bind, "persona_configs", "ix_persona_configs_profile_code"):
        op.drop_index("ix_persona_configs_profile_code", table_name="persona_configs")
    if _column_exists(bind, "persona_configs", "fallback_policy"):
        op.drop_column("persona_configs", "fallback_policy")
    if _column_exists(bind, "persona_configs", "display_name"):
        op.drop_column("persona_configs", "display_name")
    if _column_exists(bind, "persona_configs", "profile_code"):
        op.drop_column("persona_configs", "profile_code")
