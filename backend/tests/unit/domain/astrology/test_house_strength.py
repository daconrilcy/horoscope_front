"""Tests du contrat canonique de force interpretative des maisons."""

import ast
from pathlib import Path

import pytest

from app.domain.astrology.interpretation.house_strength import HouseStrengthEvaluator
from app.domain.astrology.interpretation.house_strength_contracts import (
    HouseStrengthLevel,
    HouseStrengthReason,
)
from app.domain.astrology.runtime.house_runtime_data import (
    HouseOccupantRuntimeData,
    HouseRulerRuntimeData,
    HouseStrengthRuntimeData,
)

RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


def test_calculate_house_strength_marks_stellium_luminary_house_dominant() -> None:
    """Une maison angulaire avec stellium et luminaire devient dominante."""
    strength = HouseStrengthEvaluator().evaluate(
        house_number=10,
        occupants=[
            HouseOccupantRuntimeData("sun", "aries", 12.0),
            HouseOccupantRuntimeData("mars", "aries", 15.0),
            HouseOccupantRuntimeData("venus", "taurus", 34.0),
        ],
        ruler=HouseRulerRuntimeData("mars", "aries", 12),
        sign_rulerships=RULERS,
    )

    assert strength.dominant is True
    assert strength.score == 1.0
    assert strength.normalized_score == 1.0
    assert strength.level is HouseStrengthLevel.DOMINANT
    assert strength.reasons == (
        HouseStrengthReason.BASELINE_HOUSE,
        HouseStrengthReason.ANGULAR_HOUSE,
        HouseStrengthReason.OCCUPANTS_PRESENT,
        HouseStrengthReason.STELLIUM_PRESENT,
        HouseStrengthReason.LUMINARY_PRESENT,
        HouseStrengthReason.RULER_IN_OWN_SIGN,
        HouseStrengthReason.MC_ANGLE_PROXIMITY,
    )
    assert strength.modifiers.angularity_modifier == 0.33
    assert strength.modifiers.occupancy_modifier == 0.63
    assert strength.modifiers.ruler_condition_modifier == 0.12


def test_calculate_house_strength_keeps_empty_cadent_house_non_dominant() -> None:
    """Une maison cadente vide reste faiblement priorisée."""
    strength = HouseStrengthEvaluator().evaluate(
        house_number=6,
        occupants=[],
        ruler=HouseRulerRuntimeData("mercury", "pisces", 12),
        sign_rulerships=RULERS,
    )

    assert strength.dominant is False
    assert strength.score == 0.05
    assert strength.normalized_score == 0.05
    assert strength.level is HouseStrengthLevel.LOW
    assert strength.reasons == (
        HouseStrengthReason.BASELINE_HOUSE,
        HouseStrengthReason.CADENT_HOUSE,
    )


def test_house_strength_evaluator_does_not_append_raw_reason_literals() -> None:
    """La production des raisons reste bornee par `HouseStrengthReason`."""
    source_path = (
        Path(__file__).parents[4]
        / "app"
        / "domain"
        / "astrology"
        / "interpretation"
        / "house_strength.py"
    )
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "append":
            continue
        assert not (
            node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        )


def test_house_strength_serialized_contract_requires_matching_level() -> None:
    """La rehydratation serialisee echoue si le niveau contredit le score."""
    with pytest.raises(ValueError):
        HouseStrengthRuntimeData.from_serialized(
            score=0.05,
            level=HouseStrengthLevel.DOMINANT.value,
            reasons=[HouseStrengthReason.BASELINE_HOUSE.value],
        )
