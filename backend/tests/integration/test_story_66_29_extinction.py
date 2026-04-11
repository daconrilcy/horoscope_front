from unittest.mock import MagicMock, patch

import pytest

from app.llm_orchestration.feature_taxonomy import SUPPORTED_FAMILIES
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayConfigError,
    LLMExecutionRequest,
    OutputValidationError,
)
from app.llm_orchestration.services.output_validator import ValidationResult


@pytest.fixture
def gateway():
    return LLMGateway()

@pytest.mark.asyncio
async def test_story_66_29_execute_request_rejection_if_no_assembly(gateway):
    """
    AC1, AC6: Fail explicitly at entry point if a supported feature has no assembly.
    Ensures _resolve_config is NOT used for pre-validation.
    """
    for feature in SUPPORTED_FAMILIES:
        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(
                feature=feature,
                subfeature="any",
                plan="free",
                locale="fr-FR",
                use_case="legacy_case"
            ),
            context=ExecutionContext(),
            request_id=f"test-66-29-{feature}",
            trace_id="trace-66-29"
        )

        registry_path = (
            "app.llm_orchestration.services.assembly_registry."
            "AssemblyRegistry.get_active_config_sync"
        )
        # We mock _resolve_config to prove it's NOT called for pre-validation
        with patch.object(gateway, "_resolve_config") as mock_resolve_config:
            with patch(registry_path, return_value=None):
                with pytest.raises(GatewayConfigError) as exc:
                    await gateway.execute_request(request, db=MagicMock())
                
                msg = f"Mandatory assembly missing for supported {feature} family"
                assert msg in str(exc.value)
                # Check that _resolve_config was never called (skipped in Stage 0.5)
                assert mock_resolve_config.call_count == 0

@pytest.mark.asyncio
async def test_story_66_29_recovery_blocks_legacy_fallback_for_supported(gateway):
    """
    Ensure _handle_repair_or_fallback strictly forbids legacy fallback for supported features.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat",
            feature="chat",
            locale="fr-FR"
        ),
        context=ExecutionContext(),
        request_id="test-66-29-recovery",
        trace_id="trace-66-29"
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
                validation_result,
                request,
                mock_plan,
                mock_provider_result,
                db=MagicMock()
            )
        
        assert "Legacy use_case fallback is strictly forbidden" in str(exc.value)
        assert mock_resolve_config.call_count == 0

@pytest.mark.asyncio
async def test_story_66_29_legacy_alias_normalized_rejection_at_entry(gateway):
    """
    AC11: A legacy alias normalized to a supported family must fail at execute_request.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation",
            feature="natal_interpretation", # Legacy alias
            subfeature="any",
            plan="free",
            locale="fr-FR"
        ),
        context=ExecutionContext(),
        request_id="test-66-29-alias",
        trace_id="trace-66-29"
    )

    registry_path = (
        "app.llm_orchestration.services.assembly_registry."
        "AssemblyRegistry.get_active_config_sync"
    )
    with patch(registry_path, return_value=None):
        with pytest.raises(GatewayConfigError) as exc:
            await gateway.execute_request(request, db=MagicMock())
        
        # Should be normalized to 'natal' and rejected
        assert "Mandatory assembly missing for supported natal family" in str(exc.value)

@pytest.mark.asyncio
async def test_story_66_29_other_features_still_allow_prevalidation_and_fallback(gateway):
    """
    AC8: Features NOT in supported perimeter still allow use_case-first pre-validation and fallback.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="experimental_case",
            feature="experimental_feature",
            locale="fr-FR"
        ),
        context=ExecutionContext(),
        request_id="test-66-29-other",
        trace_id="trace-66-29"
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
