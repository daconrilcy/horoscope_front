from __future__ import annotations

import logging
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.ai_engine.services.log_sanitizer import SensitiveDataFilter
from app.core.sensitive_data import (
    DataCategory,
    PolicyAction,
    Sink,
    classify_field,
    get_policy_action,
    redact_value,
    sanitize_payload,
)
from app.infra.db.base import Base
from app.services.audit_service import AuditEventCreatePayload, AuditService


def test_classify_field():
    assert classify_field("use_case") == DataCategory.OPERATIONAL_METADATA
    assert classify_field("password") == DataCategory.SECRET_CREDENTIAL
    assert classify_field("email") == DataCategory.DIRECT_IDENTIFIER
    assert classify_field("birth_date") == DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA
    assert classify_field("content") == DataCategory.USER_AUTHORED_CONTENT
    assert classify_field("user_id") == DataCategory.CORRELABLE_BUSINESS_IDENTIFIER
    assert classify_field("request_id") == DataCategory.OPERATIONAL_METADATA
    assert classify_field("unknown_field") == DataCategory.USER_AUTHORED_CONTENT  # Default


def test_get_policy_action():
    assert (
        get_policy_action(Sink.STRUCTURED_LOGS, DataCategory.SECRET_CREDENTIAL)
        == PolicyAction.FORBIDDEN
    )
    assert (
        get_policy_action(Sink.LLM_CALL_LOGS, DataCategory.USER_AUTHORED_CONTENT)
        == PolicyAction.HASHED
    )
    assert get_policy_action(Sink.ADMIN_API, DataCategory.DIRECT_IDENTIFIER) == PolicyAction.MASKED
    assert (
        get_policy_action(Sink.AUDIT_TRAIL, DataCategory.USER_AUTHORED_CONTENT)
        == PolicyAction.FORBIDDEN
    )


def test_redact_value():
    assert redact_value("secret123", PolicyAction.FORBIDDEN) is None
    assert redact_value("my message", PolicyAction.REDACED) == "[REDACTED]"
    assert redact_value("test@example.com", PolicyAction.MASKED) == "t...@example.com"
    assert redact_value("123456", PolicyAction.MASKED) == "12...56"


def test_sanitize_payload_structured_logs():
    payload = {
        "use_case": "chat",
        "password": "password123",
        "email": "user@example.com",
        "content": "Hello world",
        "user_id": 123,
    }
    sanitized = sanitize_payload(payload, Sink.STRUCTURED_LOGS)

    assert sanitized["use_case"] == "chat"
    assert "password" not in sanitized
    assert sanitized["email"] == "[REDACTED]"
    assert sanitized["content"] == "[REDACTED]"
    assert sanitized["user_id"] == "[MASKED]"


def test_sanitize_payload_llm_call_logs():
    payload = {
        "use_case": "chat",
        "content": "Sensitive content",
        "user_id": 456,
    }
    sanitized = sanitize_payload(payload, Sink.LLM_CALL_LOGS)

    assert sanitized["use_case"] == "chat"
    assert len(sanitized["content"]) > 10  # Hashed
    assert len(sanitized["user_id"]) > 10  # Hashed


def test_logging_filter(caplog):
    logger = logging.getLogger("test_logger")
    logger.addFilter(SensitiveDataFilter())

    with caplog.at_level(logging.INFO):
        # Test sanitization of dict message
        logger.info({"password": "secret_pass", "use_case": "test"})

    assert "secret_pass" not in caplog.text
    # Wait, policy for SECRET_CREDENTIAL in logs is FORBIDDEN (removed)
    assert "[REDACTED]" not in caplog.text
    assert "'use_case': 'test'" in caplog.text


engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.app_env = "dev"
        yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_audit_service_sanitization(db):
    # AuditService.record_event should sanitize details
    payload = AuditEventCreatePayload(
        request_id="req-1",
        actor_user_id=1,
        actor_role="admin",
        action="test_action",
        target_type="user",
        status="success",
        details={
            "password": "should-be-gone",
            "content": "should-be-redacted",
            "use_case": "allowed",
        },
    )

    event = AuditService.record_event(db, payload=payload)

    assert "password" not in event.details
    assert "content" not in event.details
    assert event.details["use_case"] == "allowed"
