"""Contrats JSON canoniques pour les erreurs HTTP de l'API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiErrorBody(BaseModel):
    """Décrit le corps stable d'une erreur API sérialisée."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    details: Any = Field(default_factory=dict)
    request_id: str | None = None


class ApiErrorEnvelope(BaseModel):
    """Enveloppe JSON unique renvoyée par les handlers FastAPI."""

    model_config = ConfigDict(extra="forbid")

    error: ApiErrorBody
