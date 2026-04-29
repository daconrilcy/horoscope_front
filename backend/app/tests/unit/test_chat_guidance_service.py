from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
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
from app.services.auth_service import AuthService
from app.services.llm_generation.anonymization_service import LLMAnonymizationError
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatGuidanceService,
    ChatGuidanceServiceError,
)
from app.services.llm_generation.guidance.persona_config_service import (
    PersonaConfigService,
    PersonaConfigUpdatePayload,
)
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session
from app.tests.helpers.llm_adapter_stub import reset_test_generators, set_test_chat_generator


def _cleanup_tables() -> None:
    ChatGuidanceService.reset_quality_kpis()
    reset_test_generators()
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
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
        # Seed default persona
        default_persona = LlmPersonaModel(
            name="Astrologue Standard",
            enabled=True,
            tone="direct",
            verbosity="medium",
            style_markers=[],
            boundaries=[],
            allowed_topics=[],
            disallowed_topics=[],
            formatting={},
        )
        db.add(default_persona)
        db.commit()


def _create_user_id() -> int:
    return _create_user_id_with_email("chat-user@example.com")


def _create_user_id_with_email(email: str) -> int:
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        db.commit()
        return auth.user.id


def _create_ops_user_id_with_email(email: str) -> int:
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="ops")
        db.commit()
        return auth.user.id


class RecordingGenerator:
    """Generator that records all calls and returns a simple response."""

    def __init__(self) -> None:
        self.messages_list: list[list[dict[str, str]]] = []
        self.contexts: list[dict[str, str | None]] = []

    async def __call__(
        self,
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str,
    ) -> str:
        self.messages_list.append(messages)
        self.contexts.append(dict(context))
        return "ok:20"


class TimeoutGenerator:
    """Generator that raises TimeoutError."""

    async def __call__(self, *args, **kwargs) -> str:
        raise TimeoutError("timeout")


class UnavailableGenerator:
    """Generator that raises ConnectionError."""

    async def __call__(self, *args, **kwargs) -> str:
        raise ConnectionError("unavailable")


class OffScopeThenRecoveredGenerator:
    """Generator that returns off-scope on first call, then recovers."""

    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self, *args, **kwargs) -> str:
        self.calls += 1
        if self.calls == 1:
            return "[off_scope] reponse incoherente"
        return "Reponse reformulee et pertinente"


class AlwaysOffScopeGenerator:
    """Generator that always returns off-scope."""

    async def __call__(self, *args, **kwargs) -> str:
        return "[off_scope] toujours incoherent"


class OffScopeThenRetryOnceRecoveredGenerator:
    """Generator that needs two recovery attempts."""

    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self, *args, **kwargs) -> str:
        self.calls += 1
        if self.calls <= 2:
            return "[off_scope] incoherent"
        return "Reponse retry_once pertinente"


def test_extract_assistant_text_prefers_structured_output_message() -> None:
    gateway_result = SimpleNamespace(
        structured_output={"message": "Réponse astrologue propre", "confidence": 0.8},
        raw_output='{"message":"Réponse fallback"}',
    )

    assert (
        ChatGuidanceService._extract_assistant_text(gateway_result) == "Réponse astrologue propre"
    )


def test_extract_assistant_text_reads_json_message_from_raw_output() -> None:
    gateway_result = SimpleNamespace(
        structured_output=None,
        raw_output='{"message":"Réponse parsée","suggestedreplies":["A","B"]}',
    )

    assert ChatGuidanceService._extract_assistant_text(gateway_result) == "Réponse parsée"


def test_send_message_success_creates_user_and_assistant_messages() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    generator = RecordingGenerator()
    set_test_chat_generator(generator)

    with open_app_test_db_session() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Quel est mon climat de la semaine ?",
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
    assert len(generator.messages_list) == 1
    assert any("climat" in m["content"].lower() for m in generator.messages_list[0])


def test_send_message_normalizes_structured_chat_json_before_persisting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    async def _structured_chat_reply(*args, **kwargs):
        return SimpleNamespace(
            raw_output=(
                '{"message":"Réponse astrologue formatée",'
                '"suggested_replies":["Suite 1"],"intent":"offer_event_guidance",'
                '"confidence":0.66,"safety_notes":[]}'
            ),
            structured_output={
                "message": "Réponse astrologue formatée",
                "suggested_replies": ["Suite 1"],
                "intent": "offer_event_guidance",
                "confidence": 0.66,
                "safety_notes": [],
            },
            usage=SimpleNamespace(input_tokens=10, output_tokens=20),
            meta=SimpleNamespace(model="gpt-5-nano"),
            request_id="req-structured-chat",
        )

    monkeypatch.setattr(
        "app.services.llm_generation.chat.chat_guidance_service.AIEngineAdapter.generate_chat_reply",
        _structured_chat_reply,
    )
    monkeypatch.setattr(
        "app.services.llm_generation.chat.chat_guidance_service.ChatGuidanceService._record_tokens",
        lambda *args, **kwargs: None,
    )

    with open_app_test_db_session() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Est-ce que ma soirée va bien se passer ?",
        )
        db.commit()

    assert reply.assistant_message.content == "Réponse astrologue formatée"
    with open_app_test_db_session() as db:
        stored_assistant = (
            db.query(ChatMessageModel)
            .filter(ChatMessageModel.role == "assistant")
            .order_by(ChatMessageModel.id.desc())
            .first()
        )
        assert stored_assistant is not None
        assert stored_assistant.content == "Réponse astrologue formatée"


def test_send_message_first_turn_uses_minimal_opening_context() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    generator = RecordingGenerator()
    set_test_chat_generator(generator)

    with open_app_test_db_session() as db:
        profile_repo = UserBirthProfileModel(
            user_id=user_id,
            birth_date=date(1990, 3, 22),
            birth_time=None,
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        db.add(profile_repo)
        db.commit()

    with open_app_test_db_session() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Bonjour, je traverse une journée étrange.",
        )
        db.commit()

    assert len(generator.contexts) == 1
    opening_context = generator.contexts[0]
    assert opening_context["chat_turn_stage"] == "opening"
    assert opening_context["today_date"] is not None
    assert opening_context["user_profile_brief"] is not None
    assert "chat-user@example.com" in (opening_context["user_profile_brief"] or "")
    assert "Âge:" in (opening_context["user_profile_brief"] or "")
    assert opening_context["natal_chart_summary"] is None


def test_send_message_follow_up_turn_restores_extended_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    generator = RecordingGenerator()
    set_test_chat_generator(generator)

    with open_app_test_db_session() as db:
        db.add(
            UserBirthProfileModel(
                user_id=user_id,
                birth_date=date(1990, 3, 22),
                birth_time=None,
                birth_place="Paris",
                birth_timezone="Europe/Paris",
            )
        )
        db.commit()

    class _FakeNatalChart:
        def __init__(self) -> None:
            self.result = {"sun": "aries"}

    monkeypatch.setattr(
        "app.services.llm_generation.chat.chat_guidance_service.UserNatalChartService.get_latest_for_user",
        lambda db, user_id: _FakeNatalChart(),
    )
    monkeypatch.setattr(
        "app.services.llm_generation.chat.chat_guidance_service.build_chat_natal_hint",
        lambda natal_result, degraded_mode: "Résumé natal synthétique",
    )

    with open_app_test_db_session() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Bonjour, comment me sens-tu aujourd'hui ?",
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Oui, tu peux regarder plus en détail.",
        )
        db.commit()

    assert len(generator.contexts) == 2
    follow_up_context = generator.contexts[1]
    assert follow_up_context["chat_turn_stage"] == "follow_up"
    assert follow_up_context["user_profile_brief"] is None
    assert follow_up_context["natal_chart_summary"] == "Résumé natal synthétique"


def test_send_message_anonymizes_personal_identifiers_before_llm_call() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    generator = RecordingGenerator()
    set_test_chat_generator(generator)

    with open_app_test_db_session() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Mon email est user@example.com et mon numero est +33 6 12 34 56 78",
        )
        db.commit()

    messages = generator.messages_list[0]
    all_content = " ".join(m["content"] for m in messages)
    assert "user@example.com" not in all_content
    assert "[redacted_email_" in all_content
    assert "[redacted_phone_" in all_content


def test_send_message_uses_active_persona_policy_in_prompt() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    ops_user_id = _create_ops_user_id_with_email("persona-chat-ops@example.com")
    generator = RecordingGenerator()
    set_test_chat_generator(generator)
    with open_app_test_db_session() as db:
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
        )
        db.commit()

    assert len(generator.messages_list) == 1


def test_send_message_timeout_raises_retryable_error() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    set_test_chat_generator(TimeoutGenerator())
    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Test timeout",
            )

    assert error.value.code == "llm_timeout"
    assert error.value.details["retryable"] == "true"
    assert error.value.details["action"] == "retry_message"


def test_send_message_unavailable_raises_retryable_error() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    set_test_chat_generator(UnavailableGenerator())
    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Test unavailable",
            )

    assert error.value.code == "llm_unavailable"
    assert error.value.details["retryable"] == "true"


def test_send_message_rejects_empty_input() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with open_app_test_db_session() as db:
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
    set_test_chat_generator(OffScopeThenRecoveredGenerator())

    with open_app_test_db_session() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
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
    set_test_chat_generator(AlwaysOffScopeGenerator())

    with open_app_test_db_session() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
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
    set_test_chat_generator(OffScopeThenRetryOnceRecoveredGenerator())

    with open_app_test_db_session() as db:
        reply = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
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
    set_test_chat_generator(OffScopeThenRecoveredGenerator())

    with open_app_test_db_session() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Question critique",
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
    generator = RecordingGenerator()
    set_test_chat_generator(generator)

    with open_app_test_db_session() as db:
        first = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Premiere question",
        )
        second = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Deuxieme question",
        )
        db.commit()

    assert first.conversation_id == second.conversation_id
    assert len(generator.messages_list) == 2
    second_messages = generator.messages_list[1]
    all_content = " ".join(m["content"] for m in second_messages)
    assert "Premiere question" in all_content
    assert "ok:20" in all_content
    assert "Deuxieme question" in all_content
    assert second.context.message_count == 3
    assert len(second.context.message_ids) == 3


def test_send_message_applies_context_window_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    generator = RecordingGenerator()
    set_test_chat_generator(generator)
    monkeypatch.setattr(settings, "chat_context_window_messages", 2)
    monkeypatch.setattr(settings, "chat_context_max_characters", 4000)

    with open_app_test_db_session() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Q1",
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Q2",
        )
        third = ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="Q3",
        )
        db.commit()

    assert len(generator.messages_list) == 3
    third_messages = generator.messages_list[2]
    all_content = " ".join(m["content"] for m in third_messages)
    assert "Q1" not in all_content
    assert "ok:20" in all_content
    assert "Q3" in all_content
    assert third.context.message_count == 2


def test_send_message_invalid_context_config_raises_stable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    set_test_chat_generator(RecordingGenerator())
    monkeypatch.setattr(settings, "chat_context_window_messages", 0)

    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Question",
            )

    assert error.value.code == "invalid_chat_context_config"


def test_send_message_raises_llm_anonymization_failed_when_anonymizer_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    set_test_chat_generator(RecordingGenerator())

    def _raise_anonymization_error(_: str) -> str:
        raise LLMAnonymizationError("boom")

    monkeypatch.setattr(
        "app.services.llm_generation.chat.chat_guidance_service.anonymize_text",
        _raise_anonymization_error,
    )

    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=user_id,
                message="Mon email est user@example.com",
            )

    assert error.value.code == "llm_anonymization_failed"


def test_send_message_context_selection_stays_contiguous_when_budget_is_exceeded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    generator = RecordingGenerator()
    set_test_chat_generator(generator)
    monkeypatch.setattr(settings, "chat_context_window_messages", 10)
    monkeypatch.setattr(settings, "chat_context_max_characters", 30)

    with open_app_test_db_session() as db:
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="A",
        )
        ChatGuidanceService.send_message(
            db=db,
            user_id=user_id,
            message="B",
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
        )
        db.commit()

    last_messages = generator.messages_list[-1]
    all_content = " ".join(m["content"] for m in last_messages)
    assert "C" in all_content
    assert "B" not in all_content


def test_create_message_updates_conversation_updated_at_for_latest_selection() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with open_app_test_db_session() as db:
        persona = LlmPersonaModel(
            name="Test Persona",
            enabled=True,
            tone="direct",
            verbosity="medium",
            style_markers=[],
            boundaries=[],
            allowed_topics=[],
            disallowed_topics=[],
            formatting={},
        )
        db.add(persona)
        db.flush()
        persona_id = persona.id

        persona_2 = LlmPersonaModel(
            name="Test Persona 2",
            enabled=True,
            tone="direct",
            verbosity="medium",
            style_markers=[],
            boundaries=[],
            allowed_topics=[],
            disallowed_topics=[],
            formatting={},
        )
        db.add(persona_2)
        db.flush()
        persona_2_id = persona_2.id

        repo = ChatRepository(db)
        conversation_1 = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        conversation_2 = repo.create_conversation(user_id=user_id, persona_id=persona_2_id)

        # We need to test ordering when user_id is the same.
        # But wait, get_latest_active_conversation_by_user_id(user_id) returns the latest overall.
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

    with open_app_test_db_session() as db:
        persona = LlmPersonaModel(
            name="Test Persona",
            enabled=True,
            tone="direct",
            verbosity="medium",
            style_markers=[],
            boundaries=[],
            allowed_topics=[],
            disallowed_topics=[],
            formatting={},
        )
        db.add(persona)
        db.flush()
        persona_id = persona.id

        repo = ChatRepository(db)
        own_conversation = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        repo.create_message(
            conversation_id=own_conversation.id,
            role="user",
            content="Mon historique",
        )
        other_conversation = repo.create_conversation(user_id=other_user_id, persona_id=persona_id)
        repo.create_message(
            conversation_id=other_conversation.id,
            role="user",
            content="Historique autre user",
        )
        db.commit()
    with open_app_test_db_session() as db:
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

    set_test_chat_generator(RecordingGenerator())

    with open_app_test_db_session() as db:
        response = ChatGuidanceService.send_message(
            db=db,
            user_id=owner_user_id,
            message="Thread owner",
        )
        db.commit()
        conversation_id = response.conversation_id

    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as forbidden_error:
            ChatGuidanceService.get_conversation_history(
                db=db,
                user_id=other_user_id,
                conversation_id=conversation_id,
            )
    assert forbidden_error.value.code == "conversation_forbidden"

    with open_app_test_db_session() as db:
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

    with open_app_test_db_session() as db:
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
    set_test_chat_generator(RecordingGenerator())

    with open_app_test_db_session() as db:
        owner_reply = ChatGuidanceService.send_message(
            db=db,
            user_id=owner_user_id,
            message="Owner thread",
        )
        db.commit()
        owner_conversation_id = owner_reply.conversation_id

    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as missing_error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=owner_user_id,
                message="Will fail",
                conversation_id=999999,
            )
    assert missing_error.value.code == "conversation_not_found"

    with open_app_test_db_session() as db:
        with pytest.raises(ChatGuidanceServiceError) as forbidden_error:
            ChatGuidanceService.send_message(
                db=db,
                user_id=other_user_id,
                message="Will fail",
                conversation_id=owner_conversation_id,
            )
    assert forbidden_error.value.code == "conversation_forbidden"
