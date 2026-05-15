"""Tests du socle inter-chart reutilisant le calculateur d'aspects."""

from app.domain.astrology.calculators.aspects import (
    build_aspect_body_from_position,
    calculate_interchart_aspects,
)
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectDefinitionRuntimeData,
    AspectOrbRuleRuntimeData,
)


def _definition() -> AspectDefinitionRuntimeData:
    """Construit une définition typée de trigone."""
    return AspectDefinitionRuntimeData(
        code="trine",
        angle=120.0,
        family="major",
        default_orb_deg=6.0,
        is_enabled=True,
        is_major=True,
        is_minor=False,
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
    )


def test_interchart_aspects_reuse_existing_aspect_definitions() -> None:
    """Le calcul inter-chart reutilise les definitions d'aspects existantes."""
    source_positions = [build_aspect_body_from_position({"planet_code": "sun", "longitude": 0.0})]
    target_positions = [
        build_aspect_body_from_position({"planet_code": "moon", "longitude": 120.2})
    ]

    aspects = calculate_interchart_aspects(
        source_positions,
        target_positions,
        [_definition()],
        orb_rules=[],
        system_inheritance={"modern": None},
    )

    assert aspects == [
        {
            "aspect_code": "trine",
            "planet_a": "sun",
            "planet_b": "moon",
            "chart_a": "source",
            "chart_b": "target",
            "angle": 120.0,
            "orb": 0.2,
            "orb_used": 0.2,
            "orb_max": 6.0,
            "family": "major",
            "is_major": True,
            "is_minor": False,
            "default_valence": "positive",
            "interpretive_valence": "harmonious",
            "energy_type": "harmonious_flow",
        }
    ]


def test_interchart_aspects_apply_targeted_orb_rules_to_original_body_codes() -> None:
    """Les regles ciblees matchent les codes originaux sans namespace inter-chart."""
    source_positions = [build_aspect_body_from_position({"planet_code": "sun", "longitude": 0.0})]
    target_positions = [
        build_aspect_body_from_position({"planet_code": "moon", "longitude": 127.0})
    ]
    definitions = [
        AspectDefinitionRuntimeData(
            code="trine",
            angle=120.0,
            family="major",
            default_orb_deg=3.0,
            is_enabled=True,
            is_major=True,
            is_minor=False,
            default_valence="positive",
            interpretive_valence="harmonious",
            energy_type="harmonious_flow",
        )
    ]
    orb_rules = [
        AspectOrbRuleRuntimeData(
            system_code="modern",
            aspect_code="trine",
            calculation_context="interchart",
            source_body_type="luminary",
            target_body_type="any",
            target_planet_code="moon",
            orb_deg=8.0,
            priority=1000,
            is_enabled=True,
        )
    ]

    aspects = calculate_interchart_aspects(
        source_positions,
        target_positions,
        definitions,
        orb_rules=orb_rules,
        system_code="modern",
        system_inheritance={"modern": None},
    )

    assert len(aspects) == 1
    assert aspects[0]["planet_a"] == "sun"
    assert aspects[0]["planet_b"] == "moon"
    assert aspects[0]["orb_max"] == 8.0
