from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_release import LlmReleaseSnapshotModel
from app.infra.db.session import get_db_session
from app.llm_orchestration.services.release_service import ReleaseService

router = APIRouter()
logger = logging.getLogger(__name__)


def _validate_timezone_aware_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("generated_at must include an explicit timezone offset.")
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


@router.post("/", response_model=ReleaseSnapshotRead, status_code=status.HTTP_201_CREATED)
async def create_release(
    payload: ReleaseSnapshotCreate,
    db: Session = Depends(get_db_session),
    # In a real app, we'd get the user from security dependency
    current_user: str = "admin",
):
    """AC1: Create a new DRAFT release snapshot from currently published artefacts."""
    service = ReleaseService(db)
    try:
        snapshot = await service.build_snapshot(
            version=payload.version, created_by=current_user, comment=payload.comment
        )
        return snapshot
    except Exception as e:
        logger.error("admin_release_create_failed error=%s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ReleaseSnapshotRead])
async def list_releases(db: Session = Depends(get_db_session)):
    """List all release snapshots."""
    stmt = select(LlmReleaseSnapshotModel).order_by(desc(LlmReleaseSnapshotModel.created_at))
    res = db.execute(stmt)
    return res.scalars().all()


@router.get("/{snapshot_id}", response_model=ReleaseSnapshotRead)
async def get_release(snapshot_id: uuid.UUID, db: Session = Depends(get_db_session)):
    """Get details of a specific release snapshot."""
    snapshot = db.get(LlmReleaseSnapshotModel, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.post("/{snapshot_id}/validate", response_model=ValidationReport)
async def validate_release(snapshot_id: uuid.UUID, db: Session = Depends(get_db_session)):
    """AC5: Validate a release snapshot manifest."""
    service = ReleaseService(db)
    try:
        result = await service.validate_snapshot(snapshot_id)
        return {
            "is_valid": result.is_valid,
            "errors": [
                {"code": e.error_code, "message": e.message, "details": e.details}
                for e in result.errors
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{snapshot_id}/activate", response_model=ReleaseSnapshotRead)
async def activate_release(
    snapshot_id: uuid.UUID,
    payload: ActivateReleasePayload,
    db: Session = Depends(get_db_session),
    current_user: str = "admin",
):
    """AC7: Atomically activate a release snapshot."""
    service = ReleaseService(db)
    try:
        snapshot = await service.activate_snapshot(
            snapshot_id,
            activated_by=current_user,
            qualification_report=payload.qualification_report,
            golden_report=payload.golden_report,
            smoke_result=payload.smoke_result.model_dump(mode="json"),
            monitoring_thresholds=payload.monitoring_thresholds,
            rollback_policy=payload.rollback_policy,
            max_evidence_age_minutes=payload.max_evidence_age_minutes,
        )
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rollback", response_model=ReleaseSnapshotRead)
async def rollback_release(
    db: Session = Depends(get_db_session),
    current_user: str = "admin",
):
    """AC8: Rollback to the previous active snapshot."""
    service = ReleaseService(db)
    try:
        snapshot = await service.rollback(activated_by=current_user)
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{snapshot_id}/release-health", response_model=ReleaseHealthRead)
async def evaluate_release_health(
    snapshot_id: uuid.UUID,
    payload: ReleaseHealthSignalsPayload,
    db: Session = Depends(get_db_session),
    current_user: str = "admin",
):
    """Évalue la santé post-activation et recommande ou déclenche un rollback."""
    service = ReleaseService(db)
    try:
        decision = await service.evaluate_release_health(
            snapshot_id=snapshot_id,
            signals={
                "error_rate": payload.error_rate,
                "p95_latency_ms": payload.p95_latency_ms,
                "fallback_rate": payload.fallback_rate,
            },
            triggered_by=current_user,
            auto_rollback=payload.auto_rollback,
        )
        return decision
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
