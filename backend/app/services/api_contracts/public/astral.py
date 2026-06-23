# Commentaire global: contrats publics de la facade Astral backend.
"""Contrats publics de la facade Astral backend."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.services.api_contracts.common import ResponseMeta

AstralPlan = Literal["free", "basic", "premium"]
AstralProduct = Literal["natal_simplified", "natal_full", "horoscope_daily", "horoscope_period"]
AstralPeriod = Literal["daily", "next_7_days"]


class AstralJobCreateRequest(BaseModel):
    """Payload public de soumission d'un job Astral."""

    product: AstralProduct
    plan: AstralPlan = "free"
    period: AstralPeriod | None = None
    birth_profile_id: int | None = None
    client_request_id: str = Field(min_length=8, max_length=128)
    target_language_code: str = Field(default="fr", min_length=2, max_length=16)
    audience_level: str = Field(default="beginner", min_length=1, max_length=32)


class AstralJobApiResponse(BaseModel):
    """Reponse publique enveloppant le statut Astral brut."""

    data: dict[str, Any]
    meta: ResponseMeta


class AstralJobEventsResponse(BaseModel):
    """Reponse de decouverte du flux Mercure associe a un job."""

    data: dict[str, str]
    meta: ResponseMeta
