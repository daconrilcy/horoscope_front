# Commentaire global: ces tests protegent les preuves publiques du BasicNatalReadingPlan.
"""Tests des preuves, limitations et disclaimers du plan Basic."""

from __future__ import annotations

from app.domain.astrology.interpretation.natal_fact_graph import NatalFactFamily
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode
from tests.unit.domain.astrology.basic_natal_reading_plan_helpers import build_plan, fact, theme

FORBIDDEN_PUBLIC_TERMS = {
    "ranking_score",
    "condition_axis",
    "score_profile",
    "weighted_score",
    "prompt_hint",
    "audit_input",
    "source_paths",
}


def test_public_evidence_is_user_readable_and_linked_to_sections() -> None:
    """Chaque preuve publique porte un libelle lisible et des sections sources."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("moon", NatalFactFamily.LUMINARY, ("moon", "water")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",)),
        ),
    )
    payload = plan.to_payload()

    assert payload["public_evidence"]
    assert all(item["id"].startswith("pe-") for item in payload["public_evidence"])
    assert all(item["label"] for item in payload["public_evidence"])
    assert all(item["explanation"] for item in payload["public_evidence"])
    assert all(item["source_section_codes"] for item in payload["public_evidence"])


def test_limitations_and_disclaimers_are_emitted() -> None:
    """Le plan publie les limites de portee sans ajouter de prose finale."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",)),
        ),
    )

    assert plan.limitations
    assert plan.disclaimers
    assert "prediction certaine" in plan.disclaimers[0]


def test_public_evidence_does_not_expose_internal_scoring_or_prompt_hints() -> None:
    """Les champs techniques restent absents de la preuve publique serialisee."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",)),
        ),
    )
    serialized = str(plan.to_payload())

    assert not any(term in serialized for term in FORBIDDEN_PUBLIC_TERMS)
