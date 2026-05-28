# Contrats du materiau interpretatif theme astral.
"""DTO immuables du bloc `interpretation_material` transmis au LLM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

INTERPRETATION_MATERIAL_KEYS = (
    "planet_sign_interpretations",
    "planet_house_interpretations",
    "aspect_interpretations",
    "dominant_themes",
    "tensions",
    "resources",
    "integration_levers",
    "warnings",
)

InterpretationMaterialKey = Literal[
    "planet_sign_interpretations",
    "planet_house_interpretations",
    "aspect_interpretations",
    "dominant_themes",
    "tensions",
    "resources",
    "integration_levers",
    "warnings",
]
DeliveryProfile = Literal["free", "basic", "premium"]


@dataclass(frozen=True, slots=True)
class InterpretationMaterialSource:
    """Texte source audite disponible pour un fait astrologique calcule."""

    section: InterpretationMaterialKey
    source_owner: str
    source_id: str
    source_version: str
    theme: str
    keywords: tuple[str, ...]
    risk: str
    resource: str
    base_weight: float
    planet_code: str | None = None
    sign_code: str | None = None
    house_number: int | None = None
    aspect_code: str | None = None
    dominance_code: str | None = None
    condition_code: str | None = None
    interpretive_text: str | None = None
    writing_hint: str | None = None

    @property
    def source_ref(self) -> str:
        """Expose une reference compacte et stable vers le texte source."""
        return f"{self.source_owner}:{self.source_id}@{self.source_version}"


@dataclass(frozen=True, slots=True)
class InterpretationMaterialItem:
    """Item selectionne, toujours rattache a une source et a un fait."""

    source_ref: str
    fact_ref: str
    theme: str
    keywords: tuple[str, ...]
    risk: str
    resource: str
    weight: float
    selection_reason: str
    interpretive_text: str | None = None
    writing_hint: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Serialise l'item dans le contrat JSON attendu."""
        payload: dict[str, object] = {
            "source_ref": self.source_ref,
            "fact_ref": self.fact_ref,
            "theme": self.theme,
            "keywords": list(self.keywords),
            "risk": self.risk,
            "resource": self.resource,
            "weight": self.weight,
            "selection_reason": self.selection_reason,
        }
        if self.interpretive_text is not None:
            payload["interpretive_text"] = self.interpretive_text
        else:
            payload["writing_hint"] = self.writing_hint
        return payload


@dataclass(frozen=True, slots=True)
class InterpretationMaterialBlock:
    """Bloc stable dont les cles ne varient pas selon le profil de livraison."""

    planet_sign_interpretations: tuple[InterpretationMaterialItem, ...] = ()
    planet_house_interpretations: tuple[InterpretationMaterialItem, ...] = ()
    aspect_interpretations: tuple[InterpretationMaterialItem, ...] = ()
    dominant_themes: tuple[InterpretationMaterialItem, ...] = ()
    tensions: tuple[InterpretationMaterialItem, ...] = ()
    resources: tuple[InterpretationMaterialItem, ...] = ()
    integration_levers: tuple[InterpretationMaterialItem, ...] = ()
    warnings: tuple[InterpretationMaterialItem, ...] = ()

    def to_payload(self) -> dict[str, list[dict[str, object]]]:
        """Retourne un dictionnaire JSON avec toutes les cles contractuelles."""
        return {
            key: [item.to_payload() for item in getattr(self, key)]
            for key in INTERPRETATION_MATERIAL_KEYS
        }
