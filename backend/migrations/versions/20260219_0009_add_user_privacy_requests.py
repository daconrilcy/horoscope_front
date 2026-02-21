"""add user privacy requests table

Revision ID: 20260219_0009
Revises: 20260219_0008
Create Date: 2026-02-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0009"
down_revision: Union[str, Sequence[str], None] = "20260219_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_privacy_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("request_kind", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("request_data", sa.JSON(), nullable=False),
        sa.Column("result_data", sa.JSON(), nullable=False),
        sa.Column("error_reason", sa.String(length=255), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_privacy_requests_user_id",
        "user_privacy_requests",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_privacy_requests_request_kind",
        "user_privacy_requests",
        ["request_kind"],
        unique=False,
    )
    op.create_index(
        "ix_user_privacy_requests_status",
        "user_privacy_requests",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_privacy_requests_status", table_name="user_privacy_requests")
    op.drop_index("ix_user_privacy_requests_request_kind", table_name="user_privacy_requests")
    op.drop_index("ix_user_privacy_requests_user_id", table_name="user_privacy_requests")
    op.drop_table("user_privacy_requests")
