import pytest
from sqlalchemy import delete

from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.db.session import SessionLocal, engine
from app.infra.llm.anonymizer import LLMAnonymizationError
from app.services.auth_service import AuthService
from app.services.chat_guidance_service import ChatGuidanceService, ChatGuidanceServiceError
from app.services.persona_config_service import PersonaConfigService, PersonaConfigUpdatePayload


def _cleanup_tables() -> None:
    ChatGuidanceService.reset_quality_kpis()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChatMessageModel,
            ChatConversationModel,
            ChartResultModel,
            UserBirthProfileModel,
            UserModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_user_id() -> int:
    return _create_user_id_with_email("chat-user@example.com")


def _create_user_id_with_email(email: str) -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        db.commit()
        return auth.user.id


def _create_ops_user_id_with_email(email: str) -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="ops")
        db.commit()
        return auth.user.id


class RecordingClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        self.prompts.append(prompt)
        return f"ok:{timeout_seconds}"


class TimeoutClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        raise TimeoutError("timeout")


class UnavailableClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        raise ConnectionError("unavailable")


class OffScopeThenRecoveredClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        self.calls += 1
        if self.calls == 1:
            return "[off_scope] reponse incoherente"
        return "Reponse reformulee et pertinente"


class AlwaysOffScopeClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        return "[off_scope] toujours incoherent"


class OffScopeThenRetryOnceRecoveredClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        self.calls += 1
        if self.calls <= 2:
            return "[off_scope] incoherent"
        return "Reponse retry_once pertinente"


def test_send_message_success_creates_user_and_assistant_messages() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    client = RecordingClient()

    with SessionLocal() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Quel est mon climat de la semaine ?",
            llm_client=client,
        )
        db.commit()

    assert reply.conversation_id > 0
    assert reply.user_message.role == "user"
    assert reply.assistant_message.role == "assistant"
    assert reply.attempts == 1
    assert reply.fallback_used is False
    assert reply.recovery.recovery_strategy == "none"
    assert reply.recovery.recovery_applied is False
    assert reply.context.message_count == 1
    assert reply.context.prompt_version == settings.chat_prompt_version
    assert len(reply.context.message_ids) == 1
    assert "climat" in client.prompts[0].lower()


def test_send_message_anonymizes_personal_identifiers_before_llm_call() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    client = RecordingClient()

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Mon email est user@example.com et mon numero est +33 6 12 34 56 78",
            llm_client=client,
        )
        db.commit()

    prompt = client.prompts[0]
    assert "user@example.com" not in prompt
    assert "[redacted_email_" in prompt
    assert "[redacted_phone_" in prompt


def test_send_message_uses_active_persona_policy_in_prompt() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    ops_user_id = _create_ops_user_id_with_email("persona-chat-ops@example.com")
    client = RecordingClient()
    with SessionLocal() as db:
        PersonaConfigService.update_active(
            db,
            user_id=ops_user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="high",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question persona",
            llm_client=client,
        )
        db.commit()

    prompt = client.prompts[0]
    assert "Persona policy: profile=legacy-default; tone=direct; prudence=high;" in prompt


def test_send_message_timeout_raises_retryable_error() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Test timeout",
                llm_client=TimeoutClient(),
            )

    assert error.value.code == "llm_timeout"
    assert error.value.details["retryable"] == "true"
    assert error.value.details["action"] == "retry_message"


def test_send_message_unavailable_raises_retryable_error() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Test unavailable",
                llm_client=UnavailableClient(),
            )

    assert error.value.code == "llm_unavailable"
    assert error.value.details["retryable"] == "true"


def test_send_message_rejects_empty_input() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="   ",
            )

    assert error.value.code == "invalid_chat_input"


def test_send_message_applies_reformulation_recovery_on_off_scope() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
            llm_client=OffScopeThenRecoveredClient(),
        )
        db.commit()

    assert reply.recovery.off_scope_detected is True
    assert reply.recovery.recovery_applied is True
    assert reply.recovery.recovery_strategy == "reformulate"
    assert reply.fallback_used is False
    assert "Reponse reformulee" in reply.assistant_message.content


def test_send_message_applies_safe_fallback_when_recovery_fails() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
            llm_client=AlwaysOffScopeClient(),
        )
        db.commit()

    assert reply.recovery.off_scope_detected is True
    assert reply.recovery.recovery_applied is True
    assert reply.recovery.recovery_strategy == "safe_fallback"
    assert reply.fallback_used is True
    assert "preciser votre contexte" in reply.assistant_message.content


def test_send_message_applies_retry_once_recovery_after_failed_reformulation() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
            llm_client=OffScopeThenRetryOnceRecoveredClient(),
        )
        db.commit()

    assert reply.recovery.off_scope_detected is True
    assert reply.recovery.recovery_applied is True
    assert reply.recovery.recovery_strategy == "retry_once"
    assert reply.recovery.recovery_attempts == 2
    assert reply.fallback_used is False
    assert "retry_once" in reply.assistant_message.content


def test_send_message_updates_quality_kpis_for_off_scope_recovery() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
            llm_client=OffScopeThenRecoveredClient(),
        )
        db.commit()

    kpis = ChatGuidanceService.get_quality_kpis()
    assert kpis["off_scope_count"] == 1.0
    assert kpis["recovery_success_rate"] == 1.0


def test_assess_off_scope_does_not_use_test_marker_simulate_off_scope() -> None:
    detected, score, reason = ChatGuidanceService._assess_off_scope(
        "La reponse contient simulate_off_scope mais reste normale."
    )
    assert detected is False
    assert score == 0.0
    assert reason is None


def test_send_message_second_turn_uses_previous_context_in_chronological_order() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    client = RecordingClient()

    with SessionLocal() as db:
        first = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Premiere question",
            llm_client=client,
        )
        second = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Deuxieme question",
            llm_client=client,
        )
        db.commit()

    assert first.conversation_id == second.conversation_id
    second_prompt = client.prompts[1]
    first_user_index = second_prompt.find("user: Premiere question")
    first_assistant_index = second_prompt.find("assistant: ok:20")
    second_user_index = second_prompt.find("user: Deuxieme question")
    assert first_user_index >= 0
    assert first_assistant_index > first_user_index
    assert second_user_index > first_assistant_index
    assert second.context.message_count == 3
    assert len(second.context.message_ids) == 3


def test_send_message_applies_context_window_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    client = RecordingClient()
    monkeypatch.setattr(settings, "chat_context_window_messages", 2)
    monkeypatch.setattr(settings, "chat_context_max_characters", 4000)

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Q1",
            llm_client=client,
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Q2",
            llm_client=client,
        )
        third = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Q3",
            llm_client=client,
        )
        db.commit()

    third_prompt = client.prompts[2]
    assert "Q1" not in third_prompt
    assert "assistant: ok:20" in third_prompt
    assert "Q3" in third_prompt
    assert third.context.message_count == 2


def test_send_message_invalid_context_config_raises_stable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    monkeypatch.setattr(settings, "chat_context_window_messages", 0)

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Question",
                llm_client=RecordingClient(),
            )

    assert error.value.code == "invalid_chat_context_config"


def test_send_message_raises_llm_anonymization_failed_when_anonymizer_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    def _raise_anonymization_error(_: str) -> str:
        raise LLMAnonymizationError("boom")

    monkeypatch.setattr(
        "app.services.chat_guidance_service.anonymize_text",
        _raise_anonymization_error,
    )

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Mon email est user@example.com",
                llm_client=RecordingClient(),
            )

    assert error.value.code == "llm_anonymization_failed"


def test_send_message_context_selection_stays_contiguous_when_budget_is_exceeded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    client = RecordingClient()
    monkeypatch.setattr(settings, "chat_context_window_messages", 10)
    monkeypatch.setattr(settings, "chat_context_max_characters", 30)

    with SessionLocal() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="A",
            llm_client=client,
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="B",
            llm_client=client,
        )
        conversation = ChatRepository(db).get_latest_active_conversation_by_user_id(user_id)
        assert conversation is not None
        ChatRepository(db).create_message(
            conversation_id=conversation.id,
            role="assistant",
            content="X" * 200,
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="C",
            llm_client=client,
        )
        db.commit()

    last_prompt = client.prompts[-1]
    assert "user: C" in last_prompt
    assert "user: B" not in last_prompt


def test_create_message_updates_conversation_updated_at_for_latest_selection() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        repo = ChatRepository(db)
        conversation_1 = repo.create_conversation(user_id=user_id)
        conversation_2 = repo.create_conversation(user_id=user_id)
        latest_before = repo.get_latest_active_conversation_by_user_id(user_id)
        assert latest_before is not None
        assert latest_before.id == conversation_2.id

        repo.create_message(
            conversation_id=conversation_1.id,
            role="user",
            content="Ping",
        )
        latest_after = repo.get_latest_active_conversation_by_user_id(user_id)
        assert latest_after is not None
        assert latest_after.id == conversation_1.id


def test_list_conversations_returns_user_scoped_history() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    other_user_id = _create_user_id_with_email("chat-other-user@example.com")

    with SessionLocal() as db:
        repo = ChatRepository(db)
        own_conversation = repo.create_conversation(user_id=user_id)
        repo.create_message(
            conversation_id=own_conversation.id,
            role="user",
            content="Mon historique",
        )
        other_conversation = repo.create_conversation(user_id=other_user_id)
        repo.create_message(
            conversation_id=other_conversation.id,
            role="user",
            content="Historique autre user",
        )
        db.commit()

    with SessionLocal() as db:
        result = ChatGuidanceService.list_conversations(
            db=db,
            user_id=user_id,
            limit=10,
            offset=0,
        )

    assert result.total == 1
    assert len(result.conversations) == 1
    assert result.conversations[0].last_message_preview == "Mon historique"


def test_get_conversation_history_rejects_forbidden_and_missing_conversation() -> None:
    _cleanup_tables()
    owner_user_id = _create_user_id()
    other_user_id = _create_user_id_with_email("chat-other-user@example.com")

    with SessionLocal() as db:
        response = ChatGuidanceService.send_message(
            db=db,
            user_id=owner_user_id,
            message="Thread owner",
            llm_client=RecordingClient(),
        )
        db.commit()
        conversation_id = response.conversation_id

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as forbidden_error:
            ChatGuidanceService.get_conversation_history(
                db=db,
                user_id=other_user_id,
                conversation_id=conversation_id,
            )
    assert forbidden_error.value.code == "conversation_forbidden"

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as missing_error:
            ChatGuidanceService.get_conversation_history(
                db=db,
                user_id=owner_user_id,
                conversation_id=999999,
            )
    assert missing_error.value.code == "conversation_not_found"


def test_list_conversations_rejects_invalid_pagination() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.list_conversations(
                db=db,
                user_id=user_id,
                limit=0,
                offset=0,
            )
    assert error.value.code == "invalid_chat_pagination"


def test_send_message_rejects_unknown_and_forbidden_conversation_id() -> None:
    _cleanup_tables()
    owner_user_id = _create_user_id()
    other_user_id = _create_user_id_with_email("chat-other-user@example.com")

    with SessionLocal() as db:
        owner_reply = ChatGuidanceService.send_message(
            db=db,
            user_id=owner_user_id,
            message="Owner thread",
            llm_client=RecordingClient(),
        )
        db.commit()
        owner_conversation_id = owner_reply.conversation_id

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as missing_error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=owner_user_id,
                message="Will fail",
                conversation_id=999999,
                llm_client=RecordingClient(),
            )
    assert missing_error.value.code == "conversation_not_found"

    with SessionLocal() as db:
        with pytest.raises(ChatGuidanceServiceError) as forbidden_error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=other_user_id,
                message="Will fail",
                conversation_id=owner_conversation_id,
                llm_client=RecordingClient(),
            )
    assert forbidden_error.value.code == "conversation_forbidden"
