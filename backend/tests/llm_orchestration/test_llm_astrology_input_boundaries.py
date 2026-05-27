# Guards de frontiere du payload llm_astrology_input_v1 avant appel provider.
"""Verifie la matiere prompt-visible natale sans appeler de provider externe."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.astrology.interpretation.llm_astrology_input_v1 import (
    LLM_ASTROLOGY_INPUT_DATA_ROLES,
)
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.domain.llm.runtime.gateway import LLMGateway
from tests.unit.domain.astrology.test_llm_astrology_input_v1 import _build_payload

FORBIDDEN_PROMPT_SURFACES = {
    "ChartObjectRuntimeData",
    "CalculationGraph",
    "chart_json",
    "natal_data",
}
PROMPT_VISIBLE_BLOCKS = {
    *LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"],
}
AUDIT_ONLY_PROMPT_SURFACES = {
    "provenance",
    "projection_hash",
    "llm_input_hash",
    "llm_input_version",
    "grounding_status",
    "validation_owner",
    "evidence_refs",
    "provider_response",
    "persisted_answer",
}


def test_gateway_payload_projects_prompt_visible_role_blocks_only() -> None:
    """Le gateway extrait les blocs riches sans roles runtime, validation ou audit."""
    payload = _build_payload()

    prompt_payload = _rendered_llm_input(payload)

    assert set(prompt_payload) == PROMPT_VISIBLE_BLOCKS
    assert prompt_payload["facts"]["positions"]
    assert prompt_payload["signals"]["interpretive_signal_codes"]
    assert prompt_payload["limits"]["missing_data"]["empty_collections"] == [
        "advanced_condition_facts"
    ]
    assert "evidence" in prompt_payload
    assert prompt_payload["shaping"]["plan"] == "premium"
    assert AUDIT_ONLY_PROMPT_SURFACES.isdisjoint(_nested_keys(prompt_payload))


def test_gateway_payload_makes_missing_data_limits_prompt_visible() -> None:
    """Les limites de donnees absentes arrivent dans le payload rendu."""
    payload = _build_payload(with_payloads=False, with_chart_balance=False)

    prompt_payload = _rendered_llm_input(payload)

    assert prompt_payload["limits"]["missing_data"]["sign_balances"] is None
    assert prompt_payload["limits"]["missing_data"]["empty_collections"] == [
        "advanced_condition_facts",
        "dominants",
        "fixed_star_contacts",
        "houses",
        "major_aspects",
    ]
    assert prompt_payload["limits"]["unavailable_sections"] == ["interpretive_signals_ready"]


def test_gateway_payload_does_not_promote_raw_or_legacy_prompt_owners() -> None:
    """chart_json et natal_data restent hors prompt quand le contrat riche existe."""
    payload = _build_payload()
    rendered = LLMGateway().build_user_payload(
        use_case="natal_interpretation",
        user_input={"locale": "fr-FR"},
        context={
            "llm_astrology_input_v1": payload,
            "chart_json": '{"legacy": "LEGACY_CHART_JSON_PROMPT_OWNER"}',
            "natal_data": {"legacy": "LEGACY_NATAL_DATA_PROMPT_OWNER"},
        },
        policy="none",
        locale="fr-FR",
    )

    assert "LEGACY_CHART_JSON_PROMPT_OWNER" not in rendered
    assert "LEGACY_NATAL_DATA_PROMPT_OWNER" not in rendered
    assert not (FORBIDDEN_PROMPT_SURFACES & _string_values(_parse_rendered_llm_input(rendered)))


@pytest.mark.asyncio
async def test_gateway_provider_handoff_uses_local_double_and_prompt_boundary() -> None:
    """La preuve de handoff inspecte les messages sans appel LLM externe."""
    payload = _build_payload()
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=(
            GatewayResult(
                use_case="test_natal",
                request_id="r1",
                trace_id="t1",
                raw_output='{"message": "ok"}',
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=1, model="m"),
            ),
            {},
        )
    )
    gateway = LLMGateway(responses_client=mock_client)

    await gateway.execute(
        use_case="test_natal",
        user_input={"locale": "fr-FR"},
        context={
            "llm_astrology_input_v1": payload,
            "chart_json": '{"legacy": "LEGACY_CHART_JSON_PROMPT_OWNER"}',
            "natal_data": {"legacy": "LEGACY_NATAL_DATA_PROMPT_OWNER"},
        },
        request_id="r1",
        trace_id="t1",
        flags={"test_fallback_active": True},
    )

    mock_client.execute.assert_called_once()
    messages = mock_client.execute.call_args.kwargs["messages"]
    user_message = next(message for message in messages if message["role"] == "user")
    prompt_payload = _parse_rendered_llm_input(user_message["content"])

    assert set(prompt_payload) == PROMPT_VISIBLE_BLOCKS
    assert AUDIT_ONLY_PROMPT_SURFACES.isdisjoint(_nested_keys(prompt_payload))
    assert prompt_payload["evidence"] == {}
    assert "LEGACY_CHART_JSON_PROMPT_OWNER" not in user_message["content"]
    assert "LEGACY_NATAL_DATA_PROMPT_OWNER" not in user_message["content"]


def _rendered_llm_input(payload: dict[str, object]) -> dict[str, object]:
    """Rend le payload via le gateway comme juste avant composition des messages."""
    rendered = LLMGateway().build_user_payload(
        use_case="natal_interpretation",
        user_input={"locale": "fr-FR"},
        context={"llm_astrology_input_v1": payload},
        policy="none",
        locale="fr-FR",
    )
    return _parse_rendered_llm_input(rendered)


def _parse_rendered_llm_input(rendered: str) -> dict[str, object]:
    """Decode le bloc JSON `llm_astrology_input_v1` rendu par le gateway."""
    prefix = "llm_astrology_input_v1: "
    assert rendered.startswith(prefix)
    payload = json.loads(rendered.removeprefix(prefix))
    assert isinstance(payload, dict)
    return payload


def _string_values(value: object) -> set[str]:
    """Collecte les valeurs texte pour detecter les carriers interdits."""
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {item for nested_value in value.values() for item in _string_values(nested_value)}
    if isinstance(value, list):
        return {item for nested_value in value for item in _string_values(nested_value)}
    return set()


def _nested_keys(value: object) -> set[str]:
    """Collecte les cles imbriquees pour refuser les champs audit-only au prompt."""
    if isinstance(value, dict):
        return set(value) | {
            item for nested_value in value.values() for item in _nested_keys(nested_value)
        }
    if isinstance(value, list):
        return {item for nested_value in value for item in _nested_keys(nested_value)}
    return set()
