"""Tests unitaires pour le filtrage sécurisé evidence (Story 30-8 T4).

Couverture :
- Evidence hors catalog → filtré silencieusement (pas rejeté)
- Evidence valide → conservé
- Filtre combiné avec normalisation d'alias
- Mode non-strict : même comportement de filtrage
- Catalog vide ou absent : pas de filtrage
"""

from __future__ import annotations

import json

from app.domain.llm.runtime.output_validator import validate_output

_BASE_SCHEMA = {
    "type": "object",
    "required": ["summary", "evidence"],
    "properties": {
        "summary": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
    },
}


def _raw(summary: str = "Soleil en Taureau.", evidence: list = None) -> str:
    return json.dumps({"summary": summary, "evidence": evidence or []})


class TestSecureEvidenceFilter:
    """Tests for the secure evidence filter (T4.1 Story 30-8)."""

    def test_non_catalog_evidence_filtered_strict(self):
        """ID hors catalog → filtré, réponse valide."""
        raw = _raw(summary="Soleil en Taureau.", evidence=["SUN_TAURUS", "FAKE_PLANET_H99"])
        catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert "FAKE_PLANET_H99" not in result.parsed["evidence"]
        assert "SUN_TAURUS" in result.parsed["evidence"]

    def test_non_catalog_evidence_filtered_non_strict(self):
        """ID hors catalog → filtré aussi en mode non-strict."""
        raw = _raw(summary="Soleil en Taureau.", evidence=["SUN_TAURUS", "FAKE_PLANET_H99"])
        catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=False, schema_version="v3"
        )
        assert result.valid is True
        assert "FAKE_PLANET_H99" not in result.parsed["evidence"]

    def test_all_evidence_non_catalog_produces_empty(self):
        """Tous les IDs hors catalog → evidence vide, réponse valide."""
        raw = _raw(evidence=["FAKE1", "FAKE2", "FAKE3"])
        catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert result.parsed["evidence"] == []

    def test_valid_catalog_evidence_preserved(self):
        """IDs valides → tous conservés, pas de filtrage."""
        raw = _raw(
            summary="Soleil en Taureau. Lune en Cancer.",
            evidence=["SUN_TAURUS", "MOON_CANCER"],
        )
        catalog = {
            "SUN_TAURUS": ["Soleil en Taureau"],
            "MOON_CANCER": ["Lune en Cancer"],
        }
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert set(result.parsed["evidence"]) == {"SUN_TAURUS", "MOON_CANCER"}

    def test_alias_normalized_then_filtered(self):
        """Alias normalisé en ID catalog → conservé après normalisation."""
        raw = _raw(
            summary="Aspect entre Soleil et Venus.",
            evidence=["CONJUNCTION_SUN_VENUS"],
        )
        catalog = {"ASPECT_SUN_VENUS_CONJUNCTION": ["aspect entre Soleil et Venus"]}
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert "ASPECT_SUN_VENUS_CONJUNCTION" in result.parsed["evidence"]

    def test_no_catalog_no_filtering(self):
        """Sans catalog → aucun filtrage appliqué."""
        raw = _raw(evidence=["RANDOM_ID", "ANOTHER_ID"])
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=None, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert "RANDOM_ID" in result.parsed["evidence"]
        assert "ANOTHER_ID" in result.parsed["evidence"]

    def test_empty_catalog_filters_everything(self):
        """Catalog vide → tous les IDs sont filtrés."""
        raw = _raw(evidence=["SUN_TAURUS"])
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog={}, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert result.parsed["evidence"] == []

    def test_hallucinated_evidence_generates_warning(self):
        """ID hors catalog → warning généré (pas une erreur)."""
        raw = _raw(evidence=["HALLUCINATED_ID"])
        catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert any("Hallucinated" in w for w in result.warnings)

    def test_mixed_valid_invalid_evidence(self):
        """Mix valide/invalide → seuls les valides conservés."""
        raw = _raw(
            summary="Soleil en Taureau.",
            evidence=["SUN_TAURUS", "INVALID_1", "INVALID_2"],
        )
        catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
        result = validate_output(
            raw, _BASE_SCHEMA, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is True
        assert result.parsed["evidence"] == ["SUN_TAURUS"]
        # 2 hallucination warnings expected
        hallucinated_warnings = [w for w in result.warnings if "Hallucinated" in w]
        assert len(hallucinated_warnings) == 2

    def test_schema_errors_still_cause_failure(self):
        """Les erreurs de schéma (champs manquants) causent toujours un échec."""
        schema = {
            "type": "object",
            "required": ["title", "evidence"],
            "properties": {
                "title": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
        }
        raw = json.dumps({"evidence": []})  # missing required 'title'
        catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
        result = validate_output(
            raw, schema, evidence_catalog=catalog, strict=True, schema_version="v3"
        )
        assert result.valid is False
        assert any("title" in e for e in result.errors)
