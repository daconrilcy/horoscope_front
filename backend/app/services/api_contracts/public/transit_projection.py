"""Contrats publics pour la projection client des transits."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TransitProjectionStatus = Literal[
    "available",
    "degraded",
    "unavailable",
    "unauthorized",
    "proof_blocked",
]


class TransitProjectionFact(BaseModel):
    """Référence de fait lisible par le client, sans charge runtime interne."""

    ref_id: str
    label: str
    source: str


class TransitProjectionContent(BaseModel):
    """Sections client autorisées selon le plan B2C."""

    sections: dict[str, str] = Field(default_factory=dict)
    depth: Literal["free", "basic", "premium"]


class TransitProjectionResponse(BaseModel):
    """Réponse publique unique de la projection transit contrôlée."""

    projection_id: Literal["transit_client_projection_v1"]
    status: TransitProjectionStatus
    plan_code: Literal["free", "basic", "premium"]
    content: TransitProjectionContent
    supporting_facts: list[TransitProjectionFact] = Field(default_factory=list)
    proof_refs: list[str] = Field(default_factory=list)
    projection_hash: str
    degraded_reason: str | None = None
    upgrade_hint: str | None = None
