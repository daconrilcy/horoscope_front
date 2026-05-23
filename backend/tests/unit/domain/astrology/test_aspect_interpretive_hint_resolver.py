"""Tests du resolver de hints interpretatifs des aspects CS-230."""

from __future__ import annotations

import inspect

from app.domain.astrology.interpretation.aspect_strength_contracts import (
    AspectStrengthLevel,
    AspectStrengthReason,
    AspectStrengthRuntimeData,
)
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectInterpretiveProfileRuntimeData,
)
from app.domain.astrology.runtime.aspect_runtime_data import (
    AspectIdentityRuntimeData,
    AspectInterpretiveHintResolver,
    AspectMetadataRuntimeData,
    AspectOrbRuntimeData,
    AspectParticipantsRuntimeData,
    AspectStructuralRuntimeData,
)


def _structural_runtime() -> AspectStructuralRuntimeData:
    """Construit un runtime structurel minimal pour les tests."""
    return AspectStructuralRuntimeData(
        aspect=AspectIdentityRuntimeData(code="trine", family="major", angle=120.0),
        participants=AspectParticipantsRuntimeData(planet_a="sun", planet_b="moon"),
        orb=AspectOrbRuntimeData(exact=0.4, max=6.0, ratio=0.0667, strength_level="strong"),
        metadata=AspectMetadataRuntimeData(is_major=True, is_exact=False, is_tight=True),
        strength=AspectStrengthRuntimeData(
            normalized_score=0.9,
            level=AspectStrengthLevel.STRONG,
            is_exact=False,
            is_tight=True,
            reasons=(AspectStrengthReason.TIGHT_ORB,),
        ),
    )


def test_resolver_returns_hints_from_profile_without_mutating_structure() -> None:
    """Le resolver produit les hints depuis le profil dedie uniquement."""
    structural = _structural_runtime()
    profile = AspectInterpretiveProfileRuntimeData(
        aspect_code="trine",
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
        semantic_axes=("cooperation",),
        source_profile_code="modern-trine",
        reference_version="v1",
    )

    hints = AspectInterpretiveHintResolver().resolve(structural, profile)

    assert hints.aspect_code == "trine"
    assert hints.energy_type == "harmonious_flow"
    assert hints.source_codes == (
        "aspect:trine",
        "aspect_profile:modern-trine",
        "reference:v1",
    )
    assert structural.orb.exact == 0.4
    assert structural.strength.normalized_score == 0.9


def test_resolver_does_not_implement_geometric_calculation() -> None:
    """Le resolver ne contient pas de calcul d'angle, d'orbe ou de force."""
    source = inspect.getsource(AspectInterpretiveHintResolver)

    assert "angular_distance" not in source
    assert "orb_used" not in source
    assert "orb_max" not in source
    assert "AspectStrengthEvaluator" not in source
