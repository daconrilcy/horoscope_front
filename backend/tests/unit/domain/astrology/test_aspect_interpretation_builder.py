"""Tests du builder editorial deterministe des aspects."""

import pytest

from app.domain.astrology.interpretation.aspect_interpretation_builder import (
    AspectInterpretationBuilder,
)
from app.domain.astrology.interpretation.aspect_interpretation_facts import (
    AspectInterpretationFacts,
)
from app.domain.astrology.natal_calculation import AspectResult


def _profile() -> dict[str, object]:
    return {
        "aspect_code": "trine",
        "astral_system_code": "modern",
        "title": "Flow and Integration",
        "summary": "A trine indicates natural ease between two planetary principles.",
        "core_keywords_json": ["flow", "ease"],
        "growth_patterns_json": ["use the talent actively"],
        "relationship_keywords_json": ["comfort"],
        "shadow_keywords_json": ["complacency"],
        "psychological_keywords_json": ["inner harmony"],
    }


def _runtime_and_facts() -> tuple[object, AspectInterpretationFacts]:
    runtime = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_max=6.0,
    ).aspect_runtime
    assert runtime is not None
    return runtime, AspectInterpretationFacts.from_profile(runtime=runtime, profile=_profile())


def test_builder_produces_editorial_fields_from_profile() -> None:
    """Le builder assemble les cinq champs editoriaux depuis le profil."""
    runtime, facts = _runtime_and_facts()

    interpretation = AspectInterpretationBuilder().build(
        runtime=runtime,
        facts=facts,
        profile=_profile(),
    )

    assert interpretation.summary.startswith("A trine")
    assert interpretation.psychological_meaning == ("inner harmony",)
    assert interpretation.relationship_expression == ("comfort",)
    assert interpretation.shadow_expression == ("complacency",)
    assert interpretation.growth_path == ("use the talent actively",)
    assert interpretation.source_profile_code == "trine"


def test_builder_rejects_missing_profile_explicitly() -> None:
    """Une absence de profil ne produit pas de fallback texte silencieux."""
    runtime, facts = _runtime_and_facts()

    with pytest.raises(ValueError, match="missing aspect interpretation profile"):
        AspectInterpretationBuilder().build(runtime=runtime, facts=facts, profile=None)


def test_builder_rejects_blank_editorial_list_values() -> None:
    """Les listes editoriales obligatoires ne doivent pas contenir de texte vide."""
    runtime, facts = _runtime_and_facts()
    profile = _profile()
    profile["psychological_keywords_json"] = [" "]

    with pytest.raises(ValueError, match="psychological_keywords_json"):
        AspectInterpretationBuilder().build(runtime=runtime, facts=facts, profile=profile)
