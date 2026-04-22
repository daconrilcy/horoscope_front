import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    GatewayConfigError,
    LLMExecutionRequest,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.llm.runtime.observability_service import log_governance_event


@pytest.fixture
def gateway():
    return LLMGateway()


def test_story_66_30_runtime_rejection_emits_dedicated_counter():
    """
    Story 66.30: runtime_rejected MUST increment both the unified governance
    counter and the dedicated rejection counter with a discriminant reason.
    """
    calls = []

    def _spy_increment_counter(
        name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        calls.append((name, value, labels or {}))

    with patch(
        "app.domain.llm.runtime.observability_service.increment_counter",
        side_effect=_spy_increment_counter,
    ):
        log_governance_event(
            event_type="runtime_rejected",
            feature="chat",
            subfeature="astrologer",
            provider="openai",
            is_nominal=True,
            reason="missing_execution_profile",
        )

    assert (
        "llm_governance_event_total",
        1.0,
        {
            "event_type": "runtime_rejected",
            "provider": "openai",
            "feature": "chat",
            "subfeature": "astrologer",
            "is_nominal": "true",
            "reason": "missing_execution_profile",
        },
    ) in calls
    assert (
        "llm_runtime_rejection_total",
        1.0,
        {
            "feature": "chat",
            "subfeature": "astrologer",
            "provider": "openai",
            "is_nominal": "true",
            "reason": "missing_execution_profile",
        },
    ) in calls


@pytest.mark.asyncio
async def test_story_66_30_missing_profile_on_supported_perimeter(gateway):
    """
    Story 66.30: A supported feature (e.g., 'chat') without an
    ExecutionProfile MUST fail instead of falling back to resolve_model().
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            feature="chat",
            use_case="chat",
        ),
        context=ExecutionContext(),
        request_id="test-66-30-missing-profile",
        trace_id="trace-66-30",
    )

    # Mock assembly
    mock_assembly_db = MagicMock()
    mock_assembly_db.id = uuid.uuid4()
    mock_assembly_db.interaction_mode = "chat"
    mock_assembly_db.user_question_policy = "required"
    mock_assembly_db.input_schema = None

    mock_resolved_assembly = MagicMock()
    mock_resolved_assembly.execution_config.model = "gpt-4o"
    mock_resolved_assembly.execution_config.temperature = 0.7
    mock_resolved_assembly.execution_config.max_output_tokens = 1000
    mock_resolved_assembly.execution_config.timeout_seconds = 30
    mock_resolved_assembly.execution_config.fallback_use_case = None
    mock_resolved_assembly.execution_config.reasoning_effort = "medium"
    mock_resolved_assembly.execution_config.verbosity = "normal"
    mock_resolved_assembly.output_contract_ref = None
    mock_resolved_assembly.persona_block = "test persona"
    mock_resolved_assembly.persona_ref = None
    mock_resolved_assembly.length_budget = None
    mock_resolved_assembly.template_source = "test-source"

    with patch("app.domain.llm.runtime.gateway.is_supported_feature", return_value=True):
        with patch(
            "app.domain.llm.runtime.gateway.AssemblyRegistry.get_active_config_sync",
            return_value=mock_assembly_db,
        ):
            with patch(
                "app.domain.llm.runtime.gateway.resolve_assembly",
                return_value=mock_resolved_assembly,
            ):
                with patch(
                    "app.domain.llm.runtime.gateway.assemble_developer_prompt",
                    return_value="test prompt",
                ):
                    # CRITICAL: Ensure profile resolution returns None
                    with patch(
                        "app.domain.llm.configuration.execution_profile_registry."
                        "ExecutionProfileRegistry.get_profile_by_id",
                        return_value=None,
                    ):
                        with patch(
                            "app.domain.llm.configuration.execution_profile_registry."
                            "ExecutionProfileRegistry.get_active_profile",
                            return_value=None,
                        ):
                            with pytest.raises(
                                GatewayConfigError, match="No ExecutionProfile found"
                            ) as excinfo:
                                await gateway._resolve_plan(request, db=MagicMock())

                            assert excinfo.value.error_code == "missing_execution_profile"
                            assert (
                                excinfo.value.details["error_code"] == "missing_execution_profile"
                            )
                            assert excinfo.value.details["feature"] == "chat"


@pytest.mark.asyncio
async def test_story_70_13_supported_perimeter_bypasses_stage_0_5_legacy_config(gateway):
    """
    Story 70.13: supported canonical paths must not use the legacy compat resolver during
        Stage 0.5 pre-validation before assembly/profile resolution.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            feature="chat",
            subfeature="astrologer",
            plan="free",
            use_case="chat_astrologer",
            message="Bonjour",
        ),
        context=ExecutionContext(),
        request_id="test-70-13-stage05-bypass",
        trace_id="trace-70-13-stage05-bypass",
    )

    with patch.object(
        gateway, "_resolve_fallback_use_case_config", new=AsyncMock()
    ) as mock_resolve_config:
        with patch.object(
            gateway,
            "_resolve_plan",
            new=AsyncMock(
                side_effect=GatewayConfigError(
                    "missing assembly",
                    error_code="missing_assembly",
                )
            ),
        ):
            with pytest.raises(GatewayConfigError, match="missing assembly"):
                await gateway.execute_request(request, db=MagicMock())

    assert mock_resolve_config.await_count == 0


@pytest.mark.asyncio
async def test_story_66_30_removed_legacy_use_case_key_is_rejected(gateway):
    """
    Story 70.13 AC11 durci: les anciennes clés use_case ne doivent plus
    être acceptées à l'entrée runtime.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="daily_prediction",  # Legacy alias
        ),
        context=ExecutionContext(),
        request_id="test-66-30-legacy-alias",
        trace_id="trace-66-30",
    )

    with pytest.raises(
        GatewayConfigError, match="Legacy use_case key 'daily_prediction' is removed"
    ) as excinfo:
        await gateway.execute_request(request, db=MagicMock())

    assert excinfo.value.error_code == "removed_legacy_use_case_key"


@pytest.mark.asyncio
async def test_story_66_30_unsupported_provider_on_supported_perimeter(gateway):
    """
    Story 66.30: A supported feature with an ExecutionProfile
    demanding an unsupported provider MUST fail instead of falling back.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            feature="chat",
            use_case="chat",
        ),
        context=ExecutionContext(),
        request_id="test-66-30-unsupported-provider",
        trace_id="trace-66-30",
    )

    mock_profile = MagicMock()
    mock_profile.provider = "unsupported-provider"
    mock_profile.model = "some-model"
    mock_profile.id = uuid.uuid4()
    mock_profile.max_output_tokens = 500
    mock_profile.timeout_seconds = 10
    mock_profile.reasoning_profile = "standard"
    mock_profile.verbosity_profile = "normal"
    mock_profile.output_mode = "text"
    mock_profile.tool_mode = "none"

    mock_assembly_db = MagicMock()
    mock_assembly_db.id = uuid.uuid4()
    mock_assembly_db.interaction_mode = "chat"
    mock_assembly_db.user_question_policy = "required"
    mock_assembly_db.input_schema = None
    mock_assembly_db.execution_profile_ref = None

    mock_resolved_assembly = MagicMock()
    mock_resolved_assembly.execution_config.model = "gpt-4o"
    mock_resolved_assembly.execution_config.temperature = 0.7
    mock_resolved_assembly.execution_config.max_output_tokens = 1000
    mock_resolved_assembly.execution_config.timeout_seconds = 30
    mock_resolved_assembly.execution_config.fallback_use_case = None
    mock_resolved_assembly.execution_config.reasoning_effort = "medium"
    mock_resolved_assembly.execution_config.verbosity = "normal"
    mock_resolved_assembly.output_contract_ref = None
    mock_resolved_assembly.persona_block = "test persona"
    mock_resolved_assembly.persona_ref = None
    mock_resolved_assembly.length_budget = None
    mock_resolved_assembly.template_source = "test-source"

    with patch("app.domain.llm.runtime.gateway.is_supported_feature", return_value=True):
        with patch(
            "app.domain.llm.runtime.gateway.AssemblyRegistry.get_active_config_sync",
            return_value=mock_assembly_db,
        ):
            with patch(
                "app.domain.llm.runtime.gateway.resolve_assembly",
                return_value=mock_resolved_assembly,
            ):
                with patch(
                    "app.domain.llm.runtime.gateway.assemble_developer_prompt",
                    return_value="test prompt",
                ):
                    with patch(
                        "app.domain.llm.configuration.execution_profile_registry."
                        "ExecutionProfileRegistry.get_active_profile",
                        return_value=mock_profile,
                    ):
                        with patch(
                            "app.domain.llm.runtime.supported_providers.is_provider_supported",
                            return_value=False,
                        ):
                            with pytest.raises(
                                GatewayConfigError, match="is not nominally supported"
                            ) as excinfo:
                                await gateway._resolve_plan(request, db=MagicMock())

                            assert excinfo.value.error_code == "unsupported_execution_provider"


@pytest.mark.asyncio
async def test_story_66_30_mapping_not_implemented_on_supported_perimeter(gateway):
    """
    Story 66.30: A supported feature where ProviderParameterMapper.map
    fails MUST fail instead of falling back.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            feature="chat",
            use_case="chat",
        ),
        context=ExecutionContext(),
        request_id="test-66-30-mapping-failed",
        trace_id="trace-66-30",
    )

    mock_profile = MagicMock()
    mock_profile.provider = "openai"
    mock_profile.model = "gpt-4o"
    mock_profile.id = uuid.uuid4()
    mock_profile.max_output_tokens = 500
    mock_profile.timeout_seconds = 10
    mock_profile.reasoning_profile = "standard"
    mock_profile.verbosity_profile = "normal"
    mock_profile.output_mode = "text"
    mock_profile.tool_mode = "none"

    mock_assembly_db = MagicMock()
    mock_assembly_db.id = uuid.uuid4()
    mock_assembly_db.interaction_mode = "chat"
    mock_assembly_db.user_question_policy = "required"
    mock_assembly_db.input_schema = None
    # Default MagicMock().execution_profile_ref is truthy; gateway would call get_profile_by_id
    # with db=MagicMock and read a bogus MagicMock provider instead of the patched profile.
    mock_assembly_db.execution_profile_ref = None

    mock_resolved_assembly = MagicMock()
    mock_resolved_assembly.execution_config.model = "gpt-4o"
    mock_resolved_assembly.execution_config.temperature = 0.7
    mock_resolved_assembly.execution_config.max_output_tokens = 1000
    mock_resolved_assembly.execution_config.timeout_seconds = 30
    mock_resolved_assembly.execution_config.fallback_use_case = None
    mock_resolved_assembly.execution_config.reasoning_effort = "medium"
    mock_resolved_assembly.execution_config.verbosity = "normal"
    mock_resolved_assembly.output_contract_ref = None
    mock_resolved_assembly.persona_block = "test persona"
    mock_resolved_assembly.persona_ref = None
    mock_resolved_assembly.length_budget = None
    mock_resolved_assembly.template_source = "test-source"

    with patch("app.domain.llm.runtime.gateway.is_supported_feature", return_value=True):
        with patch(
            "app.domain.llm.runtime.gateway.AssemblyRegistry.get_active_config_sync",
            return_value=mock_assembly_db,
        ):
            with patch(
                "app.domain.llm.runtime.gateway.resolve_assembly",
                return_value=mock_resolved_assembly,
            ):
                with patch(
                    "app.domain.llm.runtime.gateway.assemble_developer_prompt",
                    return_value="test prompt",
                ):
                    with patch(
                        "app.domain.llm.configuration.execution_profile_registry."
                        "ExecutionProfileRegistry.get_active_profile",
                        return_value=mock_profile,
                    ):
                        with patch(
                            "app.domain.llm.runtime.supported_providers.is_provider_supported",
                            return_value=True,
                        ):
                            with patch(
                                "app.domain.llm.runtime.provider_parameter_mapper.ProviderParameterMapper.map",
                                side_effect=NotImplementedError("Not implemented"),
                            ):
                                with pytest.raises(
                                    GatewayConfigError, match="Provider mapping failed"
                                ) as excinfo:
                                    await gateway._resolve_plan(request, db=MagicMock())

                                assert excinfo.value.error_code == "provider_mapping_failed"
                                assert (
                                    excinfo.value.details["error_code"] == "provider_mapping_failed"
                                )


@pytest.mark.asyncio
async def test_story_66_30_fallback_tolerated_on_unsupported_perimeter(gateway):
    """
    Story 66.30: Features OUTSIDE supported perimeter (e.g., 'experimental')
    STILL tolerate resolve_model() fallback IF NOT NOMINAL.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            feature="experimental",
            use_case="experimental_test",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(test_fallback_active=True),  # NOT NOMINAL
        request_id="test-66-30-fallback-tolerated",
        trace_id="trace-66-30",
    )

    # Mock is_supported_feature to return False
    with patch("app.domain.llm.runtime.gateway.is_supported_feature", return_value=False):
        # Mock resolve_config and resolve_model
        mock_config = MagicMock()
        mock_config.model = "gpt-3.5-turbo"
        mock_config.temperature = 0.7
        mock_config.timeout_seconds = 30
        mock_config.max_output_tokens = 500
        mock_config.prompt_version_id = "test"
        mock_config.safety_profile = "astrology"
        mock_config.reasoning_effort = None
        mock_config.verbosity = None
        mock_config.developer_prompt = "test prompt"
        mock_config.output_schema_id = None
        mock_config.input_schema = None
        mock_config.interaction_mode = "structured"
        mock_config.user_question_policy = "none"
        mock_config.required_prompt_placeholders = []

        with patch.object(
            gateway,
            "_resolve_fallback_use_case_config",
            new_callable=AsyncMock,
            return_value=mock_config,
        ):
            with patch(
                "app.domain.llm.configuration.execution_profile_registry."
                "ExecutionProfileRegistry.get_active_profile",
                return_value=None,
            ):
                with patch(
                    "app.domain.llm.runtime.gateway.resolve_model",
                    return_value="gpt-4o-fallback",
                ) as mock_resolve:
                    result, _ = await gateway._resolve_plan(request, db=MagicMock())

                    assert result.execution_profile_source == "fallback_resolve_model"
                    assert result.model_id == "gpt-4o-fallback"
                    assert mock_resolve.called
