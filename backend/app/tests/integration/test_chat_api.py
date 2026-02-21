from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import settings
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
from app.infra.db.models.feature_flag import FeatureFlagModel
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
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.chat_guidance_service import ChatGuidanceServiceError

client = TestClient(app)


def _cleanup_tables() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChatMessageModel,
            ChatConversationModel,
            FeatureFlagModel,
            ChartResultModel,
            UserDailyQuotaUsageModel,
            PaymentAttemptModel,
            UserSubscriptionModel,
            BillingPlanModel,
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
        json={"email": "chat-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


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


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _enable_module_for_user(
    *,
    module: str,
    ops_token: str,
    user_id: int,
    enabled: bool = True,
) -> None:
    flag_key = f"{module}_enabled"
    response = client.put(
        f"/v1/ops/feature-flags/{flag_key}",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "enabled": enabled,
            "target_roles": ["user"],
            "target_user_ids": [user_id],
        },
    )
    assert response.status_code == 200


def test_send_chat_message_requires_token() -> None:
    _cleanup_tables()
    response = client.post("/v1/chat/messages", json={"message": "Bonjour"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_send_chat_message_success() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-success-1")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Quelle est mon energie du jour ?"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"] > 0
    assert payload["user_message"]["role"] == "user"
    assert payload["assistant_message"]["role"] == "assistant"
    assert payload["fallback_used"] is False
    assert payload["recovery"]["recovery_strategy"] == "none"
    assert "context" in payload


def test_send_chat_message_returns_429_when_daily_quota_is_reached() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-quota-1")
    headers = {"Authorization": f"Bearer {access_token}"}
    for attempt in range(5):
        response = client.post(
            "/v1/chat/messages",
            headers=headers,
            json={"message": f"Question quota {attempt}"},
        )
        assert response.status_code == 200

    blocked = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Question depassement quota"},
    )
    assert blocked.status_code == 429
    payload = blocked.json()["error"]
    assert payload["code"] == "quota_exceeded"
    assert payload["details"]["remaining"] == "0"
    assert payload["details"]["limit"] == "5"


def test_chat_message_consumption_is_reflected_in_billing_quota_status() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-quota-progress-1")
    headers = {"Authorization": f"Bearer {access_token}"}

    first_message = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Question progression 1"},
    )
    assert first_message.status_code == 200
    first_quota = client.get("/v1/billing/quota", headers=headers)
    assert first_quota.status_code == 200
    assert first_quota.json()["data"]["consumed"] == 1
    assert first_quota.json()["data"]["remaining"] == 4

    second_message = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Question progression 2"},
    )
    assert second_message.status_code == 200
    second_quota = client.get("/v1/billing/quota", headers=headers)
    assert second_quota.status_code == 200
    assert second_quota.json()["data"]["consumed"] == 2
    assert second_quota.json()["data"]["remaining"] == 3


def test_chat_enforcement_uses_updated_limit_after_plan_change() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    _activate_entry_plan(access_token, "chat-checkout-plan-change-1")

    plan_change = client.post(
        "/v1/billing/plan-change",
        headers=headers,
        json={
            "target_plan_code": "premium-unlimited",
            "idempotency_key": "chat-plan-change-1",
        },
    )
    assert plan_change.status_code == 200
    assert plan_change.json()["data"]["subscription"]["plan"]["code"] == "premium-unlimited"

    for attempt in range(6):
        response = client.post(
            "/v1/chat/messages",
            headers=headers,
            json={"message": f"Question premium {attempt}"},
        )
        assert response.status_code == 200

    quota = client.get("/v1/billing/quota", headers=headers)
    assert quota.status_code == 200
    assert quota.json()["data"]["limit"] == 1000
    assert quota.json()["data"]["consumed"] == 6
    assert quota.json()["data"]["remaining"] == 994


def test_send_chat_message_second_turn_uses_first_turn_context() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-context-1")

    first = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Premiere question contexte"},
    )
    assert first.status_code == 200
    conversation_id = first.json()["data"]["conversation_id"]

    second = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Deuxieme question contexte"},
    )
    assert second.status_code == 200
    payload = second.json()["data"]
    assert payload["conversation_id"] == conversation_id
    assert "Premiere question contexte" in payload["assistant_message"]["content"]
    assert "Deuxieme question contexte" in payload["assistant_message"]["content"]
    assert payload["context"]["message_count"] >= 3


def test_send_chat_message_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token("chat-support@example.com", "support")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {support_access_token}"},
        json={"message": "Question support"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_send_chat_message_invalid_input_returns_422() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-invalid-input-1")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "   "},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_chat_input"


def test_send_chat_message_invalid_payload_uses_standard_error_envelope() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-invalid-payload-1")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json=["not-an-object"],
    )
    assert response.status_code == 422
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == "invalid_chat_request"


def test_send_chat_message_timeout_returns_503(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-timeout-1")

    def _raise_timeout(*args: object, **kwargs: object) -> object:
        raise ChatGuidanceServiceError(
            code="llm_timeout",
            message="llm provider timeout",
            details={"retryable": "true", "action": "retry_message"},
        )

    monkeypatch.setattr("app.api.v1.routers.chat.ChatGuidanceService.send_message", _raise_timeout)
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_timeout"


def test_send_chat_message_unavailable_returns_503(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-unavailable-1")

    def _raise_unavailable(*args: object, **kwargs: object) -> object:
        raise ChatGuidanceServiceError(
            code="llm_unavailable",
            message="llm provider is unavailable",
            details={"retryable": "true", "action": "retry_message"},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.chat.ChatGuidanceService.send_message",
        _raise_unavailable,
    )
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_unavailable"


def test_send_chat_message_invalid_context_config_returns_422(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-invalid-context-1")
    monkeypatch.setattr(settings, "chat_context_window_messages", 0)

    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_chat_context_config"


def test_list_chat_conversations_returns_user_history_sorted() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-history-1")
    first = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Conversation one"},
    )
    assert first.status_code == 200
    first_id = first.json()["data"]["conversation_id"]

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        second_conversation = ChatRepository(db).create_conversation(user.id)
        ChatRepository(db).create_message(
            conversation_id=second_conversation.id,
            role="user",
            content="Conversation two",
        )
        db.commit()
        second_id = second_conversation.id

    response = client.get(
        "/v1/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] >= 2
    ids = [item["conversation_id"] for item in payload["conversations"]]
    assert ids[0] == second_id
    assert first_id in ids
    assert payload["limit"] == 10
    assert payload["offset"] == 0


def test_list_chat_conversations_paginates_with_limit_and_offset() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-pagination-1")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        repo = ChatRepository(db)
        conversation_ids: list[int] = []
        for index in range(5):
            conversation = repo.create_conversation(user.id)
            repo.create_message(
                conversation_id=conversation.id,
                role="user",
                content=f"Conversation {index}",
            )
            conversation_ids.append(conversation.id)
        db.commit()

    response = client.get(
        "/v1/chat/conversations?limit=2&offset=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] == 5
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    returned_ids = [item["conversation_id"] for item in payload["conversations"]]
    expected_order = sorted(conversation_ids, reverse=True)
    assert returned_ids == expected_order[1:3]


def test_list_chat_conversations_uses_id_tiebreak_when_updated_at_is_equal() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-tiebreak-1")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        repo = ChatRepository(db)
        conversation_a = repo.create_conversation(user.id)
        repo.create_message(
            conversation_id=conversation_a.id,
            role="user",
            content="Conversation A",
        )
        conversation_b = repo.create_conversation(user.id)
        repo.create_message(
            conversation_id=conversation_b.id,
            role="user",
            content="Conversation B",
        )
        same_timestamp = datetime(2026, 2, 20, 10, 0, 0, tzinfo=timezone.utc)
        conversation_a.updated_at = same_timestamp
        conversation_b.updated_at = same_timestamp
        conversation_a_id = conversation_a.id
        conversation_b_id = conversation_b.id
        db.commit()

    response = client.get(
        "/v1/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    ids = [item["conversation_id"] for item in response.json()["data"]["conversations"]]
    assert ids.index(conversation_b_id) < ids.index(conversation_a_id)


def test_list_chat_conversations_pagination_pages_do_not_overlap() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-pages-1")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        repo = ChatRepository(db)
        for index in range(6):
            conversation = repo.create_conversation(user.id)
            repo.create_message(
                conversation_id=conversation.id,
                role="user",
                content=f"Conversation page {index}",
            )
        db.commit()

    first_page = client.get(
        "/v1/chat/conversations?limit=3&offset=0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_page = client.get(
        "/v1/chat/conversations?limit=3&offset=3",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert first_page.status_code == 200
    assert second_page.status_code == 200
    first_ids = {item["conversation_id"] for item in first_page.json()["data"]["conversations"]}
    second_ids = {item["conversation_id"] for item in second_page.json()["data"]["conversations"]}
    assert len(first_ids) == 3
    assert len(second_ids) == 3
    assert first_ids.isdisjoint(second_ids)


def test_list_chat_conversations_propagates_request_id() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-chat-list-1"},
    )
    assert response.status_code == 200
    assert response.json()["meta"]["request_id"] == "rid-chat-list-1"


def test_get_chat_conversation_history_returns_messages() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-history-1")
    send = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Historique test"},
    )
    assert send.status_code == 200
    conversation_id = send.json()["data"]["conversation_id"]

    response = client.get(
        f"/v1/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"] == conversation_id
    assert len(payload["messages"]) >= 2
    assert payload["messages"][0]["role"] == "user"


def test_get_chat_conversation_history_propagates_request_id() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-history-rid-1")
    send = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Historique rid"},
    )
    assert send.status_code == 200
    conversation_id = send.json()["data"]["conversation_id"]

    response = client.get(
        f"/v1/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-chat-history-1"},
    )
    assert response.status_code == 200
    assert response.json()["meta"]["request_id"] == "rid-chat-history-1"


def test_get_chat_conversation_history_forbidden_for_other_user() -> None:
    _cleanup_tables()
    first_token = _register_and_get_access_token()
    _activate_entry_plan(first_token, "chat-checkout-forbidden-history-1")
    send = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"message": "Private thread"},
    )
    assert send.status_code == 200
    conversation_id = send.json()["data"]["conversation_id"]

    second_token = _register_user_with_role_and_token("chat-second-user@example.com", "user")
    response = client.get(
        f"/v1/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "conversation_forbidden"


def test_get_chat_conversation_history_not_found() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/chat/conversations/999999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "conversation_not_found"


def test_send_chat_message_with_conversation_id_targets_selected_thread() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-conversation-target-1")

    first = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Thread A"},
    )
    assert first.status_code == 200
    conversation_a = first.json()["data"]["conversation_id"]

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        conversation_b = ChatRepository(db).create_conversation(user.id)
        ChatRepository(db).create_message(
            conversation_id=conversation_b.id,
            role="user",
            content="Thread B",
        )
        db.commit()

    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Follow-up A", "conversation_id": conversation_a},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"] == conversation_a

    history = client.get(
        f"/v1/chat/conversations/{conversation_a}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert history.status_code == 200
    contents = [message["content"] for message in history.json()["data"]["messages"]]
    assert "Thread A" in contents
    assert "Follow-up A" in contents


def test_send_chat_message_off_scope_recovery_reformulates_response(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-offscope-reformulate-1")
    calls = {"count": 0}

    def _off_scope_then_recover(*args: object, **kwargs: object) -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            return "[off_scope] incoherent"
        return "Reponse reformulee pertinente"

    monkeypatch.setattr(
        "app.services.chat_guidance_service.LLMClient.generate_reply",
        _off_scope_then_recover,
    )
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["recovery"]["off_scope_detected"] is True
    assert payload["recovery"]["recovery_applied"] is True
    assert payload["recovery"]["recovery_strategy"] == "reformulate"
    assert payload["fallback_used"] is False


def test_send_chat_message_off_scope_recovery_uses_safe_fallback(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-offscope-fallback-1")

    def _always_off_scope(*args: object, **kwargs: object) -> str:
        return "[off_scope] incoherent"

    monkeypatch.setattr(
        "app.services.chat_guidance_service.LLMClient.generate_reply",
        _always_off_scope,
    )
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["recovery"]["off_scope_detected"] is True
    assert payload["recovery"]["recovery_strategy"] == "safe_fallback"
    assert payload["fallback_used"] is True


def test_send_chat_message_requires_active_subscription() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question sans abonnement"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "no_active_subscription"


def test_chat_modules_availability_is_locked_by_default() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-modules-default-1")

    response = client.get(
        "/v1/chat/modules/availability",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    modules = {item["module"]: item for item in response.json()["data"]["modules"]}
    assert modules["tarot"]["status"] == "module-locked"
    assert modules["tarot"]["reason"] == "feature_disabled"
    assert modules["runes"]["status"] == "module-locked"
    assert modules["runes"]["reason"] == "feature_disabled"


def test_chat_module_execute_requires_flag_enabled_for_user_segment() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-modules-segment-1")
    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        user_id = user.id
    ops_token = _register_user_with_role_and_token("chat-modules-ops@example.com", "ops")

    locked = client.post(
        "/v1/chat/modules/tarot/execute",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"question": "Faut-il temporiser ?"},
    )
    assert locked.status_code == 403
    assert locked.json()["error"]["code"] == "module_locked"

    _enable_module_for_user(module="tarot", ops_token=ops_token, user_id=user_id, enabled=True)

    available = client.get(
        "/v1/chat/modules/availability",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert available.status_code == 200
    tarot = next(item for item in available.json()["data"]["modules"] if item["module"] == "tarot")
    assert tarot["status"] == "module-ready"
    assert tarot["available"] is True

    execute = client.post(
        "/v1/chat/modules/tarot/execute",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"question": "Faut-il temporiser ?", "situation": "Choix professionnel"},
    )
    assert execute.status_code == 200
    payload = execute.json()["data"]
    assert payload["module"] == "tarot"
    assert payload["status"] == "completed"
    assert "Tirage tarot" in payload["interpretation"]

    _enable_module_for_user(module="tarot", ops_token=ops_token, user_id=user_id, enabled=False)
    disabled = client.post(
        "/v1/chat/modules/tarot/execute",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"question": "Nouvelle question"},
    )
    assert disabled.status_code == 403
    assert disabled.json()["error"]["code"] == "module_locked"


def test_chat_module_execute_locked_does_not_consume_quota() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-modules-quota-locked-1")
    headers = {"Authorization": f"Bearer {access_token}"}

    before = client.get("/v1/billing/quota", headers=headers)
    assert before.status_code == 200
    consumed_before = before.json()["data"]["consumed"]

    locked = client.post(
        "/v1/chat/modules/tarot/execute",
        headers=headers,
        json={"question": "Question verrouillee"},
    )
    assert locked.status_code == 403
    assert locked.json()["error"]["code"] == "module_locked"

    after = client.get("/v1/billing/quota", headers=headers)
    assert after.status_code == 200
    consumed_after = after.json()["data"]["consumed"]
    assert consumed_after == consumed_before


def test_chat_module_execute_forbidden_conversation_returns_403() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-modules-conv-forbidden-1")
    other_user_token = _register_user_with_role_and_token("chat-modules-other@example.com", "user")
    assert other_user_token
    ops_token = _register_user_with_role_and_token("chat-modules-ops-403@example.com", "ops")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        other_user = db.scalar(
            select(UserModel).where(UserModel.email == "chat-modules-other@example.com")
        )
        assert user is not None
        assert other_user is not None
        user_id = user.id
        foreign_conversation = ChatRepository(db).create_conversation(other_user.id)
        ChatRepository(db).create_message(
            conversation_id=foreign_conversation.id,
            role="user",
            content="Conversation externe",
        )
        db.commit()
        foreign_conversation_id = foreign_conversation.id

    _enable_module_for_user(module="tarot", ops_token=ops_token, user_id=user_id, enabled=True)

    forbidden = client.post(
        "/v1/chat/modules/tarot/execute",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"question": "Question", "conversation_id": foreign_conversation_id},
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "conversation_forbidden"


def test_chat_module_user_override_takes_precedence_over_role_segment() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-modules-override-1")
    ops_token = _register_user_with_role_and_token("chat-modules-ops-override@example.com", "ops")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        user_id = user.id

    set_flag = client.put(
        "/v1/ops/feature-flags/tarot_enabled",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "enabled": True,
            "target_roles": ["ops"],
            "target_user_ids": [user_id],
        },
    )
    assert set_flag.status_code == 200

    availability = client.get(
        "/v1/chat/modules/availability",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert availability.status_code == 200
    tarot = next(
        item for item in availability.json()["data"]["modules"] if item["module"] == "tarot"
    )
    assert tarot["status"] == "module-ready"
    assert tarot["available"] is True
