"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.api_constants import (
    DEFAULT_CONFIG_TEXTS,
    DEFAULT_EDITORIAL_TEMPLATES,
)
from app.core.auth_context import AuthenticatedUser
from app.core.datetime_provider import datetime_provider
from app.core.exceptions import ApplicationError
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.services.api_contracts.admin.content import (
    AdminFeatureFlagData,
    ConfigTextData,
    EditorialTemplateVersionData,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.ops.feature_flag_service import (
    FeatureFlagData,
)


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, object],
    **_: Any,
) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
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
    now = datetime_provider.utcnow()
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


def update_config_text_value(
    db: Session,
    *,
    key: str,
    value: str,
    actor: AuthenticatedUser,
    request_id: str,
) -> ConfigTextData:
    """Met a jour un texte de configuration et journalise l'audit applicatif."""
    _ensure_config_texts_seeded(db)
    row = db.scalar(select(ConfigTextModel).where(ConfigTextModel.key == key).limit(1))
    if row is None:
        _raise_error(
            request_id=request_id,
            code="content_text_not_found",
            message="content text was not found",
            details={"key": key},
        )
    before_value = row.value
    row.value = value
    row.updated_by_user_id = actor.id
    db.flush()
    _record_audit_event(
        db,
        request_id=request_id,
        actor=actor,
        action="content_text_updated",
        target_type="config_text",
        target_id=key,
        status="success",
        details={"content_key": key, "before": before_value, "after": value},
    )
    db.commit()
    db.refresh(row)
    return _to_config_text_data(row)


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
