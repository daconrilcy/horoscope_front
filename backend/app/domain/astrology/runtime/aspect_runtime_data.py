"""Contrats runtime canoniques des aspects astrologiques.

Ce module porte les faits aspect enrichis, produits par le domaine astrology et
consommes par les projections ou interpretations sans recomposition locale.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.astrology.interpretation.aspect_strength_contracts import (
    AspectStrengthRuntimeData,
)
from app.domain.astrology.runtime.aspect_modifiers import AspectModifierRuntimeData


@dataclass(frozen=True, slots=True)
class AspectIdentityRuntimeData:
    """Identite astrologique stable de l'aspect."""

    code: str
    family: str
    angle: float

    def __post_init__(self) -> None:
        """Valide les identifiants minimaux de l'aspect."""
        if not self.code.strip() or not self.family.strip():
            raise ValueError("aspect identity requires code and family")


@dataclass(frozen=True, slots=True)
class AspectParticipantsRuntimeData:
    """Participants canoniques d'un aspect."""

    planet_a: str
    planet_b: str

    def __post_init__(self) -> None:
        """Valide les deux participants canoniques."""
        if not self.planet_a.strip() or not self.planet_b.strip():
            raise ValueError("aspect participants require two planet codes")


@dataclass(frozen=True, slots=True)
class AspectOrbRuntimeData:
    """Orbe resolue et ratio derive du calculateur canonique."""

    exact: float
    max: float
    ratio: float
    strength_level: str

    def __post_init__(self) -> None:
        """Garantit une orbe positive et un ratio normalise."""
        if self.max <= 0.0 or self.exact < 0.0:
            raise ValueError("aspect orb requires positive max and non-negative exact")
        if not 0.0 <= self.ratio <= 1.0:
            raise ValueError("aspect orb ratio must be between 0 and 1")
        if not self.strength_level.strip():
            raise ValueError("aspect orb requires strength_level")


@dataclass(frozen=True, slots=True)
class AspectPhaseRuntimeData:
    """Phase applicative disponible pour un aspect."""

    type: str

    def __post_init__(self) -> None:
        """Valide la phase textuelle explicite."""
        if not self.type.strip():
            raise ValueError("aspect phase type is required")


@dataclass(frozen=True, slots=True)
class AspectInterpretationRuntimeData:
    """Indices interpretatifs courts attaches au runtime aspect."""

    default_valence: str
    interpretive_valence: str
    energy_type: str

    def __post_init__(self) -> None:
        """Valide les indices interpretatifs courts."""
        if (
            not self.default_valence.strip()
            or not self.interpretive_valence.strip()
            or not self.energy_type.strip()
        ):
            raise ValueError("aspect interpretation runtime requires non-empty values")


@dataclass(frozen=True, slots=True)
class AspectMetadataRuntimeData:
    """Metadonnees de classification runtime de l'aspect."""

    is_major: bool
    is_exact: bool
    is_tight: bool


@dataclass(frozen=True, slots=True)
class AspectRuntimeData:
    """Faits enrichis canoniques pour un aspect natal ou inter-chart."""

    aspect: AspectIdentityRuntimeData
    participants: AspectParticipantsRuntimeData
    orb: AspectOrbRuntimeData
    metadata: AspectMetadataRuntimeData
    strength: AspectStrengthRuntimeData
    phase: AspectPhaseRuntimeData | None = None
    interpretation: AspectInterpretationRuntimeData | None = None
    modifiers: tuple[AspectModifierRuntimeData, ...] = field(default_factory=tuple)
