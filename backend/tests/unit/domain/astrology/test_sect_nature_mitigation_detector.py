"""Tests de mitigation benefique/malefique par la secte runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from app.domain.astrology.advanced_conditions.contracts import (
    SectNatureMitigationCondition,
)
from app.domain.astrology.advanced_conditions.sect_nature_mitigation_detector import (
    SectNatureMitigationDetector,
)
from app.domain.astrology.runtime.runtime_reference import (
    PlanetNatureReferenceData,
    PlanetNatureReferenceSet,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.unit.domain.astrology.advanced_condition_test_helpers import dignity


def test_sect_nature_mitigation_contract_is_immutable() -> None:
    """Le contrat CS-206 est immutable et porte tous les champs obligatoires."""
    condition = _first_fact("mars", "malefic", is_in_sect=True)

    assert condition.condition_family == "sect_nature_mitigation"
    assert condition.condition_code == "malefic_mitigated_by_sect"
    with pytest.raises(FrozenInstanceError):
        condition.mitigation_state = "changed"


def test_malefic_in_sect_is_mitigated_from_runtime_nature() -> None:
    """Une nature malefique runtime en secte est mitigated."""
    condition = _first_fact("test_planet", "malefic", is_in_sect=True)

    assert condition.planet_nature == "malefic"
    assert condition.condition_code == "malefic_mitigated_by_sect"
    assert condition.mitigation_state == "mitigated"


def test_malefic_out_of_sect_is_aggravated_from_runtime_nature() -> None:
    """Une nature malefique runtime hors secte est aggravated."""
    condition = _first_fact("test_planet", "malefic", is_in_sect=False)

    assert condition.condition_code == "malefic_aggravated_out_of_sect"
    assert condition.mitigation_state == "aggravated"


def test_benefic_in_sect_is_supported_from_runtime_nature() -> None:
    """Une nature benefique runtime en secte est supported."""
    condition = _first_fact("test_planet", "benefic", is_in_sect=True)

    assert condition.condition_code == "benefic_supported_by_sect"
    assert condition.mitigation_state == "supported"


def test_benefic_out_of_sect_is_weakened_from_runtime_nature() -> None:
    """Une nature benefique runtime hors secte est weakened."""
    condition = _first_fact("test_planet", "benefic", is_in_sect=False)

    assert condition.condition_code == "benefic_weakened_out_of_sect"
    assert condition.mitigation_state == "weakened"


@pytest.mark.parametrize("nature", ["mixed", "neutral", "luminary"])
def test_neutral_runtime_natures_are_explicit(nature: str) -> None:
    """Les natures non benefiques/malefiques produisent un fait neutral."""
    condition = _first_fact("test_planet", nature, is_in_sect=True)

    assert condition.condition_code == "sect_nature_neutral"
    assert condition.mitigation_state == "neutral"


def test_missing_runtime_nature_is_explicit_unknown() -> None:
    """Une planete absente des natures runtime n'est pas coercée."""
    reference = complete_reference()

    facts = SectNatureMitigationDetector().detect(
        dignities=(
            dignity(
                "uranus",
                intrinsic_sect="unknown",
                planet_sect_condition="unknown",
            ),
        ),
        runtime_reference=reference,
    )

    assert facts[0].planet_nature == "unknown"
    assert facts[0].condition_code == "sect_nature_unknown"
    assert facts[0].mitigation_state == "unknown"


def test_missing_planet_sect_condition_does_not_fabricate_signal() -> None:
    """Sans PlanetSectCondition, le detecteur CS-206 n'invente aucun fait."""
    facts = SectNatureMitigationDetector().detect(
        dignities=(dignity("mars", include_sect_condition=False),),
        runtime_reference=complete_reference(),
    )

    assert facts == ()


def test_emission_uses_runtime_condition_support() -> None:
    """L'emission scoree depend du type runtime `sect_nature_mitigation`."""
    reference = complete_reference()
    emitted = SectNatureMitigationDetector().calculate(
        dignities=(
            dignity(
                "mars",
                chart_sect="night",
                intrinsic_sect="nocturnal",
                planet_sect_condition="in_sect",
                is_in_sect=True,
            ),
        ),
        runtime_reference=reference,
        emit_condition=_emit_condition,
        condition_type_codes=frozenset({"sect_nature_mitigation"}),
    )

    assert emitted[0].condition_type_code == "sect_nature_mitigation"
    assert emitted[0].condition_code == "malefic_mitigated_by_sect"
    assert emitted[0].calculation_facts["planet_nature"] == "malefic"


def test_emission_skips_when_runtime_condition_type_is_absent() -> None:
    """Un runtime sans type supporte ne produit pas d'AdvancedCondition."""
    emitted = SectNatureMitigationDetector().calculate(
        dignities=(dignity("mars"),),
        runtime_reference=complete_reference(),
        emit_condition=_emit_condition,
        condition_type_codes=frozenset(),
    )

    assert emitted == ()


def _first_fact(
    planet_code: str,
    nature: str,
    *,
    is_in_sect: bool,
) -> SectNatureMitigationCondition:
    """Construit le premier fait avec une nature injectee."""
    reference = replace(
        complete_reference(),
        planet_natures=PlanetNatureReferenceSet(
            (
                PlanetNatureReferenceData(
                    code=nature,
                    label=nature.title(),
                    planet_codes=(planet_code,),
                    sort_order=1,
                ),
            )
        ),
    )
    return SectNatureMitigationDetector().detect(
        dignities=(
            dignity(
                planet_code,
                intrinsic_sect="diurnal",
                planet_sect_condition="in_sect" if is_in_sect else "out_of_sect",
                is_in_sect=is_in_sect,
                is_out_of_sect=not is_in_sect,
            ),
        ),
        runtime_reference=reference,
    )[0]


def _emit_condition(**kwargs):
    """Emetteur de test gardant les faits transmis par le detecteur."""
    from app.domain.astrology.advanced_conditions.contracts import (
        AdvancedPlanetaryCondition,
        PlanetConditionAxisImpact,
    )

    return AdvancedPlanetaryCondition(
        score_profile="test",
        reference_version="test",
        score_impact=0.0,
        ranking_weight=0.0,
        axes_impact=PlanetConditionAxisImpact(0, 0, 0, 0, 0, 0, 0),
        **kwargs,
    )
