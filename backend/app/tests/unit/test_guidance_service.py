import pytest
from sqlalchemy import delete

from app.core.config import settings
from app.domain.astrology.natal_preparation import BirthInput
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
from app.services.auth_service import AuthService
from app.services.guidance_service import GuidanceService, GuidanceServiceError
from app.services.persona_config_service import PersonaConfigService, PersonaConfigUpdatePayload
from app.services.user_birth_profile_service import UserBirthProfileService


def _cleanup_tables() -> None:
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
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="guidance-user@example.com",
            password="strong-pass-123",
        )
        db.commit()
        return auth.user.id


def _seed_birth_profile(user_id: int) -> None:
    with SessionLocal() as db:
        UserBirthProfileService.upsert_for_user(
            db,
            user_id=user_id,
            payload=BirthInput(
                birth_date="1990-06-15",
                birth_time="10:30",
                birth_place="Paris",
                birth_timezone="Europe/Paris",
            ),
        )
        db.commit()


def _create_ops_user_id(email: str) -> int:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="ops",
        )
        db.commit()
        return auth.user.id


class RecordingClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        self.prompts.append(prompt)
        return f"guidance-ok:{timeout_seconds}"


class TimeoutClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        raise TimeoutError("timeout")


class UnavailableClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        raise ConnectionError("unavailable")


class EchoPromptClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        return f"Guidance astrologique: {prompt}"


class OffScopeThenRecoveredClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        self.calls += 1
        if self.calls == 1:
            return "[off_scope] guidance incoherente"
        return "Guidance reformulee et pertinente"


class AlwaysOffScopeClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        return "[off_scope] guidance toujours incoherente"


def test_request_guidance_daily_success() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    client = RecordingClient()

    with SessionLocal() as db:
        conversation = ChatRepository(db).create_conversation(user_id=user_id)
        ChatRepository(db).create_message(
            conversation.id,
            "user",
            "Que dois-je surveiller aujourd hui ?",
        )
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
            llm_client=client,
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
    assert "Period: daily" in client.prompts[0]


def test_request_guidance_uses_active_persona_policy_in_prompt() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    ops_user_id = _create_ops_user_id("guidance-ops@example.com")
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
        GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
            llm_client=client,
        )
        db.commit()

    assert (
        "Persona policy: profile=legacy-default; tone=direct; prudence=high;" in client.prompts[0]
    )


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

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as timeout_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=user_id,
                period="daily",
                llm_client=TimeoutClient(),
            )
    assert timeout_error.value.code == "llm_timeout"
    assert timeout_error.value.details["retryable"] == "true"

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as unavailable_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=user_id,
                period="weekly",
                llm_client=UnavailableClient(),
            )
    assert unavailable_error.value.code == "llm_unavailable"
    assert unavailable_error.value.details["retryable"] == "true"


def test_request_guidance_applies_retry_backoff_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    delays: list[float] = []

    monkeypatch.setattr(settings, "chat_llm_retry_count", 1)
    monkeypatch.setattr(settings, "chat_llm_retry_backoff_seconds", 0.01)
    monkeypatch.setattr(settings, "chat_llm_retry_backoff_max_seconds", 0.01)
    monkeypatch.setattr(settings, "chat_llm_retry_jitter_seconds", 0.0)
    monkeypatch.setattr("app.services.guidance_service.sleep", lambda delay: delays.append(delay))

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as timeout_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=user_id,
                period="daily",
                llm_client=TimeoutClient(),
            )

    assert timeout_error.value.code == "llm_timeout"
    assert len(delays) == 1
    assert delays[0] == pytest.approx(0.01, abs=0.0001)


def test_request_guidance_never_leaks_internal_prompt_in_summary() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)

    with SessionLocal() as db:
        conversation = ChatRepository(db).create_conversation(user_id=user_id)
        ChatRepository(db).create_message(conversation.id, "user", "Question sensible")
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
            llm_client=EchoPromptClient(),
        )
        db.commit()

    assert "[guidance_prompt_version:" not in response.summary
    assert "Recent context:" not in response.summary


def test_request_guidance_rejects_unknown_or_foreign_conversation_id() -> None:
    _cleanup_tables()
    owner_user_id = _create_user_id()
    _seed_birth_profile(owner_user_id)
    with SessionLocal() as db:
        foreign_user = AuthService.register(
            db,
            email="guidance-foreign-user@example.com",
            password="strong-pass-123",
        ).user
        db.commit()
        foreign_user_id = foreign_user.id
    _seed_birth_profile(foreign_user_id)

    with SessionLocal() as db:
        owner_conversation = ChatRepository(db).create_conversation(user_id=owner_user_id)
        ChatRepository(db).create_message(owner_conversation.id, "user", "Thread owner")
        owner_conversation_id = owner_conversation.id
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as missing_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=owner_user_id,
                period="daily",
                conversation_id=999999,
                llm_client=RecordingClient(),
            )
    assert missing_error.value.code == "conversation_not_found"

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as forbidden_error:
            GuidanceService.request_guidance(
                db=db,
                user_id=foreign_user_id,
                period="daily",
                conversation_id=owner_conversation_id,
                llm_client=RecordingClient(),
            )
    assert forbidden_error.value.code == "conversation_forbidden"


def test_request_contextual_guidance_success() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)
    client = RecordingClient()

    with SessionLocal() as db:
        conversation = ChatRepository(db).create_conversation(user_id=user_id)
        ChatRepository(db).create_message(conversation.id, "user", "Contexte personnel")
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Je dois choisir entre deux offres.",
            objective="Prendre une decision sereine.",
            time_horizon="48h",
            conversation_id=conversation.id,
            llm_client=client,
        )
        db.commit()

    assert response.guidance_type == "contextual"
    assert response.situation == "Je dois choisir entre deux offres."
    assert response.objective == "Prendre une decision sereine."
    assert response.time_horizon == "48h"
    assert response.recovery.recovery_strategy == "none"
    assert response.recovery.recovery_applied is False
    assert response.context_message_count >= 1
    assert "Situation:" in client.prompts[0]


def test_request_guidance_applies_recovery_when_off_scope_detected() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)

    with SessionLocal() as db:
        response = GuidanceService.request_guidance(
            db=db,
            user_id=user_id,
            period="daily",
            llm_client=OffScopeThenRecoveredClient(),
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

    with SessionLocal() as db:
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Situation",
            objective="Objectif",
            llm_client=AlwaysOffScopeClient(),
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

    with SessionLocal() as db:
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Situation",
            objective="Objectif",
            time_horizon="   ",
            llm_client=RecordingClient(),
        )
        db.commit()

    assert response.time_horizon is None


def test_request_contextual_guidance_never_leaks_internal_prompt_in_summary() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)

    with SessionLocal() as db:
        conversation = ChatRepository(db).create_conversation(user_id=user_id)
        ChatRepository(db).create_message(conversation.id, "user", "Question sensible contextual")
        response = GuidanceService.request_contextual_guidance(
            db=db,
            user_id=user_id,
            situation="Situation sensible",
            objective="Objectif sensible",
            llm_client=EchoPromptClient(),
        )
        db.commit()

    assert "[guidance_prompt_version:" not in response.summary
    assert "Recent context:" not in response.summary
    assert "semaine" not in response.summary.lower()


def test_request_contextual_guidance_invalid_context_rejected() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _seed_birth_profile(user_id)

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as error:
            GuidanceService.request_contextual_guidance(
                db=db,
                user_id=user_id,
                situation="   ",
                objective="   ",
                llm_client=RecordingClient(),
            )
    assert error.value.code == "invalid_guidance_context"


def test_request_contextual_guidance_missing_birth_profile() -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with SessionLocal() as db:
        with pytest.raises(GuidanceServiceError) as error:
            GuidanceService.request_contextual_guidance(
                db=db,
                user_id=user_id,
                situation="Situation",
                objective="Objectif",
                llm_client=RecordingClient(),
            )
    assert error.value.code == "missing_birth_profile"


def test_request_contextual_guidance_rejects_unknown_or_foreign_conversation_id() -> None:
    _cleanup_tables()
    owner_user_id = _create_user_id()
    _seed_birth_profile(owner_user_id)
    with SessionLocal() as db:
        foreign_user = AuthService.register(
            db,
            email="guidance-context-foreign-user@example.com",
            password="strong-pass-123",
        ).user
        db.commit()
        foreign_user_id = foreign_user.id
    _seed_birth_profile(foreign_user_id)

    with SessionLocal() as db:
        owner_conversation = ChatRepository(db).create_conversation(user_id=owner_user_id)
        ChatRepository(db).create_message(owner_conversation.id, "user", "Thread owner contextual")
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
                llm_client=RecordingClient(),
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
                llm_client=RecordingClient(),
            )
    assert forbidden_error.value.code == "conversation_forbidden"
