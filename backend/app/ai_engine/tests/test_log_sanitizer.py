"""Tests for the log sanitizer."""

from __future__ import annotations

from app.ai_engine.services.log_sanitizer import (
    REDACTED,
    sanitize_for_logging,
    sanitize_messages_for_logging,
    sanitize_request_for_logging,
)


class TestSanitizeForLogging:
    """Tests for sanitize_for_logging function."""

    def test_redacts_birth_data(self) -> None:
        """Birth data should be fully redacted."""
        payload = {
            "birth_data": {
                "date": "1990-01-15",
                "time": "14:30",
                "place": "Paris, France",
            }
        }
        result = sanitize_for_logging(payload)
        assert result["birth_data"] == REDACTED

    def test_redacts_password(self) -> None:
        """Password should be fully redacted."""
        payload = {"password": "secret123", "user_password": "also_secret"}
        result = sanitize_for_logging(payload)
        assert result["password"] == REDACTED
        assert result["user_password"] == REDACTED

    def test_redacts_api_key(self) -> None:
        """API keys should be fully redacted."""
        payload = {"api_key": "sk-abc123", "openai_api_key": "sk-xyz"}
        result = sanitize_for_logging(payload)
        assert result["api_key"] == REDACTED
        assert result["openai_api_key"] == REDACTED

    def test_redacts_token(self) -> None:
        """Tokens should be fully redacted."""
        payload = {"token": "jwt_token", "auth_token": "bearer_token"}
        result = sanitize_for_logging(payload)
        assert result["token"] == REDACTED
        assert result["auth_token"] == REDACTED

    def test_redacts_natal_chart_summary(self) -> None:
        """Natal chart summary should be fully redacted."""
        payload = {"natal_chart_summary": "Sun in Aries, Moon in Taurus..."}
        result = sanitize_for_logging(payload)
        assert result["natal_chart_summary"] == REDACTED

    def test_redacts_message_content(self) -> None:
        """Message content should be fully redacted."""
        payload = {"content": "This is a private message"}
        result = sanitize_for_logging(payload)
        assert result["content"] == REDACTED

    def test_truncates_question(self) -> None:
        """Question should be truncated but not fully redacted."""
        long_question = "What is my career outlook? " * 20
        payload = {"question": long_question}
        result = sanitize_for_logging(payload)
        assert result["question"] != REDACTED
        assert "[truncated" in result["question"]
        assert len(result["question"]) < len(long_question)

    def test_preserves_safe_fields(self) -> None:
        """Safe fields should be preserved as-is."""
        payload = {
            "use_case": "chat",
            "locale": "fr-FR",
            "request_id": "req_123",
            "trace_id": "trace_456",
        }
        result = sanitize_for_logging(payload)
        assert result["use_case"] == "chat"
        assert result["locale"] == "fr-FR"
        assert result["request_id"] == "req_123"

    def test_handles_nested_dicts(self) -> None:
        """Nested dictionaries should be recursively sanitized."""
        payload = {
            "context": {
                "birth_data": {"date": "1990-01-15"},
                "user_preferences": {"theme": "dark"},
            }
        }
        result = sanitize_for_logging(payload)
        assert result["context"]["birth_data"] == REDACTED
        assert result["context"]["user_preferences"]["theme"] == "dark"

    def test_handles_lists(self) -> None:
        """Lists should have their items sanitized."""
        payload = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ]
        }
        result = sanitize_for_logging(payload)
        assert result["messages"] == REDACTED

    def test_handles_none_values(self) -> None:
        """None values should be preserved."""
        payload = {"birth_data": None, "use_case": "chat"}
        result = sanitize_for_logging(payload)
        assert result["birth_data"] is None
        assert result["use_case"] == "chat"

    def test_redacts_email_in_text(self) -> None:
        """Email addresses in text should be redacted."""
        payload = {"question": "Contact me at user@example.com please"}
        result = sanitize_for_logging(payload)
        assert "user@example.com" not in result["question"]
        assert "[EMAIL_REDACTED]" in result["question"]

    def test_handles_empty_dict(self) -> None:
        """Empty dict should return empty dict."""
        result = sanitize_for_logging({})
        assert result == {}


class TestSanitizeRequestForLogging:
    """Tests for sanitize_request_for_logging function."""

    def test_basic_fields_included(self) -> None:
        """Basic fields should be included in result."""
        result = sanitize_request_for_logging(
            use_case="chat",
            user_id=123,
            request_id="req_abc",
            trace_id="trace_xyz",
        )
        assert result["use_case"] == "chat"
        assert result["user_id"] == "123"
        assert result["request_id"] == "req_abc"
        assert result["trace_id"] == "trace_xyz"

    def test_input_data_sanitized(self) -> None:
        """Input data should be sanitized."""
        result = sanitize_request_for_logging(
            use_case="chat",
            user_id=123,
            request_id="req_abc",
            trace_id="trace_xyz",
            input_data={"question": "What about my birth chart?"},
        )
        assert "input" in result
        assert "question" in result["input"]

    def test_context_sanitized(self) -> None:
        """Context should be sanitized."""
        result = sanitize_request_for_logging(
            use_case="chat",
            user_id=123,
            request_id="req_abc",
            trace_id="trace_xyz",
            context={"birth_data": {"date": "1990-01-15"}},
        )
        assert "context" in result
        assert result["context"]["birth_data"] == REDACTED

    def test_extra_fields_included(self) -> None:
        """Extra fields should be included."""
        result = sanitize_request_for_logging(
            use_case="chat",
            user_id=123,
            request_id="req_abc",
            trace_id="trace_xyz",
            latency_ms=150,
            cached=True,
        )
        assert result["latency_ms"] == 150
        assert result["cached"] is True


class TestSanitizeMessagesForLogging:
    """Tests for sanitize_messages_for_logging function."""

    def test_preserves_role(self) -> None:
        """Message role should be preserved."""
        messages = [
            {"role": "system", "content": "You are an astrologer"},
            {"role": "user", "content": "Read my chart"},
        ]
        result = sanitize_messages_for_logging(messages)
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"

    def test_masks_content(self) -> None:
        """Message content should be masked."""
        messages = [{"role": "user", "content": "This is sensitive"}]
        result = sanitize_messages_for_logging(messages)
        assert "content" not in result[0] or result[0].get("content") == REDACTED
        assert "content_length" in result[0]
        assert "content_preview" in result[0]

    def test_includes_content_length(self) -> None:
        """Content length should be included for debugging."""
        content = "Hello world"
        messages = [{"role": "user", "content": content}]
        result = sanitize_messages_for_logging(messages)
        assert result[0]["content_length"] == len(content)

    def test_handles_empty_messages(self) -> None:
        """Empty message list should return empty list."""
        result = sanitize_messages_for_logging([])
        assert result == []

    def test_handles_missing_content(self) -> None:
        """Messages without content should be handled."""
        messages = [{"role": "user"}]
        result = sanitize_messages_for_logging(messages)
        assert result[0]["role"] == "user"
        assert result[0]["content_length"] == 0
