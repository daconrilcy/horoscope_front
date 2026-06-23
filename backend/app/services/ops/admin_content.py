"""Logique admin des textes et feature flags applicatifs."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.api_constants import (
    DEFAULT_CONFIG_TEXTS,
)
from app.core.auth_context import AuthenticatedUser
from app.core.exceptions import ApplicationError
from app.infra.db.models.config_text import ConfigTextModel
from app.services.api_contracts.admin.content import (
    AdminFeatureFlagData,
    ConfigTextData,
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
