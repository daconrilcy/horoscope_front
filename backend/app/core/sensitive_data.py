from __future__ import annotations

import enum
from typing import Any, Dict, Set


class DataCategory(str, enum.Enum):
    SECRET_CREDENTIAL = "secret_credential"
    DIRECT_IDENTIFIER = "direct_identifier"
    TECHNICAL_CORRELATION_IDENTIFIER = "technical_correlation_identifier"
    CORRELABLE_BUSINESS_IDENTIFIER = "correlable_business_identifier"
    USER_AUTHORED_CONTENT = "user_authored_content"
    DERIVED_SENSITIVE_DOMAIN_DATA = "derived_sensitive_domain_data"
    OPERATIONAL_METADATA = "operational_metadata"


class Sink(str, enum.Enum):
    STRUCTURED_LOGS = "structured_logs"
    OBS_SNAPSHOT = "obs_snapshot"
    LLM_CALL_LOGS = "llm_call_logs"
    LLM_REPLAY_SNAPSHOTS = "llm_replay_snapshots"
    ADMIN_API = "admin_api"
    AUDIT_TRAIL = "audit_trail"


class PolicyAction(str, enum.Enum):
    FORBIDDEN = "forbidden"
    REDACED = "redacted"
    MASKED = "masked"
    HASHED = "hashed"
    ENCRYPTED_ISOLATED = "encrypted_isolated"
    ALLOWED = "allowed"


# AC3: Positive allowlist of operational fields
# These fields are considered OPERATIONAL_METADATA and are allowed in most sinks.
OPERATIONAL_FIELDS: Set[str] = {
    "use_case",
    "use_case_key",
    "from_version",
    "to_version",
    "target_version_id",
    "feature",
    "subfeature",
    "plan",
    "template_source",
    "provider",
    "model",
    "latency_ms",
    "tokens_in",
    "tokens_out",
    "cost_usd",
    "cost_usd_estimated",
    "validation_status",
    "repair_attempted",
    "fallback_triggered",
    "environment",
    "evidence_warnings_count",
    "pipeline_kind",
    "execution_path_kind",
    "fallback_kind",
    "requested_provider",
    "resolved_provider",
    "executed_provider",
    "context_compensation_status",
    "max_output_tokens_source",
    "max_output_tokens_final",
    "max_output_tokens",
    "timeout_seconds",
    "executed_provider_mode",
    "attempt_count",
    "provider_error_code",
    "breaker_state",
    "breaker_scope",
    "active_snapshot_id",
    "active_snapshot_version",
    "manifest_entry_id",
    "timestamp",
    "expires_at",
    "prompt_version_id",
    "persona_id",
    "assembly_id",
    "status",
    "attempt",
    "error_code",
    "input_hash",  # SHA-256 hash is allowed for correlation (AC12)
    "locale",
    "export_type",
    "filters",
    "period",
    "start",
    "end",
    "content_key",
    "template_code",
    "flag_code",
    "rule_code",
    "persona_name",
    "gesture_type",
    "reason",
    "account_id",
    "failure_rate",
    "errors",
    "cached",
    "action",
    "before",
    "after",
    "commercial_gestures_count",
    "record_count",
    "variant_id",
    "event_name",
    "conversion_status",
    "user_segment",
    "plan_code",
    "event_version",
    "revenue_cents",
}

# AC2: Matrix sink -> treatment
SINK_POLICY: Dict[Sink, Dict[DataCategory, PolicyAction]] = {
    Sink.STRUCTURED_LOGS: {
        DataCategory.SECRET_CREDENTIAL: PolicyAction.FORBIDDEN,
        DataCategory.DIRECT_IDENTIFIER: PolicyAction.REDACED,
        DataCategory.TECHNICAL_CORRELATION_IDENTIFIER: PolicyAction.ALLOWED,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER: PolicyAction.MASKED,
        DataCategory.USER_AUTHORED_CONTENT: PolicyAction.REDACED,
        DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA: PolicyAction.REDACED,
        DataCategory.OPERATIONAL_METADATA: PolicyAction.ALLOWED,
    },
    Sink.OBS_SNAPSHOT: {
        DataCategory.SECRET_CREDENTIAL: PolicyAction.FORBIDDEN,
        DataCategory.DIRECT_IDENTIFIER: PolicyAction.FORBIDDEN,
        DataCategory.TECHNICAL_CORRELATION_IDENTIFIER: PolicyAction.ALLOWED,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER: PolicyAction.FORBIDDEN,
        DataCategory.USER_AUTHORED_CONTENT: PolicyAction.FORBIDDEN,
        DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA: PolicyAction.FORBIDDEN,
        DataCategory.OPERATIONAL_METADATA: PolicyAction.ALLOWED,
    },
    Sink.LLM_CALL_LOGS: {
        DataCategory.SECRET_CREDENTIAL: PolicyAction.FORBIDDEN,
        DataCategory.DIRECT_IDENTIFIER: PolicyAction.FORBIDDEN,
        DataCategory.TECHNICAL_CORRELATION_IDENTIFIER: PolicyAction.ALLOWED,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER: PolicyAction.HASHED,
        DataCategory.USER_AUTHORED_CONTENT: PolicyAction.HASHED,
        DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA: PolicyAction.HASHED,
        DataCategory.OPERATIONAL_METADATA: PolicyAction.ALLOWED,
    },
    Sink.LLM_REPLAY_SNAPSHOTS: {
        DataCategory.SECRET_CREDENTIAL: PolicyAction.FORBIDDEN,
        DataCategory.DIRECT_IDENTIFIER: PolicyAction.ENCRYPTED_ISOLATED,
        DataCategory.TECHNICAL_CORRELATION_IDENTIFIER: PolicyAction.ALLOWED,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER: PolicyAction.ENCRYPTED_ISOLATED,
        DataCategory.USER_AUTHORED_CONTENT: PolicyAction.ENCRYPTED_ISOLATED,
        DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA: PolicyAction.ENCRYPTED_ISOLATED,
        DataCategory.OPERATIONAL_METADATA: PolicyAction.ALLOWED,
    },
    Sink.ADMIN_API: {
        DataCategory.SECRET_CREDENTIAL: PolicyAction.FORBIDDEN,
        DataCategory.DIRECT_IDENTIFIER: PolicyAction.MASKED,
        DataCategory.TECHNICAL_CORRELATION_IDENTIFIER: PolicyAction.ALLOWED,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER: PolicyAction.MASKED,
        DataCategory.USER_AUTHORED_CONTENT: PolicyAction.REDACED,
        DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA: PolicyAction.REDACED,
        DataCategory.OPERATIONAL_METADATA: PolicyAction.ALLOWED,
    },
    Sink.AUDIT_TRAIL: {
        DataCategory.SECRET_CREDENTIAL: PolicyAction.FORBIDDEN,
        DataCategory.DIRECT_IDENTIFIER: PolicyAction.MASKED,
        DataCategory.TECHNICAL_CORRELATION_IDENTIFIER: PolicyAction.ALLOWED,
        DataCategory.CORRELABLE_BUSINESS_IDENTIFIER: PolicyAction.MASKED,  # Medium Finding fix
        DataCategory.USER_AUTHORED_CONTENT: PolicyAction.FORBIDDEN,
        DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA: PolicyAction.FORBIDDEN,
        DataCategory.OPERATIONAL_METADATA: PolicyAction.ALLOWED,
    },
}

# Mapping of field names to categories
FIELD_CLASSIFICATION: Dict[str, DataCategory] = {
    "password": DataCategory.SECRET_CREDENTIAL,
    "api_key": DataCategory.SECRET_CREDENTIAL,
    "apikey": DataCategory.SECRET_CREDENTIAL,
    "secret": DataCategory.SECRET_CREDENTIAL,
    "token": DataCategory.SECRET_CREDENTIAL,
    "authorization": DataCategory.SECRET_CREDENTIAL,
    "credentials": DataCategory.SECRET_CREDENTIAL,
    "email": DataCategory.DIRECT_IDENTIFIER,
    "phone": DataCategory.DIRECT_IDENTIFIER,
    "address": DataCategory.DIRECT_IDENTIFIER,
    "request_id": DataCategory.TECHNICAL_CORRELATION_IDENTIFIER,
    "trace_id": DataCategory.TECHNICAL_CORRELATION_IDENTIFIER,
    "user_id": DataCategory.CORRELABLE_BUSINESS_IDENTIFIER,
    "target_id": DataCategory.CORRELABLE_BUSINESS_IDENTIFIER,
    "profile_id": DataCategory.CORRELABLE_BUSINESS_IDENTIFIER,
    "content": DataCategory.USER_AUTHORED_CONTENT,
    "message": DataCategory.USER_AUTHORED_CONTENT,
    "messages": DataCategory.USER_AUTHORED_CONTENT,
    "question": DataCategory.USER_AUTHORED_CONTENT,
    "prompt": DataCategory.USER_AUTHORED_CONTENT,
    "raw_output": DataCategory.USER_AUTHORED_CONTENT,
    "structured_output": DataCategory.USER_AUTHORED_CONTENT,
    "birth_data": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "birth_date": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "birthdate": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "birth_time": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "birth_place": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "natal_data": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "natal_chart_summary": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
    "chart_json": DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA,
}


def classify_field(field_name: str) -> DataCategory:
    """Classifies a field name into a DataCategory."""
    # Priority 1: Check explicit classification mapping
    field_lower = field_name.lower()
    if field_lower in FIELD_CLASSIFICATION:
        return FIELD_CLASSIFICATION[field_lower]

    # Priority 2: Check operational allowlist
    if field_name in OPERATIONAL_FIELDS:
        return DataCategory.OPERATIONAL_METADATA

    # Heuristics for unknown fields
    if any(s in field_lower for s in ("password", "secret", "token", "key", "credential")):
        return DataCategory.SECRET_CREDENTIAL

    if any(s in field_lower for s in ("id", "user", "target", "profile", "account")):
        return DataCategory.CORRELABLE_BUSINESS_IDENTIFIER

    if any(s in field_lower for s in ("content", "text", "msg", "prompt", "output", "input")):
        return DataCategory.USER_AUTHORED_CONTENT

    if any(s in field_lower for s in ("birth", "natal", "chart", "astro")):
        return DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA

    # Default to USER_AUTHORED_CONTENT for safety if it looks like text, or DIRECT_IDENTIFIER
    return DataCategory.USER_AUTHORED_CONTENT


def get_policy_action(sink: Sink, category: DataCategory) -> PolicyAction:
    """Returns the policy action for a given sink and category."""
    return SINK_POLICY.get(sink, {}).get(category, PolicyAction.FORBIDDEN)


def redact_value(value: Any, action: PolicyAction) -> Any:
    """Applies the policy action to a value."""
    if value is None:
        return None

    if action == PolicyAction.FORBIDDEN:
        return None

    if action == PolicyAction.REDACED:
        return "[REDACTED]"

    if action == PolicyAction.MASKED:
        if isinstance(value, str):
            if "@" in value:  # Email-like
                parts = value.split("@")
                return f"{parts[0][0]}...@{parts[1]}" if len(parts[0]) > 0 else "[MASKED]"
            return f"{value[:2]}...{value[-2:]}" if len(value) > 4 else "***"
        return "[MASKED]"

    if action == PolicyAction.HASHED:
        import hashlib

        return hashlib.sha256(str(value).encode()).hexdigest()[:16] + "..."

    return value


def sanitize_payload(payload: Dict[str, Any], sink: Sink) -> Dict[str, Any]:
    """Sanitizes a payload dictionary for a specific sink."""
    result = {}
    for key, value in payload.items():
        category = classify_field(key)
        action = get_policy_action(sink, category)

        if action == PolicyAction.ALLOWED or action == PolicyAction.ENCRYPTED_ISOLATED:
            if isinstance(value, dict):
                result[key] = sanitize_payload(value, sink)
            elif isinstance(value, list):
                result[key] = [
                    sanitize_payload(v, sink) if isinstance(v, dict) else v for v in value
                ]
            else:
                result[key] = value
        elif action == PolicyAction.FORBIDDEN:
            continue
        else:
            result[key] = redact_value(value, action)

    return result
