from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.request_id import resolve_request_id
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel, RulesetParameterModel
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService
from app.services.feature_flag_service import (
    FeatureFlagData,
    FeatureFlagService,
    FeatureFlagServiceError,
    FeatureFlagUpdatePayload,
)

router = APIRouter(prefix="/v1/admin/content", tags=["admin-content"])


DEFAULT_CONFIG_TEXTS: tuple[dict[str, str], ...] = (
    {
        "key": "paywall.daily.locked_section",
        "value": "Passez premium pour debloquer l'analyse complete de la journee.",
        "category": "paywall",
    },
    {
        "key": "paywall.natal.upgrade_cta",
        "value": "Activez le theme complet et comparez plusieurs astrologues.",
        "category": "paywall",
    },
    {
        "key": "transactional.billing.success",
        "value": "Votre abonnement a bien ete mis a jour.",
        "category": "transactional",
    },
    {
        "key": "marketing.in_app.welcome",
        "value": "Explorez vos tendances du moment avec un guidage plus precis.",
        "category": "marketing",
    },
)

DEFAULT_EDITORIAL_TEMPLATES: tuple[dict[str, object], ...] = (
    {
        "template_code": "daily_overview",
        "title": "Daily overview",
        "content": "<intro>\n<momentum>\n<advice>",
        "expected_tags": ["intro", "momentum", "advice"],
        "example_render": "Intro concise puis momentum et un conseil actionnable.",
    },
    {
        "template_code": "natal_unlock",
        "title": "Natal unlock",
        "content": "<context>\n<insights>\n<next_step>",
        "expected_tags": ["context", "insights", "next_step"],
        "example_render": "Contexte natal suivi de deux insights et d'une recommandation.",
    },
)

CALIBRATION_RULE_DESCRIPTIONS: dict[str, str] = {
    "turning_point.min_duration_minutes": "Duree minimale retenue pour un turning point.",
    "scores.rare_bonus_factor": "Bonus applique aux signaux juges rares.",
    "scores.flat_day_threshold": "Seuil en dessous duquel la journee est classee comme plate.",
}


class ResponseMeta(BaseModel):
    request_id: str


class ConfigTextData(BaseModel):
    key: str
    value: str
    category: str
    updated_at: datetime
    updated_by_user_id: int | None


class ConfigTextListResponse(BaseModel):
    data: list[ConfigTextData]
    meta: ResponseMeta


class ConfigTextResponse(BaseModel):
    data: ConfigTextData
    meta: ResponseMeta


class ConfigTextUpdatePayload(BaseModel):
    value: str


class AdminFeatureFlagData(BaseModel):
    key: str
    description: str
    enabled: bool
    target_roles: list[str]
    target_user_ids: list[int]
    updated_by_user_id: int | None
    updated_at: datetime
    scope: str


class AdminFeatureFlagListResponse(BaseModel):
    data: list[AdminFeatureFlagData]
    meta: ResponseMeta


class AdminFeatureFlagResponse(BaseModel):
    data: AdminFeatureFlagData
    meta: ResponseMeta


class EditorialTemplateSummary(BaseModel):
    template_code: str
    title: str
    active_version_id: uuid.UUID | None
    active_version_number: int | None
    published_at: datetime | None


class EditorialTemplateVersionData(BaseModel):
    id: uuid.UUID
    template_code: str
    version_number: int
    title: str
    content: str
    expected_tags: list[str]
    example_render: str | None
    status: str
    created_at: datetime
    published_at: datetime | None
    created_by_user_id: int | None


class EditorialTemplateListResponse(BaseModel):
    data: list[EditorialTemplateSummary]
    meta: ResponseMeta


class EditorialTemplateDetail(BaseModel):
    template_code: str
    active_version_id: uuid.UUID | None
    versions: list[EditorialTemplateVersionData]


class EditorialTemplateDetailResponse(BaseModel):
    data: EditorialTemplateDetail
    meta: ResponseMeta


class EditorialTemplateVersionCreatePayload(BaseModel):
    title: str
    content: str
    expected_tags: list[str] = Field(default_factory=list)
    example_render: str | None = None


class EditorialTemplateRollbackPayload(BaseModel):
    version_id: uuid.UUID


class CalibrationRuleData(BaseModel):
    rule_code: str
    value: str
    data_type: str
    description: str
    ruleset_version: str


class CalibrationRuleListResponse(BaseModel):
    data: list[CalibrationRuleData]
    meta: ResponseMeta


class CalibrationRuleResponse(BaseModel):
    data: CalibrationRuleData
    meta: ResponseMeta


class CalibrationRuleUpdatePayload(BaseModel):
    value: Any


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, object],
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
    target_type: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor.id,
            actor_role=actor.role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


def _ensure_config_texts_seeded(db: Session) -> None:
    existing_keys = {item[0] for item in db.execute(select(ConfigTextModel.key)).all()}
    for item in DEFAULT_CONFIG_TEXTS:
        if item["key"] in existing_keys:
            continue
        db.add(
            ConfigTextModel(
                key=item["key"],
                value=item["value"],
                category=item["category"],
                updated_by_user_id=None,
            )
        )
    db.flush()


def _ensure_editorial_templates_seeded(db: Session) -> None:
    existing_codes = {
        item[0]
        for item in db.execute(select(EditorialTemplateVersionModel.template_code).distinct()).all()
    }
    now = datetime.now(timezone.utc)
    for item in DEFAULT_EDITORIAL_TEMPLATES:
        if item["template_code"] in existing_codes:
            continue
        db.add(
            EditorialTemplateVersionModel(
                template_code=str(item["template_code"]),
                version_number=1,
                title=str(item["title"]),
                content=str(item["content"]),
                expected_tags=list(item["expected_tags"]),
                example_render=str(item["example_render"]),
                status="published",
                published_at=now,
                created_by_user_id=None,
            )
        )
    db.flush()


def _to_config_text_data(model: ConfigTextModel) -> ConfigTextData:
    return ConfigTextData(
        key=model.key,
        value=model.value,
        category=model.category,
        updated_at=model.updated_at,
        updated_by_user_id=model.updated_by_user_id,
    )


def _to_feature_flag_data(model: FeatureFlagData) -> AdminFeatureFlagData:
    scope = "Tous plans" if not model.target_roles and not model.target_user_ids else "Cible"
    return AdminFeatureFlagData(
        key=model.key,
        description=model.description,
        enabled=model.enabled,
        target_roles=model.target_roles,
        target_user_ids=model.target_user_ids,
        updated_by_user_id=model.updated_by_user_id,
        updated_at=model.updated_at,
        scope=scope,
    )


def _to_editorial_version_data(
    model: EditorialTemplateVersionModel,
) -> EditorialTemplateVersionData:
    return EditorialTemplateVersionData(
        id=model.id,
        template_code=model.template_code,
        version_number=model.version_number,
        title=model.title,
        content=model.content,
        expected_tags=list(model.expected_tags or []),
        example_render=model.example_render,
        status=model.status,
        created_at=model.created_at,
        published_at=model.published_at,
        created_by_user_id=model.created_by_user_id,
    )


def _get_latest_ruleset(db: Session) -> PredictionRulesetModel | None:
    return db.scalar(
        select(PredictionRulesetModel)
        .order_by(PredictionRulesetModel.created_at.desc(), PredictionRulesetModel.id.desc())
        .limit(1)
    )


def _serialize_calibration_value(value: Any, data_type: str) -> str:
    if data_type == "float":
        try:
            return str(float(value))
        except (TypeError, ValueError) as error:
            raise ValueError("calibration value must be a float") from error
    if data_type == "int":
        try:
            if isinstance(value, str) and "." in value:
                raise ValueError
            return str(int(value))
        except (TypeError, ValueError) as error:
            raise ValueError("calibration value must be an integer") from error
    if data_type == "bool":
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "oui"}:
                return "true"
            if normalized in {"false", "0", "no", "non"}:
                return "false"
        raise ValueError("calibration value must be a boolean")
    if data_type == "json":
        if isinstance(value, str):
            try:
                json.loads(value)
            except json.JSONDecodeError as error:
                raise ValueError("calibration value must be valid JSON") from error
            return value
        return json.dumps(value)
    return str(value)


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
    _ensure_config_texts_seeded(db)
    row = db.scalar(select(ConfigTextModel).where(ConfigTextModel.key == key).limit(1))
    if row is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="content_text_not_found",
            message="content text was not found",
            details={"key": key},
        )
    before_value = row.value
    row.value = payload.value
    row.updated_by_user_id = current_user.id
    db.flush()
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="content_text_updated",
        target_type="config_text",
        target_id=key,
        status="success",
        details={"content_key": key, "before": before_value, "after": payload.value},
    )
    db.commit()
    db.refresh(row)
    return {"data": _to_config_text_data(row), "meta": {"request_id": request_id}}


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
        return _error_response(
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


@router.get("/editorial-templates", response_model=EditorialTemplateListResponse)
def list_editorial_templates(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    _ensure_editorial_templates_seeded(db)
    codes = [
        item[0]
        for item in db.execute(select(EditorialTemplateVersionModel.template_code).distinct())
    ]
    summaries: list[EditorialTemplateSummary] = []
    for code in sorted(codes):
        active = db.scalar(
            select(EditorialTemplateVersionModel)
            .where(
                EditorialTemplateVersionModel.template_code == code,
                EditorialTemplateVersionModel.status == "published",
            )
            .order_by(EditorialTemplateVersionModel.version_number.desc())
            .limit(1)
        )
        latest = active or db.scalar(
            select(EditorialTemplateVersionModel)
            .where(EditorialTemplateVersionModel.template_code == code)
            .order_by(EditorialTemplateVersionModel.version_number.desc())
            .limit(1)
        )
        if latest is None:
            continue
        summaries.append(
            EditorialTemplateSummary(
                template_code=code,
                title=latest.title,
                active_version_id=active.id if active else None,
                active_version_number=active.version_number if active else None,
                published_at=active.published_at if active else None,
            )
        )
    return {"data": summaries, "meta": {"request_id": request_id}}


@router.get("/editorial-templates/{template_code}", response_model=EditorialTemplateDetailResponse)
def get_editorial_template_detail(
    template_code: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    _ensure_editorial_templates_seeded(db)
    versions = db.scalars(
        select(EditorialTemplateVersionModel)
        .where(EditorialTemplateVersionModel.template_code == template_code)
        .order_by(EditorialTemplateVersionModel.version_number.desc())
    ).all()
    if not versions:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="editorial_template_not_found",
            message="editorial template was not found",
            details={"template_code": template_code},
        )
    active = next((version for version in versions if version.status == "published"), None)
    return {
        "data": {
            "template_code": template_code,
            "active_version_id": active.id if active else None,
            "versions": [_to_editorial_version_data(version) for version in versions],
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/editorial-templates/{template_code}/versions",
    response_model=EditorialTemplateDetailResponse,
)
def create_editorial_template_version(
    template_code: str,
    request: Request,
    payload: EditorialTemplateVersionCreatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    _ensure_editorial_templates_seeded(db)
    current_max = db.scalar(
        select(func.max(EditorialTemplateVersionModel.version_number)).where(
            EditorialTemplateVersionModel.template_code == template_code
        )
    )
    current_active = db.scalar(
        select(EditorialTemplateVersionModel)
        .where(
            EditorialTemplateVersionModel.template_code == template_code,
            EditorialTemplateVersionModel.status == "published",
        )
        .order_by(EditorialTemplateVersionModel.version_number.desc())
        .limit(1)
    )
    if current_active:
        current_active.status = "archived"
    version = EditorialTemplateVersionModel(
        template_code=template_code,
        version_number=int(current_max or 0) + 1,
        title=payload.title,
        content=payload.content,
        expected_tags=payload.expected_tags,
        example_render=payload.example_render,
        status="published",
        published_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
    )
    db.add(version)
    db.flush()
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="editorial_template_updated",
        target_type="editorial_template",
        target_id=template_code,
        status="success",
        details={
            "template_code": template_code,
            "before_version": current_active.version_number if current_active else None,
            "after_version": version.version_number,
        },
    )
    db.commit()
    versions = db.scalars(
        select(EditorialTemplateVersionModel)
        .where(EditorialTemplateVersionModel.template_code == template_code)
        .order_by(EditorialTemplateVersionModel.version_number.desc())
    ).all()
    return {
        "data": {
            "template_code": template_code,
            "active_version_id": version.id,
            "versions": [_to_editorial_version_data(item) for item in versions],
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/editorial-templates/{template_code}/rollback",
    response_model=EditorialTemplateDetailResponse,
)
def rollback_editorial_template(
    template_code: str,
    request: Request,
    payload: EditorialTemplateRollbackPayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    versions = db.scalars(
        select(EditorialTemplateVersionModel)
        .where(EditorialTemplateVersionModel.template_code == template_code)
        .order_by(EditorialTemplateVersionModel.version_number.desc())
    ).all()
    if not versions:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="editorial_template_not_found",
            message="editorial template was not found",
            details={"template_code": template_code},
        )
    current_active = next((version for version in versions if version.status == "published"), None)
    target = next((version for version in versions if version.id == payload.version_id), None)
    if target is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="editorial_template_version_not_found",
            message="editorial template version was not found",
            details={"template_code": template_code, "version_id": str(payload.version_id)},
        )
    if current_active and current_active.id == target.id:
        return {
            "data": {
                "template_code": template_code,
                "active_version_id": target.id,
                "versions": [_to_editorial_version_data(item) for item in versions],
            },
            "meta": {"request_id": request_id},
        }
    if current_active and current_active.id != target.id:
        current_active.status = "archived"
    target.status = "published"
    target.published_at = datetime.now(timezone.utc)
    db.flush()
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="editorial_template_updated",
        target_type="editorial_template",
        target_id=template_code,
        status="success",
        details={
            "template_code": template_code,
            "before_version": current_active.version_number if current_active else None,
            "after_version": target.version_number,
        },
    )
    db.commit()
    refreshed = db.scalars(
        select(EditorialTemplateVersionModel)
        .where(EditorialTemplateVersionModel.template_code == template_code)
        .order_by(EditorialTemplateVersionModel.version_number.desc())
    ).all()
    return {
        "data": {
            "template_code": template_code,
            "active_version_id": target.id,
            "versions": [_to_editorial_version_data(item) for item in refreshed],
        },
        "meta": {"request_id": request_id},
    }


@router.get("/calibration-rules", response_model=CalibrationRuleListResponse)
def list_calibration_rules(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    ruleset = _get_latest_ruleset(db)
    if ruleset is None:
        return {"data": [], "meta": {"request_id": request_id}}
    rows = db.scalars(
        select(RulesetParameterModel)
        .where(RulesetParameterModel.ruleset_id == ruleset.id)
        .order_by(RulesetParameterModel.param_key.asc())
    ).all()
    data = [
        CalibrationRuleData(
            rule_code=row.param_key,
            value=row.param_value,
            data_type=row.data_type,
            description=CALIBRATION_RULE_DESCRIPTIONS.get(
                row.param_key,
                f"Parametre runtime du ruleset {ruleset.version}.",
            ),
            ruleset_version=ruleset.version,
        )
        for row in rows
    ]
    return {"data": data, "meta": {"request_id": request_id}}


@router.patch("/calibration-rules/{rule_code}", response_model=CalibrationRuleResponse)
def update_calibration_rule(
    rule_code: str,
    request: Request,
    payload: CalibrationRuleUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    ruleset = _get_latest_ruleset(db)
    if ruleset is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="ruleset_not_found",
            message="no active prediction ruleset found",
            details={},
        )
    row = db.scalar(
        select(RulesetParameterModel)
        .where(
            RulesetParameterModel.ruleset_id == ruleset.id,
            RulesetParameterModel.param_key == rule_code,
        )
        .limit(1)
    )
    if row is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="calibration_rule_not_found",
            message="calibration rule was not found",
            details={"rule_code": rule_code},
        )
    before_value = row.param_value
    try:
        row.param_value = _serialize_calibration_value(payload.value, row.data_type)
    except ValueError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_calibration_rule_value",
            message=str(error),
            details={"rule_code": rule_code, "data_type": row.data_type},
        )
    db.flush()
    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="calibration_rule_updated",
        target_type="calibration_rule",
        target_id=rule_code,
        status="success",
        details={"rule_code": rule_code, "before": before_value, "after": row.param_value},
    )
    db.commit()
    return {
        "data": CalibrationRuleData(
            rule_code=row.param_key,
            value=row.param_value,
            data_type=row.data_type,
            description=CALIBRATION_RULE_DESCRIPTIONS.get(
                row.param_key,
                f"Parametre runtime du ruleset {ruleset.version}.",
            ),
            ruleset_version=ruleset.version,
        ),
        "meta": {"request_id": request_id},
    }
