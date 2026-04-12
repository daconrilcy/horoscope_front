from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_release import LlmReleaseSnapshotModel
from app.infra.db.session import get_db_session
from app.llm_orchestration.services.release_service import ReleaseService

router = APIRouter()
logger = logging.getLogger(__name__)


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

    class Config:
        from_attributes = True


class ValidationReport(BaseModel):
    is_valid: bool
    errors: List[Dict[str, Any]]


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
    db: Session = Depends(get_db_session),
    current_user: str = "admin",
):
    """AC7: Atomically activate a release snapshot."""
    service = ReleaseService(db)
    try:
        snapshot = await service.activate_snapshot(snapshot_id, activated_by=current_user)
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
