# Commentaire global: contrats HTTP publics des actions produit de lecture theme natal.
"""Schemas Pydantic publics pour les commandes de lecture theme natal."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.theme_natal.product_contract import ThemeNatalReadingAction

ThemeNatalReadingState = Literal["accepted", "generating", "locked", "readonly", "rejected"]


class ThemeNatalReadingCommandRequest(BaseModel):
    """Commande publique limitee a l'intention produit de lecture theme natal."""

    model_config = ConfigDict(extra="forbid")

    chart_id: str = Field(min_length=1)
    action: ThemeNatalReadingAction
    persona_profile_id: UUID | None = None
    locale: str = Field(pattern=r"^[a-z]{2}-[A-Z]{2}$")
    client_request_id: str | None = Field(default=None, min_length=1, max_length=128)


class ThemeNatalReadingCommandResponse(BaseModel):
    """Reponse publique: slot accepte ou etat produit controle."""

    state: ThemeNatalReadingState
    data: dict[str, Any] | None = None
    details: dict[str, Any] = Field(default_factory=dict)
