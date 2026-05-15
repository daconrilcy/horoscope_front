"""Assemblage du runtime canonique des aspects.

Le builder transforme les resultats plats en faits runtime sans reimplementer
la resolution d'orbe, deja portee par le calculateur d'aspects.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.astrology.celestial_runtime_catalog import (
    LIGHT_BODY_CODES,
    OUTER_PLANET_CODES,
    is_major_aspect_code,
)
from app.domain.astrology.interpretation.aspect_strength import (
    AspectStrengthEvaluator,
    aspect_family,
)
from app.domain.astrology.runtime.aspect_modifiers import (
    AspectModifierRuntimeData,
    AspectModifierType,
)
from app.domain.astrology.runtime.aspect_runtime_data import (
    AspectIdentityRuntimeData,
    AspectInterpretationRuntimeData,
    AspectMetadataRuntimeData,
    AspectOrbRuntimeData,
    AspectParticipantsRuntimeData,
    AspectPhaseRuntimeData,
    AspectRuntimeData,
)

VALENCE_BY_ASPECT = {
    "conjunction": "contextual",
    "opposition": "polarized",
    "trine": "harmonious",
    "square": "dynamic",
    "sextile": "constructive",
}
ENERGY_BY_ASPECT = {
    "conjunction": "fusion",
    "opposition": "polarity",
    "trine": "flow",
    "square": "friction",
    "sextile": "opportunity",
}


class AspectLike(Protocol):
    """Interface minimale d'un resultat aspect consommable par le builder."""

    aspect_code: str
    planet_a: str
    planet_b: str
    angle: float
    orb: float
    orb_used: float | None
    orb_max: float | None


def build_aspect_runtime_data(aspect: AspectLike) -> AspectRuntimeData:
    """Construit le runtime enrichi depuis un aspect plat existant."""
    code = aspect.aspect_code.strip().lower()
    orb_used = float(aspect.orb_used if aspect.orb_used is not None else aspect.orb)
    orb_max = float(aspect.orb_max if aspect.orb_max is not None else orb_used)
    safe_orb_max = max(orb_max, 0.01)
    ratio = round(min(max(orb_used / safe_orb_max, 0.0), 1.0), 4)
    participants = (aspect.planet_a.strip().lower(), aspect.planet_b.strip().lower())
    strength = AspectStrengthEvaluator().evaluate(
        aspect_code=code,
        orb_used=orb_used,
        orb_max=safe_orb_max,
        participants=participants,
    )
    modifiers = _build_modifiers(strength.is_exact, strength.is_tight, participants)
    return AspectRuntimeData(
        aspect=AspectIdentityRuntimeData(
            code=code,
            family=aspect_family(code),
            angle=float(aspect.angle),
        ),
        participants=AspectParticipantsRuntimeData(
            planet_a=participants[0],
            planet_b=participants[1],
        ),
        orb=AspectOrbRuntimeData(
            exact=round(orb_used, 6),
            max=round(safe_orb_max, 6),
            ratio=ratio,
            strength_level=strength.level.value,
        ),
        phase=AspectPhaseRuntimeData(type="unknown"),
        interpretation=AspectInterpretationRuntimeData(
            default_valence=VALENCE_BY_ASPECT.get(code, "contextual"),
            interpretive_valence=VALENCE_BY_ASPECT.get(code, "contextual"),
            energy_type=ENERGY_BY_ASPECT.get(code, aspect_family(code)),
        ),
        metadata=AspectMetadataRuntimeData(
            is_major=is_major_aspect_code(code),
            is_exact=strength.is_exact,
            is_tight=strength.is_tight,
        ),
        strength=strength,
        modifiers=modifiers,
    )


def _build_modifiers(
    is_exact: bool,
    is_tight: bool,
    participants: tuple[str, str],
) -> tuple[AspectModifierRuntimeData, ...]:
    """Derive les modifiers locaux disponibles sans source externe."""
    modifiers: list[AspectModifierRuntimeData] = []
    if is_exact:
        modifiers.append(
            AspectModifierRuntimeData(
                modifier_type=AspectModifierType.EXACT_ORB,
                source="aspect_strength",
                intensity=1.0,
                applies_to=participants,
            )
        )
    elif is_tight:
        modifiers.append(
            AspectModifierRuntimeData(
                modifier_type=AspectModifierType.TIGHT_ORB,
                source="aspect_strength",
                intensity=0.75,
                applies_to=participants,
            )
        )
    if any(code in LIGHT_BODY_CODES for code in participants):
        modifiers.append(
            AspectModifierRuntimeData(
                modifier_type=AspectModifierType.LUMINARY,
                source="participants",
                intensity=0.8,
                applies_to=tuple(code for code in participants if code in LIGHT_BODY_CODES),
            )
        )
    if all(code in OUTER_PLANET_CODES for code in participants):
        modifiers.append(
            AspectModifierRuntimeData(
                modifier_type=AspectModifierType.TRANSPERSONAL,
                source="participants",
                intensity=0.35,
                applies_to=participants,
            )
        )
    return tuple(modifiers)
