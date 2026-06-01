"""Test d'integration du handoff provider theme astral sans appel LLM."""

from __future__ import annotations

import json

from app.domain.llm.configuration.theme_astral_contracts import THEME_ASTRAL_INPUT_CONTRACT_ID
from app.domain.llm.runtime.gateway import LLMGateway
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


def test_gateway_handoff_uses_theme_astral_provider_payload_once() -> None:
    """Le gateway transmet le payload construit dans le user block canonique."""
    chart_input = _build_chart_input(aspect_codes=("trine", "square", "opposition"))
    payload = ThemeAstralProviderPayloadBuilder().build(
        chart_input=chart_input,
        interpretation_sources=_sources_for(chart_input),
        commercial_plan="premium",
        astrologer_voice={"tone": "sobre"},
    )

    rendered = LLMGateway().build_user_payload(
        use_case="theme_astral",
        user_input={"locale": "fr-FR"},
        context={THEME_ASTRAL_INPUT_CONTRACT_ID: payload},
        policy="none",
        locale="fr-FR",
    )

    prefix = f"{THEME_ASTRAL_INPUT_CONTRACT_ID}: "
    assert rendered.startswith(prefix)
    rendered_payload = json.loads(rendered.removeprefix(prefix))
    assert rendered_payload == payload
    assert rendered.count('"interpretation_material":') == 1
    assert rendered_payload["input_data"]["birth_context"]["birth_date"] == "1973-04-24"
    assert rendered_payload["input_data"]["birth_context"]["birth_time_local"] == "11:00"
    assert rendered_payload["input_data"]["birth_context"]["birth_place"]["city"] == "Paris"
    assert rendered_payload["input_data"]["selected_themes"]["section_keys"]
    assert not rendered_payload["input_data"]["limits"]["missing_data"]["birth_context"]
    assert not rendered_payload["input_data"]["limits"]["missing_data"]["empty_fact_groups"]
    assert '"plan"' not in rendered
    assert '"chart_json"' not in rendered
    assert '"natal_data"' not in rendered


def test_gateway_handoff_keeps_basic_prompt_payload_private_and_complete() -> None:
    """Le flux Basic transmet le payload redactionnel sans carriers legacy."""
    chart_input = _build_chart_input(aspect_codes=("trine", "square", "opposition"))
    payload = ThemeAstralProviderPayloadBuilder().build(
        chart_input=chart_input,
        interpretation_sources=_sources_for(chart_input),
        commercial_plan="basic",
        astrologer_voice={"tone": "sobre"},
        basic_reading_plan=build_basic_reading_plan(),
    )

    rendered = LLMGateway().build_user_payload(
        use_case="theme_astral",
        user_input={"locale": "fr-FR"},
        context={THEME_ASTRAL_INPUT_CONTRACT_ID: payload},
        policy="none",
        locale="fr-FR",
    )

    prefix = f"{THEME_ASTRAL_INPUT_CONTRACT_ID}: "
    rendered_payload = json.loads(rendered.removeprefix(prefix))
    prompt_payload = rendered_payload["input_data"]["basic_natal_prompt_payload"]
    serialized = json.dumps(rendered_payload, ensure_ascii=False, sort_keys=True)

    assert rendered.startswith(prefix)
    assert rendered_payload == payload
    assert rendered.count('"basic_natal_prompt_payload":') == 1
    assert rendered_payload["runtime_contract"]["prompt_contract_id"] == "theme_astral_prompt_v1"
    assert rendered_payload["delivery_profile"]["depth"] == "expanded"
    assert set(prompt_payload) == {
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
    }
    assert prompt_payload["sections"]
    assert prompt_payload["editorial_evidence"]
    assert prompt_payload["style_constraints"]
    assert prompt_payload["limitations"]
    assert prompt_payload["disclaimers"]
    for forbidden in (
        '"chart_json"',
        '"natal_data"',
        '"audit_input"',
        '"ranking_score"',
        '"weighted_score"',
        '"condition_axis"',
        '"prompt_hint"',
        '"user_id"',
        '"email"',
        '"latitude"',
        '"longitude"',
        '"plan"',
    ):
        assert forbidden not in serialized
