# Contrats centraux du calcul runtime des conjonctions d'etoiles fixes.
"""Regles immutables appliquees aux contacts d'etoiles fixes."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from math import isfinite
from typing import Any

DEFAULT_FIXED_STAR_CONJUNCTION_MAX_ORB_DEG = 1.0
DEFAULT_FIXED_STAR_CONJUNCTION_RULE_CODE = "default_fixed_star_conjunction"


@dataclass(frozen=True, slots=True)
class FixedStarOrbOverrideRuntimeData:
    """Surcharge nommee d'orbe pour une etoile fixe ou une categorie."""

    code: str
    orb_deg: float

    def __iter__(self) -> Iterator[str | float]:
        """Permet un depaquetage uniforme des surcharges d'orbe."""
        yield self.code
        yield self.orb_deg


@dataclass(frozen=True, slots=True)
class FixedStarConjunctionRulesRuntimeData:
    """Regles d'orbe centralisees pour les contacts d'etoiles fixes."""

    default_max_orb_deg: float = DEFAULT_FIXED_STAR_CONJUNCTION_MAX_ORB_DEG
    orb_by_star_code: tuple[FixedStarOrbOverrideRuntimeData | tuple[Any, ...], ...] = ()
    orb_by_category: tuple[FixedStarOrbOverrideRuntimeData | tuple[Any, ...], ...] = ()
    default_rule_code: str = DEFAULT_FIXED_STAR_CONJUNCTION_RULE_CODE

    def __post_init__(self) -> None:
        """Valide les orbes sans accepter de seuil local implicite."""
        if not isfinite(self.default_max_orb_deg) or self.default_max_orb_deg < 0.0:
            raise ValueError("fixed star rules require a positive default orb")
        if not self.default_rule_code.strip():
            raise ValueError("fixed star rules require a default rule code")
        _validate_overrides(self.orb_by_star_code, "star")
        _validate_overrides(self.orb_by_category, "category")

    def resolve_for(self, *, star_code: str, categories: tuple[str, ...]) -> tuple[float, str]:
        """Retourne l'orbe applicable et le code de regle associe."""
        normalized_star_code = star_code.strip().lower()
        for code, orb in self.orb_by_star_code:
            if code.strip().lower() == normalized_star_code:
                return orb, f"fixed_star:{normalized_star_code}"
        normalized_categories = {category.strip().lower() for category in categories}
        for category, orb in self.orb_by_category:
            normalized_category = category.strip().lower()
            if normalized_category in normalized_categories:
                return orb, f"fixed_star_category:{normalized_category}"
        return self.default_max_orb_deg, self.default_rule_code


def _validate_overrides(
    overrides: tuple[FixedStarOrbOverrideRuntimeData | tuple[Any, ...], ...],
    label: str,
) -> None:
    """Valide les surcharges nommees des regles d'orbe."""
    seen_codes: set[str] = set()
    for code, orb in overrides:
        normalized_code = code.strip().lower()
        if not normalized_code:
            raise ValueError(f"fixed star rules reject empty {label} code")
        if normalized_code in seen_codes:
            raise ValueError(f"fixed star rules reject duplicate {label} code")
        if not isfinite(orb) or orb < 0.0:
            raise ValueError(f"fixed star rules require positive {label} orb")
        seen_codes.add(normalized_code)
