"""Tests des conditions avancees de secte."""

from __future__ import annotations

from dataclasses import replace

from app.domain.astrology.advanced_conditions.advanced_condition_engine import (
    AdvancedConditionEngine,
)
from app.domain.astrology.runtime.runtime_reference import (
    AccidentalDignityRuleReferenceData,
    DignityConditionValue,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
    profile,
)


def test_hayz_and_out_of_sect_are_projected_from_canonical_sect_facts() -> None:
    """Les conditions avancees de secte consomment PlanetSectCondition."""
    conditions, _profiles = advanced_engine_result(
        (position("sun", "leo", house_number=10), position("mars", "aries")),
        (
            dignity(
                "sun",
                "hayz",
                intrinsic_sect="diurnal",
                planet_sect_condition="in_sect",
                is_in_sect=True,
            ),
            dignity(
                "mars",
                intrinsic_sect="nocturnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    assert [(item.source_planet_code, item.condition_code) for item in conditions] == [
        ("mars", "out_of_sect"),
        ("sun", "hayz"),
    ]
    assert {item.condition_type_code for item in conditions} == {"hayz", "out_of_sect"}
    hayz = next(item for item in conditions if item.condition_code == "hayz")
    assert hayz.calculation_facts == {
        "sect_match": True,
        "hemisphere_match": True,
        "sign_gender_match": True,
        "planet_horizon_position": "above_horizon",
        "sign_gender": "masculine",
        "calculation_basis": "sect_hemisphere_sign_gender",
        "reference_system": "traditional",
    }


def test_hayz_requires_in_sect_even_when_non_sect_factors_match() -> None:
    """Hayz reste faux quand seule la precondition canonique de secte echoue."""
    conditions, _profiles = advanced_engine_result(
        (position("moon", "cancer"),),
        (
            dignity(
                "moon",
                "hayz",
                intrinsic_sect="nocturnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    assert [item.condition_code for item in conditions] == ["out_of_sect"]


def test_hayz_evaluates_later_runtime_rule_when_first_candidate_fails() -> None:
    """Hayz parcourt toutes les regles runtime applicables avant de conclure."""
    runtime_reference = _reference_with_failing_hayz_rule_before_matching_rule()
    sun = position("sun", "leo", house_number=10)
    sun_dignity = dignity(
        "sun",
        "hayz",
        intrinsic_sect="diurnal",
        planet_sect_condition="in_sect",
        is_in_sect=True,
    )

    conditions, _profiles = AdvancedConditionEngine().calculate(
        runtime_reference=runtime_reference,
        planet_positions=(sun,),
        aspects=(),
        dignities=(sun_dignity,),
        condition_profiles=(profile("sun"),),
    )

    hayz = next(item for item in conditions if item.condition_code == "hayz")
    assert hayz.calculation_facts["hemisphere_match"] is True
    assert hayz.calculation_facts["sign_gender_match"] is True


def _reference_with_failing_hayz_rule_before_matching_rule():
    """Place une regle hayz non applicable avant la regle canonique qui matche."""
    runtime_reference = complete_reference()
    dignity_reference = runtime_reference.dignity_reference
    failing_rule = AccidentalDignityRuleReferenceData(
        dignity_type_code="hayz",
        planet_code="sun",
        condition_schema_code="hayz",
        conditions=(
            DignityConditionValue("chart_sect_code", "day"),
            DignityConditionValue("horizon_position_code", "above"),
            DignityConditionValue("sign_gender_code", "feminine"),
        ),
        system_code="traditional",
    )
    return replace(
        runtime_reference,
        dignity_reference=replace(
            dignity_reference,
            accidental_rules=(failing_rule, *dignity_reference.accidental_rules),
        ),
    )
