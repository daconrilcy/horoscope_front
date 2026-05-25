"""Tests du builder structured_facts_v1 non narratif."""

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
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_CONTRACT_VERSION,
    STRUCTURED_FACTS_V1_PROJECTION_ID,
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.main import app
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object

REPO_ROOT = Path(__file__).resolve().parents[4]
INTERPRETATION_DIR = REPO_ROOT / "app/domain/astrology/interpretation"


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source runtime minimale pour le builder structured facts."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult | None = None
    advanced_condition_facts: tuple[object, ...] = ()
    chart_balance: object | None = None


def test_structured_facts_v1_shape_is_hashable_and_json_serializable() -> None:
    """Le builder produit la projection stable attendue."""
    payload = _build_payload()

    assert payload["projection_id"] == STRUCTURED_FACTS_V1_PROJECTION_ID
    assert payload["contract_version"] == STRUCTURED_FACTS_V1_CONTRACT_VERSION
    assert set(payload) == {
        "projection_id",
        "contract_version",
        "source_versions",
        "structural_facts",
        "interpretive_signals",
        "dominants",
        "hash_input",
        "missing_data",
        "excluded_surfaces",
    }
    assert payload["structural_facts"]["positions"][0]["code"] == "mars"
    assert payload["structural_facts"]["houses"][0]["house_number"] == 1
    assert payload["structural_facts"]["major_aspects"][0]["code"] == "trine"
    assert payload["interpretive_signals"]["dignity_codes"] == ["mars"]
    assert payload["dominants"][0]["code"] == "mars"
    json.dumps(payload, sort_keys=True)
    json.dumps(payload["hash_input"], sort_keys=True)


def test_structured_facts_v1_output_is_stable_for_identical_runtime_input() -> None:
    """Deux entrees equivalentes produisent le meme hash input canonique."""
    builder = StructuredFactsV1Builder()
    first = builder.canonical_hash_input_json(_build_payload())
    second = builder.canonical_hash_input_json(_build_payload())

    assert first == second


def test_structured_facts_v1_missing_runtime_data_is_deterministic() -> None:
    """Les collections optionnelles absentes restent explicites et stables."""
    source = _NatalSource(
        chart_objects=(interpretable_chart_object("mars", with_payloads=False),),
        aspects=(),
        dominant_planets=None,
    )

    payload = StructuredFactsV1Builder().build(source)

    assert payload["structural_facts"]["major_aspects"] == []
    assert payload["structural_facts"]["houses"] == []
    assert payload["dominants"] == []
    assert payload["missing_data"] == {
        "chart_id": None,
        "sign_balances": None,
        "empty_collections": [
            "advanced_condition_facts",
            "dominants",
            "fixed_star_contacts",
            "houses",
            "major_aspects",
        ],
    }


def test_structured_facts_v1_excludes_narrative_owned_fields() -> None:
    """Les champs redactionnels ne deviennent pas des faits hashables."""
    forbidden = {
        "nar" + "rative_text",
        "ad" + "vice_text",
        "pro" + "mpt",
        "pro" + "mpt_text",
        "llm" + "_output",
        "final" + "_narrative",
        "rendered" + "_text",
        "provider" + "_response",
        "provider" + "_completion",
    }
    serialized = json.dumps(_build_payload(), sort_keys=True)

    assert all(token not in serialized for token in forbidden)


def test_structured_facts_v1_stays_out_of_public_api_surface() -> None:
    """Le builder domaine ne cree aucune route dediee hors endpoint generique."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    client = TestClient(app)

    assert all("structured_facts" not in path for path in route_paths)
    assert "/v1/astrology/projections/structured_facts_v1" not in route_paths
    assert client.get("/health").status_code == 200


def test_structured_facts_v1_builder_reuses_interpretation_owner() -> None:
    """La projection passe par le builder interpretatif canonique."""
    tree = ast.parse((INTERPRETATION_DIR / "structured_facts_v1_builder.py").read_text())
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "ChartInterpretationInputBuilder" in imported_names


def test_structured_facts_v1_has_one_canonical_builder_owner() -> None:
    """Aucun pipeline parallele ne porte le meme builder."""
    builder_files = [
        path
        for path in INTERPRETATION_DIR.glob("*.py")
        if "StructuredFactsV1Builder" in path.read_text()
    ]

    assert builder_files == [INTERPRETATION_DIR / "structured_facts_v1_builder.py"]


def _build_payload() -> dict[str, object]:
    """Construit une projection representative pour les assertions."""
    source = _NatalSource(
        chart_objects=(interpretable_chart_object("mars"),),
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
