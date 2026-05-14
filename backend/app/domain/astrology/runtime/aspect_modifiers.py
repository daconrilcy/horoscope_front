"""Contrats runtime des modifiers astrologiques d'aspect.

Les modifiers explicitent les facteurs locaux sans melanger force technique,
dominance structurelle, interpretation et scoring produit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AspectModifierType(StrEnum):
    """Type canonique d'un modifier runtime applique a un aspect."""

    LUMINARY = "luminary"
    ANGULAR = "angular"
    EXACT_ORB = "exact_orb"
    TIGHT_ORB = "tight_orb"
    APPLYING = "applying"
    SEPARATING = "separating"
    RETROGRADE = "retrograde"
    CHART_RULER = "chart_ruler"
    TRANSPERSONAL = "transpersonal"


@dataclass(frozen=True, slots=True)
class AspectModifierRuntimeData:
    """Modifier type qui documente sa source et son intensite locale."""

    modifier_type: AspectModifierType
    source: str
    intensity: float
    reason: str | None = None
    applies_to: tuple[str, ...] = ()
    interpretive_weight: float | None = None

    def __post_init__(self) -> None:
        """Borne les valeurs locales pour garder la taxonomie exploitable."""
        if not self.source.strip():
            raise ValueError("aspect modifier source is required")
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("aspect modifier intensity must be between 0 and 1")
        if self.interpretive_weight is not None and self.interpretive_weight < 0.0:
            raise ValueError("aspect modifier interpretive_weight must be positive")


@dataclass(frozen=True, slots=True)
class AspectRuntimeWeightTaxonomy:
    """Taxonomie nommee pour eviter un poids aspect universel ambigu."""

    technical_strength: str = "AspectStrengthEvaluator.normalized_score"
    structural_dominance: str = "DominantAspectEvaluator.dominance_score"
    interpretive_weight: str = "AspectModifierRuntimeData.interpretive_weight"
    product_owner: str = "domain/prediction owns prediction weighting"
