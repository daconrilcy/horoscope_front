import uuid
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from app.llm_orchestration.admin_models import LlmExecutionProfileCreate
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionUserInput,
    LLMExecutionRequest,
    UseCaseConfig,
)


def test_admin_validation_rejects_unsupported_provider():
    """
    AC1/AC2: LlmExecutionProfileCreate must reject unsupported providers like 'anthropic'.
    """
    with pytest.raises(ValidationError) as exc:
        LlmExecutionProfileCreate(
            name="test-unsupported",
            description="Test",
            feature="chat",
            subfeature="default",
            plan="premium",
            model="claude-3-opus",
            provider="anthropic",
            timeout_seconds=30,
        )
    assert "not nominally supported" in str(exc.value)


@pytest.mark.asyncio
async def test_gateway_nominal_path_rejects_unsupported_provider():
    """
    AC4: Le gateway lève une erreur explicite sur chemin nominal si le provider est injouable.
    """
    gateway = LLMGateway()

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="any_case",
            feature="chat",  # Nominal family (Story 66.25)
            plan="free",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="req-123",
        trace_id="trace-123",
    )

    mock_profile = MagicMock()
    mock_profile.id = "mock-id"
    mock_profile.model = "claude-3"
    mock_profile.provider = "anthropic"
    mock_profile.timeout_seconds = 30
    mock_profile.reasoning_profile = None
    mock_profile.verbosity_profile = None
    mock_profile.output_mode = "text"
    mock_profile.tool_mode = "none"

    mock_config = MagicMock()
    mock_config.model = "gpt-4"
    mock_config.developer_prompt = "stub"
    mock_config.required_prompt_placeholders = []
    mock_config.output_schema_id = None
    mock_config.prompt_version_id = "stub"
    mock_config.interaction_mode = "chat"
    mock_config.user_question_policy = "none"
    mock_config.temperature = 0.7
    mock_config.max_output_tokens = 100
    mock_config.reasoning_effort = None
    mock_config.verbosity = None
    mock_config.input_schema = None
    mock_config.fallback_use_case = None
    mock_config.safety_profile = "astrology"

    mock_config = UseCaseConfig(
        model="gpt-4",
        developer_prompt="stub",
        required_prompt_placeholders=[],
        output_schema_id=None,
        prompt_version_id="stub",
        interaction_mode="chat",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=100,
        reasoning_effort=None,
        verbosity=None,
        input_schema=None,
        fallback_use_case=None,
        safety_profile="astrology",
    )

    mock_assembly_db = MagicMock()
    # Configure mock_assembly_db to have valid string values for UseCaseConfig
    mock_assembly_db.id = uuid.uuid4()
    mock_assembly_db.interaction_mode = "chat"
    mock_assembly_db.user_question_policy = "none"
    mock_assembly_db.output_schema_id = None

    mock_resolved = MagicMock()
    mock_resolved.feature_template_id = uuid.uuid4()
    mock_resolved.subfeature_template_id = None
    mock_resolved.template_source = "explicit_subfeature"
    mock_resolved.execution_config.model = "gpt-4"
    mock_resolved.execution_config.temperature = 0.7
    mock_resolved.execution_config.max_output_tokens = 100
    mock_resolved.execution_config.timeout_seconds = 30
    mock_resolved.execution_config.reasoning_effort = None
    mock_resolved.execution_config.verbosity = None
    mock_resolved.execution_config.fallback_use_case = None
    mock_resolved.persona_block = "Persona"
    mock_resolved.persona_ref = None
    mock_resolved.output_contract_ref = None

    db_mock = MagicMock()
    db_mock.execute().scalar_one_or_none.return_value = None

    with (
        patch(
            "app.llm_orchestration.services.execution_profile_registry.ExecutionProfileRegistry.get_active_profile",
            return_value=mock_profile,
        ),
        patch(
            "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync",
            return_value=mock_assembly_db,
        ),
        patch("app.llm_orchestration.gateway.resolve_assembly", return_value=mock_resolved),
        patch("app.llm_orchestration.gateway.assemble_developer_prompt", return_value="Prompt"),
        patch.object(gateway, "_resolve_config", return_value=mock_config),
        patch.object(gateway, "_resolve_schema", return_value=(None, "test", "v1")),
        patch.object(gateway, "_resolve_persona", return_value=(None, None, None)),
    ):
        with pytest.raises(ValueError) as exc:
            await gateway._resolve_plan(request, db=db_mock)

        assert "Provider 'anthropic' is not nominally supported by the platform" in str(exc.value)


@pytest.mark.asyncio
async def test_gateway_nominal_path_accepts_openai():
    """
    Testing OpenAI is accepted normally (Non-régression).
    """
    gateway = LLMGateway()

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="any_case",
            feature="chat",  # Nominal family (Story 66.25)
            plan="free",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="req-123",
        trace_id="trace-123",
    )

    mock_profile = MagicMock()
    mock_profile.id = "mock-id"
    mock_profile.model = "gpt-4o"
    mock_profile.provider = "openai"
    mock_profile.timeout_seconds = 30
    mock_profile.reasoning_profile = None
    mock_profile.verbosity_profile = None
    mock_profile.output_mode = "text"
    mock_profile.tool_mode = "none"

    mock_config = MagicMock()
    mock_config.model = "gpt-4"
    mock_config.developer_prompt = "stub"
    mock_config.required_prompt_placeholders = []
    mock_config.output_schema_id = None
    mock_config.prompt_version_id = "stub"
    mock_config.interaction_mode = "chat"
    mock_config.user_question_policy = "none"
    mock_config.temperature = 0.7
    mock_config.max_output_tokens = 100
    mock_config.reasoning_effort = None
    mock_config.verbosity = None
    mock_config.input_schema = None
    mock_config.fallback_use_case = None
    mock_config.safety_profile = "astrology"

    mock_config = UseCaseConfig(
        model="gpt-4",
        developer_prompt="stub",
        required_prompt_placeholders=[],
        output_schema_id=None,
        prompt_version_id="stub",
        interaction_mode="chat",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=100,
        reasoning_effort=None,
        verbosity=None,
        input_schema=None,
        fallback_use_case=None,
        safety_profile="astrology",
    )

    mock_assembly_db = MagicMock()
    # Configure mock_assembly_db to have valid string values for UseCaseConfig
    mock_assembly_db.id = uuid.uuid4()
    mock_assembly_db.interaction_mode = "chat"
    mock_assembly_db.user_question_policy = "none"
    mock_assembly_db.output_schema_id = None

    mock_resolved = MagicMock()
    mock_resolved.feature_template_id = uuid.uuid4()
    mock_resolved.subfeature_template_id = None
    mock_resolved.template_source = "explicit_subfeature"
    mock_resolved.execution_config.model = "gpt-4"
    mock_resolved.execution_config.temperature = 0.7
    mock_resolved.execution_config.max_output_tokens = 100
    mock_resolved.execution_config.timeout_seconds = 30
    mock_resolved.execution_config.reasoning_effort = None
    mock_resolved.execution_config.verbosity = None
    mock_resolved.execution_config.fallback_use_case = None
    mock_resolved.persona_block = "Persona"
    mock_resolved.persona_ref = None
    mock_resolved.output_contract_ref = None

    db_mock = MagicMock()
    db_mock.execute().scalar_one_or_none.return_value = None

    with (
        patch(
            "app.llm_orchestration.services.execution_profile_registry.ExecutionProfileRegistry.get_active_profile",
            return_value=mock_profile,
        ),
        patch(
            "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync",
            return_value=mock_assembly_db,
        ),
        patch("app.llm_orchestration.gateway.resolve_assembly", return_value=mock_resolved),
        patch("app.llm_orchestration.gateway.assemble_developer_prompt", return_value="Prompt"),
        patch.object(gateway, "_resolve_config", return_value=mock_config),
        patch.object(gateway, "_resolve_schema", return_value=(None, "test", "v1")),
        patch.object(gateway, "_resolve_persona", return_value=(None, None, None)),
    ):
        plan, _ = await gateway._resolve_plan(request, db=db_mock)
        assert plan.provider == "openai"
        assert plan.model_id == "gpt-4o"


@pytest.mark.asyncio
async def test_gateway_non_nominal_accepts_fallback_and_logs():
    """
    Testing that fallback to openai is triggered for anthropic if non-nominal,
    and emitting explicit telemetry (event_type / is_nominal=false).
    """
    gateway = LLMGateway()

    # Non-nominal by setting feature to None
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="any_case",
            feature="other",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="req-123",
        trace_id="trace-123",
    )
    request.flags.test_fallback_active = True

    mock_profile = MagicMock()
    mock_profile.id = "mock-id"
    mock_profile.model = "claude-3"
    mock_profile.provider = "anthropic"
    mock_profile.timeout_seconds = 30
    mock_profile.reasoning_profile = None
    mock_profile.verbosity_profile = None
    mock_profile.output_mode = "text"
    mock_profile.tool_mode = "none"

    mock_config = MagicMock()
    mock_config.model = "gpt-4"
    mock_config.developer_prompt = "stub"
    mock_config.required_prompt_placeholders = []
    mock_config.output_schema_id = None
    mock_config.prompt_version_id = "stub"
    mock_config.interaction_mode = "chat"
    mock_config.user_question_policy = "none"
    mock_config.temperature = 0.7
    mock_config.max_output_tokens = 100
    mock_config.reasoning_effort = None
    mock_config.verbosity = None
    mock_config.input_schema = None
    mock_config.fallback_use_case = None
    mock_config.safety_profile = "astrology"

    with (
        patch(
            "app.llm_orchestration.services.execution_profile_registry.ExecutionProfileRegistry.get_active_profile",
            return_value=mock_profile,
        ),
        patch(
            "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync",
            return_value=MagicMock(),  # Mock assembly
        ),
        patch("app.llm_orchestration.gateway.resolve_assembly", return_value=MagicMock()),
        patch("app.llm_orchestration.gateway.assemble_developer_prompt", return_value="Prompt"),
        patch.object(gateway, "_resolve_config", return_value=mock_config),
        patch.object(gateway, "_resolve_schema", return_value=(None, "test", "v1")),
        patch.object(gateway, "_resolve_persona", return_value=(None, None, None)),
        patch("app.llm_orchestration.services.fallback_governance.increment_counter") as mock_inc,
    ):
        plan, _ = await gateway._resolve_plan(request, db=MagicMock())
        assert plan.provider == "openai"  # Fallback explicit to supported provider

        # Verify metric emission
        calls = [
            c for c in mock_inc.call_args_list if c[0][0] == "llm_gateway_fallback_usage_total"
        ]
        assert len(calls) > 0, "Telemetry missing"

        found = False
        for call in calls:
            kwargs = call[1]
            labels = kwargs.get("labels", {})
            if labels.get("fallback_type") == "provider_openai":
                assert labels.get("is_nominal") == "false"
                found = True
        assert found, "Expected fallback telemetry not found with is_nominal=false"
