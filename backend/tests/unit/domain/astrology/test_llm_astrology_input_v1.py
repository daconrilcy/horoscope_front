"""Tests du contrat interne llm_astrology_input_v1."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.interpretation.ai_narrative_input_builder import (
    AINarrativeInputBuilder,
)
from app.domain.astrology.interpretation.client_interpretation_projection_v1_builder import (
    ClientInterpretationProjectionV1Builder,
)
from app.domain.astrology.interpretation.llm_astrology_input_v1 import (
    LLM_ASTROLOGY_INPUT_V1_CONTRACT_ID,
    LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION,
    LLMAstrologyInputV1Builder,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_PROJECTION_ID,
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.main import app
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object

REPO_ROOT = Path(__file__).resolve().parents[4]
INTERPRETATION_DIR = REPO_ROOT / "app/domain/astrology/interpretation"
CONTRACT_PATH = INTERPRETATION_DIR / "llm_astrology_input_v1.py"


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source runtime minimale pour les builders internes existants."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult
    advanced_condition_facts: tuple[object, ...] = ()
    chart_balance: object | None = None


def test_llm_astrology_input_v1_shape_and_sources_are_stable() -> None:
    """Le contrat expose les blocs requis et route chaque source autorisee."""
    payload = _build_payload()

    assert payload["contract_id"] == LLM_ASTROLOGY_INPUT_V1_CONTRACT_ID
    assert payload["contract_version"] == LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION
    assert set(payload) == {
        "contract_id",
        "contract_version",
        "facts",
        "signals",
        "limits",
        "evidence",
        "shaping",
        "provenance",
        "exclusions",
    }
    assert payload["facts"]["source_projection_id"] == STRUCTURED_FACTS_V1_PROJECTION_ID
    assert payload["signals"]["source_contract"] == "AINarrativeInputContract"
    assert payload["shaping"]["source_projection_id"] == "client_interpretation_projection_v1"
    assert payload["shaping"]["plan"] == "premium"
    assert "sections" not in payload["shaping"]
    json.dumps(payload, sort_keys=True)


def test_llm_astrology_input_v1_hash_is_deterministic_and_covers_prompt_blocks() -> None:
    """Le hash LLM depend des blocs qui influencent le futur prompt."""
    first = _build_payload()
    second = _build_payload()

    assert first["provenance"]["llm_input_hash"] == second["provenance"]["llm_input_hash"]
    assert len(first["provenance"]["llm_input_hash"]) == 64
    assert first["provenance"]["hash_policy"]["prompt_influencing_blocks"] == [
        "facts",
        "signals",
        "limits",
        "evidence",
        "shaping",
    ]


def test_llm_astrology_input_v1_rejects_raw_or_wrong_fact_source() -> None:
    """Les faits ne peuvent pas venir d'un carrier runtime ou public arbitraire."""
    structured_facts, ai_input, client_projection = _build_sources()
    wrong_source = dict(structured_facts)
    wrong_source["projection_id"] = "chart_payload"

    with pytest.raises(ValueError, match="structured_facts_v1"):
        LLMAstrologyInputV1Builder().build(
            structured_facts_v1=wrong_source,
            ai_narrative_input=ai_input,
            client_interpretation_projection_v1=client_projection,
        )


def test_llm_astrology_input_v1_excludes_runtime_public_and_provider_surfaces() -> None:
    """Les carriers larges sont seulement declares comme exclusions."""
    payload = _build_payload()
    serialized_facts = json.dumps(payload["facts"], sort_keys=True)
    serialized_signals = json.dumps(payload["signals"], sort_keys=True)
    excluded = set(payload["exclusions"]["excluded_surfaces"])

    assert {"ChartObjectRuntimeData", "CalculationGraph", "chart_json", "natal_data"}.issubset(
        excluded
    )
    assert "chart_json" not in serialized_facts
    assert "natal_data" not in serialized_facts
    assert "provider_response" not in serialized_signals


def test_llm_astrology_input_v1_stays_out_of_public_api_surface() -> None:
    """Le contrat domaine ne cree ni route dediee ni schema OpenAPI."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    client = TestClient(app)

    assert all("llm_astrology" not in path for path in route_paths)
    assert LLM_ASTROLOGY_INPUT_V1_CONTRACT_ID not in str(app.openapi())
    assert client.get("/health").status_code == 200


def test_llm_astrology_input_v1_has_one_canonical_owner_and_imports_sources() -> None:
    """Le module canonique reutilise les owners facts, signaux, shaping et hash."""
    tree = ast.parse(CONTRACT_PATH.read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    owner_files = [
        path
        for path in INTERPRETATION_DIR.glob("*.py")
        if "LLMAstrologyInputV1Builder" in path.read_text(encoding="utf-8")
    ]

    assert owner_files == [CONTRACT_PATH]
    assert {
        "AINarrativeInputContract",
        "STRUCTURED_FACTS_V1_PROJECTION_ID",
        "compute_projection_hash",
        "validate_evidence_refs_by_section",
    }.issubset(imported_names)
    assert "SHAPING_SOURCE_PROJECTION_ID" in CONTRACT_PATH.read_text(encoding="utf-8")


def _build_payload() -> dict[str, object]:
    """Construit un payload representatif du contrat LLM interne."""
    structured_facts, ai_input, client_projection = _build_sources()
    return LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=ai_input,
        client_interpretation_projection_v1=client_projection,
        evidence_refs=(),
        prompt_ref="natal.astrology.compact.v1",
    )


def _build_sources() -> tuple[dict[str, object], object, dict[str, object]]:
    """Assemble les trois sources canoniques attendues par la story."""
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
                            weight=1.0,
                            weighted_score=1.0,
                            reason="fixture",
                        ),
                    ),
                    explanation_facts=("fixture",),
                ),
            ),
            top_planet_code="mars",
            chart_ruler_code="mars",
            most_elevated_planet_code=None,
        ),
    )
    structured_facts = StructuredFactsV1Builder().build(source, chart_id="chart-1", locale="fr")
    ai_input = AINarrativeInputBuilder().build(source, chart_id="chart-1", locale="fr")
    client_projection = ClientInterpretationProjectionV1Builder().build(
        structured_facts,
        requested_plan="premium",
        current_plan="premium",
    )
    return structured_facts, ai_input, client_projection
