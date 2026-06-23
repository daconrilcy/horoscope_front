"""Routeur HTTP admin pour les contenus applicatifs non astrologiques."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.request_id import resolve_request_id
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.session import get_db_session
from app.services.api_contracts.admin.content import (
    AdminFeatureFlagListResponse,
    AdminFeatureFlagResponse,
    ConfigTextListResponse,
    ConfigTextResponse,
    ConfigTextUpdatePayload,
)
from app.services.ops.admin_content import (
    _ensure_config_texts_seeded,
    _raise_error,
    _record_audit_event,
    _to_config_text_data,
    _to_feature_flag_data,
    update_config_text_value,
)
from app.services.ops.feature_flag_service import (
    FeatureFlagService,
    FeatureFlagServiceError,
    FeatureFlagUpdatePayload,
)

router = APIRouter(prefix="/v1/admin/content", tags=["admin-content"])


@router.get("/texts", response_model=ConfigTextListResponse)
def list_content_texts(
    request: Request,
    category: str | None = None,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    _ensure_config_texts_seeded(db)
    stmt = select(ConfigTextModel).order_by(ConfigTextModel.key.asc())
    if category is not None:
        stmt = stmt.where(ConfigTextModel.category == category)
    rows = db.scalars(stmt).all()
    return {"data": [_to_config_text_data(row) for row in rows], "meta": {"request_id": request_id}}


@router.patch("/texts/{key}", response_model=ConfigTextResponse)
def update_content_text(
    key: str,
    request: Request,
    payload: ConfigTextUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    data = update_config_text_value(
        db,
        key=key,
        value=payload.value,
        actor=current_user,
        request_id=request_id,
    )
    return {"data": data, "meta": {"request_id": request_id}}


@router.get("/feature-flags", response_model=AdminFeatureFlagListResponse)
def list_admin_feature_flags(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    data = FeatureFlagService.list_flags(db)
    return {
        "data": [_to_feature_flag_data(item) for item in data.flags],
        "meta": {"request_id": request_id},
    }


@router.patch("/feature-flags/{flag_key}", response_model=AdminFeatureFlagResponse)
def update_admin_feature_flag(
    flag_key: str,
    request: Request,
    payload: FeatureFlagUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    before = db.scalar(select(FeatureFlagModel).where(FeatureFlagModel.key == flag_key).limit(1))
    before_enabled = before.enabled if before else False
    try:
        updated = FeatureFlagService.update_flag(
            db,
            key=flag_key,
            payload=payload,
            updated_by_user_id=current_user.id,
        )
    except FeatureFlagServiceError as error:
        db.rollback()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="feature_flag_toggled",
        target_type="feature_flag",
        target_id=flag_key,
        status="success",
        details={"flag_code": flag_key, "before": before_enabled, "after": updated.enabled},
    )
    db.commit()
    return {"data": _to_feature_flag_data(updated), "meta": {"request_id": request_id}}
