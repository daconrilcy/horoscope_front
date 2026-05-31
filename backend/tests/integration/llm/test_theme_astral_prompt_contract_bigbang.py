"""Prouve le handoff bigbang du contrat prompt theme astral."""

from __future__ import annotations

import json

import pytest

from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
)
from app.domain.llm.runtime.contracts import InputValidationError
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


def test_theme_astral_handoff_uses_only_canonical_prompt_contract() -> None:
    """Le provider ne recoit que theme_astral_llm_input_v1 pour theme_astral."""
    payload = _build_provider_payload("premium")

    rendered = LLMGateway().build_user_payload(
        use_case="theme_astral",
        user_input={"locale": "fr-FR"},
        context={
            THEME_ASTRAL_INPUT_CONTRACT_ID: payload,
            "llm_astrology_input_v1": {"legacy": True},
            "chart_json": '{"legacy": true}',
            "natal_data": {"legacy": True},
        },
        policy="none",
        locale="fr-FR",
    )

    prefix = f"{THEME_ASTRAL_INPUT_CONTRACT_ID}: "
    rendered_payload = json.loads(rendered.removeprefix(prefix))
    serialized = json.dumps(rendered_payload, ensure_ascii=False, sort_keys=True)

    assert rendered.startswith(prefix)
    assert rendered_payload["runtime_contract"]["prompt_contract_id"] == (
        THEME_ASTRAL_PROMPT_CONTRACT_ID
    )
    assert THEME_ASTRAL_PROMPT_CONTRACT_ID == "theme_astral_prompt_v1"
    assert "llm_astrology_input_v1:" not in rendered
    assert "chart_json" not in serialized
    assert "natal_data" not in serialized
    assert '"plan"' not in serialized
    assert rendered_payload["input_data"]["birth_context"]["birth_date"] == "1973-04-24"
    assert rendered_payload["input_data"]["birth_context"]["birth_time_local"] == "11:00"
    assert rendered_payload["input_data"]["birth_context"]["birth_place"] == {
        "city": "Paris",
        "country": "France",
        "timezone": "Europe/Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
    }
    assert rendered_payload["input_data"]["birth_context"]["precision"] == {
        "birth_time_known": True,
        "coordinates_known": True,
    }
    assert {"free", "basic", "premium"}.isdisjoint(_json_strings(rendered_payload))


def test_theme_astral_rejects_legacy_carriers_without_canonical_payload() -> None:
    """chart_json, natal_data et llm_astrology_input_v1 ne remplacent pas le contrat cible."""
    with pytest.raises(InputValidationError, match="theme_astral_llm_input_v1"):
        LLMGateway().build_user_payload(
            use_case="theme_astral",
            user_input={"locale": "fr-FR"},
            context={
                "llm_astrology_input_v1": {"legacy": True},
                "chart_json": '{"legacy": true}',
                "natal_data": {"legacy": True},
            },
            policy="none",
            locale="fr-FR",
        )


def test_example_payload_shapes_are_stable() -> None:
    """Les trois profils commerciaux produisent le meme squelette provider."""
    payloads = {plan: _build_provider_payload(plan) for plan in ("free", "basic", "premium")}

    assert {tuple(payload) for payload in payloads.values()} == {
        (
            "runtime_contract",
            "safety_contract",
            "astrologer_voice",
            "feature_context",
            "delivery_profile",
            "input_data",
            "output_contract",
        )
    }
    assert {tuple(payload["input_data"]) for payload in payloads.values()} == {
        (
            "birth_context",
            "astrological_facts",
            "interpretation_material",
            "selected_themes",
            "limits",
        ),
        ("basic_natal_prompt_payload",),
    }
    assert {payload["delivery_profile"]["depth"] for payload in payloads.values()} == {
        "essential",
        "expanded",
        "complete",
    }


def _build_provider_payload(plan: str) -> dict[str, object]:
    """Construit un payload representatif sans appel provider."""
    chart_input = _build_chart_input(
        aspect_codes=("trine", "square", "opposition", "conjunction", "sextile", "quincunx")
    )
    return ThemeAstralProviderPayloadBuilder().build(
        chart_input=chart_input,
        interpretation_sources=_sources_for(chart_input),
        commercial_plan=plan,  # type: ignore[arg-type]
        astrologer_voice={"tone": "calme", "vocabulary": ["symbolique"]},
        basic_reading_plan=build_basic_reading_plan() if plan == "basic" else None,
    )


def _json_strings(value: object) -> set[str]:
    """Collecte les chaines provider pour detecter une fuite commerciale."""
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {item for nested in value.values() for item in _json_strings(nested)}
    if isinstance(value, list):
        return {item for nested in value for item in _json_strings(nested)}
    return set()
