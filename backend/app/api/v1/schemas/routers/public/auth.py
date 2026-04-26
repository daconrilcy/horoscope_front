"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.auth_service import AuthResponse, AuthTokens

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
