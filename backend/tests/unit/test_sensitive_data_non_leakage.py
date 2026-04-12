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
    # Fix Medium Finding: request_id should be TECHNICAL_CORRELATION_IDENTIFIER
    assert classify_field("request_id") == DataCategory.TECHNICAL_CORRELATION_IDENTIFIER
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
    # Fix Medium Finding: AUDIT_TRAIL CORRELABLE_BUSINESS_IDENTIFIER should be MASKED
    assert (
        get_policy_action(Sink.AUDIT_TRAIL, DataCategory.CORRELABLE_BUSINESS_IDENTIFIER)
        == PolicyAction.MASKED
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
    # CORRELABLE_BUSINESS_IDENTIFIER is MASKED in structured logs
    assert sanitized["user_id"] == "[MASKED]"


def test_sanitize_payload_llm_call_logs():
    payload = {
        "use_case": "chat",
        "content": "Sensitive content",
        "user_id": 456,
        "request_id": "req-123",
    }
    sanitized = sanitize_payload(payload, Sink.LLM_CALL_LOGS)

    assert sanitized["use_case"] == "chat"
    assert len(sanitized["content"]) > 10  # Hashed
    assert len(sanitized["user_id"]) > 10  # Hashed
    assert sanitized["request_id"] == "req-123"  # ALLOWED (Technical identifier)


def test_sanitize_payload_does_not_whitelist_generic_container_scalar_values():
    payload = {
        "payload": "full prompt text",
        "details": "user-authored diagnostic blob",
        "user_id": 123,
        "email": "user@example.com",
    }

    sanitized = sanitize_payload(payload, Sink.AUDIT_TRAIL)

    assert "payload" not in sanitized
    assert "details" not in sanitized
    assert sanitized["user_id"] == "[MASKED]"
    assert sanitized["email"] == "u...@example.com"


def test_logging_filter(caplog):
    logger = logging.getLogger("test_logger")
    # AC11 Terminal safety filter
    log_filter = SensitiveDataFilter()
    logger.addFilter(log_filter)

    try:
        with caplog.at_level(logging.INFO, logger="test_logger"):
            # 1. Test sanitization of dict message
            logger.info({"password": "secret_pass", "use_case": "test"})
            assert "secret_pass" not in caplog.text
            assert "'use_case': 'test'" in caplog.text

            caplog.clear()

            # 2. Test fix for High Finding: Positional arguments (tuple)
            logger.info("User login attempt for %s with password %s", "test@user.com", "secret123")
            assert "secret123" not in caplog.text
            assert "[REDACTED]" in caplog.text
            assert "test@user.com" not in caplog.text
            assert "t...@user.com" in caplog.text

            caplog.clear()

            # 3. Test fix for High Finding: 'extra' fields
            logger.info({"msg": "with_extra"}, extra={"secret_token": "hidden", "user_id": 12345})
            record = caplog.records[-1]
            assert getattr(record, "secret_token") is None
            assert getattr(record, "user_id") == "[MASKED]"
    finally:
        logger.removeFilter(log_filter)


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
    # Fix Medium Finding: Nested structure sanitization
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
            "user_id": 12345,
            "nested": {"email": "nested@leak.com", "inner": {"secret": "very-secret"}},
        },
    )

    event = AuditService.record_event(db, payload=payload)

    assert "password" not in event.details
    assert "content" not in event.details
    assert event.details["use_case"] == "allowed"
    assert event.details["user_id"] == "[MASKED]"
    assert "nested" not in event.details
