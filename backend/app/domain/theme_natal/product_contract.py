# Commentaire global: definit le contrat produit ferme avant toute generation LLM.
"""Contrats produit purs pour les actions de lecture natale."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

THEME_NATAL_READING_FEATURE = "theme_natal"
THEME_NATAL_READING_CONTRACT_KEYS: dict["ThemeNatalOutputVariant", str] = {
    # La cle est le pont versionne vers une future selection de contrat de generation.
    # Elle ne selectionne pas directement un provider, un modele ou un prompt legacy.
    "free_preview": "theme_natal.reading.free_preview.v1",
    "basic_full_reading": "theme_natal.reading.basic_full_reading.v1",
    "premium_full_reading": "theme_natal.reading.premium_full_reading.v1",
}


class _StrictProductModel(BaseModel):
    """Base stricte pour refuser les champs techniques hors contrat produit."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ThemeNatalReadingAction(StrEnum):
    """Actions metier acceptees pour une lecture natale theme natal."""

    PREVIEW = "preview"
    GENERATE_FULL = "generate_full"
    REGENERATE = "regenerate"
    DOWNLOAD = "download"


class ThemeNatalReadingKind(StrEnum):
    """Nature stable de lecture exposee par le contrat produit."""

    NATAL_READING = "natal_reading"


class ThemeNatalOutputVariant(StrEnum):
    """Variantes de sortie produit autorisees pour le theme natal."""

    FREE_PREVIEW = "free_preview"
    BASIC_FULL_READING = "basic_full_reading"
    PREMIUM_FULL_READING = "premium_full_reading"


class ThemeNatalPersonaMode(StrEnum):
    """Mode persona separe du schema de sortie et de la variante produit."""

    NONE = "none"
    SINGLE = "single"
    MULTI = "multi"


class ThemeNatalEntitlementTier(StrEnum):
    """Tier backend issu d'un entitlement frais, sans choix frontend direct."""

    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class ThemeNatalReadingDecisionStatus(StrEnum):
    """Vocabulaire ferme des decisions du resolver produit."""

    ALLOWED = "allowed"
    LOCKED_PAYWALL = "locked_paywall"
    EXISTING_READING = "existing_reading"
    GENERATE_WITH_CONTRACT_KEY = "generate_with_contract_key"
    INVALID_REQUEST = "invalid_request"


class ThemeNatalReadingProductEntitlement(_StrictProductModel):
    """Droit backend deja resolu pour l'action produit demandee."""

    tier: ThemeNatalEntitlementTier
    granted: bool = True
    reason_code: str = "granted"


class ThemeNatalReadingActionRequest(_StrictProductModel):
    """Entree metier du resolver, construite cote backend depuis des donnees deja validees."""

    user_id: int = Field(gt=0)
    chart_id: int = Field(gt=0)
    action: ThemeNatalReadingAction
    entitlement: ThemeNatalReadingProductEntitlement
    locale: str = Field(min_length=2)
    persona_mode: ThemeNatalPersonaMode = ThemeNatalPersonaMode.NONE
    existing_reading_id: int | None = Field(default=None, gt=0)


class ThemeNatalReadingProductContract(_StrictProductModel):
    """Contrat produit transmis a la couche de generation apres autorisation."""

    feature: Literal["theme_natal"] = THEME_NATAL_READING_FEATURE
    reading_kind: ThemeNatalReadingKind = ThemeNatalReadingKind.NATAL_READING
    action: ThemeNatalReadingAction
    output_variant: ThemeNatalOutputVariant
    persona_mode: ThemeNatalPersonaMode
    locale: str = Field(min_length=2)
    entitlement: ThemeNatalReadingProductEntitlement
    contract_key: str | None = None


class ThemeNatalReadingProductDecision(_StrictProductModel):
    """Resultat ferme du resolver produit sans effet de bord."""

    status: ThemeNatalReadingDecisionStatus
    contract: ThemeNatalReadingProductContract | None = None
    existing_reading_id: int | None = Field(default=None, gt=0)
    reason_code: str | None = None

    @model_validator(mode="after")
    def _validate_contract_shape(self) -> "ThemeNatalReadingProductDecision":
        """Verifie que la cle de contrat n'est exposee que pour les generations."""
        if self.status is ThemeNatalReadingDecisionStatus.GENERATE_WITH_CONTRACT_KEY:
            if self.contract is None or self.contract.contract_key is None:
                raise ValueError("generation decisions require a contract key")
            return self
        if self.contract is not None and self.contract.contract_key is not None:
            raise ValueError("contract_key is only emitted for generation decisions")
        return self
