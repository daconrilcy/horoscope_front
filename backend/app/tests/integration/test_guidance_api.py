from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
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
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.guidance_service import GuidanceServiceError

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChatMessageModel,
            ChatConversationModel,
            UserDailyQuotaUsageModel,
            PaymentAttemptModel,
            UserSubscriptionModel,
            BillingPlanModel,
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


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "guidance-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _seed_birth_profile(access_token: str) -> None:
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 200


def _activate_entry_plan(access_token: str, idempotency_key: str) -> None:
    checkout = client.post(
        "/v1/billing/checkout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": idempotency_key,
        },
    )
    assert checkout.status_code == 200


def test_guidance_requires_token() -> None:
    _cleanup_tables()
    response = client.post("/v1/guidance", json={"period": "daily"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_guidance_success_daily_and_weekly() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    daily = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "daily"},
    )
    assert daily.status_code == 200
    assert daily.json()["data"]["period"] == "daily"

    weekly = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "weekly"},
    )
    assert weekly.status_code == 200
    assert weekly.json()["data"]["period"] == "weekly"


def test_guidance_invalid_period_returns_422() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "monthly"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_guidance_period"


def test_guidance_missing_birth_profile_returns_404() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "daily"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "missing_birth_profile"


def test_guidance_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token(
        "guidance-support@example.com",
        "support",
    )
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {support_access_token}"},
        json={"period": "daily"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_guidance_timeout_returns_503(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()

    def _raise_timeout(*args: object, **kwargs: object) -> object:
        raise GuidanceServiceError(
            code="llm_timeout",
            message="llm provider timeout",
            details={"retryable": "true", "action": "retry_guidance"},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.guidance.GuidanceService.request_guidance",
        _raise_timeout,
    )
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "daily"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_timeout"


def test_guidance_invalid_payload_uses_standard_error_envelope() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": 123},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_guidance_request"


def test_guidance_accepts_selected_conversation_id() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)
    _activate_entry_plan(access_token, "guidance-chat-context-1")
    created = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Mon contexte cible"},
    )
    assert created.status_code == 200
    conversation_id = created.json()["data"]["conversation_id"]

    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "daily", "conversation_id": conversation_id},
    )
    assert response.status_code == 200
    assert response.json()["data"]["context_message_count"] >= 1


def test_guidance_rejects_foreign_or_unknown_conversation_id() -> None:
    _cleanup_tables()
    first_access_token = _register_and_get_access_token()
    _seed_birth_profile(first_access_token)
    _activate_entry_plan(first_access_token, "guidance-chat-context-2")
    created = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {first_access_token}"},
        json={"message": "Thread prive"},
    )
    assert created.status_code == 200
    foreign_conversation_id = created.json()["data"]["conversation_id"]

    second_access_token = _register_user_with_role_and_token(
        "guidance-second-user@example.com",
        "user",
    )
    _seed_birth_profile(second_access_token)

    forbidden = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {second_access_token}"},
        json={"period": "daily", "conversation_id": foreign_conversation_id},
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "conversation_forbidden"

    missing = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {second_access_token}"},
        json={"period": "daily", "conversation_id": 999999},
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "conversation_not_found"


def test_guidance_response_keeps_guardrailed_output_contract() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "daily"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data["summary"], str)
    assert data["summary"].strip() != ""
    assert isinstance(data["key_points"], list)
    assert len(data["key_points"]) >= 1
    assert isinstance(data["actionable_advice"], list)
    assert len(data["actionable_advice"]) >= 1
    assert "medical" in data["disclaimer"]
    assert "legal" in data["disclaimer"]
    assert "financier" in data["disclaimer"]


def test_guidance_response_never_exposes_internal_prompt_on_provider_echo(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    def _echo_prompt(*args: object, **kwargs: object) -> str:
        return (
            "Guidance astrologique: [guidance_prompt_version:guidance-v1]\n"
            "Recent context:\nuser: donnee sensible"
        )

    monkeypatch.setattr(
        "app.services.guidance_service.LLMClient.generate_reply",
        _echo_prompt,
    )
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "weekly"},
    )
    assert response.status_code == 200
    summary = response.json()["data"]["summary"]
    assert "[guidance_prompt_version:" not in summary
    assert "Recent context:" not in summary


def test_guidance_applies_recovery_metadata_when_off_scope_detected(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)
    calls = {"count": 0}

    def _off_scope_then_recover(*args: object, **kwargs: object) -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            return "[off_scope] incoherent"
        return "Guidance reformulee pertinente"

    monkeypatch.setattr(
        "app.services.guidance_service.LLMClient.generate_reply",
        _off_scope_then_recover,
    )
    response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"period": "daily"},
    )
    assert response.status_code == 200
    recovery = response.json()["data"]["recovery"]
    assert recovery["off_scope_detected"] is True
    assert recovery["recovery_applied"] is True
    assert recovery["recovery_strategy"] == "reformulate"


def test_contextual_guidance_success() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "situation": "Je dois choisir entre deux opportunites.",
            "objective": "Choisir sereinement.",
            "time_horizon": "3 jours",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["guidance_type"] == "contextual"
    assert data["situation"] == "Je dois choisir entre deux opportunites."
    assert data["objective"] == "Choisir sereinement."
    assert "summary" in data


def test_contextual_guidance_blank_time_horizon_returns_null() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "situation": "Je dois choisir entre deux opportunites.",
            "objective": "Choisir sereinement.",
            "time_horizon": "   ",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["time_horizon"] is None


def test_contextual_guidance_invalid_context_returns_422() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"situation": "   ", "objective": "   "},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_guidance_context"


def test_contextual_guidance_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token(
        "guidance-context-support@example.com",
        "support",
    )
    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {support_access_token}"},
        json={"situation": "Test", "objective": "Test"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_contextual_guidance_missing_birth_profile_returns_404() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"situation": "Test", "objective": "Test"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "missing_birth_profile"


def test_contextual_guidance_invalid_payload_uses_standard_error_envelope() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"situation": 123, "objective": "ok"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_contextual_guidance_request"


def test_contextual_guidance_accepts_selected_conversation_id() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)
    _activate_entry_plan(access_token, "guidance-chat-context-3")
    created = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Contexte cible contextual"},
    )
    assert created.status_code == 200
    conversation_id = created.json()["data"]["conversation_id"]

    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "situation": "Je dois choisir entre deux opportunites.",
            "objective": "Choisir sereinement.",
            "conversation_id": conversation_id,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["context_message_count"] >= 1


def test_contextual_guidance_rejects_foreign_or_unknown_conversation_id() -> None:
    _cleanup_tables()
    first_access_token = _register_and_get_access_token()
    _seed_birth_profile(first_access_token)
    _activate_entry_plan(first_access_token, "guidance-chat-context-4")
    created = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {first_access_token}"},
        json={"message": "Thread prive contextual"},
    )
    assert created.status_code == 200
    foreign_conversation_id = created.json()["data"]["conversation_id"]

    second_access_token = _register_user_with_role_and_token(
        "guidance-context-second-user@example.com",
        "user",
    )
    _seed_birth_profile(second_access_token)

    forbidden = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {second_access_token}"},
        json={
            "situation": "Situation",
            "objective": "Objectif",
            "conversation_id": foreign_conversation_id,
        },
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "conversation_forbidden"

    missing = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {second_access_token}"},
        json={
            "situation": "Situation",
            "objective": "Objectif",
            "conversation_id": 999999,
        },
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "conversation_not_found"


def test_contextual_guidance_uses_safe_fallback_metadata_when_recovery_fails(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _seed_birth_profile(access_token)

    def _always_off_scope(*args: object, **kwargs: object) -> str:
        return "[off_scope] incoherent"

    monkeypatch.setattr(
        "app.services.guidance_service.LLMClient.generate_reply",
        _always_off_scope,
    )
    response = client.post(
        "/v1/guidance/contextual",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"situation": "Situation", "objective": "Objectif"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["fallback_used"] is True
    assert data["recovery"]["off_scope_detected"] is True
    assert data["recovery"]["recovery_applied"] is True
    assert data["recovery"]["recovery_strategy"] == "safe_fallback"
