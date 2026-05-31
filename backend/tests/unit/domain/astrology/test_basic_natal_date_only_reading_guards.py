"""Tests de garde pour l'application aval de l'eligibilite Basic."""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

from app.domain.astrology.interpretation.llm_astrology_input_v1 import LLMAstrologyInputV1Builder

REPO_ROOT = Path(__file__).resolve().parents[4]
LLM_INPUT_PATH = REPO_ROOT / "app/domain/astrology/interpretation/llm_astrology_input_v1.py"


def test_date_only_llm_input_removes_house_surfaces_but_keeps_core_facts() -> None:
    """Le payload Basic date seule garde signes/aspects en coupant les maisons."""
    payload = LLMAstrologyInputV1Builder().build(
        structured_facts_v1=_structured_facts_date_only(),
        ai_narrative_input=_ai_input(),
        evidence_refs=(),
    )

    eligibility = payload["limits"]["birth_time_eligibility"]
    assert eligibility["birth_time_status"] == "date_only"
    assert eligibility["can_use_houses"] is False
    assert eligibility["can_use_angles"] is False
    assert eligibility["can_use_house_rulers"] is False
    assert payload["facts"]["houses"] == []
    assert payload["facts"]["positions"] == [
        {
            "code": "sun",
            "zodiac_sign": "aries",
            "degree_in_sign": 10.0,
            "house_number": None,
        },
        {
            "code": "moon",
            "zodiac_sign": "taurus",
            "degree_in_sign": 12.0,
            "house_number": None,
        },
    ]
    assert payload["facts"]["major_aspects"] == [
        {"code": "trine", "participant_codes": ["sun", "moon"]}
    ]
    assert payload["signals"]["interpretive_signal_codes"]["house_position_codes"] == []
    assert payload["signals"]["interpretive_signal_codes"]["dispositor_codes"] == []
    assert "angularity" not in payload["facts"]["dominants"][0]["factors"]


def test_llm_input_builder_consumes_canonical_eligibility_guard() -> None:
    """Le builder LLM importe et applique le garde canonique au lieu de redecider."""
    tree = ast.parse(LLM_INPUT_PATH.read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "apply_basic_natal_eligibility_to_llm_blocks" in imported_names
    assert "apply_basic_natal_eligibility_to_llm_blocks" in called_names


def _structured_facts_date_only() -> dict[str, object]:
    """Construit des faits avec maisons historiques que le garde doit neutraliser."""
    return {
        "projection_id": "structured_facts_v1",
        "contract_version": "structured_facts_v1.contract.v1",
        "structural_facts": {
            "positions": [
                {
                    "code": "sun",
                    "zodiac_sign": "aries",
                    "degree_in_sign": 10.0,
                    "house_number": 1,
                },
                {
                    "code": "moon",
                    "zodiac_sign": "taurus",
                    "degree_in_sign": 12.0,
                    "house_number": 4,
                },
            ],
            "houses": [{"house_number": 1}],
            "major_aspects": [{"code": "trine", "participant_codes": ["sun", "moon"]}],
            "source_metadata": {"chart_id": "chart-1"},
            "sign_profile_balances": {
                "elements": [{"code": "fire", "score": 1.0}],
                "modalities": [{"code": "fixed", "score": 1.0}],
            },
        },
        "interpretive_signals": {
            "dignity_codes": ["sun"],
            "house_position_codes": ["sun"],
            "dispositor_codes": ["mars"],
        },
        "dominants": [{"code": "sun", "factors": ["angularity", "luminary"]}],
        "missing_data": {
            "birth_time": "missing",
            "birth_timezone": "missing",
            "reasons": ["no_time"],
            "empty_collections": [],
        },
    }


def _ai_input() -> SimpleNamespace:
    """Construit le minimum du contrat narratif consomme par le builder."""
    return SimpleNamespace(
        contract_version="ai_narrative_input.v1",
        interpretive_signals={
            "dignity_codes": ["sun"],
            "house_position_codes": ["sun"],
            "dispositor_codes": ["mars"],
        },
        readiness_flags={"ready_for_narrative": True},
        masking_policy={"policy": "test"},
        source_versions={"test": "v1"},
        public_projection_links=(),
    )
