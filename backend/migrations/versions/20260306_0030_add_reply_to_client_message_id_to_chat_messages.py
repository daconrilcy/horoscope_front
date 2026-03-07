"""add reply_to_client_message_id to chat_messages for assistant idempotency

Revision ID: 20260306_0030
Revises: 20260306_0029
Create Date: 2026-03-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260306_0030"
down_revision: Union[str, Sequence[str], None] = "20260306_0029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("chat_messages"):
        return

    op.add_column(
        "chat_messages",
        sa.Column("reply_to_client_message_id", sa.String(36), nullable=True),
    )
    # Partial unique index: ensures at most one assistant message per client_message_id
    # per conversation, regardless of how many concurrent workers try to create it.
    op.create_index(
        "uq_chat_messages_conversation_reply_client_id",
        "chat_messages",
        ["conversation_id", "reply_to_client_message_id"],
        unique=True,
        postgresql_where=sa.text("reply_to_client_message_id IS NOT NULL"),
        sqlite_where=sa.text("reply_to_client_message_id IS NOT NULL"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("chat_messages"):
        return

    op.drop_index(
        "uq_chat_messages_conversation_reply_client_id",
        table_name="chat_messages",
    )
    op.drop_column("chat_messages", "reply_to_client_message_id")
