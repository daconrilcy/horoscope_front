"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class RepairBlockerPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    account_id: int
    company_name: str
    reason: str
    recommended_action: str


class RepairRunData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    accounts_scanned: int
    plans_created: int
    bindings_created: int
    quotas_created: int
    skipped_already_canonical: int
    remaining_blockers: list[RepairBlockerPayload]
    dry_run: bool


class RepairRunResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: RepairRunData
    meta: ResponseMeta


class SetAdminUserRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    account_id: int
    user_id: int


class SetAdminUserResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    account_id: int
    user_id: int
    status: str


class ClassifyZeroUnitsRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    canonical_plan_id: int
    access_mode: Literal["disabled", "unlimited", "quota"]
    quota_limit: int | None = Field(default=None, ge=1)


class ClassifyZeroUnitsResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    canonical_plan_id: int
    access_mode: str
    quota_limit: int | None
    status: str
