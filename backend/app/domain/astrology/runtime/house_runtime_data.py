"""Structures runtime riches des maisons natales.

Ce module porte uniquement les faits astrologiques calcules pour les maisons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.astrology.interpretation.house_strength_contracts import (
    HouseStrengthLevel,
    HouseStrengthModifiers,
    HouseStrengthReason,
    resolve_house_strength_level,
)
from app.domain.astrology.zodiac import sign_from_longitude


@dataclass(slots=True)
class HouseRulerRuntimeData:
    """Placement runtime du maître planétaire d'une maison."""

    planet: str
    sign: str | None
    house: int | None


@dataclass(slots=True)
class HouseOccupantRuntimeData:
    """Placement runtime d'un occupant planétaire d'une maison."""

    planet: str
    sign: str
    longitude: float
    is_dominant: bool = False


@dataclass(slots=True)
class HouseAxisRuntimeData:
    """Axe miroir reliant une maison à sa maison opposée."""

    opposite_house: int
    theme: str


@dataclass(frozen=True, slots=True)
class HouseStrengthRuntimeData:
    """Contrat de force maison base sur un score normalise et des raisons enumerees."""

    normalized_score: float
    dominant: bool
    reasons: tuple[HouseStrengthReason, ...]
    level: HouseStrengthLevel
    modifiers: HouseStrengthModifiers = field(default_factory=HouseStrengthModifiers)

    @classmethod
    def from_parts(
        cls,
        *,
        normalized_score: float,
        reasons: tuple[HouseStrengthReason, ...],
        modifiers: HouseStrengthModifiers | None = None,
    ) -> HouseStrengthRuntimeData:
        """Construit le contrat en derivant dominance et niveau qualitatif."""
        bounded_score = round(min(max(normalized_score, 0.0), 1.0), 2)
        return cls(
            normalized_score=bounded_score,
            dominant=bounded_score >= 0.6,
            reasons=reasons,
            level=resolve_house_strength_level(bounded_score),
            modifiers=modifiers or HouseStrengthModifiers(),
        )

    @classmethod
    def from_serialized(
        cls,
        *,
        score: float,
        level: str,
        reasons: list[object],
    ) -> HouseStrengthRuntimeData:
        """Reconstruit le contrat runtime depuis la projection JSON publique."""
        contract = cls.from_parts(
            normalized_score=score,
            reasons=tuple(HouseStrengthReason(str(reason)) for reason in reasons),
        )
        if contract.level.value != level:
            raise ValueError("Serialized house strength level does not match score")
        return contract

    @property
    def score(self) -> float:
        """Expose le nom JSON historique pour le score normalise."""
        return self.normalized_score


@dataclass(slots=True)
class HouseRuntimeData:
    """Maison natale enrichie par des faits astrologiques purs."""

    number: int
    cusp_longitude: float
    cusp_sign: str | None = None
    house_kind: str | None = None
    sign: str | None = None
    contained_signs: list[str] = field(default_factory=list)
    intercepted_signs: list[str] = field(default_factory=list)
    ruler: HouseRulerRuntimeData | None = None
    occupants: list[HouseOccupantRuntimeData] = field(default_factory=list)
    axis: HouseAxisRuntimeData | None = None
    strength: HouseStrengthRuntimeData | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Complète les champs dérivables pour accepter les anciens tests."""
        if self.cusp_sign is None and self.sign is not None:
            self.cusp_sign = self.sign
        if self.cusp_sign is None:
            self.cusp_sign = sign_from_longitude(self.cusp_longitude)
        if self.sign is None or self.sign != self.cusp_sign:
            self.sign = self.cusp_sign
        if self.house_kind is None:
            self.house_kind = resolve_house_kind(self.number)
        if self.strength is None:
            self.strength = HouseStrengthRuntimeData.from_parts(
                normalized_score=0.0,
                reasons=(HouseStrengthReason.BASELINE_HOUSE,),
            )


def resolve_house_kind(house_number: int) -> str:
    """Retourne la qualite astrologique canonique d'une maison."""
    if house_number in {1, 4, 7, 10}:
        return "angular"
    if house_number in {2, 5, 8, 11}:
        return "succedent"
    return "cadent"
