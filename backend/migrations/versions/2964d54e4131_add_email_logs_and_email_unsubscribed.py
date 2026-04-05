"""Add email_logs and email_unsubscribed

Revision ID: 2964d54e4131
Revises: 20260402_0066
Create Date: 2026-04-03 21:02:31.693845
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2964d54e4131"
down_revision: Union[str, Sequence[str], None] = "20260402_0066"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table update
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("email_unsubscribed", sa.Boolean(), nullable=False, server_default="0")
        )

    # Email logs table creation
    op.create_table(
        "email_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),  # user.id is Integer
        sa.Column("email_type", sa.String(length=50), nullable=False),
        sa.Column("recipient_email", sa.String(length=255), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("email_logs", schema=None) as batch_op:
        batch_op.create_index("idx_email_logs_user_type", ["user_id", "email_type"], unique=False)


def downgrade() -> None:
    op.drop_table("email_logs")
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("email_unsubscribed")
