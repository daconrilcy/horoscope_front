from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class BaseSafeAuditDetails(BaseModel):
    """Base class for all safe audit detail DTOs."""

    model_config = ConfigDict(extra="forbid")  # AC8: Force bounded structure


class LlmCallAuditDetails(BaseSafeAuditDetails):
    """Safe structure for LLM call related events."""

    request_id: str
    log_id: Optional[str] = None
    prompt_version_id: Optional[str] = None
    feature: Optional[str] = None
    subfeature: Optional[str] = None
    status: str
    reason: Optional[str] = None


class LlmReplayAuditDetails(BaseSafeAuditDetails):
    """Safe structure for LLM replay events."""

    original_request_id: str
    replay_request_id: str
    log_id: str
    status: str
    diff_summary: Optional[Dict[str, Any]] = None


class AdminActionAuditDetails(BaseSafeAuditDetails):
    """Safe structure for generic admin actions."""

    action_type: str
    target_id: Optional[str] = None
    change_summary: Optional[str] = None


class NatalInterpretationAuditDetails(BaseSafeAuditDetails):
    """Safe structure for natal interpretation events."""

    target_interpretation_id: int
    chart_id: int
    level: str
    persona_id: Optional[str] = None
    created_at: str
    deleted_at: Optional[str] = None


class LlmPromptAuditDetails(BaseSafeAuditDetails):
    """Safe structure for LLM prompt management events."""

    use_case_key: str
    from_version: Optional[str] = None
    to_version: str
    action: Optional[str] = None


class GenericSafeAuditDetails(BaseSafeAuditDetails):
    """
    Generic bounded structure for non-specific events.
    M4 Finding Fix: Bounded structure for any audit event.
    """

    model_config = ConfigDict(extra="allow")  # Explicitly allow for generic usage
    message: Optional[str] = None


def to_safe_details(details: Any) -> Dict[str, Any]:
    """
    Ensures that audit details are converted to a safe, bounded dictionary.
    AC8: Force bounded structure.
    """
    if isinstance(details, BaseSafeAuditDetails):
        return details.model_dump(exclude_none=True)

    if isinstance(details, dict):
        # M4 Finding Fix: Wrap raw dicts in a generic DTO to ensure bounded structure
        # according to the central policy even if the call site is not yet fully migrated.
        return GenericSafeAuditDetails(**details).model_dump(exclude_none=True)

    return {"raw_value": str(details)}
