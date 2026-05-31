# Commentaire global: ces tests prouvent que le plan Basic ne se reduit pas a la maison dix.
"""Tests archetypaux du BasicNatalReadingPlan."""

from __future__ import annotations

from app.domain.astrology.interpretation.natal_fact_graph import NatalFactFamily
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode
from tests.unit.domain.astrology.basic_natal_reading_plan_helpers import build_plan, fact, theme


def test_house_10_is_not_the_only_basic_narrative_model() -> None:
    """Un plan riche conserve des sections non professionnelles autour de la vocation."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
            fact("house-10", NatalFactFamily.HOUSE_EMPHASIS, ("house:10", "angular")),
            fact("house-7", NatalFactFamily.HOUSE_EMPHASIS, ("house:7", "venus")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",)),
            theme(BasicThemeCode.PUBLIC_VOCATION, ("house-10",), objects=("house:10",)),
            theme(BasicThemeCode.RELATIONSHIP_PATTERN, ("house-7",), objects=("house:7",)),
        ),
    )
    section_codes = {section.section_code for section in plan.sections}

    assert "vocation" in section_codes
    assert {"identity", "inner_life", "relationships"}.issubset(section_codes)


def test_house_4_archetype_routes_to_inner_life() -> None:
    """La maison quatre nourrit une section de vie interieure, pas la vocation."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("moon-house-4", NatalFactFamily.HOUSE_EMPHASIS, ("moon", "house:4")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon-house-4",), objects=("house:4",)),
        ),
    )

    assert "inner_life" in {section.section_code for section in plan.sections}
    assert "vocation" not in {section.section_code for section in plan.sections}


def test_house_7_archetype_routes_to_relationships() -> None:
    """La maison sept garde une section relationnelle autonome."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("venus-house-7", NatalFactFamily.HOUSE_EMPHASIS, ("venus", "house:7")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(BasicThemeCode.RELATIONSHIP_PATTERN, ("venus-house-7",), objects=("house:7",)),
        ),
    )

    assert "relationships" in {section.section_code for section in plan.sections}


def test_house_12_archetype_routes_to_tensions() -> None:
    """La maison douze reste traitee comme integration prudente."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("saturn-house-12", NatalFactFamily.HOUSE_EMPHASIS, ("saturn", "house:12")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(
                BasicThemeCode.TENSION_TO_INTEGRATE,
                ("saturn-house-12",),
                objects=("house:12",),
            ),
        ),
    )

    assert "tensions" in {section.section_code for section in plan.sections}


def test_contradictions_shape_plan_nuance_without_final_prose() -> None:
    """Une contradiction conserve ressource et interdit voisin dans le plan."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("venus-detriment", NatalFactFamily.CONDITION, ("venus", "detriment")),
            fact("venus-square-mars", NatalFactFamily.ASPECT, ("venus", "mars", "square")),
            fact("venus-trine-jupiter", NatalFactFamily.ASPECT, ("venus", "jupiter", "trine")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(
                BasicThemeCode.TENSION_TO_INTEGRATE,
                ("venus-detriment", "venus-square-mars"),
                do_not_mention=("venus-trine-jupiter",),
                objects=("venus", "square", "detriment"),
            ),
        ),
    )
    tension = next(section for section in plan.sections if section.section_code == "tensions")

    assert set(tension.required_fact_ids) == {"venus-detriment", "venus-square-mars"}
    assert tension.forbidden_fact_ids == ("venus-trine-jupiter",)
    assert tension.target_length_words >= 130
