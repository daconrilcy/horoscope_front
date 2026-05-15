"""Tests du contrat semantique pur des aspects."""

import pytest

from app.domain.astrology.interpretation.aspect_interpretation_facts import (
    AspectInterpretationFacts,
)
from app.domain.astrology.natal_calculation import AspectResult

ASPECT_META = {
    "family": "major",
    "is_major": True,
    "is_minor": False,
    "default_valence": "positive",
    "interpretive_valence": "harmonious",
    "energy_type": "harmonious_flow",
}


def _profile() -> dict[str, object]:
    return {
        "aspect_code": "trine",
        "astral_system_code": "modern",
        "title": "Flow and Integration",
        "core_keywords_json": ["flow", "ease"],
        "growth_patterns_json": ["use the talent actively"],
        "relationship_keywords_json": ["comfort"],
        "shadow_keywords_json": ["complacency"],
    }


def test_interpretation_facts_expose_symbolic_primitives() -> None:
    """Les faits semantiques exposent des primitives courtes et typables."""
    runtime = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        **ASPECT_META,
    ).aspect_runtime
    assert runtime is not None

    facts = AspectInterpretationFacts.from_profile(runtime=runtime, profile=_profile())

    assert facts.symbolic_primitives == ("trine", "major", "sun", "moon")
    assert facts.semantic_axes == ("flow", "ease")
    assert facts.growth_axes == ("use the talent actively",)
    assert facts.editorial_theme_refs == ("Flow and Integration",)
    assert facts.semantic_candidates[0].provenance.source_system == "modern"


def test_interpretation_facts_keep_editorial_theme_out_of_semantic_axes() -> None:
    """Le titre editorial reste reference de theme, pas axe semantique."""
    runtime = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        **ASPECT_META,
    ).aspect_runtime
    assert runtime is not None

    facts = AspectInterpretationFacts.from_profile(runtime=runtime, profile=_profile())

    assert "Flow and Integration" not in facts.semantic_axes
    assert all("\n" not in axis for axis in facts.semantic_axes)


def test_interpretation_facts_reject_blank_required_axes() -> None:
    """Les axes obligatoires vides ne doivent pas passer en facts semantiques."""
    runtime = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        **ASPECT_META,
    ).aspect_runtime
    assert runtime is not None
    profile = _profile()
    profile["core_keywords_json"] = [" "]

    with pytest.raises(ValueError, match="core_keywords_json"):
        AspectInterpretationFacts.from_profile(runtime=runtime, profile=profile)
