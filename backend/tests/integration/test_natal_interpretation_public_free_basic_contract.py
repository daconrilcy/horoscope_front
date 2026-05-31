# Commentaire global: preuves du contrat public free short et Basic V2.
"""Verifie le contrat public stable de l'interpretation natale free et Basic."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.main import app
from app.services.api_contracts.public.natal_interpretation import InterpretationMeta
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from tests.integration.basic_natal_v2_helpers import basic_runtime_plan, persisted_basic_payload

_FORBIDDEN_PUBLIC_MARKERS = (
    "audit_input",
    "chart_json",
    "condition_axis",
    "interpretive_signal_ids",
    "internal_evidence",
    "natal_data",
    "ranking_score",
    "raw_answer_storage",
    "score_profile",
    "visibility_expression",
    "weighted_score",
)


def _public_meta(model: UserNatalInterpretationModel, level: str) -> InterpretationMeta:
    """Construit une meta minimale comme le handler public avant projection finale."""
    return InterpretationMeta(
        id=model.id,
        level=level,
        use_case=model.use_case,
        schema_version="unknown",
        validation_status="valid",
    )


def _free_short_row() -> UserNatalInterpretationModel:
    """Retourne une ligne free short persistee avec son ancien owner runtime interne."""
    return UserNatalInterpretationModel(
        id=4191,
        user_id=419,
        chart_id="chart-free-public",
        level=InterpretationLevel.COMPLETE,
        use_case="natal_long_free",
        variant_code="free_short",
        interpretation_payload={
            "title": "Lecture gratuite",
            "summary": "Resume public gratuit suffisamment lisible.",
            "sections": [{"key": "section_0", "heading": "Axe public", "content": ""}],
            "highlights": ["Point d'appui"],
            "advice": ["Conseil nuance"],
            "evidence": [],
        },
        was_fallback=False,
    )


def _basic_complete_row() -> UserNatalInterpretationModel:
    """Retourne une ligne Basic complete compatible avec le contrat V2 public."""
    plan = basic_runtime_plan(chart_id="chart-basic-public")
    return UserNatalInterpretationModel(
        id=4192,
        user_id=419,
        chart_id="chart-basic-public",
        level=InterpretationLevel.COMPLETE,
        use_case="natal_interpretation",
        variant_code="single_astrologer",
        interpretation_payload=persisted_basic_payload(plan),
        was_fallback=False,
    )


def _assert_no_forbidden_public_marker(payload: dict[str, object]) -> None:
    """Verifie que le JSON public accepte ne transporte aucun marqueur technique."""
    serialized = json.dumps(payload, ensure_ascii=False)
    for marker in _FORBIDDEN_PUBLIC_MARKERS:
        assert marker not in serialized


def test_free_short_public_contract_exposes_short_astro_free_payload() -> None:
    """La branche free reste lisible et classable sans lecture narrative complete."""
    response = NatalInterpretationService.format_interpretation_response(
        _free_short_row(),
        _public_meta(_free_short_row(), "complete"),
        "fr-FR",
    )

    payload = response.model_dump(mode="json")
    data = payload["data"]
    interpretation = data["interpretation"]

    assert data["meta"]["level"] == "short"
    assert data["use_case"] == "natal_interpretation_short"
    assert data["meta"]["use_case"] == "natal_interpretation_short"
    assert interpretation["title"]
    assert interpretation["summary"]
    assert interpretation["sections"]
    assert interpretation["highlights"]
    assert interpretation["advice"]
    assert interpretation["disclaimers"] == response.disclaimers
    assert data["narrative_natal_reading_v1"] is None
    assert data["basic_natal_interpretation_v2"] is None
    _assert_no_forbidden_public_marker(payload)


def test_free_short_public_contract_accepts_stabilized_public_use_case() -> None:
    """Une ligne deja stabilisee reste classable comme free short public."""
    row = _free_short_row()
    row.use_case = "natal_interpretation_short"
    row.variant_code = None

    response = NatalInterpretationService.format_interpretation_response(
        row,
        _public_meta(row, "complete"),
        "fr-FR",
    )

    payload = response.model_dump(mode="json")
    data = payload["data"]

    assert data["meta"]["level"] == "short"
    assert data["use_case"] == "natal_interpretation_short"
    assert data["meta"]["use_case"] == "natal_interpretation_short"
    assert data["basic_natal_interpretation_v2"] is None


def test_basic_complete_public_contract_exposes_basic_v2_payload() -> None:
    """La branche Basic complete expose le contrat V2 canonique et sa synthese."""
    response = NatalInterpretationService.format_interpretation_response(
        _basic_complete_row(),
        _public_meta(_basic_complete_row(), "complete"),
        "fr-FR",
    )

    payload = response.model_dump(mode="json")
    data = payload["data"]
    basic = data["basic_natal_interpretation_v2"]

    assert data["meta"]["level"] == "complete"
    assert data["meta"]["schema_version"] == "basic_natal_interpretation_v2"
    assert data["interpretation"]["summary"]
    assert basic["locale"] == "fr-FR"
    assert basic["level"] == "basic"
    assert basic["engine_version"] == "basic-natal-reading-v1"
    assert basic["schema_version"] == "basic_natal_interpretation_v2"
    assert basic["taxonomy_version"] == "basic-natal-theme-taxonomy-v1"
    assert basic["salience_version"] == "basic-natal-salience-v1"
    assert basic["prompt_version"] == "basic-natal-draft-prompt-v1"
    assert basic["validator_version"] == "basic-natal-validator-v1"
    assert basic["interpretation"]["introduction"]
    assert basic["interpretation"]["themes"]
    assert basic["public_evidence"]
    assert basic["disclaimers"]
    _assert_no_forbidden_public_marker(payload)


def test_runtime_route_and_openapi_register_public_response_schema() -> None:
    """Le contrat runtime FastAPI garde la route et le schema public attendus."""
    client = TestClient(app)

    route_paths = {getattr(route, "path", "") for route in app.routes}
    openapi = client.app.openapi()

    assert "/v1/natal/interpretation" in route_paths
    assert "/v1/natal/interpretation" in openapi["paths"]
    response_schema = openapi["paths"]["/v1/natal/interpretation"]["post"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    assert response_schema["$ref"].endswith("/NatalInterpretationResponse")
    schema_blob = json.dumps(openapi["components"]["schemas"], ensure_ascii=False)
    assert "basic_natal_interpretation_v2" in schema_blob
    assert "narrative_natal_reading_v1" in schema_blob
