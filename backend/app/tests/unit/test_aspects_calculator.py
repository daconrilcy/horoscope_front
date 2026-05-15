"""Tests unitaires du calculateur strict des aspects astrologiques."""

import pytest

from app.domain.astrology.calculators.aspects import (
    build_aspect_body_from_position,
    calculate_major_aspects,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectDefinitionRuntimeData,
    AspectOrbRuleRuntimeData,
)


def _definition(code: str = "square", angle: float = 90.0) -> AspectDefinitionRuntimeData:
    """Construit une définition d'aspect majeure typée."""
    return AspectDefinitionRuntimeData(
        code=code,
        angle=angle,
        family="major",
        default_orb_deg=6.0,
        is_enabled=True,
        is_major=True,
        is_minor=False,
        default_valence="negative",
        interpretive_valence="dynamic_challenging",
        energy_type="friction_activation",
    )


def _rule(orb_deg: float = 6.0) -> AspectOrbRuleRuntimeData:
    """Construit une règle d'orbe typée."""
    return AspectOrbRuleRuntimeData(
        aspect_code="square",
        system_code="modern",
        calculation_context="natal",
        source_body_type="any",
        target_body_type="any",
        orb_deg=orb_deg,
        priority=100,
        is_enabled=True,
    )


def test_calculate_major_aspects_uses_typed_orb_rules() -> None:
    """Le calcul détecte un aspect via contrats typés uniquement."""
    positions = [
        build_aspect_body_from_position({"planet_code": "sun", "longitude": 0.0}),
        build_aspect_body_from_position({"planet_code": "mars", "longitude": 95.5}),
    ]

    result = calculate_major_aspects(
        positions,
        [_definition()],
        orb_rules=[_rule()],
        system_inheritance={"modern": None},
    )

    assert result == [
        {
            "aspect_code": "square",
            "planet_a": "mars",
            "planet_b": "sun",
            "angle": 90.0,
            "orb": 5.5,
            "orb_used": 5.5,
            "orb_max": 6.0,
            "family": "major",
            "is_major": True,
            "is_minor": False,
            "default_valence": "negative",
            "interpretive_valence": "dynamic_challenging",
            "energy_type": "friction_activation",
        }
    ]


def test_calculate_major_aspects_rejects_legacy_definition_fields() -> None:
    """Les anciens champs d'orbes ne sont plus acceptés à la frontière."""
    with pytest.raises(ValueError, match="legacy aspect orb fields"):
        AspectDefinitionRuntimeData.from_mapping(
            {
                "code": "square",
                "angle": 90.0,
                "family": "major",
                "default_orb_deg": 6.0,
                "default_valence": "negative",
                "interpretive_valence": "dynamic_challenging",
                "energy_type": "friction_activation",
                "orb_luminaries": 8.0,
            }
        )


def test_aspect_result_requires_resolved_orb_and_reference_metadata() -> None:
    """AspectResult ne reconstruit plus les champs absents par compatibilité."""
    with pytest.raises(ValueError):
        AspectResult(
            aspect_code="square",
            planet_a="mars",
            planet_b="sun",
            angle=90.0,
            orb=3.5,
        )

    aspect = AspectResult(
        aspect_code="square",
        planet_a="mars",
        planet_b="sun",
        angle=90.0,
        orb=3.5,
        orb_used=3.5,
        orb_max=6.0,
        family="major",
        is_major=True,
        is_minor=False,
        default_valence="negative",
        interpretive_valence="dynamic_challenging",
        energy_type="friction_activation",
    )
    payload = aspect.model_dump()
    assert payload["orb_used"] == 3.5
    assert payload["orb_max"] == 6.0
    assert "aspect_runtime" not in payload
