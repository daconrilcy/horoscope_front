from __future__ import annotations

import re
import uuid
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.routers.admin_llm_error_codes import AdminLlmErrorCode
from app.core.request_id import resolve_request_id
from app.core.sensitive_data import DataCategory, classify_field
from app.infra.db.models.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.llm_orchestration.feature_taxonomy import is_supported_feature, normalize_feature
from app.services.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/admin/llm/sample-payloads", tags=["admin-llm"])

LOCALE_PATTERN = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
BLOCKED_CATEGORIES = {
    DataCategory.SECRET_CREDENTIAL,
    DataCategory.DIRECT_IDENTIFIER,
    DataCategory.CORRELABLE_BUSINESS_IDENTIFIER,
}


class ResponseMeta(BaseModel):
    request_id: str


class AdminLlmSamplePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    feature: str
    locale: str
    payload_json: dict[str, Any]
    description: str | None = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdminLlmSamplePayloadSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    feature: str
    locale: str
    description: str | None = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdminLlmSamplePayloadListData(BaseModel):
    items: list[AdminLlmSamplePayloadSummary]
    recommended_default_id: uuid.UUID | None = None


class AdminLlmSamplePayloadResponse(BaseModel):
    data: AdminLlmSamplePayload
    meta: ResponseMeta


class AdminLlmSamplePayloadListResponse(BaseModel):
    data: AdminLlmSamplePayloadListData
    meta: ResponseMeta


class AdminLlmSamplePayloadDeleteData(BaseModel):
    id: uuid.UUID


class AdminLlmSamplePayloadDeleteResponse(BaseModel):
    data: AdminLlmSamplePayloadDeleteData
    meta: ResponseMeta


class AdminLlmSamplePayloadCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    feature: str = Field(min_length=1, max_length=64)
    locale: str = Field(min_length=5, max_length=16)
    payload_json: dict[str, Any]
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool = False
    is_active: bool = True


class AdminLlmSamplePayloadUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    locale: str | None = Field(default=None, min_length=5, max_length=16)
    payload_json: dict[str, Any] | None = None
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool | None = None
    is_active: bool | None = None


def _iter_payload_keys(payload: Any, prefix: str = "") -> Iterator[str]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            full_key = f"{prefix}.{key}" if prefix else str(key)
            yield str(key)
            yield from _iter_payload_keys(value, full_key)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_payload_keys(item, prefix)


def _validate_locale(locale: str) -> str:
    if not LOCALE_PATTERN.match(locale):
        raise ValueError("locale must follow format xx-XX (example: fr-FR)")
    return locale


def _validate_payload_json(feature: str, payload_json: dict[str, Any]) -> None:
    if not payload_json:
        raise ValueError("payload_json cannot be empty")

    blocked_keys: list[str] = []
    for key in _iter_payload_keys(payload_json):
        if classify_field(key) in BLOCKED_CATEGORIES:
            blocked_keys.append(key)

    if blocked_keys:
        unique_keys = sorted(set(blocked_keys))
        raise ValueError(
            f"payload_json contains forbidden sensitive keys: {', '.join(unique_keys)}"
        )

    if feature == "natal" and "chart_json" not in payload_json:
        raise ValueError("natal sample payload must include chart_json")


def _normalize_name(name: str) -> str:
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("name cannot be empty or whitespace-only")
    return normalized_name


def _validate_feature(feature: str) -> str:
    normalized_feature = normalize_feature(feature)
    if not is_supported_feature(normalized_feature):
        raise ValueError(f"feature '{feature}' is not supported for sample payloads")
    return normalized_feature


def _error_response(
    *, request_id: str, status_code: int, code: str, message: str, details: dict[str, Any]
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    action: str,
    target_id: str | None,
    details: dict[str, Any],
) -> None:
    actor_user_id: int | None = actor.id
    if actor_user_id is not None:
        user_exists = db.scalar(select(UserModel.id).where(UserModel.id == actor_user_id).limit(1))
        if user_exists is None:
            actor_user_id = None

    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor.role,
            action=action,
            target_type="llm_sample_payload",
            target_id=target_id,
            status="success",
            details=details,
        ),
    )


def _to_api_payload(model: LlmSamplePayloadModel) -> AdminLlmSamplePayload:
    """JSON tel qu’en base : pas de sanitize ADMIN_API (évite [REDACTED] au round-trip édition)."""
    return AdminLlmSamplePayload.model_validate(model)


def _sample_payload_name_conflict_response(
    *, request_id: str, feature: str, locale: str
) -> JSONResponse:
    return _error_response(
        request_id=request_id,
        status_code=409,
        code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NAME_CONFLICT.value,
        message="a sample payload with this name already exists for this feature/locale",
        details={"feature": feature, "locale": locale},
    )


def _sample_payload_default_conflict_response(
    *, request_id: str, feature: str, locale: str
) -> JSONResponse:
    return _error_response(
        request_id=request_id,
        status_code=409,
        code=AdminLlmErrorCode.SAMPLE_PAYLOAD_DEFAULT_CONFLICT.value,
        message="another default sample payload already exists for this feature/locale",
        details={"feature": feature, "locale": locale},
    )


def _sample_payload_generic_conflict_response(
    *, request_id: str, feature: str, locale: str
) -> JSONResponse:
    return _error_response(
        request_id=request_id,
        status_code=409,
        code=AdminLlmErrorCode.SAMPLE_PAYLOAD_CONFLICT.value,
        message="sample payload update conflicts with existing data",
        details={"feature": feature, "locale": locale},
    )


def _find_name_conflict(
    db: Session,
    *,
    feature: str,
    locale: str,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> LlmSamplePayloadModel | None:
    stmt = (
        select(LlmSamplePayloadModel)
        .where(LlmSamplePayloadModel.feature == feature)
        .where(LlmSamplePayloadModel.locale == locale)
        .where(LlmSamplePayloadModel.name == name)
    )
    if exclude_id is not None:
        stmt = stmt.where(LlmSamplePayloadModel.id != exclude_id)
    return db.scalar(stmt.limit(1))


def _find_default_conflict(
    db: Session,
    *,
    feature: str,
    locale: str,
    exclude_id: uuid.UUID | None = None,
) -> LlmSamplePayloadModel | None:
    stmt = (
        select(LlmSamplePayloadModel)
        .where(LlmSamplePayloadModel.feature == feature)
        .where(LlmSamplePayloadModel.locale == locale)
        .where(LlmSamplePayloadModel.is_default == True)  # noqa: E712
    )
    if exclude_id is not None:
        stmt = stmt.where(LlmSamplePayloadModel.id != exclude_id)
    return db.scalar(stmt.limit(1))


@router.post("", response_model=AdminLlmSamplePayloadResponse)
def create_sample_payload(
    request: Request,
    payload: AdminLlmSamplePayloadCreatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    try:
        normalized_name = _normalize_name(payload.name)
        feature = _validate_feature(payload.feature)
        locale = _validate_locale(payload.locale)
        _validate_payload_json(feature, payload.payload_json)
    except ValueError as exc:
        return _error_response(
            request_id=request_id,
            status_code=422,
            code=AdminLlmErrorCode.INVALID_SAMPLE_PAYLOAD.value,
            message=str(exc),
            details={},
        )

    if _find_name_conflict(
        db,
        feature=feature,
        locale=locale,
        name=normalized_name,
    ):
        return _sample_payload_name_conflict_response(
            request_id=request_id,
            feature=feature,
            locale=locale,
        )

    if payload.is_default:
        if _find_default_conflict(db, feature=feature, locale=locale):
            existing_defaults = db.scalars(
                select(LlmSamplePayloadModel)
                .where(LlmSamplePayloadModel.feature == feature)
                .where(LlmSamplePayloadModel.locale == locale)
                .where(LlmSamplePayloadModel.is_default == True)  # noqa: E712
            ).all()
        else:
            existing_defaults = []
        for row in existing_defaults:
            row.is_default = False
        # Flush first to avoid transient uniqueness violations on SQLite
        # when promoting a new default.
        db.flush()

    model = LlmSamplePayloadModel(
        name=normalized_name,
        feature=feature,
        locale=locale,
        payload_json=payload.payload_json,
        description=payload.description,
        is_default=payload.is_default,
        is_active=payload.is_active,
    )
    db.add(model)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _sample_payload_generic_conflict_response(
            request_id=request_id,
            feature=feature,
            locale=locale,
        )
    db.refresh(model)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_sample_payload_create",
        target_id=str(model.id),
        details={
            "feature": model.feature,
            "locale": model.locale,
            "is_default": model.is_default,
        },
    )
    db.commit()
    return {"data": _to_api_payload(model), "meta": {"request_id": request_id}}


@router.get("", response_model=AdminLlmSamplePayloadListResponse)
def list_sample_payloads(
    request: Request,
    feature: str = Query(..., min_length=1),
    locale: str = Query(..., min_length=5),
    include_inactive: bool = False,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)

    try:
        normalized_feature = _validate_feature(feature)
        normalized_locale = _validate_locale(locale)
    except ValueError as exc:
        return _error_response(
            request_id=request_id,
            status_code=422,
            code=AdminLlmErrorCode.INVALID_QUERY.value,
            message=str(exc),
            details={},
        )

    stmt = (
        select(LlmSamplePayloadModel)
        .where(LlmSamplePayloadModel.feature == normalized_feature)
        .where(LlmSamplePayloadModel.locale == normalized_locale)
        .order_by(LlmSamplePayloadModel.name.asc())
    )
    if not include_inactive:
        stmt = stmt.where(LlmSamplePayloadModel.is_active == True)  # noqa: E712
    rows = db.scalars(stmt).all()

    recommended_default = next((row for row in rows if row.is_default), None)
    return {
        "data": {
            "items": [AdminLlmSamplePayloadSummary.model_validate(row) for row in rows],
            "recommended_default_id": recommended_default.id if recommended_default else None,
        },
        "meta": {"request_id": request_id},
    }


@router.get("/{sample_payload_id}", response_model=AdminLlmSamplePayloadResponse)
def get_sample_payload(
    sample_payload_id: uuid.UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)

    model = db.get(LlmSamplePayloadModel, sample_payload_id)
    if model is None:
        return _error_response(
            request_id=request_id,
            status_code=404,
            code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NOT_FOUND.value,
            message=f"sample payload {sample_payload_id} not found",
            details={},
        )

    return {"data": _to_api_payload(model), "meta": {"request_id": request_id}}


@router.patch("/{sample_payload_id}", response_model=AdminLlmSamplePayloadResponse)
def update_sample_payload(
    sample_payload_id: uuid.UUID,
    request: Request,
    payload: AdminLlmSamplePayloadUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    model = db.get(LlmSamplePayloadModel, sample_payload_id)
    if model is None:
        return _error_response(
            request_id=request_id,
            status_code=404,
            code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NOT_FOUND.value,
            message=f"sample payload {sample_payload_id} not found",
            details={},
        )

    next_name = payload.name if payload.name is not None else model.name
    next_locale = payload.locale if payload.locale is not None else model.locale
    next_feature = model.feature
    next_payload_json = (
        payload.payload_json if payload.payload_json is not None else model.payload_json
    )

    try:
        next_name = _normalize_name(next_name)
        next_feature = _validate_feature(next_feature)
        next_locale = _validate_locale(next_locale)
        _validate_payload_json(next_feature, next_payload_json)
    except ValueError as exc:
        return _error_response(
            request_id=request_id,
            status_code=422,
            code=AdminLlmErrorCode.INVALID_SAMPLE_PAYLOAD.value,
            message=str(exc),
            details={},
        )

    if _find_name_conflict(
        db,
        feature=next_feature,
        locale=next_locale,
        name=next_name,
        exclude_id=model.id,
    ):
        return _sample_payload_name_conflict_response(
            request_id=request_id,
            feature=next_feature,
            locale=next_locale,
        )

    if (
        payload.is_default is not False
        and model.is_default
        and next_locale != model.locale
        and _find_default_conflict(
            db,
            feature=next_feature,
            locale=next_locale,
            exclude_id=model.id,
        )
    ):
        return _sample_payload_default_conflict_response(
            request_id=request_id,
            feature=next_feature,
            locale=next_locale,
        )

    if payload.is_default is True:
        existing_defaults = db.scalars(
            select(LlmSamplePayloadModel)
            .where(LlmSamplePayloadModel.feature == next_feature)
            .where(LlmSamplePayloadModel.locale == next_locale)
            .where(LlmSamplePayloadModel.is_default == True)  # noqa: E712
            .where(LlmSamplePayloadModel.id != model.id)
        ).all()
        for row in existing_defaults:
            row.is_default = False
        # Flush first to avoid transient uniqueness violations on SQLite
        # when promoting a new default.
        db.flush()

    model.name = next_name
    model.locale = next_locale
    model.payload_json = next_payload_json
    if "description" in payload.model_fields_set:
        model.description = payload.description
    if payload.is_default is not None:
        model.is_default = payload.is_default
    if payload.is_active is not None:
        model.is_active = payload.is_active

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _sample_payload_generic_conflict_response(
            request_id=request_id,
            feature=next_feature,
            locale=next_locale,
        )
    db.refresh(model)
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_sample_payload_update",
        target_id=str(model.id),
        details={
            "feature": model.feature,
            "locale": model.locale,
            "is_default": model.is_default,
            "is_active": model.is_active,
        },
    )
    db.commit()
    return {"data": _to_api_payload(model), "meta": {"request_id": request_id}}


@router.delete("/{sample_payload_id}", response_model=AdminLlmSamplePayloadDeleteResponse)
def delete_sample_payload(
    sample_payload_id: uuid.UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    model = db.get(LlmSamplePayloadModel, sample_payload_id)
    if model is None:
        return _error_response(
            request_id=request_id,
            status_code=404,
            code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NOT_FOUND.value,
            message=f"sample payload {sample_payload_id} not found",
            details={},
        )

    db.delete(model)
    db.commit()
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_sample_payload_delete",
        target_id=str(sample_payload_id),
        details={"feature": model.feature, "locale": model.locale},
    )
    db.commit()
    return {"data": {"id": sample_payload_id}, "meta": {"request_id": request_id}}
