# Commentaire global: ces tests protegent les preuves publiques du BasicNatalReadingPlan.
"""Tests des preuves, limitations et disclaimers du plan Basic."""

from __future__ import annotations

import re

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
    serialized = str(payload["public_evidence"]).casefold()
    assert "moon" not in serialized
    assert "sun" not in serialized
    assert "ce repere retient" not in serialized
    assert "position planetaire" not in serialized


def test_public_evidence_ids_are_opaque_and_do_not_reuse_fact_ids() -> None:
    """Les IDs publics restent opaques et ne copient pas les fact_id internes."""
    plan = build_plan(
        (
            fact("SUN_H10_INTERNAL", NatalFactFamily.LUMINARY, ("sun",)),
            fact("MOON_SOURCE_PATH_INTERNAL", NatalFactFamily.LUMINARY, ("moon",)),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("SUN_H10_INTERNAL",)),
            theme(BasicThemeCode.EMOTIONAL_PATTERN, ("MOON_SOURCE_PATH_INTERNAL",)),
        ),
    )
    payload = plan.to_payload()
    evidence_ids = [item["id"] for item in payload["public_evidence"]]
    section_evidence_ids = [
        evidence_id
        for section in payload["sections"]
        for evidence_id in section["supporting_evidence_ids"]
    ]

    assert all(re.fullmatch(r"pe-\d{3}", evidence_id) for evidence_id in evidence_ids)
    assert set(section_evidence_ids) == set(evidence_ids)
    assert "SUN_H10_INTERNAL" not in repr(evidence_ids)
    assert "MOON_SOURCE_PATH_INTERNAL" not in repr(evidence_ids)


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
