"""Tests unitaires pour AstroResponseV3, AstroSectionV3, AstroErrorResponseV3.

Couverture story 30-8 T1:
- Contraintes min_length=280 sur sections[].content
- Contraintes min_length=900 sur summary
- Contraintes min_length=5 sur sections, highlights, advice
- Absence du champ disclaimers dans AstroResponseV3
- Mode erreur AstroErrorResponseV3 valide sans contraintes densité
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.llm_orchestration.schemas import (
    AstroErrorResponseV3,
    AstroResponseV3,
    AstroSectionErrorV3,
    AstroSectionV3,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_SECTION = {
    "key": "overall",
    "heading": "Vue d'ensemble",
    "content": "x" * 280,  # Exactement le minimum requis
}

_VALID_SUMMARY = "s" * 900  # Exactement le minimum requis


def _make_valid_v3(**overrides) -> dict:
    base = {
        "title": "Mon thème natal",
        "summary": _VALID_SUMMARY,
        "sections": [
            {"key": "overall", "heading": "Vue d'ensemble", "content": "x" * 300},
            {"key": "career", "heading": "Carrière", "content": "x" * 300},
            {"key": "relationships", "heading": "Relations", "content": "x" * 300},
            {"key": "inner_life", "heading": "Vie intérieure", "content": "x" * 300},
            {"key": "strengths", "heading": "Forces", "content": "x" * 300},
        ],
        "highlights": [f"Point fort {i}" for i in range(5)],
        "advice": [f"Conseil {i}" for i in range(5)],
        "evidence": ["SUN_GEMINI_H10", "MOON_CANCER_H11"],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# AstroSectionV3
# ---------------------------------------------------------------------------


class TestAstroSectionV3:
    def test_valid_section(self):
        s = AstroSectionV3(**_VALID_SECTION)
        assert s.content == "x" * 280

    def test_content_too_short_rejected(self):
        data = dict(_VALID_SECTION, content="x" * 279)
        with pytest.raises(ValidationError, match="string_too_short"):
            AstroSectionV3(**data)

    def test_content_empty_rejected(self):
        data = dict(_VALID_SECTION, content="")
        with pytest.raises(ValidationError):
            AstroSectionV3(**data)

    def test_content_max_length_boundary(self):
        s = AstroSectionV3(**dict(_VALID_SECTION, content="x" * 6500))
        assert len(s.content) == 6500

    def test_content_too_long_rejected(self):
        data = dict(_VALID_SECTION, content="x" * 6501)
        with pytest.raises(ValidationError):
            AstroSectionV3(**data)

    def test_invalid_key_rejected(self):
        data = dict(_VALID_SECTION, key="invalid_key")
        with pytest.raises(ValidationError):
            AstroSectionV3(**data)

    def test_thematic_module_key_accepted(self):
        data = dict(_VALID_SECTION, key="leadership_signature")
        s = AstroSectionV3(**data)
        assert s.key == "leadership_signature"


# ---------------------------------------------------------------------------
# AstroResponseV3
# ---------------------------------------------------------------------------


class TestAstroResponseV3:
    def test_valid_response(self):
        r = AstroResponseV3(**_make_valid_v3())
        assert r.title == "Mon thème natal"
        assert len(r.sections) == 5
        assert len(r.highlights) == 5
        assert len(r.advice) == 5

    def test_no_disclaimers_field(self):
        """AstroResponseV3 ne doit PAS avoir de champ disclaimers."""
        r = AstroResponseV3(**_make_valid_v3())
        assert not hasattr(r, "disclaimers")

    def test_summary_too_short_rejected(self):
        data = _make_valid_v3(summary="s" * 899)
        with pytest.raises(ValidationError, match="string_too_short"):
            AstroResponseV3(**data)

    def test_summary_exact_minimum(self):
        r = AstroResponseV3(**_make_valid_v3(summary="s" * 900))
        assert len(r.summary) == 900

    def test_sections_too_few_rejected(self):
        data = _make_valid_v3()
        data["sections"] = data["sections"][:4]  # 4 instead of 5
        with pytest.raises(ValidationError, match="too_short"):
            AstroResponseV3(**data)

    def test_sections_section_content_too_short_rejected(self):
        data = _make_valid_v3()
        data["sections"][0] = {"key": "overall", "heading": "Vue", "content": "x" * 100}
        with pytest.raises(ValidationError, match="string_too_short"):
            AstroResponseV3(**data)

    def test_highlights_too_few_rejected(self):
        data = _make_valid_v3(highlights=["h1", "h2", "h3", "h4"])  # 4 instead of 5
        with pytest.raises(ValidationError, match="too_short"):
            AstroResponseV3(**data)

    def test_advice_too_few_rejected(self):
        data = _make_valid_v3(advice=["a1", "a2", "a3", "a4"])  # 4 instead of 5
        with pytest.raises(ValidationError, match="too_short"):
            AstroResponseV3(**data)

    def test_evidence_invalid_pattern_rejected(self):
        data = _make_valid_v3(evidence=["invalid evidence with spaces"])
        with pytest.raises(ValidationError):
            AstroResponseV3(**data)

    def test_evidence_empty_allowed(self):
        r = AstroResponseV3(**_make_valid_v3(evidence=[]))
        assert r.evidence == []

    def test_max_sections(self):
        data = _make_valid_v3()
        data["sections"] = [
            {"key": k, "heading": f"H{i}", "content": "x" * 280}
            for i, k in enumerate(
                [
                    "overall",
                    "career",
                    "relationships",
                    "inner_life",
                    "strengths",
                    "challenges",
                    "daily_life",
                    "tarot_spread",
                    "event_context",
                    "overall",
                ]
            )
        ]
        # 10 sections (max), mais "overall" en double n'est pas interdit par schema
        # On teste juste qu'on peut avoir 10
        # Réduction à 10 items uniques avec clés valides
        data["sections"] = [
            {"key": "overall", "heading": f"H{i}", "content": "x" * 280} for i in range(10)
        ]
        r = AstroResponseV3(**data)
        assert len(r.sections) == 10

    def test_more_than_max_sections_rejected(self):
        data = _make_valid_v3()
        data["sections"] = [
            {"key": "overall", "heading": f"H{i}", "content": "x" * 280} for i in range(11)
        ]
        with pytest.raises(ValidationError):
            AstroResponseV3(**data)


# ---------------------------------------------------------------------------
# AstroErrorResponseV3
# ---------------------------------------------------------------------------


class TestAstroErrorResponseV3:
    def _make_valid_error(self, **overrides) -> dict:
        base = {
            "error_code": "insufficient_data",
            "message": "Données insuffisantes pour l'interprétation.",
            "title": "Interprétation indisponible",
            "summary": "Le thème natal fourni ne contient pas assez de données.",
        }
        base.update(overrides)
        return base

    def test_valid_error_response(self):
        r = AstroErrorResponseV3(**self._make_valid_error())
        assert r.error_code == "insufficient_data"
        assert r.sections == []
        assert r.highlights == []
        assert r.advice == []

    def test_valid_calculation_failed(self):
        r = AstroErrorResponseV3(**self._make_valid_error(error_code="calculation_failed"))
        assert r.error_code == "calculation_failed"

    def test_invalid_error_code_rejected(self):
        with pytest.raises(ValidationError):
            AstroErrorResponseV3(**self._make_valid_error(error_code="unknown_error"))

    def test_short_summary_allowed_in_error_mode(self):
        """Mode erreur n'a pas de contrainte min 900 sur summary."""
        r = AstroErrorResponseV3(**self._make_valid_error(summary="Court résumé erreur."))
        assert len(r.summary) < 900

    def test_empty_sections_allowed(self):
        r = AstroErrorResponseV3(**self._make_valid_error(sections=[]))
        assert r.sections == []

    def test_sections_with_v3_section(self):
        section = {"key": "overall", "heading": "Vue", "content": "x" * 280}
        r = AstroErrorResponseV3(**self._make_valid_error(sections=[section]))
        assert len(r.sections) == 1

    def test_too_many_sections_in_error_rejected(self):
        sections = [{"key": "overall", "heading": f"H{i}", "content": "x" * 280} for i in range(3)]
        with pytest.raises(ValidationError):
            AstroErrorResponseV3(**self._make_valid_error(sections=sections))

    def test_error_section_short_content_allowed(self):
        """Sections en mode erreur acceptent un contenu < 280 chars (pas de contrainte densité)."""
        section = {"key": "overall", "heading": "Vue", "content": "x" * 10}
        r = AstroErrorResponseV3(**self._make_valid_error(sections=[section]))
        assert len(r.sections) == 1
        assert len(r.sections[0].content) == 10

    def test_error_section_is_error_v3_type(self):
        """Les sections de AstroErrorResponseV3
        sont des AstroSectionErrorV3 (pas AstroSectionV3)."""
        section = {"key": "overall", "heading": "Vue", "content": "x" * 50}
        r = AstroErrorResponseV3(**self._make_valid_error(sections=[section]))
        assert isinstance(r.sections[0], AstroSectionErrorV3)
