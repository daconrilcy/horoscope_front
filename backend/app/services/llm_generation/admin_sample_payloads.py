"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.api.v1.constants import BLOCKED_CATEGORIES, LOCALE_PATTERN
from app.api.v1.schemas.routers.admin.llm.error_codes import AdminLlmErrorCode
from app.api.v1.schemas.routers.admin.llm.sample_payloads import AdminLlmSamplePayload
from app.core.exceptions import ApplicationError
from app.core.sensitive_data import classify_field
from app.domain.llm.governance.feature_taxonomy import (
    is_supported_feature,
    normalize_feature,
    normalize_plan_scope,
    normalize_subfeature,
)
from app.infra.db.models.llm.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.models.user import UserModel
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService


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


def _normalize_scope_value(value: str | None) -> str:
    """Normalise une dimension optionnelle de scope vers la valeur globale."""
    if value is None:
        return ""
    normalized = value.strip()
    if not normalized:
        return ""
    return normalized


def _normalize_scope_dimensions(
    feature: str,
    subfeature: str | None,
    plan: str | None,
) -> tuple[str, str]:
    """Aligne le scope admin sur les clés canoniques réellement utilisées au runtime."""
    normalized_subfeature = normalize_subfeature(feature, subfeature)
    normalized_plan = normalize_plan_scope(plan)
    return normalized_subfeature or "", normalized_plan


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
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
    *, request_id: str, feature: str, subfeature: str, plan: str, locale: str
) -> Any:
    return _raise_error(
        request_id=request_id,
        code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NAME_CONFLICT.value,
        message="a sample payload with this name already exists for this canonical scope",
        details={"feature": feature, "subfeature": subfeature, "plan": plan, "locale": locale},
    )


def _sample_payload_default_conflict_response(
    *, request_id: str, feature: str, subfeature: str, plan: str, locale: str
) -> Any:
    return _raise_error(
        request_id=request_id,
        code=AdminLlmErrorCode.SAMPLE_PAYLOAD_DEFAULT_CONFLICT.value,
        message="another default sample payload already exists for this canonical scope",
        details={"feature": feature, "subfeature": subfeature, "plan": plan, "locale": locale},
    )


def _sample_payload_generic_conflict_response(
    *, request_id: str, feature: str, subfeature: str, plan: str, locale: str
) -> Any:
    return _raise_error(
        request_id=request_id,
        code=AdminLlmErrorCode.SAMPLE_PAYLOAD_CONFLICT.value,
        message="sample payload update conflicts with existing data",
        details={"feature": feature, "subfeature": subfeature, "plan": plan, "locale": locale},
    )


def _find_name_conflict(
    db: Session,
    *,
    feature: str,
    subfeature: str,
    plan: str,
    locale: str,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> LlmSamplePayloadModel | None:
    stmt = (
        select(LlmSamplePayloadModel)
        .where(LlmSamplePayloadModel.feature == feature)
        .where(LlmSamplePayloadModel.subfeature == subfeature)
        .where(LlmSamplePayloadModel.plan == plan)
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
    subfeature: str,
    plan: str,
    locale: str,
    exclude_id: uuid.UUID | None = None,
) -> LlmSamplePayloadModel | None:
    stmt = (
        select(LlmSamplePayloadModel)
        .where(LlmSamplePayloadModel.feature == feature)
        .where(LlmSamplePayloadModel.subfeature == subfeature)
        .where(LlmSamplePayloadModel.plan == plan)
        .where(LlmSamplePayloadModel.locale == locale)
        .where(LlmSamplePayloadModel.is_default == True)  # noqa: E712
    )
    if exclude_id is not None:
        stmt = stmt.where(LlmSamplePayloadModel.id != exclude_id)
    return db.scalar(stmt.limit(1))
