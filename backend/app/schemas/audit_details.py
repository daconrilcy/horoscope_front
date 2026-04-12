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


def to_safe_details(details: Any) -> Dict[str, Any]:
    """
    Ensures that audit details are converted to a safe, bounded dictionary.
    If 'details' is already a Safe DTO, it returns its dict representation.
    """
    if isinstance(details, BaseSafeAuditDetails):
        return details.model_dump(exclude_none=True)
    if isinstance(details, dict):
        return details
    return {"raw_value": str(details)}
