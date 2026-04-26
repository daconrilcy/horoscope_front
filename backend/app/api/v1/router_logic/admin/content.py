"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.datetime_provider import datetime_provider
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.ops.feature_flag_service import (
    FeatureFlagData,
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
from app.api.v1.schemas.routers.admin.content import *


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
