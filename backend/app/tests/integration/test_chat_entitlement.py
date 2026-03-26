from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.chat_entitlement_gate import ChatEntitlementResult
from app.services.entitlement_types import UsageState

client = TestClient(app)


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.role = "user"
    return user


@pytest.fixture(autouse=True)
def override_auth(mock_user):
    from app.api.dependencies.auth import require_authenticated_user

    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(require_authenticated_user, None)


def test_send_message_canonical_quota_ok(mock_user):
    mock_result = ChatEntitlementResult(
        path="canonical_quota",
        usage_states=[
            UsageState(
                feature_code="astrologer_chat",
                quota_key="daily",
                quota_limit=5,
                used=3,
                remaining=2,
                exhausted=False,
                period_unit="day",
                period_value=1,
                reset_mode="calendar",
                window_start=None,
                window_end=None,
            )
        ],
    )

    # Use MagicMock instead of real ChatReplyData to avoid validation errors
    mock_reply = MagicMock()
    mock_reply.model_dump.return_value = {
        "conversation_id": 1,
        "attempts": 1,
        "user_message": {
            "message_id": 1,
            "role": "user",
            "content": "Hi",
            "created_at": "2026-03-25T10:00:00Z",
        },
        "assistant_message": {
            "message_id": 2,
            "role": "assistant",
            "content": "Hello user",
            "created_at": "2026-03-25T10:00:01Z",
        },
        "fallback_used": False,
        "context": {
            "message_ids": [1],
            "message_count": 1,
            "context_characters": 2,
            "prompt_version": "v1",
        },
        "recovery": {
            "off_scope_detected": False,
            "off_scope_score": 0.0,
            "recovery_strategy": "none",
            "recovery_applied": False,
            "recovery_attempts": 0,
            "recovery_reason": None,
        },
    }

    with (
        patch(
            "app.services.chat_entitlement_gate.ChatEntitlementGate.check_and_consume",
            return_value=mock_result,
        ),
        patch(
            "app.services.chat_guidance_service.ChatGuidanceService.send_message",
            return_value=mock_reply,
        ),
        patch("app.infra.db.session.get_db_session"),
    ):
        response = client.post(
            "/v1/chat/messages", json={"message": "Hi"}, headers={"X-Request-ID": "test-req"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "quota_info" in data
    assert data["quota_info"]["remaining"] == 2
    assert data["quota_info"]["limit"] == 5


def test_send_message_canonical_unlimited_ok(mock_user):
    mock_result = ChatEntitlementResult(path="canonical_unlimited", usage_states=[])

    mock_reply = MagicMock()
    mock_reply.model_dump.return_value = {
        "conversation_id": 1,
        "attempts": 1,
        "user_message": {
            "message_id": 1,
            "role": "user",
            "content": "Hi",
            "created_at": "2026-03-25T10:00:00Z",
        },
        "assistant_message": {
            "message_id": 2,
            "role": "assistant",
            "content": "Hello unlimited user",
            "created_at": "2026-03-25T10:00:01Z",
        },
        "fallback_used": False,
        "context": {
            "message_ids": [1],
            "message_count": 1,
            "context_characters": 2,
            "prompt_version": "v1",
        },
        "recovery": {
            "off_scope_detected": False,
            "off_scope_score": 0.0,
            "recovery_strategy": "none",
            "recovery_applied": False,
            "recovery_attempts": 0,
            "recovery_reason": None,
        },
    }

    with (
        patch(
            "app.services.chat_entitlement_gate.ChatEntitlementGate.check_and_consume",
            return_value=mock_result,
        ),
        patch(
            "app.services.chat_guidance_service.ChatGuidanceService.send_message",
            return_value=mock_reply,
        ),
        patch("app.infra.db.session.get_db_session"),
    ):
        response = client.post(
            "/v1/chat/messages",
            json={"message": "Hi unlimited"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "quota_info" in data
    assert data["quota_info"]["remaining"] is None


def test_send_message_no_plan_rejected(mock_user):
    from app.services.chat_entitlement_gate import ChatAccessDeniedError

    error = ChatAccessDeniedError(reason="no_plan", billing_status="inactive", plan_code="none")

    with (
        patch(
            "app.services.chat_entitlement_gate.ChatEntitlementGate.check_and_consume",
            side_effect=error,
        ),
        patch("app.infra.db.session.get_db_session"),
    ):
        response = client.post(
            "/v1/chat/messages",
            json={"message": "Hi"},
        )

    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "chat_access_denied"
    assert data["error"]["details"]["reason"] == "no_plan"


def test_send_message_quota_exhausted_rejected(mock_user):
    from datetime import datetime

    from app.services.chat_entitlement_gate import ChatQuotaExceededError

    now = datetime.now()
    error = ChatQuotaExceededError(quota_key="daily", used=5, limit=5, window_end=now)

    with (
        patch(
            "app.services.chat_entitlement_gate.ChatEntitlementGate.check_and_consume",
            side_effect=error,
        ),
        patch("app.infra.db.session.get_db_session"),
    ):
        response = client.post(
            "/v1/chat/messages",
            json={"message": "Hi"},
        )

    assert response.status_code == 429
    data = response.json()
    assert data["error"]["code"] == "chat_quota_exceeded"
    assert data["error"]["details"]["quota_key"] == "daily"
    assert data["error"]["details"]["window_end"] == now.isoformat()


def test_send_message_quota_service_never_called(mock_user):
    """AC: 11 - Vérifier que QuotaService n'est jamais appelé."""
    mock_result = ChatEntitlementResult(path="canonical_quota", usage_states=[])

    mock_reply = MagicMock()
    mock_reply.model_dump.return_value = {
        "conversation_id": 1,
        "attempts": 1,
        "user_message": {
            "message_id": 1,
            "role": "user",
            "content": "Hi",
            "created_at": "2026-03-25T10:00:00Z",
        },
        "assistant_message": {
            "message_id": 2,
            "role": "assistant",
            "content": "Hello",
            "created_at": "2026-03-25T10:00:01Z",
        },
        "fallback_used": False,
        "context": {
            "message_ids": [1],
            "message_count": 1,
            "context_characters": 2,
            "prompt_version": "v1",
        },
        "recovery": {
            "off_scope_detected": False,
            "off_scope_score": 0.0,
            "recovery_strategy": "none",
            "recovery_applied": False,
            "recovery_attempts": 0,
            "recovery_reason": None,
        },
    }

    with (
        patch(
            "app.services.chat_entitlement_gate.ChatEntitlementGate.check_and_consume",
            return_value=mock_result,
        ),
        patch(
            "app.services.quota_service.QuotaService.consume_quota_or_raise"
        ) as mock_legacy_consume,
        patch(
            "app.services.chat_guidance_service.ChatGuidanceService.send_message",
            return_value=mock_reply,
        ),
        patch("app.infra.db.session.get_db_session"),
    ):
        client.post(
            "/v1/chat/messages",
            json={"message": "Hi"},
        )

    mock_legacy_consume.assert_not_called()
