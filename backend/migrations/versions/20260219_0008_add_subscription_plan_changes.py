"""add subscription plan changes table

Revision ID: 20260219_0008
Revises: 20260219_0007
Create Date: 2026-02-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0008"
down_revision: Union[str, Sequence[str], None] = "20260219_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription_plan_changes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("from_plan_id", sa.Integer(), nullable=False),
        sa.Column("to_plan_id", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["from_plan_id"], ["billing_plans.id"]),
        sa.ForeignKeyConstraint(["to_plan_id"], ["billing_plans.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_subscription_plan_changes_user_id_idempotency_key",
        ),
    )
    op.create_index(
        "ix_subscription_plan_changes_user_id",
        "subscription_plan_changes",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_plan_changes_from_plan_id",
        "subscription_plan_changes",
        ["from_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_plan_changes_to_plan_id",
        "subscription_plan_changes",
        ["to_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_plan_changes_idempotency_key",
        "subscription_plan_changes",
        ["idempotency_key"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_plan_changes_status",
        "subscription_plan_changes",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_subscription_plan_changes_status", table_name="subscription_plan_changes")
    op.drop_index(
        "ix_subscription_plan_changes_idempotency_key",
        table_name="subscription_plan_changes",
    )
    op.drop_index("ix_subscription_plan_changes_to_plan_id", table_name="subscription_plan_changes")
    op.drop_index(
        "ix_subscription_plan_changes_from_plan_id",
        table_name="subscription_plan_changes",
    )
    op.drop_index("ix_subscription_plan_changes_user_id", table_name="subscription_plan_changes")
    op.drop_table("subscription_plan_changes")
