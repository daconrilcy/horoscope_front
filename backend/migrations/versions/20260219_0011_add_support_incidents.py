"""add support incidents table

Revision ID: 20260219_0011
Revises: 20260219_0010
Create Date: 2026-02-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0011"
down_revision: Union[str, Sequence[str], None] = "20260219_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "support_incidents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("assigned_to_user_id", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_support_incidents_user_id",
        "support_incidents",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_support_incidents_created_by_user_id",
        "support_incidents",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_support_incidents_assigned_to_user_id",
        "support_incidents",
        ["assigned_to_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_support_incidents_category",
        "support_incidents",
        ["category"],
        unique=False,
    )
    op.create_index(
        "ix_support_incidents_status",
        "support_incidents",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_support_incidents_priority",
        "support_incidents",
        ["priority"],
        unique=False,
    )
    op.create_index(
        "ix_support_incidents_created_at",
        "support_incidents",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_support_incidents_created_at", table_name="support_incidents")
    op.drop_index("ix_support_incidents_priority", table_name="support_incidents")
    op.drop_index("ix_support_incidents_status", table_name="support_incidents")
    op.drop_index("ix_support_incidents_category", table_name="support_incidents")
    op.drop_index("ix_support_incidents_assigned_to_user_id", table_name="support_incidents")
    op.drop_index("ix_support_incidents_created_by_user_id", table_name="support_incidents")
    op.drop_index("ix_support_incidents_user_id", table_name="support_incidents")
    op.drop_table("support_incidents")
