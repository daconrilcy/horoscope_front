"""Structures runtime riches des maisons natales."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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


@dataclass(slots=True)
class HouseStrengthRuntimeData:
    """Score interprétatif déterministe de dominance d'une maison."""

    score: float
    dominant: bool
    reasons: list[str]


@dataclass(slots=True)
class HouseRuntimeData:
    """Maison natale enrichie pour les moteurs IA, narratifs et prédictifs."""

    number: int
    cusp_longitude: float
    cusp_sign: str | None = None
    # TODO legacy compatibility field planned removal: use `cusp_sign`.
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
        if self.axis is None:
            self.axis = HouseAxisRuntimeData(opposite_house=0, theme="unknown")
        if self.strength is None:
            self.strength = HouseStrengthRuntimeData(
                score=0.0,
                dominant=False,
                reasons=["baseline_house"],
            )
