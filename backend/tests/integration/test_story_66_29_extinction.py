from unittest.mock import MagicMock, patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayConfigError,
    InputValidationError,
    LLMExecutionRequest,
    OutputValidationError,
)
from app.llm_orchestration.services.output_validator import ValidationResult


@pytest.fixture
def gateway():
    return LLMGateway()


@pytest.mark.asyncio
async def test_story_66_29_legacy_use_case_entry_bypasses_stage_05(gateway):
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
        "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync"
    )

    # We mock _resolve_config to prove it's NOT called for pre-validation (Stage 0.5)
    with patch.object(gateway, "_resolve_config") as mock_resolve_config:
        # We fail assembly resolution to stop the pipeline after Stage 1
        with patch(registry_path, return_value=None):
            with pytest.raises(GatewayConfigError) as exc:
                await gateway.execute_request(request, db=MagicMock())

            assert "Mandatory assembly missing for supported chat family" in str(exc.value)
            # PROOF: _resolve_config was NOT called in Stage 0.5
            assert mock_resolve_config.call_count == 0


@pytest.mark.asyncio
async def test_story_66_29_input_schema_propagation_and_validation(gateway):
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
async def test_story_66_29_recovery_blocks_legacy_fallback_for_supported(gateway):
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

    # We patch _resolve_config to ensure it's NOT called during recovery for supported features
    with patch.object(gateway, "_resolve_config") as mock_resolve_config:
        with pytest.raises(OutputValidationError) as exc:
            await gateway._handle_repair_or_fallback(
                validation_result, request, mock_plan, mock_provider_result, db=MagicMock()
            )

        assert "Legacy use_case fallback is strictly forbidden" in str(exc.value)
        assert mock_resolve_config.call_count == 0


@pytest.mark.asyncio
async def test_story_66_29_other_features_still_allow_prevalidation_and_fallback(gateway):
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

    # Stage 0.5 should call _resolve_config
    with patch.object(gateway, "_resolve_config", return_value=mock_config) as mock_resolve:
        # We simulate a failure in _resolve_plan to stop execution after Stage 0.5
        with patch.object(gateway, "_resolve_plan", side_effect=ValueError("stop here")):
            with pytest.raises(ValueError, match="stop here"):
                await gateway.execute_request(request, db=MagicMock())

            assert mock_resolve.call_count >= 1
