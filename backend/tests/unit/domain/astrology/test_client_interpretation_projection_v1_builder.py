"""Tests de la projection client_interpretation_projection_v1 par plan."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.interpretation.client_interpretation_projection_v1_builder import (
    CLIENT_INTERPRETATION_PROJECTION_V1_ID,
    ClientInterpretationProjectionV1Builder,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_PROJECTION_ID,
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import AspectResult, NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.main import app
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object

REPO_ROOT = Path(__file__).resolve().parents[4]
INTERPRETATION_DIR = REPO_ROOT / "app/domain/astrology/interpretation"
BUILDER_PATH = INTERPRETATION_DIR / "client_interpretation_projection_v1_builder.py"


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source minimale pour obtenir structured_facts_v1 sans runtime public."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult | None = None
    advanced_condition_facts: tuple[object, ...] = ()
    chart_balance: object | None = None


def test_free_projection_is_short_and_client_safe() -> None:
    """Le plan free expose des sections courtes sans audit ni runtime brut."""
    payload = ClientInterpretationProjectionV1Builder().build(
        _structured_facts(),
        requested_plan="free",
        current_plan="free",
    )

    assert payload["projection_id"] == CLIENT_INTERPRETATION_PROJECTION_V1_ID
    assert payload["source_projection_id"] == STRUCTURED_FACTS_V1_PROJECTION_ID
    assert payload["plan"] == "free"
    assert payload["plan_variant"] == "free"
    assert payload["state"] == "normal"
    assert payload["llm_input_selection"]["contract"] == "LLMInputSelection"
    assert payload["editorial_depth_profile"]["contract"] == "EditorialDepthProfile"
    assert payload["editorial_depth_profile"]["depth_code"] == "free_short"
    assert payload["precision_level"] == "orientation"
    assert payload["frontend_visibility_rules"]["contract"] == "FrontendVisibilityRules"
    assert payload["calculation_scope"] == "full_projection_available_before_shaping"
    assert [section["code"] for section in payload["sections"]] == [
        "orientation_generale",
        "points_forts",
        "limite_de_lecture",
        "upgrade_hint",
    ]
    assert {section["depth"] for section in payload["sections"]} == {"free_short"}
    assert "audit_input" not in payload
    assert _payload_excludes_forbidden_surfaces(payload)


def test_basic_projection_adds_audit_ready_content() -> None:
    """Le plan basic ajoute les sections personnelles et l'entree d'audit."""
    payload = ClientInterpretationProjectionV1Builder().build(
        _structured_facts(),
        requested_plan="basic",
        current_plan="basic",
    )

    section_codes = [section["code"] for section in payload["sections"]]
    assert "themes_personnels" in section_codes
    assert "relations_aux_autres" in section_codes
    assert "conseil_pratique" in section_codes
    assert {section["depth"] for section in payload["sections"]} == {"basic_contextual"}
    assert "relationship_patterns" in payload["llm_input_selection"]["allowed_fact_groups"]
    assert payload["editorial_depth_profile"]["depth_code"] == "basic_contextual"
    assert payload["precision_level"] == "contextual"
    assert payload["frontend_visibility_rules"]["summarized_section_codes"] == [
        "analyse_approfondie",
        "tensions_et_ressources",
        "fenetres_de_prediction",
        "plan_d_action",
        "nuances_et_arbitrages",
    ]
    assert payload["audit_input"]["audit_contract"] == "narrative_answer_audit_v1"
    assert payload["audit_input"]["section_codes"] == section_codes
    assert "audit_rows" in payload["audit_input"]["excluded_audit_surfaces"]
    assert _payload_excludes_forbidden_surfaces(payload)


def test_premium_projection_is_deepest_without_expert_payload() -> None:
    """Le plan premium ajoute les sections riches sans projection experte."""
    payload = ClientInterpretationProjectionV1Builder().build(
        _structured_facts(),
        requested_plan="premium",
        current_plan="premium",
    )

    section_codes = [section["code"] for section in payload["sections"]]
    assert "analyse_approfondie" in section_codes
    assert "fenetres_de_prediction" in section_codes
    assert "nuances_et_arbitrages" in section_codes
    assert {section["depth"] for section in payload["sections"]} == {"premium_deep"}
    assert "prediction_windows" in payload["llm_input_selection"]["allowed_fact_groups"]
    assert payload["editorial_depth_profile"]["depth_code"] == "premium_deep"
    assert payload["precision_level"] == "detailed"
    assert payload["frontend_visibility_rules"]["visible_section_codes"] == section_codes
    assert any(item["code"] == "personalization_note" for item in payload["support_elements"])
    assert len(payload["interpretive_signals"]) >= 3
    assert _payload_excludes_forbidden_surfaces(payload)


def test_plan_insufficient_is_controlled() -> None:
    """Un plan courant trop faible renvoie une erreur stable et lisible."""
    payload = ClientInterpretationProjectionV1Builder().build(
        _structured_facts(),
        requested_plan="premium",
        current_plan="basic",
    )

    assert payload["state"] == "plan_insufficient"
    assert payload["sections"] == []
    assert payload["support_elements"] == []
    assert payload["error"] == {
        "code": "plan_insufficient",
        "message": "Votre plan actuel ne permet pas cette profondeur d'interpretation.",
        "current_plan": "basic",
        "required_plan": "premium",
        "projection_id": CLIENT_INTERPRETATION_PROJECTION_V1_ID,
        "upgrade_hint": "Passez au plan premium pour debloquer cette lecture.",
    }
    assert _payload_excludes_forbidden_surfaces(payload)


def test_disclaimer_codes_follow_application_policy() -> None:
    """Les disclaimers restent des codes applicatifs stables."""
    payload = ClientInterpretationProjectionV1Builder().build(
        _structured_facts(no_time=True),
        requested_plan="basic",
        current_plan="premium",
    )

    assert payload["state"] == "degraded"
    assert payload["disclaimer_codes"] == [
        "ASTROLOGY_GENERAL_LIMITATION",
        "ASTROLOGY_MISSING_BIRTH_TIME",
    ]
    assert payload["missing_data"] == ["no_time"]


def test_builder_consumes_structured_facts_and_reuses_existing_owners() -> None:
    """Le builder depend du owner structured_facts_v1 et des disclaimers existants."""
    tree = ast.parse(BUILDER_PATH.read_text())
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "STRUCTURED_FACTS_V1_PROJECTION_ID" in imported_names
    assert "BEGINNER_SUMMARY_V1_DISCLAIMER_CODES" in imported_names
    assert "BEGINNER_SUMMARY_V1_NO_TIME_DISCLAIMER_CODES" in imported_names


def test_client_interpretation_projection_v1_has_one_canonical_builder() -> None:
    """Aucun builder parallele ne porte cette projection."""
    builder_files = [
        path
        for path in INTERPRETATION_DIR.glob("*.py")
        if "CLIENT_INTERPRETATION_PROJECTION_V1_ID" in path.read_text()
    ]

    assert builder_files == [BUILDER_PATH]


def test_client_interpretation_projection_v1_persisted_basic_returns_normal() -> None:
    """Un theme persiste complet reste normal pour le plan basic."""
    result = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
    )
    persisted = NatalResult.model_validate(result.model_dump(mode="json"))
    structured = StructuredFactsV1Builder().build(persisted, chart_id="chart-persisted")

    payload = ClientInterpretationProjectionV1Builder().build(
        structured,
        requested_plan="basic",
        current_plan="basic",
    )

    assert payload["state"] == "normal"
    assert payload.get("missing_data") is None


def test_client_interpretation_projection_v1_stays_out_of_public_api_surface() -> None:
    """La projection ne cree pas de route dediee hors endpoint generique."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    client = TestClient(app)

    assert all("client_interpretation_projection_v1" not in path for path in route_paths)
    assert "/v1/astrology/projections/client_interpretation_projection_v1" not in route_paths
    assert client.get("/health").status_code == 200


def test_builder_rejects_non_structured_facts_source() -> None:
    """Une source non canonique est refusee au lieu de produire un fallback."""
    try:
        ClientInterpretationProjectionV1Builder().build(
            {"projection_id": "legacy_projection"},
            requested_plan="free",
            current_plan="premium",
        )
    except ValueError as exc:
        assert "structured_facts_v1" in str(exc)
    else:
        raise AssertionError("source non canonique acceptee")


def _payload_excludes_forbidden_surfaces(payload: dict[str, object]) -> bool:
    """Verifie l'absence des surfaces interdites dans le JSON client."""
    active_payload = {
        key: value for key, value in payload.items() if key not in {"excluded_surfaces", "error"}
    }
    if isinstance(active_payload.get("audit_input"), dict):
        active_payload["audit_input"] = {
            key: value
            for key, value in active_payload["audit_input"].items()
            if key != "excluded_audit_surfaces"
        }
    serialized = json.dumps(active_payload, sort_keys=True)
    forbidden = {
        "ChartObjectRuntimeData",
        "chart_objects",
        "debug_rows",
        "evidence_refs",
        "final_narrative",
        "model_identifier",
        "provider_response",
        "technical_score",
    }
    return all(token not in serialized for token in forbidden)


def _structured_facts(*, no_time: bool = False) -> dict[str, object]:
    """Construit la source amont representative depuis le builder canonique."""
    source = _NatalSource(
        chart_objects=(
            interpretable_chart_object("sun"),
            interpretable_chart_object("moon"),
            interpretable_chart_object("asc" if not no_time else "mars", with_payloads=not no_time),
        ),
        aspects=(
            AspectResult(
                aspect_code="trine",
                planet_a="sun",
                planet_b="moon",
                angle=120.0,
                orb=1.0,
                orb_used=1.0,
                orb_max=6.0,
                family="major",
                is_major=True,
                is_minor=False,
            ),
        ),
        dominant_planets=DominantPlanetsResult(
            score_profile_code="fixture.profile",
            tradition_code="fixture",
            reference_version_code="v1",
            planets=(
                PlanetDominanceResult(
                    planet_code="mars",
                    total_score=0.82,
                    rank=1,
                    dominance_level="dominant",
                    factors=(
                        PlanetDominanceFactor(
                            factor_code="angularity",
                            raw_value=1.0,
                            normalized_value=1.0,
                            weight=0.5,
                            weighted_score=0.5,
                            reason="fixture",
                        ),
                    ),
                    explanation_facts=("fixture",),
                ),
            ),
            top_planet_code="mars",
            chart_ruler_code=None,
            most_elevated_planet_code=None,
        ),
    )
    payload = StructuredFactsV1Builder().build(source, chart_id="chart-1", locale="fr")
    if no_time:
        payload["missing_data"] = {"reasons": ["no_time"], "empty_collections": ["houses"]}
    return payload
