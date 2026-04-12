"""add_llm_release_tables_and_obs

Revision ID: b91ce4044d7c
Revises: 8b2d52442493
Create Date: 2026-04-12 10:11:54.844910
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b91ce4044d7c"
down_revision: Union[str, Sequence[str], None] = "8b2d52442493"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create llm_release_snapshots table
    op.create_table(
        "llm_release_snapshots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("manifest", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("llm_release_snapshots", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_llm_release_snapshots_status"), ["status"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_llm_release_snapshots_version"), ["version"], unique=False
        )

    # 2. Create llm_active_releases table
    op.create_table(
        "llm_active_releases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("release_snapshot_id", sa.UUID(), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activated_by", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["release_snapshot_id"], ["llm_release_snapshots.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Add observability columns to llm_call_logs
    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("active_snapshot_id", sa.UUID(), nullable=True))
        batch_op.add_column(
            sa.Column("active_snapshot_version", sa.String(length=64), nullable=True)
        )
        batch_op.add_column(sa.Column("manifest_entry_id", sa.String(length=100), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.drop_column("manifest_entry_id")
        batch_op.drop_column("active_snapshot_version")
        batch_op.drop_column("active_snapshot_id")

    op.drop_table("llm_active_releases")
    op.drop_table("llm_release_snapshots")
