"""Contrats runtime canoniques des aspects astrologiques.

Ce module porte les faits aspect enrichis, produits par le domaine astrology et
consommes par les projections ou interpretations sans recomposition locale.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.astrology.interpretation.aspect_strength_contracts import (
    AspectStrengthRuntimeData,
)
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectInterpretiveProfileRuntimeData,
)
from app.domain.astrology.runtime.aspect_modifiers import (
    AspectModifierRuntimeData,
    AspectStructuralModifierRuntimeData,
)


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
class AspectMetadataRuntimeData:
    """Metadonnees de classification runtime de l'aspect."""

    is_major: bool
    is_exact: bool
    is_tight: bool


@dataclass(frozen=True, slots=True)
class AspectRuntimeData:
    """Facade runtime structurelle conservee pour compatibilite interne bornee."""

    aspect: AspectIdentityRuntimeData
    participants: AspectParticipantsRuntimeData
    orb: AspectOrbRuntimeData
    metadata: AspectMetadataRuntimeData
    strength: AspectStrengthRuntimeData
    phase: AspectPhaseRuntimeData | None = None
    modifiers: tuple[AspectModifierRuntimeData, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AspectStructuralRuntimeData:
    """Contrat structurel pur d'un aspect, sans hint interpretatif."""

    aspect: AspectIdentityRuntimeData
    participants: AspectParticipantsRuntimeData
    orb: AspectOrbRuntimeData
    metadata: AspectMetadataRuntimeData
    strength: AspectStrengthRuntimeData
    phase: AspectPhaseRuntimeData | None = None
    modifiers: tuple[AspectStructuralModifierRuntimeData, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AspectInterpretiveHintsRuntimeData:
    """Hints interpretatifs types et sources pour un aspect structurel."""

    aspect_code: str
    default_valence: str
    interpretive_valence: str
    energy_type: str
    semantic_axes: tuple[str, ...] = ()
    growth_axes: tuple[str, ...] = ()
    shadow_axes: tuple[str, ...] = ()
    relationship_axes: tuple[str, ...] = ()
    interpretive_weight: float | None = None
    source_profile_code: str | None = None
    source_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Valide que les hints restent explicites, sources et non narratifs."""
        required_values = (
            self.aspect_code,
            self.default_valence,
            self.interpretive_valence,
            self.energy_type,
        )
        if any(not value.strip() for value in required_values):
            raise ValueError("aspect interpretive hints require non-empty core values")
        if not self.source_codes:
            raise ValueError("aspect interpretive hints require source_codes")
        if self.interpretive_weight is not None and self.interpretive_weight < 0.0:
            raise ValueError("aspect interpretive hints weight must be positive")


def project_structural_aspect_runtime(runtime: AspectRuntimeData) -> AspectStructuralRuntimeData:
    """Projette le runtime legacy vers le contrat structurel cible CS-229."""
    return AspectStructuralRuntimeData(
        aspect=runtime.aspect,
        participants=runtime.participants,
        orb=runtime.orb,
        metadata=runtime.metadata,
        strength=runtime.strength,
        phase=runtime.phase,
        modifiers=tuple(
            AspectStructuralModifierRuntimeData(
                modifier_type=modifier.modifier_type,
                source=modifier.source,
                intensity=modifier.intensity,
                reason=modifier.reason,
                applies_to=modifier.applies_to,
            )
            for modifier in runtime.modifiers
        ),
    )


def resolve_aspect_interpretive_hints(
    structural: AspectStructuralRuntimeData,
    profile: AspectInterpretiveProfileRuntimeData,
) -> AspectInterpretiveHintsRuntimeData:
    """Assemble les hints interpretatifs depuis le runtime structurel et le profil."""
    if structural.aspect.code != profile.aspect_code:
        raise ValueError("aspect interpretive profile does not match structural aspect")
    source_profile_code = profile.source_profile_code or profile.aspect_code
    source_codes = (
        f"aspect:{structural.aspect.code}",
        f"aspect_profile:{source_profile_code}",
    )
    if profile.reference_version:
        source_codes += (f"reference:{profile.reference_version}",)
    return AspectInterpretiveHintsRuntimeData(
        aspect_code=profile.aspect_code,
        default_valence=profile.default_valence,
        interpretive_valence=profile.interpretive_valence,
        energy_type=profile.energy_type,
        semantic_axes=profile.semantic_axes,
        growth_axes=profile.growth_axes,
        shadow_axes=profile.shadow_axes,
        relationship_axes=profile.relationship_axes,
        source_profile_code=source_profile_code,
        source_codes=source_codes,
    )


class AspectInterpretiveHintResolver:
    """Resolver dedie aux hints interpretatifs courts des aspects."""

    def resolve(
        self,
        structural: AspectStructuralRuntimeData,
        profile: AspectInterpretiveProfileRuntimeData,
    ) -> AspectInterpretiveHintsRuntimeData:
        """Produit les hints sans recalculer angle, orbe, seuil ou force."""
        return resolve_aspect_interpretive_hints(structural, profile)
