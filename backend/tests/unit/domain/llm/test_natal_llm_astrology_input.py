# Tests du transport runtime natal pour llm_astrology_input_v1.
"""Verifie que le runtime natal consomme le contrat riche sans appel provider."""

from __future__ import annotations

import pytest

from app.domain.llm.configuration.canonical_use_case_registry import (
    NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    get_canonical_use_case_contract,
)
from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.domain.llm.runtime import adapter as adapter_module
from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    GatewayMeta,
    GatewayResult,
    NatalExecutionInput,
    UsageInfo,
    UseCaseConfig,
)
from app.domain.llm.runtime.gateway import LLMGateway


@pytest.mark.asyncio
async def test_natal_execution_input_transports_rich_contract_to_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le transport natal place le contrat riche dans la cle schema-owned."""
    captured_request = None
    rich_input = {"contract_id": "llm_astrology_input_v1", "facts": {"positions": []}}

    class FakeGateway:
        async def execute_request(self, request, db=None):
            nonlocal captured_request
            captured_request = request
            return GatewayResult(
                use_case=request.user_input.use_case,
                request_id=request.request_id,
                trace_id=request.trace_id,
                raw_output="{}",
                usage=UsageInfo(input_tokens=1, output_tokens=1),
                meta=GatewayMeta(latency_ms=1, model="test-model"),
            )

    monkeypatch.setattr(adapter_module, "LLMGateway", FakeGateway)

    await AIEngineAdapter.generate_natal_interpretation(
        NatalExecutionInput(
            use_case_key="natal_interpretation",
            locale="fr-FR",
            level="complete",
            llm_astrology_input_v1=rich_input,
            plan="premium",
            validation_strict=True,
            user_id=42,
            request_id="req-rich",
            trace_id="trace-rich",
        )
    )

    assert captured_request is not None
    assert captured_request.context.extra_context["llm_astrology_input_v1"] == rich_input
    assert captured_request.context.chart_json is None
    assert captured_request.context.natal_data is None
    assert captured_request.flags.evidence_catalog is None
    assert "llm_astrology_input_v1" not in ExecutionContext.model_fields


def test_gateway_prefers_rich_input_over_chart_json_in_user_payload() -> None:
    """Le bloc utilisateur natal ignore les anciens carriers meme sans contrat riche."""
    rich_input = {"contract_id": "llm_astrology_input_v1", "facts": {"positions": []}}

    payload = LLMGateway().build_user_payload(
        use_case="natal_interpretation",
        user_input={},
        context={
            "llm_astrology_input_v1": rich_input,
            "chart_json": '{"legacy": "secret"}',
            "natal_data": {"legacy": "secret"},
        },
        policy="none",
        locale="fr-FR",
    )

    assert "llm_astrology_input_v1" in payload
    assert "legacy" not in payload
    assert "Technical Data" not in payload

    fallback_payload = LLMGateway().build_user_payload(
        use_case="natal_interpretation",
        user_input={},
        context={
            "chart_json": '{"legacy": "secret"}',
            "natal_data": {"legacy": "secret"},
        },
        policy="none",
        locale="fr-FR",
    )

    assert fallback_payload == "Interprète les données astrologiques fournies."
    assert "legacy" not in fallback_payload


def test_validation_payload_uses_llm_astrology_input_v1_schema_key() -> None:
    """La validation interne lit la cle riche depuis extra_context."""
    rich_input = {"contract_id": "llm_astrology_input_v1"}
    config = UseCaseConfig(
        model="test-model",
        developer_prompt="Prompt {{llm_astrology_input_v1}}",
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    )

    payload = LLMGateway()._build_validation_payload(
        config,
        user_input={"locale": "fr-FR"},
        context=ExecutionContext(
            extra_context={"llm_astrology_input_v1": rich_input},
        ),
    )

    assert payload["llm_astrology_input_v1"] == rich_input
    assert "chart_json" not in payload


def test_natal_execution_input_excludes_legacy_carrier_fields() -> None:
    """Le contrat natal ne peut plus transporter les anciens carriers prompt."""

    forbidden_fields = {"chart_json", "natal_data", "evidence_catalog"}

    assert forbidden_fields.isdisjoint(NatalExecutionInput.model_fields)


def test_natal_prompt_placeholder_registry_accepts_rich_key_without_legacy_carrier() -> None:
    """Le renderer natal peut rendre la cle riche sans chart_json ni natal_data."""
    contract = get_canonical_use_case_contract("natal_interpretation")
    assert contract is not None
    assert contract.required_prompt_placeholders == ["llm_astrology_input_v1", "persona_name"]

    rendered = PromptRenderer.render(
        "Payload {{llm_astrology_input_v1}} / legacy {{chart_json}}",
        {
            "llm_astrology_input_v1": {"contract_id": "llm_astrology_input_v1"},
            "persona_name": "Standard",
        },
        required_variables=contract.required_prompt_placeholders,
        feature="natal",
    )

    assert "llm_astrology_input_v1" in rendered
    assert "{{chart_json}}" not in rendered
    assert "legacy " in rendered
