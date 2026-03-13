"""Tests unitaires pour les métriques d'observabilité natal (Story 30-8 T8)."""

from __future__ import annotations

import json

from app.infra.observability.metrics import get_metrics_snapshot
from app.llm_orchestration.services.output_validator import validate_output

_SIMPLE_SCHEMA = {
    "type": "object",
    "required": ["message"],
    "properties": {"message": {"type": "string"}},
}

_V3_SCHEMA = {
    "type": "object",
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence"],
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string", "minLength": 900},
        "sections": {"type": "array", "minItems": 5},
        "highlights": {"type": "array", "minItems": 5},
        "advice": {"type": "array", "minItems": 5},
        "evidence": {"type": "array"},
    },
}


class TestNatalValidationPassCounter:
    def test_natal_pass_counter_incremented_on_success(self):
        """natal_validation_pass_total should increment for natal use cases on success."""
        raw = json.dumps({"message": "hello"})
        before = get_metrics_snapshot()["counters"].get(
            "natal_validation_pass_total{schema_version=v1,use_case=natal_interpretation}", 0.0
        )
        validate_output(raw, _SIMPLE_SCHEMA, use_case="natal_interpretation", schema_version="v1")
        after = get_metrics_snapshot()["counters"].get(
            "natal_validation_pass_total{schema_version=v1,use_case=natal_interpretation}", 0.0
        )
        assert after == before + 1.0

    def test_non_natal_pass_counter_not_incremented(self):
        """natal_validation_pass_total should NOT increment for non-natal use cases."""
        raw = json.dumps({"message": "hello"})
        before = get_metrics_snapshot()["counters"].get(
            "natal_validation_pass_total{use_case=chat_astrologer}", 0.0
        )
        validate_output(raw, _SIMPLE_SCHEMA, use_case="chat_astrologer")
        after = get_metrics_snapshot()["counters"].get(
            "natal_validation_pass_total{use_case=chat_astrologer}", 0.0
        )
        assert after == before  # unchanged


class TestNatalValidationFailCounter:
    def test_fail_counter_incremented_on_json_error(self):
        """natal_validation_fail_total should increment when JSON parse fails."""
        key = (
            "natal_validation_fail_total{reason=json_error,"
            "schema_version=v1,use_case=natal_interpretation}"
        )
        before = get_metrics_snapshot()["counters"].get(key, 0.0)
        validate_output(
            "INVALID JSON", _SIMPLE_SCHEMA, use_case="natal_interpretation", schema_version="v1"
        )
        after = get_metrics_snapshot()["counters"].get(key, 0.0)
        assert after == before + 1.0

    def test_fail_counter_incremented_on_schema_error(self):
        """natal_validation_fail_total should increment when schema validation fails."""
        key = (
            "natal_validation_fail_total{reason=schema_error,"
            "schema_version=v1,use_case=natal_interpretation}"
        )
        before = get_metrics_snapshot()["counters"].get(key, 0.0)
        raw = json.dumps({"wrong_field": 123})  # missing required "message"
        validate_output(raw, _SIMPLE_SCHEMA, use_case="natal_interpretation", schema_version="v1")
        after = get_metrics_snapshot()["counters"].get(key, 0.0)
        assert after == before + 1.0

    def test_fail_counter_not_incremented_for_non_natal(self):
        """natal_validation_fail_total should NOT increment for non-natal use cases."""
        key = "natal_validation_fail_total{reason=json_error,use_case=event_guidance}"
        before = get_metrics_snapshot()["counters"].get(key, 0.0)
        validate_output("BAD JSON", _SIMPLE_SCHEMA, use_case="event_guidance")
        after = get_metrics_snapshot()["counters"].get(key, 0.0)
        # event_guidance doesn't start with "natal" so no increment
        assert after == before


class TestNatalInvalidEvidenceCounter:
    def test_invalid_evidence_counter_incremented_on_filter(self):
        """natal_invalid_evidence_total increments when evidence is filtered out."""
        key = "natal_invalid_evidence_total{schema_version=v1,use_case=natal_interpretation}"
        before = get_metrics_snapshot()["counters"].get(key, 0.0)

        schema = {
            "type": "object",
            "required": ["evidence"],
            "properties": {"evidence": {"type": "array", "items": {"type": "string"}}},
        }
        catalog = {"SUN_GEMINI_H10": ["Soleil Gémeaux maison 10"]}
        raw = json.dumps({"evidence": ["SUN_GEMINI_H10", "HALLUCINATED_ID"]})
        validate_output(
            raw,
            schema,
            evidence_catalog=catalog,
            use_case="natal_interpretation",
            schema_version="v1",
        )

        after = get_metrics_snapshot()["counters"].get(key, 0.0)
        assert after == before + 1.0  # 1 filtered

    def test_invalid_evidence_counter_not_incremented_for_non_natal(self):
        """natal_invalid_evidence_total should NOT increment for non-natal use cases."""
        key = "natal_invalid_evidence_total"
        before = get_metrics_snapshot()["counters"].get(key, 0.0)

        schema = {
            "type": "object",
            "required": ["evidence"],
            "properties": {"evidence": {"type": "array", "items": {"type": "string"}}},
        }
        catalog = {"VALID_ID": []}
        raw = json.dumps({"evidence": ["HALLUCINATED_ID"]})
        validate_output(raw, schema, evidence_catalog=catalog, use_case="event_guidance")

        after = get_metrics_snapshot()["counters"].get(key, 0.0)
        assert after == before  # event_guidance doesn't start with "natal"
