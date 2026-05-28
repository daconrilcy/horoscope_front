# Commentaire global: ces tests verrouillent l'extinction des chemins legacy du runtime LLM.

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.llm.configuration.canonical_use_case_registry import (
    get_canonical_use_case_contract,
    list_modern_natal_use_case_contracts,
)
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayConfigError,
    InputValidationError,
    LLMExecutionRequest,
    OutputValidationError,
    UseCaseConfig,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.llm.runtime.output_validator import ValidationResult
from app.ops.llm.bootstrap.seed_guidance_prompts import GUIDANCE_PROMPTS_TO_SEED


@pytest.fixture
def gateway():
    return LLMGateway()


def test_modern_natal_contracts_only_expose_llm_astrology_input_v1() -> None:
    """Verifie que les contrats natals modernes n'exposent aucun carrier legacy."""

    forbidden_carriers = {"chart_json", "natal_data", "evidence_catalog"}

    for contract in list_modern_natal_use_case_contracts():
        assert "llm_astrology_input_v1" in contract.required_prompt_placeholders
        assert not forbidden_carriers.intersection(contract.required_prompt_placeholders)

        assert contract.input_schema is not None
        assert contract.input_schema.get("required") == ["llm_astrology_input_v1"]
        properties = set(contract.input_schema.get("properties", {}))
        assert "llm_astrology_input_v1" in properties
        assert not forbidden_carriers.intersection(properties)


def test_event_guidance_contract_and_seed_are_removed() -> None:
    """Prouve que le use case evenementiel dormant n'a plus de surface runtime."""

    assert get_canonical_use_case_contract("event_guidance") is None
    assert all(prompt["use_case_key"] != "event_guidance" for prompt in GUIDANCE_PROMPTS_TO_SEED)


def test_natal_user_payload_ignores_legacy_carriers_when_modern_input_exists(gateway) -> None:
    """Prouve que le payload utilisateur natal ne consomme que l'entree moderne."""

    payload = gateway.build_user_payload(
        use_case="natal_interpretation",
        user_input={},
        context={
            "llm_astrology_input_v1": {"facts": {"sun": "Aries"}},
            "chart_json": '{"legacy": true}',
            "natal_data": {"legacy": True},
            "evidence_catalog": ["legacy-evidence"],
        },
        policy="none",
        locale="fr-FR",
    )

    assert "llm_astrology_input_v1" in payload
    assert "Aries" in payload
    assert "chart_json" not in payload
    assert "natal_data" not in payload
    assert "legacy-evidence" not in payload


def test_natal_validation_payload_ignores_declared_legacy_carriers(gateway) -> None:
    """Bloque la reintroduction de carriers legacy via le schema de validation natal."""

    config = UseCaseConfig(
        model="gpt-5-nano",
        developer_prompt="Prompt {{llm_astrology_input_v1}}",
        input_schema={
            "type": "object",
            "required": ["llm_astrology_input_v1"],
            "properties": {
                "llm_astrology_input_v1": {"type": "object"},
                "chart_json": {"type": "object"},
                "natal_data": {"type": "object"},
                "evidence_catalog": {"type": "array"},
            },
        },
    )

    payload = gateway._build_validation_payload(
        config,
        {"use_case": "natal_interpretation"},
        ExecutionContext(
            chart_json='{"legacy": true}',
            natal_data={"legacy": True},
            extra_context={
                "llm_astrology_input_v1": {"contract_id": "llm_astrology_input_v1"},
                "evidence_catalog": ["legacy-evidence"],
            },
        ),
    )

    assert payload == {
        "use_case": "natal_interpretation",
        "llm_astrology_input_v1": {"contract_id": "llm_astrology_input_v1"},
    }


@pytest.mark.asyncio
async def test_legacy_use_case_entry_is_rejected_before_stage_05(gateway):
    """
    Issue 1: Pure legacy use_case entries (e.g., 'chat_astrologer') MUST bypass
    Stage 0.5 pre-validation because they map to supported families.
    """
    # 'chat_astrologer' maps to feature='chat'
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat_astrologer", locale="fr-FR"),
        context=ExecutionContext(),
        request_id="test-66-29-legacy-entry",
        trace_id="trace-66-29",
    )

    registry_path = (
        "app.domain.llm.configuration.assembly_registry.AssemblyRegistry.get_active_config_sync"
    )

    stage05 = UseCaseConfig(
        model="gpt-4",
        developer_prompt="stub-stage05",
        input_schema=None,
    )
    # Story 70.13: once normalized to a supported family, Stage 0.5 must no longer
    # resolve a legacy use-case config before canonical assembly/profile resolution.
    with patch.object(
        gateway, "_resolve_fallback_use_case_config", new=AsyncMock(return_value=stage05)
    ) as mock_resolve_config:
        # We fail assembly resolution to stop the pipeline after Stage 1
        with patch(registry_path, return_value=None):
            with pytest.raises(GatewayConfigError) as exc:
                await gateway.execute_request(request, db=MagicMock())

            assert "Legacy use_case key 'chat_astrologer' is removed" in str(exc.value)
            assert mock_resolve_config.call_count == 0


@pytest.mark.asyncio
async def test_input_schema_is_propagated_and_validated(gateway):
    """
    Issue 2: Assembly input_schema MUST be propagated and used for Stage 1.5 validation.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            feature="chat",
            subfeature="astrologer",
            plan="free",
            locale="fr-FR",
            use_case="chat",
            message="hello",
        ),
        context=ExecutionContext(),
        request_id="test-66-29-input-schema",
        trace_id="trace-66-29",
    )

    # Mock resolved plan (Stage 1) with an input schema
    mock_plan = MagicMock()
    mock_plan.model_id = "gpt-4o"
    mock_plan.temperature = 0.7
    mock_plan.max_output_tokens = 1000
    mock_plan.rendered_developer_prompt = "test"
    mock_plan.output_schema_id = None
    mock_plan.interaction_mode = "chat"
    mock_plan.user_question_policy = "required"
    mock_plan.required_prompt_placeholders = []
    # REQUIRE 'required_field' in input
    mock_plan.input_schema = {
        "type": "object",
        "required": ["required_field"],
        "properties": {"required_field": {"type": "string"}},
    }

    # We patch _resolve_plan to return our plan with schema
    with patch.object(gateway, "_resolve_plan", return_value=(mock_plan, None)):
        # Stage 1.5 SHOULD fail because 'required_field' is missing from user_input
        with pytest.raises(InputValidationError) as exc:
            await gateway.execute_request(request, db=MagicMock())

        assert "Input validation failed" in str(exc.value)
        assert "required_field" in str(exc.value)


@pytest.mark.asyncio
async def test_recovery_blocks_legacy_fallback_for_supported_feature(gateway):
    """
    Ensure _handle_repair_or_fallback strictly forbids legacy fallback for supported features.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="chat", locale="fr-FR"),
        context=ExecutionContext(),
        request_id="test-66-29-recovery",
        trace_id="trace-66-29",
    )

    # Mock Stage 4 result: invalid output
    validation_result = ValidationResult(valid=False, parsed=None, errors=["format error"])

    # Mock resolved plan (Stage 1)
    mock_plan = MagicMock()
    mock_plan.feature = "chat"
    mock_plan.output_schema_version = "v1"

    # Mock provider result (Stage 3)
    mock_provider_result = MagicMock()
    mock_provider_result.raw_output = "bad json"

    async def abort_nested_repair(*_args, **_kwargs):
        raise RuntimeError("abort nested execute_request during repair (test)")

    # Repair : execute_request imbriqué ; on l’interrompt pour tester le refus de fallback legacy.
    with patch.object(gateway, "execute_request", side_effect=abort_nested_repair):
        with patch.object(
            gateway, "_resolve_fallback_use_case_config", new=AsyncMock()
        ) as mock_resolve_config:
            with pytest.raises(OutputValidationError) as exc:
                await gateway._handle_repair_or_fallback(
                    validation_result, request, mock_plan, mock_provider_result, db=MagicMock()
                )

            assert "Legacy use_case fallback is strictly forbidden" in str(exc.value)
            assert mock_resolve_config.call_count == 0


@pytest.mark.asyncio
async def test_unsupported_features_still_allow_prevalidation_and_fallback(gateway):
    """
    AC8: Features NOT in supported perimeter still allow use_case-first pre-validation and fallback.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="experimental_case", feature="experimental_feature", locale="fr-FR"
        ),
        context=ExecutionContext(),
        request_id="test-66-29-other",
        trace_id="trace-66-29",
    )

    mock_config = MagicMock()
    mock_config.input_schema = None
    mock_config.fallback_use_case = "some_fallback"

    # Stage 0.5 should call the bounded legacy compatibility resolver.
    with patch.object(
        gateway, "_resolve_fallback_use_case_config", return_value=mock_config
    ) as mock_resolve:
        # We simulate a failure in _resolve_plan to stop execution after Stage 0.5
        with patch.object(gateway, "_resolve_plan", side_effect=ValueError("stop here")):
            with pytest.raises(ValueError, match="stop here"):
                await gateway.execute_request(request, db=MagicMock())

            assert mock_resolve.call_count >= 1
