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
from app.domain.astrology.runtime.chart_signature_runtime_data import (
    BalanceScoreRuntimeData,
    ChartBalanceRuntimeData,
    ChartSignatureRuntimeData,
)
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
    assert payload["facts"]["positions"][0]["zodiac_sign"] == "aries"
    assert payload["facts"]["houses"][0]["house_number"] == 1
    assert payload["facts"]["major_aspects"][0]["code"] == "trine"
    assert payload["facts"]["sign_profile_balances"]["elements"][0]["code"] == "fire"
    assert payload["facts"]["sign_profile_balances"]["modalities"][0]["code"] == "cardinal"
    assert payload["facts"]["sign_profile_balances"]["polarities"][0]["code"] == "yang"
    assert payload["signals"]["interpretive_signal_codes"]["dignity_codes"] == ["mars"]
    assert payload["signals"]["readiness_flags"]["ready_for_narrative"] is True
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


def test_llm_astrology_input_v1_missing_data_is_prompt_visible() -> None:
    """Les donnees absentes restent visibles dans limits sans carrier brut."""
    payload = _build_payload(with_payloads=False, with_chart_balance=False)

    assert payload["limits"]["missing_data"]["sign_balances"] is None
    assert payload["limits"]["missing_data"]["empty_collections"] == [
        "advanced_condition_facts",
        "dominants",
        "fixed_star_contacts",
        "houses",
        "major_aspects",
    ]
    assert payload["limits"]["unavailable_sections"] == ["interpretive_signals_ready"]
    assert payload["facts"]["houses"] == []
    assert payload["facts"]["major_aspects"] == []
    assert payload["facts"]["sign_profile_balances"] is None


def test_llm_astrology_input_v1_keeps_facts_signals_and_shaping_disjoint() -> None:
    """Les blocs ont un owner lisible et ne recopient pas les memes champs."""
    payload = _build_payload()

    assert "interpretive_signal_codes" not in payload["facts"]
    assert "structural_facts" not in payload["signals"]
    assert {"positions", "houses", "major_aspects"}.isdisjoint(payload["signals"])
    assert {"plan", "module", "llm_input_selection"}.isdisjoint(payload["facts"])
    assert payload["provenance"]["source_ids"] == {
        "facts": "structured_facts_v1",
        "signals": "AINarrativeInputContract",
        "shaping": "client_interpretation_projection_v1",
    }


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


def _build_payload(
    *,
    with_payloads: bool = True,
    with_chart_balance: bool = True,
) -> dict[str, object]:
    """Construit un payload representatif du contrat LLM interne."""
    structured_facts, ai_input, client_projection = _build_sources(
        with_payloads=with_payloads,
        with_chart_balance=with_chart_balance,
    )
    return LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=ai_input,
        client_interpretation_projection_v1=client_projection,
        evidence_refs=(),
        prompt_ref="natal.astrology.compact.v1",
    )


def _build_sources(
    *,
    with_payloads: bool = True,
    with_chart_balance: bool = True,
) -> tuple[dict[str, object], object, dict[str, object]]:
    """Assemble les trois sources canoniques attendues par la story."""
    source = _NatalSource(
        chart_objects=(interpretable_chart_object("mars", with_payloads=with_payloads),),
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
        )
        if with_payloads
        else (),
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
            )
            if with_payloads
            else (),
            top_planet_code="mars" if with_payloads else None,
            chart_ruler_code="mars" if with_payloads else None,
            most_elevated_planet_code=None,
        ),
        chart_balance=_chart_balance() if with_chart_balance else None,
    )
    structured_facts = StructuredFactsV1Builder().build(source, chart_id="chart-1", locale="fr")
    ai_input = AINarrativeInputBuilder().build(source, chart_id="chart-1", locale="fr")
    client_projection = ClientInterpretationProjectionV1Builder().build(
        structured_facts,
        requested_plan="premium",
        current_plan="premium",
    )
    return structured_facts, ai_input, client_projection


def _chart_balance() -> ChartBalanceRuntimeData:
    """Construit des balances synthetiques deja calculees pour le mapping facts."""
    return ChartBalanceRuntimeData(
        elements=(BalanceScoreRuntimeData(code="fire", score=1.0, rank=1),),
        modalities=(BalanceScoreRuntimeData(code="cardinal", score=1.0, rank=1),),
        polarities=(BalanceScoreRuntimeData(code="yang", score=1.0, rank=1),),
        seasonal_quadrants=(BalanceScoreRuntimeData(code="spring", score=1.0, rank=1),),
        fertility=(BalanceScoreRuntimeData(code="barren", score=1.0, rank=1),),
        voices=(BalanceScoreRuntimeData(code="vocal", score=1.0, rank=1),),
        forms=(BalanceScoreRuntimeData(code="humane", score=1.0, rank=1),),
        dominant_signs=(),
        dominant_planets=(),
        dominant_houses=(),
        dominant_aspects=(),
        synthesis=ChartSignatureRuntimeData(
            primary_element="fire",
            primary_modality="cardinal",
            primary_polarity="yang",
            primary_seasonal_quadrant="spring",
            primary_fertility="barren",
            primary_voice="vocal",
            primary_form="humane",
            primary_sign=None,
            primary_planet=None,
            primary_house=None,
        ),
    )
