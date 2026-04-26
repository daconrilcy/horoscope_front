"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ops.feature_flag_service import (
    FeatureFlagData,
    FeatureFlagListData,
)

router = APIRouter(prefix="/v1/ops/feature-flags", tags=["ops-feature-flags"])


class ResponseMeta(BaseModel):
    request_id: str


class FeatureFlagListApiResponse(BaseModel):
    data: FeatureFlagListData
    meta: ResponseMeta


class FeatureFlagApiResponse(BaseModel):
    data: FeatureFlagData
    meta: ResponseMeta
