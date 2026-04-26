"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
from typing import Any, Literal
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.entitlement_repair_service import (
    B2BEntitlementRepairService,
    RepairValidationError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/ops/b2b/entitlements/repair", tags=["ops-b2b-entitlements"])


class ResponseMeta(BaseModel):
    request_id: str


class RepairBlockerPayload(BaseModel):
    account_id: int
    company_name: str
    reason: str
    recommended_action: str


class RepairRunData(BaseModel):
    accounts_scanned: int
    plans_created: int
    bindings_created: int
    quotas_created: int
    skipped_already_canonical: int
    remaining_blockers: list[RepairBlockerPayload]
    dry_run: bool


class RepairRunResponse(BaseModel):
    data: RepairRunData
    meta: ResponseMeta


class SetAdminUserRequest(BaseModel):
    account_id: int
    user_id: int


class SetAdminUserResponse(BaseModel):
    account_id: int
    user_id: int
    status: str


class ClassifyZeroUnitsRequest(BaseModel):
    canonical_plan_id: int
    access_mode: Literal["disabled", "unlimited", "quota"]
    quota_limit: int | None = Field(default=None, ge=1)


class ClassifyZeroUnitsResponse(BaseModel):
    canonical_plan_id: int
    access_mode: str
    quota_limit: int | None
    status: str
