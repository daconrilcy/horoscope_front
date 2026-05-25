# Contrats publics du endpoint generique de projections B2C.
"""Definit la requete et la reponse publiques de `POST /v1/astrology/projections`."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.services.api_contracts.public.astrology_engine import NatalCalculateRequest

PublicProjectionType = Literal[
    "structured_facts_v1",
    "beginner_summary_v1",
    "client_interpretation_projection_v1",
]


class ProjectionCommandRequest(BaseModel):
    """Requete publique de generation d'une projection B2C."""

    model_config = ConfigDict(extra="forbid")

    chart_id: str | None = Field(default=None, min_length=1)
    birth_input: NatalCalculateRequest | None = None
    projection_type: str = Field(min_length=1)
    projection_version: str = Field(min_length=1)
    persist: bool = False


class ProjectionCommandMetadata(BaseModel):
    """Metadonnees publiques associees a la projection generee."""

    source: Literal["chart_id", "birth_input"]
    plan_code: Literal["free", "basic", "premium"]
    request_id: str
    persisted_id: int | None = None


class ProjectionCommandResponse(BaseModel):
    """Reponse publique unique du endpoint de projections B2C."""

    chart_id: str
    projection_type: PublicProjectionType
    projection_version: str
    persisted: bool
    projection_hash: str
    payload: dict[str, Any]
    metadata: ProjectionCommandMetadata
