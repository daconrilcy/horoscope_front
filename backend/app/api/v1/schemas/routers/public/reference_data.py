"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

from typing import Any
from fastapi import APIRouter, Body, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, get_optional_authenticated_user
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.reference_data_service import ReferenceDataService, ReferenceDataServiceError

router = APIRouter(prefix="/v1/reference-data", tags=["reference-data"])


class ResponseMeta(BaseModel):
    request_id: str


class CloneReferenceVersionPayload(BaseModel):
    source_version: str
    new_version: str
