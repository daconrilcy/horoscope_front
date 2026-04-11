from unittest.mock import MagicMock, patch

import pytest

from app.llm_orchestration.feature_taxonomy import SUPPORTED_FAMILIES
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayConfigError,
    LLMExecutionRequest,
    UseCaseConfig,
)


@pytest.fixture
def gateway():
    return LLMGateway()

@pytest.mark.asyncio
async def test_story_66_29_supported_feature_rejection_if_no_assembly(gateway):
    """
    AC1, AC6: Fail explicitly if a supported feature has no assembly.
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
        with patch(registry_path, return_value=None):
            with patch("app.llm_orchestration.gateway.log_governance_event") as mock_log:
                with pytest.raises(GatewayConfigError) as exc:
                    await gateway._resolve_plan(request, db=MagicMock())
                
                msg = f"Mandatory assembly missing for supported {feature} family"
                assert msg in str(exc.value)
                # AC4: Telemetry check
                mock_log.assert_called_with(
                    event_type="supported_perimeter_rejection",
                    feature=feature,
                    subfeature="any",
                    is_nominal=True,
                )

@pytest.mark.asyncio
async def test_story_66_29_legacy_alias_normalization_rejection(gateway):
    """
    AC11: A legacy alias normalized to a supported family must also fail if no assembly.
    """
    # Assuming 'natal_interpretation' is normalized to 'natal'
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
            await gateway._resolve_plan(request, db=MagicMock())
        
        # Should be normalized to 'natal'
        assert "Mandatory assembly missing for supported natal family" in str(exc.value)

@pytest.mark.asyncio
async def test_story_66_29_forbid_use_case_first_fallback_final_check(gateway):
    """
    AC2: Ensure no supported feature uses use_case-first even if resolve_plan continues.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat",
            feature="chat",
            locale="fr-FR"
        ),
        context=ExecutionContext(),
        request_id="test-66-29-final-check",
        trace_id="trace-66-29"
    )

    # We mock it so that it passes the first check (assembly_db is None but we don't raise)
    # This simulates a situation where for some reason the first check was bypassed
    # and we reach the final check before resolve_config.
    with patch("app.llm_orchestration.gateway.is_supported_feature", side_effect=[False, True]):
        with pytest.raises(GatewayConfigError) as exc:
            await gateway._resolve_plan(request, db=MagicMock())
        
        msg = (
            "Resolution failed for supported feature 'chat'. "
            "Fallback to USE_CASE_FIRST is strictly forbidden."
        )
        assert msg in str(exc.value)

@pytest.mark.asyncio
async def test_story_66_29_other_features_still_allow_fallback(gateway):
    """
    AC8: Features NOT in supported perimeter still allow use_case-first for now.
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

    mock_config = UseCaseConfig(
        model="gpt-4o",
        temperature=0.7,
        max_output_tokens=1000,
        system_core_key="default_v1",
        developer_prompt="test",
        prompt_version_id="stub"
    )

    registry_path = (
        "app.llm_orchestration.services.assembly_registry."
        "AssemblyRegistry.get_active_config_sync"
    )
    profile_path = (
        "app.llm_orchestration.services.execution_profile_registry."
        "ExecutionProfileRegistry.get_active_profile"
    )
    with patch(registry_path, return_value=None):
        with patch(profile_path, return_value=None):
            with patch.object(gateway, "_resolve_config", return_value=mock_config):
                plan, _ = await gateway._resolve_plan(request, db=MagicMock())
                assert plan.feature == "experimental_feature"
                assert plan.prompt_version_id == "stub"
