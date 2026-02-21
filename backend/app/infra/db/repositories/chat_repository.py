from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_active_conversation_by_user_id(
        self,
        user_id: int,
    ) -> ChatConversationModel | None:
        return self.db.scalar(
            select(ChatConversationModel)
            .where(ChatConversationModel.user_id == user_id)
            .where(ChatConversationModel.status == "active")
            .order_by(desc(ChatConversationModel.updated_at), desc(ChatConversationModel.id))
            .limit(1)
        )

    def create_conversation(self, user_id: int) -> ChatConversationModel:
        model = ChatConversationModel(user_id=user_id, status="active")
        self.db.add(model)
        self.db.flush()
        return model

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        metadata_payload: dict[str, object] | None = None,
    ) -> ChatMessageModel:
        model = ChatMessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_payload=metadata_payload or {},
        )
        self.db.add(model)
        conversation = self.db.get(ChatConversationModel, conversation_id)
        if conversation is not None:
            conversation.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return model

    def get_recent_messages(self, conversation_id: int, limit: int) -> list[ChatMessageModel]:
        rows = list(
            self.db.scalars(
                select(ChatMessageModel)
                .where(ChatMessageModel.conversation_id == conversation_id)
                .order_by(desc(ChatMessageModel.created_at), desc(ChatMessageModel.id))
                .limit(limit)
            )
        )
        rows.reverse()
        return rows

    def list_conversations_by_user_id(
        self,
        user_id: int,
        *,
        limit: int,
        offset: int,
    ) -> list[ChatConversationModel]:
        return list(
            self.db.scalars(
                select(ChatConversationModel)
                .where(ChatConversationModel.user_id == user_id)
                .order_by(desc(ChatConversationModel.updated_at), desc(ChatConversationModel.id))
                .limit(limit)
                .offset(offset)
            )
        )

    def list_conversations_with_last_preview_by_user_id(
        self,
        user_id: int,
        *,
        limit: int,
        offset: int,
    ) -> list[tuple[ChatConversationModel, str | None]]:
        last_message_preview = (
            select(ChatMessageModel.content)
            .where(ChatMessageModel.conversation_id == ChatConversationModel.id)
            .order_by(desc(ChatMessageModel.created_at), desc(ChatMessageModel.id))
            .limit(1)
            .scalar_subquery()
        )
        rows = self.db.execute(
            select(ChatConversationModel, last_message_preview.label("last_message_preview"))
            .where(ChatConversationModel.user_id == user_id)
            .order_by(desc(ChatConversationModel.updated_at), desc(ChatConversationModel.id))
            .limit(limit)
            .offset(offset)
        )
        return [(conversation, preview) for conversation, preview in rows.all()]

    def count_conversations_by_user_id(self, user_id: int) -> int:
        return int(
            self.db.scalar(
                select(func.count(ChatConversationModel.id)).where(
                    ChatConversationModel.user_id == user_id
                )
            )
            or 0
        )

    def get_conversation_by_id(self, conversation_id: int) -> ChatConversationModel | None:
        return self.db.get(ChatConversationModel, conversation_id)

    def get_messages_by_conversation_id(self, conversation_id: int) -> list[ChatMessageModel]:
        return list(
            self.db.scalars(
                select(ChatMessageModel)
                .where(ChatMessageModel.conversation_id == conversation_id)
                .order_by(ChatMessageModel.created_at, ChatMessageModel.id)
            )
        )
