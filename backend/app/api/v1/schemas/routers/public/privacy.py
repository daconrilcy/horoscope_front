"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.privacy_service import (
    PrivacyComplianceEvidenceData,
    PrivacyRequestData,
)

router = APIRouter(prefix="/v1/privacy", tags=["privacy"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class PrivacyApiResponse(BaseModel):
    data: PrivacyRequestData
    meta: ResponseMeta


class PrivacyEvidenceApiResponse(BaseModel):
    data: PrivacyComplianceEvidenceData
    meta: ResponseMeta


class DeleteRequestPayload(BaseModel):
    confirmation: str
