# Commentaire global: ces tests verrouillent le payload LLM Basic derive du reading plan.
"""Tests du payload prompt Basic envoye au provider theme_astral."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from app.domain.llm.runtime.theme_astral_provider_payload_builder import (
    ThemeAstralProviderPayloadBuilder,
)
from tests.llm_orchestration.theme_astral_provider_payload_helpers import (
    build_basic_reading_plan,
)
from tests.unit.domain.astrology.interpretation.test_interpretation_material_builder import (
    _build_chart_input,
    _sources_for,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = REPO_ROOT / "app/domain/llm/runtime/theme_astral_provider_payload_builder.py"
FORBIDDEN_PROMPT_TOKENS = {
    "birth_context",
    "astrological_facts",
    "interpretation_material",
    "selected_themes",
    "limits",
    "chart_json",
    "natal_data",
    "email",
    "user_id",
    "place_id",
    "latitude",
    "longitude",
    "audit_input",
    "ranking_score",
    "weighted_score",
    "score_profile",
    "condition_axis",
    "prompt_hint",
    "required_fact_ids",
    "forbidden_fact_ids",
    "supporting_evidence_ids",
    "runtime.fact",
}


def test_basic_natal_prompt_payload_is_derived_from_reading_plan() -> None:
    """Le provider Basic recoit les sections et preuves selectionnees par le plan."""
    plan = build_basic_reading_plan()
    payload = _build_basic_payload(plan)
    prompt_payload = payload["input_data"]["basic_natal_prompt_payload"]

    assert len(prompt_payload["sections"]) == len(plan.sections)
    assert len(prompt_payload["resolved_syntheses"]) == len(plan.sections)
    assert len(prompt_payload["section_editorial_briefs"]) == len(plan.sections)
    assert len(prompt_payload["editorial_evidence"]) == len(plan.public_evidence)
    assert prompt_payload["limitations"] == list(plan.limitations)
    assert prompt_payload["disclaimers"] == list(plan.disclaimers)
    assert {item["section_code"] for item in prompt_payload["sections"]} == {
        section.section_code for section in plan.sections
    }


def test_basic_natal_prompt_payload_contract_shape_and_style_constraints() -> None:
    """Le contrat expose les blocs attendus et les contraintes redactionnelles Basic."""
    prompt_payload = _build_basic_payload(build_basic_reading_plan())["input_data"][
        "basic_natal_prompt_payload"
    ]

    assert tuple(prompt_payload) == (
        "report_arc",
        "sections",
        "resolved_syntheses",
        "section_editorial_briefs",
        "plain_language_glossary",
        "forbidden_template_phrases",
        "source_usage_policy",
        "editorial_evidence",
        "limitations",
        "disclaimers",
        "style_constraints",
    )
    assert prompt_payload["style_constraints"]["word_count"] == {
        "minimum": 900,
        "maximum": 1300,
    }
    assert prompt_payload["style_constraints"]["section_count"] == {
        "minimum": 6,
        "maximum": 8,
    }
    assert prompt_payload["style_constraints"]["tone"] == "vous"
    assert prompt_payload["style_constraints"]["prediction_policy"] == "no_firm_prediction"
    assert prompt_payload["style_constraints"]["advice_policy"] == "no_prescriptive_advice"
    assert "introduction" in prompt_payload["report_arc"]
    assert "annexe courte" in prompt_payload["source_usage_policy"]


def test_basic_natal_section_editorial_briefs_are_controlled_and_plan_scoped() -> None:
    """Chaque section recoit une matiere redactionnelle sans IDs internes."""
    prompt_payload = _build_basic_payload(build_basic_reading_plan())["input_data"][
        "basic_natal_prompt_payload"
    ]
    briefs = prompt_payload["section_editorial_briefs"]

    assert all(
        {
            "public_label",
            "reader_meaning",
            "possible_manifestation",
            "nuance",
            "allowed_section_role",
            "forbidden_claims",
            "source_fact_refs",
        }.issubset(brief)
        for brief in briefs
    )
    assert {brief["section_code"] for brief in briefs} == {
        section["section_code"] for section in prompt_payload["sections"]
    }
    assert all("plan Basic canonique" in " ".join(brief["forbidden_claims"]) for brief in briefs)


def test_basic_natal_prompt_payload_excludes_raw_carriers_and_private_fields() -> None:
    """Le JSON prompt-visible Basic reste sans PII, scores, chemins et IDs bruts."""
    payload = _build_basic_payload(build_basic_reading_plan())
    prompt_payload = payload["input_data"]["basic_natal_prompt_payload"]
    payload_without_denylist = {
        key: value for key, value in prompt_payload.items() if key != "forbidden_template_phrases"
    }
    serialized = json.dumps(payload_without_denylist, ensure_ascii=False, sort_keys=True)

    assert all(token not in serialized for token in FORBIDDEN_PROMPT_TOKENS)
    assert "moon" not in serialized.casefold()
    assert "north_node" not in serialized.casefold()
    editorial_evidence = prompt_payload["editorial_evidence"]
    assert all("id" not in item for item in editorial_evidence)


def test_basic_provider_payload_requires_reading_plan() -> None:
    """Le builder refuse un payload Basic sans owner de selection canonique."""
    chart_input = _build_chart_input(aspect_codes=("trine", "square", "opposition"))

    with pytest.raises(ValueError, match="BasicNatalReadingPlan"):
        ThemeAstralProviderPayloadBuilder().build(
            chart_input=chart_input,
            interpretation_sources=_sources_for(chart_input),
            commercial_plan="basic",
        )


def test_basic_provider_builder_does_not_select_from_natal_result() -> None:
    """AST guard: le builder Basic ne traverse pas de NatalResult brut."""
    tree = ast.parse(BUILDER_PATH.read_text(encoding="utf-8"))
    source = ast.unparse(tree)

    assert "NatalResult" not in source
    assert "build_chart_json" not in source
    assert "basic_reading_plan" in source
    assert "_basic_natal_prompt_payload" in source


def _build_basic_payload(plan: object) -> dict[str, object]:
    """Construit un payload Basic representatif sans appel provider."""
    chart_input = _build_chart_input(aspect_codes=("trine", "square", "opposition"))
    return ThemeAstralProviderPayloadBuilder().build(
        chart_input=chart_input,
        interpretation_sources=_sources_for(chart_input),
        commercial_plan="basic",
        astrologer_voice={"tone": "sobre"},
        basic_reading_plan=plan,
    )
