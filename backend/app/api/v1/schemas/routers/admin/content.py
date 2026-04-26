"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import json
import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel, RulesetParameterModel
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.ops.feature_flag_service import (
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
