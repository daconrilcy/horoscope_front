"""Tests du builder beginner_summary_v1 client-safe."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.interpretation.beginner_summary_v1_builder import (
    BEGINNER_SUMMARY_V1_PROJECTION_ID,
    BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID,
    BeginnerSummaryV1Builder,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.chart_object_runtime_data import ZodiacPositionRuntimeData
from app.main import app
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object

BACKEND_ROOT = Path(__file__).resolve().parents[4]
INTERPRETATION_DIR = BACKEND_ROOT / "app/domain/astrology/interpretation"


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source runtime minimale pour produire structured_facts_v1."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult | None = None
    advanced_condition_facts: tuple[object, ...] = ()
    chart_balance: object | None = None


def test_beginner_summary_v1_shape_is_json_serializable_and_deterministic() -> None:
    """Le builder produit un payload public stable depuis structured_facts_v1."""
    source = _structured_facts()
    builder = BeginnerSummaryV1Builder()

    payload = builder.build(source)

    assert payload["projection_id"] == BEGINNER_SUMMARY_V1_PROJECTION_ID
    assert payload["audience"] == ["basic", "beginner", "free", "public-user"]
    assert payload["source_projection"] == BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID
    assert payload["source_projection_id"] == BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID
    assert payload["allowed_fields"] == [
        "ascendant",
        "dominant_house",
        "dominant_themes",
        "main_signs",
    ]
    assert payload["state"] == "normal"
    assert payload["message_code"] == "BGS_NORMAL"
    assert payload["display_messages"] == [
        {"code": "BGS_NORMAL", "message": "Votre resume debutant est disponible."}
    ]
    assert payload["main_signs"] == [
        {"code": "moon_sign", "value": "taurus"},
        {"code": "sun_sign", "value": "aries"},
    ]
    assert payload["ascendant"] == {"code": "ascendant", "value": "cancer"}
    assert payload["dominant_house"] == {"code": "dominant_house", "value": 1}
    assert payload["dominant_themes"] == [{"code": "mars", "label": "mars"}]
    assert builder.canonical_json(payload) == builder.canonical_json(builder.build(source))
    json.dumps(payload, sort_keys=True)


def test_beginner_summary_v1_empty_state_is_controlled() -> None:
    """Une source sans signes ni dominantes donne un etat empty controle."""
    source = _structured_facts()
    source["structural_facts"]["positions"] = []
    source["dominants"] = []

    payload = BeginnerSummaryV1Builder().build(source)

    assert payload["state"] == "empty"
    assert payload["message_code"] == "BGS_EMPTY"
    assert payload["display_messages"] == [
        {
            "code": "BGS_EMPTY",
            "message": "Aucun resume debutant n'est disponible pour ces donnees.",
        }
    ]
    assert payload["summary_items"] == []
    assert "missing_data" not in payload


def test_beginner_summary_v1_missing_birth_time_is_degraded() -> None:
    """Le mode no_time retire ascendant et maisons du payload public."""
    source = _structured_facts()
    source["structural_facts"]["houses"] = []
    source["missing_data"] = {"reasons": ["no_time"], "empty_collections": ["houses"]}
    source["dominants"].append({"code": "house_1", "rank": 2, "source": "fixture"})

    payload = BeginnerSummaryV1Builder().build(source)

    assert payload["state"] == "degraded"
    assert payload["message_code"] == "BGS_DEGRADED_NO_TIME"
    assert payload["display_messages"] == [
        {
            "code": "BGS_DEGRADED_NO_TIME",
            "message": (
                "Votre resume est affiche sans ascendant ni maisons detaillees car l'heure "
                "de naissance manque."
            ),
        }
    ]
    assert payload["degraded_reason"] == "no_time"
    assert payload["missing_data"] == ["no_time"]
    assert "ascendant" not in payload
    assert "dominant_house" not in payload
    assert payload["dominant_themes"] == [{"code": "mars", "label": "mars"}]


def test_beginner_summary_v1_unavailable_and_invalid_source_are_explicit() -> None:
    """La source absente est controlee et la mauvaise projection est refusee."""
    builder = BeginnerSummaryV1Builder()

    unavailable = builder.build(None)

    assert unavailable["state"] == "unavailable"
    assert unavailable["message_code"] == "BGS_UNAVAILABLE"
    assert unavailable["display_messages"] == [
        {
            "code": "BGS_UNAVAILABLE",
            "message": "Le resume debutant est temporairement indisponible.",
        }
    ]
    assert unavailable["missing_data"] == ["source_unavailable"]
    with pytest.raises(ValueError, match="structured_facts_v1 source"):
        builder.build({"projection_id": "raw_runtime_payload"})


def test_beginner_summary_v1_excludes_internal_and_llm_owned_fields() -> None:
    """Aucun detail technique, audit ou LLM ne fuit dans le resume."""
    forbidden_keys = {
        "audit",
        "debug",
        "evidence_refs",
        "hash_input",
        "pro" + "mpt",
        "llm" + "_output",
        "provider" + "_response",
        "runtime_contract",
        "source_versions",
        "technical_scores",
    }
    payload = BeginnerSummaryV1Builder().build(_structured_facts())
    serialized = json.dumps(payload, sort_keys=True)

    assert forbidden_keys.isdisjoint(payload)
    assert all(
        token not in serialized
        for token in ("pro" + "mpt", "llm" + "_output", "provider" + "_response")
    )


def test_beginner_summary_v1_stays_out_of_public_api_surface() -> None:
    """Le builder domaine ne cree aucune route dediee hors endpoint generique."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    client = TestClient(app)

    assert all("beginner_summary" not in path for path in route_paths)
    assert "/v1/astrology/projections/beginner_summary_v1" not in route_paths
    assert client.get("/health").status_code == 200


def test_beginner_summary_v1_builder_consumes_structured_facts_only() -> None:
    """Le guard AST interdit un builder base sur le runtime brut."""
    tree = ast.parse((INTERPRETATION_DIR / "beginner_summary_v1_builder.py").read_text())
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    function_args = {
        arg.arg
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        for arg in node.args.args
    }

    assert "STRUCTURED_FACTS_V1_PROJECTION_ID" in imported_names
    assert "natal_result" not in function_args
    assert "runtime" + "_payload" not in function_args


def test_beginner_summary_v1_has_one_canonical_builder_owner() -> None:
    """Aucun second pipeline actif ne porte le builder beginner_summary_v1."""
    builder_files = [
        path
        for path in INTERPRETATION_DIR.glob("*.py")
        if "BeginnerSummaryV1Builder" in path.read_text()
    ]

    assert builder_files == [INTERPRETATION_DIR / "beginner_summary_v1_builder.py"]


def _structured_facts() -> dict[str, Any]:
    """Construit une source structured_facts_v1 representative."""
    source = _NatalSource(
        chart_objects=(
            interpretable_chart_object(
                "sun",
                zodiac_position=ZodiacPositionRuntimeData(
                    sign_code="aries",
                    degree_in_sign=15.0,
                ),
            ),
            interpretable_chart_object(
                "moon",
                zodiac_position=ZodiacPositionRuntimeData(
                    sign_code="taurus",
                    degree_in_sign=10.0,
                ),
            ),
            interpretable_chart_object(
                "asc",
                zodiac_position=ZodiacPositionRuntimeData(
                    sign_code="cancer",
                    degree_in_sign=5.0,
                ),
            ),
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
    return StructuredFactsV1Builder().build(source, chart_id="chart-1", locale="fr")
