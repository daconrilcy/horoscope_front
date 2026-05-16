"""Contrats runtime canoniques des signes natals.

Ce module porte les faits calcules d'un signe pour un theme donne, sans label
localise ni logique produit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SignDominanceReason(StrEnum):
    """Raisons canoniques de dominance d'un signe natal."""

    OCCUPANTS_PRESENT = "occupants_present"
    STELLIUM_PRESENT = "stellium_present"
    LUMINARY_PRESENT = "luminary_present"
    ACTIVE_DIGNITY = "active_dignity"
    REFERENCE_PROFILE = "reference_profile"


@dataclass(frozen=True, slots=True)
class SignOccupantRuntimeData:
    """Placement d'un corps celeste dans un signe natal."""

    planet: str
    longitude: float
    house: int | None

    def __post_init__(self) -> None:
        """Valide les donnees minimales du placement."""
        if not self.planet.strip():
            raise ValueError("sign occupant requires a planet code")


@dataclass(frozen=True, slots=True)
class SignDignityRuntimeData:
    """Dignite active d'un occupant dans son signe."""

    planet: str
    dignity_type: str
    system: str
    weight: float
    is_primary: bool

    def __post_init__(self) -> None:
        """Garantit une dignite explicitement sourcee par le referentiel."""
        if not self.planet.strip() or not self.dignity_type.strip() or not self.system.strip():
            raise ValueError("sign dignity requires planet, type and system")


@dataclass(frozen=True, slots=True)
class SignRuntimeData:
    """Faits runtime calcules pour un signe natal."""

    sign: str
    occupants: tuple[SignOccupantRuntimeData, ...]
    weight: float
    dominant: bool
    active_dignities: tuple[SignDignityRuntimeData, ...]
    reasons: tuple[SignDominanceReason, ...]
    synthesis_role: str | None = None
    element: str | None = None
    modality: str | None = None
    polarity: str | None = None

    def __post_init__(self) -> None:
        """Borne le poids et impose un code de signe canonique."""
        if not self.sign.strip():
            raise ValueError("sign runtime requires a sign code")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("sign runtime weight must be between 0 and 1")
        if self.dominant and not self.reasons:
            raise ValueError("dominant sign runtime requires at least one reason")
