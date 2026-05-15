"""Tests du builder runtime canonique des aspects."""

import pytest

from app.domain.astrology.builders.aspect_runtime_builder import build_aspect_runtime_data
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.aspect_modifiers import AspectModifierType
from app.domain.astrology.runtime.aspect_runtime_data import (
    AspectIdentityRuntimeData,
    AspectOrbRuntimeData,
    AspectParticipantsRuntimeData,
)

ASPECT_META = {
    "family": "major",
    "is_major": True,
    "is_minor": False,
    "default_valence": "positive",
    "interpretive_valence": "harmonious",
    "energy_type": "harmonious_flow",
}


def test_aspect_result_builds_canonical_runtime_without_changing_flat_fields() -> None:
    """Le runtime enrichit l'aspect sans modifier les champs historiques."""
    aspect = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        **ASPECT_META,
    )

    runtime = aspect.aspect_runtime

    assert aspect.aspect_code == "trine"
    assert aspect.planet_a == "sun"
    assert aspect.planet_b == "moon"
    assert aspect.orb == 0.3
    assert runtime is not None
    assert runtime.aspect.code == "trine"
    assert runtime.aspect.family == "major"
    assert runtime.participants.planet_a == "sun"
    assert runtime.orb.ratio == 0.05
    assert runtime.metadata.is_exact is True
    assert runtime.interpretation is not None
    assert runtime.interpretation.energy_type == "harmonious_flow"


def test_runtime_builder_adds_typed_modifiers() -> None:
    """Les modifiers runtime sont portes par l'enum canonique."""
    runtime = build_aspect_runtime_data(
        AspectResult(
            aspect_code="square",
            planet_a="sun",
            planet_b="mars",
            angle=90.0,
            orb=1.0,
            orb_used=1.0,
            orb_max=8.0,
            **{
                **ASPECT_META,
                "default_valence": "negative",
                "interpretive_valence": "dynamic_challenging",
                "energy_type": "friction_activation",
            },
        )
    )

    modifier_types = {modifier.modifier_type for modifier in runtime.modifiers}

    assert AspectModifierType.TIGHT_ORB in modifier_types
    assert AspectModifierType.LUMINARY in modifier_types


def test_aspect_runtime_contracts_reject_incomplete_core_values() -> None:
    """Les sous-contrats runtime refusent les valeurs vides ou hors bornes."""
    with pytest.raises(ValueError, match="code and family"):
        AspectIdentityRuntimeData(code=" ", family="major", angle=120.0)
    with pytest.raises(ValueError, match="two planet codes"):
        AspectParticipantsRuntimeData(planet_a="sun", planet_b=" ")
    with pytest.raises(ValueError, match="ratio"):
        AspectOrbRuntimeData(exact=0.3, max=6.0, ratio=1.4, strength_level="strong")
