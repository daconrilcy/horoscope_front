"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.config import settings
from app.core.rbac import is_valid_role
from app.core.request_id import resolve_request_id
from app.core.security import SecurityError, decode_token
from app.infra.db.session import get_db_session
from app.services.auth_service import AuthResponse, AuthService, AuthServiceError, AuthTokens
from app.services.email.service import EmailService
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/auth", tags=["auth"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthApiResponse(BaseModel):
    data: AuthResponse
    meta: ResponseMeta


class RefreshApiResponse(BaseModel):
    data: AuthTokens
    meta: ResponseMeta


class AuthMeData(BaseModel):
    id: int
    role: str
    email: str
    created_at: str


class AuthMeApiResponse(BaseModel):
    data: AuthMeData
    meta: ResponseMeta
