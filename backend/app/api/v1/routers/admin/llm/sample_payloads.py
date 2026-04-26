"""Routes admin de gestion des sample payloads LLM alignés sur le scope canonique."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.routers.admin.llm.error_codes import AdminLlmErrorCode
from app.api.v1.schemas.routers.admin.llm.sample_payloads import (
    AdminLlmSamplePayloadCreatePayload,
    AdminLlmSamplePayloadDeleteResponse,
    AdminLlmSamplePayloadListResponse,
    AdminLlmSamplePayloadResponse,
    AdminLlmSamplePayloadSummary,
    AdminLlmSamplePayloadUpdatePayload,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.llm.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.session import get_db_session
from app.services.llm_generation.admin_sample_payloads import (
    _error_response,
    _find_default_conflict,
    _find_name_conflict,
    _normalize_name,
    _normalize_scope_dimensions,
    _normalize_scope_value,
    _record_audit_event,
    _sample_payload_default_conflict_response,
    _sample_payload_generic_conflict_response,
    _sample_payload_name_conflict_response,
    _to_api_payload,
    _validate_feature,
    _validate_locale,
    _validate_payload_json,
)

router = APIRouter(prefix="/v1/admin/llm/sample-payloads", tags=["admin-llm"])


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
        raw_subfeature = _normalize_scope_value(payload.subfeature) or None
        raw_plan = _normalize_scope_value(payload.plan) or None
        subfeature, plan = _normalize_scope_dimensions(feature, raw_subfeature, raw_plan)
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
        subfeature=subfeature,
        plan=plan,
        locale=locale,
        name=normalized_name,
    ):
        return _sample_payload_name_conflict_response(
            request_id=request_id,
            feature=feature,
            subfeature=subfeature,
            plan=plan,
            locale=locale,
        )

    if payload.is_default:
        if _find_default_conflict(
            db, feature=feature, subfeature=subfeature, plan=plan, locale=locale
        ):
            existing_defaults = db.scalars(
                select(LlmSamplePayloadModel)
                .where(LlmSamplePayloadModel.feature == feature)
                .where(LlmSamplePayloadModel.subfeature == subfeature)
                .where(LlmSamplePayloadModel.plan == plan)
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
        subfeature=subfeature,
        plan=plan,
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
            subfeature=subfeature,
            plan=plan,
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
            "subfeature": model.subfeature,
            "plan": model.plan,
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
    subfeature: str | None = Query(default=None, max_length=64),
    plan: str | None = Query(default=None, max_length=64),
    locale: str = Query(..., min_length=5),
    include_inactive: bool = False,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)

    try:
        normalized_feature = _validate_feature(feature)
        normalized_subfeature, normalized_plan = _normalize_scope_dimensions(
            normalized_feature,
            _normalize_scope_value(subfeature) or None,
            _normalize_scope_value(plan) or None,
        )
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
        .where(LlmSamplePayloadModel.subfeature == normalized_subfeature)
        .where(LlmSamplePayloadModel.plan == normalized_plan)
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
    next_subfeature = (
        _normalize_scope_value(payload.subfeature) or None
        if "subfeature" in payload.model_fields_set
        else model.subfeature
    )
    next_plan = (
        _normalize_scope_value(payload.plan) or None
        if "plan" in payload.model_fields_set
        else model.plan
    )
    next_locale = payload.locale if payload.locale is not None else model.locale
    next_feature = model.feature
    next_payload_json = (
        payload.payload_json if payload.payload_json is not None else model.payload_json
    )

    try:
        next_name = _normalize_name(next_name)
        next_feature = _validate_feature(next_feature)
        next_subfeature, next_plan = _normalize_scope_dimensions(
            next_feature,
            next_subfeature,
            next_plan,
        )
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
        subfeature=next_subfeature,
        plan=next_plan,
        locale=next_locale,
        name=next_name,
        exclude_id=model.id,
    ):
        return _sample_payload_name_conflict_response(
            request_id=request_id,
            feature=next_feature,
            subfeature=next_subfeature,
            plan=next_plan,
            locale=next_locale,
        )

    if (
        payload.is_default is not False
        and model.is_default
        and (
            next_subfeature != model.subfeature
            or next_plan != model.plan
            or next_locale != model.locale
        )
        and _find_default_conflict(
            db,
            feature=next_feature,
            subfeature=next_subfeature,
            plan=next_plan,
            locale=next_locale,
            exclude_id=model.id,
        )
    ):
        return _sample_payload_default_conflict_response(
            request_id=request_id,
            feature=next_feature,
            subfeature=next_subfeature,
            plan=next_plan,
            locale=next_locale,
        )

    if payload.is_default is True:
        existing_defaults = db.scalars(
            select(LlmSamplePayloadModel)
            .where(LlmSamplePayloadModel.feature == next_feature)
            .where(LlmSamplePayloadModel.subfeature == next_subfeature)
            .where(LlmSamplePayloadModel.plan == next_plan)
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
    model.subfeature = next_subfeature
    model.plan = next_plan
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
            subfeature=next_subfeature,
            plan=next_plan,
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
            "subfeature": model.subfeature,
            "plan": model.plan,
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
        details={
            "feature": model.feature,
            "subfeature": model.subfeature,
            "plan": model.plan,
            "locale": model.locale,
        },
    )
    db.commit()
    return {"data": {"id": sample_payload_id}, "meta": {"request_id": request_id}}
