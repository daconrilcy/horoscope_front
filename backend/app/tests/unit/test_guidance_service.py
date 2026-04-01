import uuid
from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import select

from app.infra.db.base import Base
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.entitlement_types import UsageState
from app.services.guidance_service import GuidanceService, GuidanceServiceError
from app.services.persona_config_service import PersonaConfigService, PersonaConfigUpdatePayload


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _create_user_id(email: str = "guidance-user@example.com") -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        db.commit()
        return auth.user.id


def _create_ops_user_id(email: str = "ops-user@example.com") -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="ops")
        db.commit()
        return auth.user.id


def _seed_birth_profile(user_id: int) -> None:
    with SessionLocal() as db:
        profile = UserBirthProfileModel(
            user_id=user_id,
            birth_date=date(1990, 1, 1),
            birth_time="12:00:00",
            birth_place="Paris, France",
            birth_timezone="Europe/Paris",
            birth_lat=48.8566,
            birth_lon=2.3522,
        )
        db.add(profile)
        db.commit()


class RecordingGenerator:
    def __init__(self) -> None:
        self.messages: list[list[dict[str, str]]] = []
        self.contexts: list[dict[str, str | None]] = []
        self.use_cases: list[str] = []

    async def __call__(
        self,
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        use_case: str,
        *args: object,
        **kwargs: object,
    ) -> str:
        self.messages.append(messages)
        self.contexts.append(context)
        self.use_cases.append(use_case)
        return (
            "1. Synthesis of the day. High energy.\n"
            "2. Point 1: Positive vibes.\nPoint 2: Clarity.\n"
            "3. Advice 1: Act now.\nAdvice 2: Keep moving.\n"
            "4. Disclaimer: Not medical advice."
        )

    async def generate_chat(self, *args, **kwargs) -> str:
        return "Chat response"

    async def generate_guidance(self, use_case, context, *args, **kwargs) -> str:
        self.use_cases.append(use_case)
        self.contexts.append(context)
        return (
            "1. Synthesis of the day. High energy.\n"
            "2. Point 1: Positive vibes.\nPoint 2: Clarity.\n"
            "3. Advice 1: Act now.\nAdvice 2: Keep moving.\n"
            "4. Disclaimer: Not medical advice."
        )


class EchoPromptGenerator:
    async def __call__(
        self,
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        *args: object,
        **kwargs: object,
    ) -> str:
        return "[guidance_prompt_version:v1]\nSummary: Success."

    async def generate_guidance(self, use_case, context, *args, **kwargs) -> str:
        return "[guidance_prompt_version:v1]\nSummary: Success."


class TimeoutGenerator:
    async def __call__(self, *args: object, **kwargs: object) -> str:
        raise TimeoutError("LLM Timeout")


class UnavailableGenerator:
    async def __call__(self, *args: object, **kwargs: object) -> str:
        raise ConnectionError("LLM Provider Down")


class OffScopeThenRecoveredGenerator:
    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self, *args: object, **kwargs: object) -> str:
        self.calls += 1
        if self.calls == 1:
            return "[off_scope] Je ne sais pas."
        return (
            "1. Recovery synthesis.\n"
            "2. Point 1: Everything is fine.\nPoint 2: Clarity.\n"
            "3. Advice 1: Keep going.\nAdvice 2: Positive outlook.\n"
            "4. Disclaimer: None."
        )


class AlwaysOffScopeGenerator:
    async def __call__(self, *args: object, **kwargs: object) -> str:
        return "[off_scope] Erreur fatale."


def set_test_generators(generator: object) -> None:
    from app.services.ai_engine_adapter import set_test_chat_generator, set_test_guidance_generator

    if hasattr(generator, "generate_chat"):
        set_test_chat_generator(generator.generate_chat)  # type: ignore
    elif callable(generator):
        set_test_chat_generator(generator)  # type: ignore
    else:
        set_test_chat_generator(None)

    if hasattr(generator, "generate_guidance"):
        set_test_guidance_generator(generator.generate_guidance)  # type: ignore
    elif callable(generator):
        set_test_guidance_generator(generator)  # type: ignore
    else:
        set_test_guidance_generator(None)


def _get_default_persona_id() -> uuid.UUID:
    with SessionLocal() as db:
        # Create persona if not exists
        persona = db.scalar(select(LlmPersonaModel).limit(1))
        if not persona:
            persona = LlmPersonaModel(
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
            db.add(persona)
            db.commit()
        return db.scalar(select(LlmPersonaModel.id).limit(1))


def test_request_guidance_daily_success() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    generator = RecordingGenerator()
    set_test_generators(generator)
    persona_id = _get_default_persona_id()

    with SessionLocal() as db:
        repo = ChatRepository(db)
        conversation = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        repo.create_message(
            conversation.id,
            "user",
            "Que dois-je surveiller aujourd hui ?",
        )
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
        )
        db.commit()

    assert response.period == "daily"
    assert response.attempts == 1
    assert response.fallback_used is False
    assert response.recovery.recovery_strategy == "none"
    assert response.recovery.recovery_applied is False
    assert len(response.key_points) > 0
    assert "medical" in response.disclaimer
    assert response.context_message_count >= 1
    assert len(generator.use_cases) == 1
    assert generator.use_cases[0] == "guidance_daily"


def test_request_guidance_weekly_success() -> None:
    """Test weekly guidance generation via AIEngineAdapter."""
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    generator = RecordingGenerator()
    set_test_generators(generator)

    persona_id = _get_default_persona_id()
    with SessionLocal() as db:
        repo = ChatRepository(db)
        conversation = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        repo.create_message(
            conversation.id,
            "user",
            "Quels sont les themes majeurs de ma semaine ?",
        )
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="weekly",
        )
        db.commit()

    assert response.period == "weekly"
    assert response.attempts == 1
    assert response.fallback_used is False
    assert response.recovery.recovery_strategy == "none"
    assert response.recovery.recovery_applied is False
    assert len(response.key_points) > 0
    assert "medical" in response.disclaimer
    assert response.context_message_count >= 1
    assert len(generator.use_cases) == 1
    assert generator.use_cases[0] == "guidance_weekly"


def test_request_guidance_uses_active_persona_policy_in_prompt() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    ops_user_id = _create_ops_user_id("guidance-ops@example.com")
    generator = RecordingGenerator()
    set_test_generators(generator)

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
        GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
        )
        db.commit()

    assert len(generator.contexts) == 1
    assert "persona_line" in generator.contexts[0]
    persona_line = generator.contexts[0].get("persona_line", "")
    assert "profile=legacy-default" in persona_line
    assert "tone=direct" in persona_line
    assert "prudence=high" in persona_line


def test_request_guidance_invalid_period() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as error:
            GuidanceService.request_guidance(db=db, user_id=user_id, period="monthly")
    assert error.value.code == "invalid_guidance_period"


def test_request_guidance_missing_birth_profile() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as error:
            GuidanceService.request_guidance(db=db, user_id=user_id, period="daily")
    assert error.value.code == "missing_birth_profile"


def test_request_guidance_timeout_and_unavailable_are_retryable() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)

    set_test_generators(TimeoutGenerator())
    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as timeout_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=user_id,
                period="daily",
            )
    assert timeout_error.value.code == "llm_timeout"
    assert timeout_error.value.details["retryable"] == "true"

    set_test_generators(UnavailableGenerator())
    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as unavailable_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=user_id,
                period="weekly",
            )
    assert unavailable_error.value.code == "llm_unavailable"
    assert unavailable_error.value.details["retryable"] == "true"


def test_request_guidance_delegates_network_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that GuidanceService doesn't apply its own sleep retry for network errors."""
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    delays: list[float] = []
    set_test_generators(TimeoutGenerator())

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr("asyncio.sleep", fake_sleep)

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as timeout_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=user_id,
                period="daily",
            )

    assert timeout_error.value.code == "llm_timeout"
    assert len(delays) == 0  # No sleep because retry is delegated to Gateway


def test_request_guidance_never_leaks_internal_prompt_in_summary() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    set_test_generators(EchoPromptGenerator())

    persona_id = _get_default_persona_id()
    with SessionLocal() as db:
        repo = ChatRepository(db)
        conversation = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        repo.create_message(conversation.id, "user", "Question sensible")
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
        )
        db.commit()

    assert "[guidance_prompt_version:" not in response.summary
    assert "Recent context:" not in response.summary


def test_request_guidance_rejects_unknown_or_foreign_conversation_id() -> None:
    _cleanup_tables()
    owner_user_id = _create_user_id()
    _seed_birth_profile(owner_user_id)
    set_test_generators(RecordingGenerator())
    with SessionLocal() as db:
        foreign_user = AuthService.register(
            db,
            email="guidance-foreign-user@example.com",
            password="strong-pass-123",
        ).user
        db.commit()
        foreign_user_id = foreign_user.id
    _seed_birth_profile(foreign_user_id)

    persona_id = _get_default_persona_id()
    with SessionLocal() as db:
        repo = ChatRepository(db)
        owner_conversation = repo.create_conversation(user_id=owner_user_id, persona_id=persona_id)
        repo.create_message(owner_conversation.id, "user", "Thread owner")
        owner_conversation_id = owner_conversation.id
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as missing_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=owner_user_id,
                period="daily",
                conversation_id=999999,
            )
    assert missing_error.value.code == "conversation_not_found"

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as forbidden_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=foreign_user_id,
                period="daily",
                conversation_id=owner_conversation_id,
            )
    assert forbidden_error.value.code == "conversation_forbidden"


def test_request_contextual_guidance_success() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    generator = RecordingGenerator()
    set_test_generators(generator)

    persona_id = _get_default_persona_id()
    with SessionLocal() as db:
        repo = ChatRepository(db)
        conversation = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        repo.create_message(conversation.id, "user", "Contexte personnel")
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Je dois choisir entre deux offres.",
            objective="Prendre une decision sereine.",
            time_horizon="48h",
            conversation_id=conversation.id,
        )
        db.commit()

    assert response.guidance_type == "contextual"
    assert response.situation == "Je dois choisir entre deux offres."
    assert response.objective == "Prendre une decision sereine."
    assert response.time_horizon == "48h"
    assert response.recovery.recovery_strategy == "none"
    assert response.recovery.recovery_applied is False
    assert response.context_message_count >= 1
    assert len(generator.use_cases) == 1
    assert generator.use_cases[0] == "guidance_contextual"


def test_request_contextual_guidance_injects_latest_natal_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id("guidance-natal-summary@example.com")
    _seed_birth_profile(user_id)
    generator = RecordingGenerator()
    set_test_generators(generator)

    class _FakeChart:
        result = object()

    monkeypatch.setattr(
        "app.services.guidance_service.UserNatalChartService.get_latest_for_user",
        lambda db, user_id: _FakeChart(),
    )
    monkeypatch.setattr(
        "app.services.guidance_service.build_natal_chart_summary",
        lambda **kwargs: "SOLEIL: Belier\nLUNE: Cancer",
    )

    with SessionLocal() as db:
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Je veux comprendre le climat de cette periode.",
            objective="Comprendre le climat astrologique du week-end.",
            time_horizon="ce week-end",
        )
        db.commit()

    assert response.guidance_type == "contextual"
    assert len(generator.contexts) == 1
    assert generator.contexts[0]["natal_chart_summary"] == "SOLEIL: Belier\nLUNE: Cancer"


def test_request_guidance_applies_recovery_when_off_scope_detected() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    set_test_generators(OffScopeThenRecoveredGenerator())

    with SessionLocal() as db:
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
        )
        db.commit()

    assert response.fallback_used is False
    assert response.recovery.off_scope_detected is True
    assert response.recovery.recovery_applied is True
    assert response.recovery.recovery_strategy == "reformulate"


def test_request_contextual_guidance_uses_safe_fallback_when_recovery_fails() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    set_test_generators(AlwaysOffScopeGenerator())

    with SessionLocal() as db:
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Situation",
            objective="Objectif",
        )
        db.commit()

    assert response.fallback_used is True
    assert response.recovery.off_scope_detected is True
    assert response.recovery.recovery_applied is True
    assert response.recovery.recovery_strategy == "safe_fallback"


def test_request_contextual_guidance_normalizes_blank_time_horizon_to_none() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    set_test_generators(RecordingGenerator())

    with SessionLocal() as db:
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Situation",
            objective="Objectif",
            time_horizon="   ",
        )
        db.commit()

    assert response.time_horizon is None


def test_request_contextual_guidance_never_leaks_internal_prompt_in_summary() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    set_test_generators(EchoPromptGenerator())

    persona_id = _get_default_persona_id()
    with SessionLocal() as db:
        repo = ChatRepository(db)
        conversation = repo.create_conversation(user_id=user_id, persona_id=persona_id)
        repo.create_message(conversation.id, "user", "Question sensible contextual")
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Situation sensible",
            objective="Objectif sensible",
        )
        db.commit()

    assert "[guidance_prompt_version:" not in response.summary
    assert "Recent context:" not in response.summary
    assert "semaine" not in response.summary.lower()


def test_request_contextual_guidance_summary_uses_first_clean_paragraph() -> None:
    _cleanup_tables()
    user_id = _create_user_id("guidance-context-summary@example.com")
    _seed_birth_profile(user_id)

    class StructuredContextualGenerator:
        async def generate_guidance(self, use_case, context, *args, **kwargs) -> str:
            return (
                "Pour explorer votre dynamique relationnelle, je regarde d abord les points "
                "d accord les plus stables.\n\n"
                "### Alignements\n"
                "1. **Communication**\n"
                "- Vous partagez une base de dialogue claire."
            )

    set_test_generators(StructuredContextualGenerator())

    with SessionLocal() as db:
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Je veux comprendre ma relation.",
            objective="Lire la dynamique relationnelle.",
        )
        db.commit()

    assert response.summary == (
        "Pour explorer votre dynamique relationnelle, je regarde d abord les points "
        "d accord les plus stables."
    )
    assert "#" not in response.summary
    assert "*" not in response.summary


def test_request_contextual_guidance_invalid_context_rejected() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    set_test_generators(RecordingGenerator())

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as error:
            GuidanceService.request_contextual_guidance(
                db=db,
                user_id=user_id,
                situation="   ",
                objective="   ",
            )
    assert error.value.code == "invalid_guidance_context"


def test_request_contextual_guidance_missing_birth_profile() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    set_test_generators(RecordingGenerator())

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as error:
            GuidanceService.request_contextual_guidance(
                db=db,
                user_id=user_id,
                situation="Situation",
                objective="Objectif",
            )
    assert error.value.code == "missing_birth_profile"


def test_request_contextual_guidance_rejects_unknown_or_foreign_conversation_id() -> None:
    _cleanup_tables()
    owner_user_id = _create_user_id()
    _seed_birth_profile(owner_user_id)
    set_test_generators(RecordingGenerator())
    with SessionLocal() as db:
        foreign_user = AuthService.register(
            db,
            email="guidance-context-foreign-user@example.com",
            password="strong-pass-123",
        ).user
        db.commit()
        foreign_user_id = foreign_user.id
    _seed_birth_profile(foreign_user_id)

    persona_id = _get_default_persona_id()
    with SessionLocal() as db:
        repo = ChatRepository(db)
        owner_conversation = repo.create_conversation(user_id=owner_user_id, persona_id=persona_id)
        repo.create_message(owner_conversation.id, "user", "Thread owner contextual")
        owner_conversation_id = owner_conversation.id
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as missing_error:
            GuidanceService.request_contextual_guidance(
                db=db,
                user_id=owner_user_id,
                situation="Situation",
                objective="Objectif",
                conversation_id=999999,
            )
    assert missing_error.value.code == "conversation_not_found"

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as forbidden_error:
            GuidanceService.request_contextual_guidance(
                db=db,
                user_id=foreign_user_id,
                situation="Situation",
                objective="Objectif",
                conversation_id=owner_conversation_id,
            )
    assert forbidden_error.value.code == "conversation_forbidden"


@pytest.mark.asyncio
async def test_guidance_recovery_records_tokens_for_each_recovery_attempt(monkeypatch) -> None:
    _cleanup_tables()
    recorded_request_ids: list[str] = []

    async def fake_generate_guidance(*args, **kwargs):
        request_id = kwargs["request_id"]
        if request_id.endswith("-recovery-1"):
            return SimpleNamespace(
                raw_output="[off_scope] encore rate",
                request_id=request_id,
                meta=SimpleNamespace(model="gpt-4o-mini"),
                usage=SimpleNamespace(input_tokens=11, output_tokens=7),
            )
        return SimpleNamespace(
            raw_output="Reponse de recovery exploitable.",
            request_id=request_id,
            meta=SimpleNamespace(model="gpt-4o-mini"),
            usage=SimpleNamespace(input_tokens=13, output_tokens=5),
        )

    def fake_record_usage(*args, **kwargs):
        recorded_request_ids.append(kwargs["request_id"])
        return None

    entitlement_result = SimpleNamespace(
        usage_states=[
            UsageState(
                feature_code="thematic_consultation",
                quota_key="tokens",
                quota_limit=200_000,
                used=0,
                remaining=200_000,
                exhausted=False,
                period_unit="month",
                period_value=1,
                reset_mode="calendar",
                window_start=datetime(2026, 4, 1, tzinfo=timezone.utc),
                window_end=datetime(2026, 5, 1, tzinfo=timezone.utc),
            )
        ]
    )

    monkeypatch.setattr(
        "app.services.guidance_service.AIEngineAdapter.generate_guidance",
        fake_generate_guidance,
    )
    monkeypatch.setattr(
        "app.services.guidance_service.LlmTokenUsageService.record_usage",
        fake_record_usage,
    )

    with SessionLocal() as db:
        recovered_text, fallback_used, metadata = (
            await GuidanceService._apply_off_scope_recovery_async(
                db=db,
                use_case="guidance_contextual",
                context={"objective": "Tester la facturation"},
                user_id=1,
                request_id="rid-guidance",
                trace_id="trace-guidance",
                assistant_content="[off_scope] reponse initiale",
                persona_profile_code="legacy-default",
                entitlement_result=entitlement_result,
            )
        )

    assert recovered_text == "Reponse de recovery exploitable."
    assert fallback_used is False
    assert metadata.recovery_strategy == "retry_once"
    assert recorded_request_ids == ["rid-guidance-recovery-1", "rid-guidance-recovery-2"]
