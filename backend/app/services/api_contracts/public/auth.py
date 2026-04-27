"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.auth_service import AuthResponse, AuthTokens


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class RegisterRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    email: str
    password: str


class LoginRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    email: str
    password: str


class RefreshRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    refresh_token: str


class AuthApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AuthResponse
    meta: ResponseMeta


class RefreshApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AuthTokens
    meta: ResponseMeta


class AuthMeData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    role: str
    email: str
    created_at: str


class AuthMeApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AuthMeData
    meta: ResponseMeta
