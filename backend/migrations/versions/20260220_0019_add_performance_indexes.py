"""add composite performance indexes for critical flows

Revision ID: 20260220_0019
Revises: 20260220_0018
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0019"
down_revision: Union[str, Sequence[str], None] = "20260220_0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("chat_conversations"):
        op.create_index(
            "ix_chat_conversations_user_status_updated_id",
            "chat_conversations",
            ["user_id", "status", "updated_at", "id"],
            unique=False,
        )
        op.create_index(
            "ix_chat_conversations_user_updated_id",
            "chat_conversations",
            ["user_id", "updated_at", "id"],
            unique=False,
        )

    if inspector.has_table("chat_messages"):
        op.create_index(
            "ix_chat_messages_conversation_created_id",
            "chat_messages",
            ["conversation_id", "created_at", "id"],
            unique=False,
        )

    if inspector.has_table("user_privacy_requests"):
        op.create_index(
            "ix_user_privacy_requests_user_kind_requested_id",
            "user_privacy_requests",
            ["user_id", "request_kind", "requested_at", "id"],
            unique=False,
        )

    if inspector.has_table("user_subscriptions"):
        op.create_index(
            "ix_user_subscriptions_user_updated_id",
            "user_subscriptions",
            ["user_id", "updated_at", "id"],
            unique=False,
        )

    if inspector.has_table("enterprise_daily_usages"):
        op.create_index(
            "ix_enterprise_daily_usages_account_date",
            "enterprise_daily_usages",
            ["enterprise_account_id", "usage_date"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("enterprise_daily_usages"):
        op.drop_index(
            "ix_enterprise_daily_usages_account_date",
            table_name="enterprise_daily_usages",
        )
    if inspector.has_table("user_subscriptions"):
        op.drop_index(
            "ix_user_subscriptions_user_updated_id",
            table_name="user_subscriptions",
        )
    if inspector.has_table("user_privacy_requests"):
        op.drop_index(
            "ix_user_privacy_requests_user_kind_requested_id",
            table_name="user_privacy_requests",
        )
    if inspector.has_table("chat_messages"):
        op.drop_index(
            "ix_chat_messages_conversation_created_id",
            table_name="chat_messages",
        )
    if inspector.has_table("chat_conversations"):
        op.drop_index(
            "ix_chat_conversations_user_updated_id",
            table_name="chat_conversations",
        )
        op.drop_index(
            "ix_chat_conversations_user_status_updated_id",
            table_name="chat_conversations",
        )
