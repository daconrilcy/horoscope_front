"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, field_validator

router = APIRouter()
logger = logging.getLogger(__name__)


def _validate_timezone_aware_timestamp(value: datetime) -> datetime:
    """Valide que les preuves d'activation portent une date absolue."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone offset")
    return value


class ReleaseSnapshotCreate(BaseModel):
    version: str = Field(..., description="Unique version identifier for the release.")
    comment: Optional[str] = Field(None, description="Optional release notes.")


class ReleaseSnapshotRead(BaseModel):
    id: uuid.UUID
    version: str
    status: str
    created_at: datetime
    created_by: str
    activated_at: Optional[datetime] = None
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ValidationReport(BaseModel):
    is_valid: bool
    errors: List[Dict[str, Any]]


class ActivationQualificationEvidence(BaseModel):
    active_snapshot_id: uuid.UUID
    active_snapshot_version: str
    manifest_entry_id: Optional[str] = None
    verdict: str
    generated_at: datetime

    @field_validator("generated_at")
    @classmethod
    def ensure_generated_at_timezone(cls, value: datetime) -> datetime:
        return _validate_timezone_aware_timestamp(value)


class ActivationGoldenEvidence(BaseModel):
    active_snapshot_id: uuid.UUID
    active_snapshot_version: str
    manifest_entry_id: Optional[str] = None
    verdict: str
    generated_at: datetime

    @field_validator("generated_at")
    @classmethod
    def ensure_generated_at_timezone(cls, value: datetime) -> datetime:
        return _validate_timezone_aware_timestamp(value)


class ActivationSmokeEvidence(BaseModel):
    status: str
    active_snapshot_id: str
    active_snapshot_version: str
    manifest_entry_id: str
    forbidden_fallback_detected: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class ActivateReleasePayload(BaseModel):
    qualification_report: ActivationQualificationEvidence
    golden_report: ActivationGoldenEvidence
    smoke_result: ActivationSmokeEvidence
    monitoring_thresholds: Dict[str, float] = Field(default_factory=dict)
    rollback_policy: str = "recommend-only"
    max_evidence_age_minutes: int = 60


class ReleaseHealthSignalsPayload(BaseModel):
    error_rate: float
    p95_latency_ms: float
    fallback_rate: float
    auto_rollback: bool = False


class ReleaseHealthRead(BaseModel):
    status: str
    breached: Dict[str, bool]
    thresholds: Dict[str, float]
