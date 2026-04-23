from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.llm_persona import LlmPersonaModel


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_active_conversation_by_user_id(
        self,
        user_id: int,
        persona_id: uuid.UUID | None = None,
    ) -> ChatConversationModel | None:
        query = (
            select(ChatConversationModel)
            .where(ChatConversationModel.user_id == user_id)
            .where(ChatConversationModel.status == "active")
        )
        if persona_id is not None:
            query = query.where(ChatConversationModel.persona_id == persona_id)

        return self.db.scalar(
            query.order_by(
                desc(ChatConversationModel.updated_at), desc(ChatConversationModel.id)
            ).limit(1)
        )

    def get_active_conversation(
        self, user_id: int, persona_id: uuid.UUID
    ) -> ChatConversationModel | None:
        """Get the active conversation for a user and persona."""
        return self.db.scalar(
            select(ChatConversationModel)
            .where(ChatConversationModel.user_id == user_id)
            .where(ChatConversationModel.persona_id == persona_id)
            .where(ChatConversationModel.status == "active")
        )

    def get_or_create_active_conversation(
        self, user_id: int, persona_id: uuid.UUID
    ) -> ChatConversationModel:
        """
        Get existing active conversation for user/persona or create a new one.
        Uses a savepoint to handle potential race conditions between select and insert.
        """
        existing = self.get_active_conversation(user_id, persona_id)
        if existing:
            return existing

        # Use a savepoint to handle the rare case where someone inserted it
        # between our SELECT and INSERT.
        try:
            with self.db.begin_nested():
                model = self.create_conversation(user_id, persona_id)
                return model
        except IntegrityError:
            # Another process inserted it first (or another constraint failed)
            # We retry getting it to be sure.
            found = self.get_active_conversation(user_id, persona_id)
            if found:
                return found
            # If still not found, it might be a foreign key error or other constraint, re-raise
            raise

    def create_conversation(self, user_id: int, persona_id: uuid.UUID) -> ChatConversationModel:
        model = ChatConversationModel(user_id=user_id, persona_id=persona_id, status="active")
        self.db.add(model)
        self.db.flush()
        return model

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        metadata_payload: dict[str, object] | None = None,
        client_message_id: str | None = None,
        reply_to_client_message_id: str | None = None,
    ) -> ChatMessageModel:
        model = ChatMessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_payload=metadata_payload or {},
            client_message_id=client_message_id,
            reply_to_client_message_id=reply_to_client_message_id,
        )
        self.db.add(model)
        conversation = self.db.get(ChatConversationModel, conversation_id)
        if conversation is not None:
            conversation.updated_at = datetime_provider.utcnow()
        self.db.flush()
        return model

    def get_assistant_by_reply_client_id(
        self, conversation_id: int, reply_to_client_message_id: str
    ) -> ChatMessageModel | None:
        return self.db.scalar(
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == conversation_id)
            .where(ChatMessageModel.reply_to_client_message_id == reply_to_client_message_id)
        )

    def get_message_by_client_id(
        self, conversation_id: int, client_message_id: str
    ) -> ChatMessageModel | None:
        return self.db.scalar(
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == conversation_id)
            .where(ChatMessageModel.client_message_id == client_message_id)
        )

    def get_next_assistant_message(
        self, conversation_id: int, after_id: int
    ) -> ChatMessageModel | None:
        return self.db.scalar(
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == conversation_id)
            .where(ChatMessageModel.role == "assistant")
            .where(ChatMessageModel.id > after_id)
            .order_by(ChatMessageModel.id)
            .limit(1)
        )

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
    ) -> list[tuple[ChatConversationModel, str | None, str | None, datetime | None]]:
        # Truncate to 120 directly in DB
        last_message_subq = (
            select(func.substr(ChatMessageModel.content, 1, 120))
            .where(ChatMessageModel.conversation_id == ChatConversationModel.id)
            .order_by(desc(ChatMessageModel.created_at), desc(ChatMessageModel.id))
            .limit(1)
            .scalar_subquery()
        )
        last_message_at_subq = (
            select(ChatMessageModel.created_at)
            .where(ChatMessageModel.conversation_id == ChatConversationModel.id)
            .order_by(desc(ChatMessageModel.created_at), desc(ChatMessageModel.id))
            .limit(1)
            .scalar_subquery()
        )
        # Sort by last_message_at if available, otherwise fall back to updated_at
        sort_key = func.coalesce(last_message_at_subq, ChatConversationModel.updated_at)
        rows = self.db.execute(
            select(
                ChatConversationModel,
                last_message_subq.label("last_message_preview"),
                LlmPersonaModel.name.label("persona_name"),
                last_message_at_subq.label("last_message_at"),
            )
            .join(LlmPersonaModel, LlmPersonaModel.id == ChatConversationModel.persona_id)
            .where(ChatConversationModel.user_id == user_id)
            .order_by(desc(sort_key), desc(ChatConversationModel.id))
            .limit(limit)
            .offset(offset)
        )
        return [
            (conversation, preview, persona_name, last_message_at)
            for conversation, preview, persona_name, last_message_at in rows.all()
        ]

    def get_or_create_conversation_by_persona(
        self, user_id: int, persona_id: uuid.UUID
    ) -> ChatConversationModel:
        """Get or create the active conversation for a user/persona pair."""
        return self.get_or_create_active_conversation(user_id=user_id, persona_id=persona_id)

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
