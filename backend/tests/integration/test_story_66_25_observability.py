import uuid
from unittest.mock import patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ContextCompensationStatus,
    ExecutionContext,
    ExecutionPathKind,
    ExecutionUserInput,
    FallbackType,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    MaxTokensSource,
    UsageInfo,
    UseCaseConfig,
)


@pytest.fixture
def gateway():
    return LLMGateway()


@pytest.mark.asyncio
async def test_observability_snapshot_canonical_assembly(gateway):
    """
    AC1, AC2, AC3: Vérifie que le snapshot d'observabilité est correctement
    peuplé pour un chemin d'assemblage canonique (nominal).
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat",
            feature="chat",
            plan="premium",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="test-obs-1",
        trace_id="trace-obs-1",
    )

    # Mock response from OpenAI
    mock_response = GatewayResult(
        use_case="chat",
        request_id="test-obs-1",
        trace_id="trace-obs-1",
        raw_output='{"response": "hello"}',
        usage=UsageInfo(
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            estimated_cost_usd=0.0001,
        ),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    # Mock config to avoid Stage 0.5 failure
    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="Prompt",
    )

    with patch.object(LLMGateway, "_resolve_legacy_compat_config", return_value=mock_config):
        with patch.object(LLMGateway, "_resolve_plan") as mock_resolve:
            from app.llm_orchestration.models import ResolvedExecutionPlan

            plan = ResolvedExecutionPlan(
                assembly_id=str(uuid.uuid4()),
                feature="chat",
                model_id="gpt-4o",
                model_source="assembly",
                execution_profile_source="waterfall",
                provider="openai",
                requested_provider="openai",
                rendered_developer_prompt="Chat prompt",
                system_core="System core",
                interaction_mode="chat",
                user_question_policy="none",
                temperature=0.7,
                max_output_tokens=2000,
                max_output_tokens_source="execution_profile",
                context_quality="full",
            )
            mock_resolve.return_value = (plan, None)

            with patch.object(LLMGateway, "_call_provider", return_value=mock_response):
                result = await gateway.execute_request(request)

                obs = result.meta.obs_snapshot
                assert obs is not None
                assert obs.pipeline_kind == "nominal_canonical"
                assert obs.execution_path_kind == ExecutionPathKind.CANONICAL_ASSEMBLY
                assert obs.context_compensation_status == ContextCompensationStatus.NOT_NEEDED


@pytest.mark.asyncio
async def test_observability_snapshot_non_nominal_provider(gateway):
    """
    AC4: Vérifie le statut NON_NOMINAL_PROVIDER_TOLERATED.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="any_case",
            feature="non_nominal",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="test-obs-2",
        trace_id="trace-obs-2",
    )

    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="Prompt",
    )

    from app.llm_orchestration.models import ResolvedExecutionPlan

    plan = ResolvedExecutionPlan(
        feature="non_nominal",
        model_id="gpt-4o",
        model_source="config",
        execution_profile_source="fallback_provider_unsupported",
        requested_provider="anthropic",
        provider="openai",
        rendered_developer_prompt="Prompt",
        system_core="System core",
        interaction_mode="structured",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=1000,
        max_output_tokens_source="unset",
        context_quality="full",
    )

    mock_response = GatewayResult(
        use_case="any_case",
        request_id="test-obs-2",
        trace_id="trace-obs-2",
        raw_output='{"ok": true}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch.object(LLMGateway, "_resolve_legacy_compat_config", return_value=mock_config):
        with patch.object(LLMGateway, "_resolve_plan", return_value=(plan, None)):
            with patch.object(LLMGateway, "_call_provider", return_value=mock_response):
                result = await gateway.execute_request(request)

                obs = result.meta.obs_snapshot
                assert obs.pipeline_kind == "transitional_governance"
                assert obs.execution_path_kind == ExecutionPathKind.NON_NOMINAL_PROVIDER_TOLERATED
                assert obs.fallback_kind == FallbackType.PROVIDER_OPENAI


@pytest.mark.asyncio
async def test_observability_snapshot_context_compensation_injected(gateway):
    """
    AC6: Vérifie le statut INJECTOR_APPLIED.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal",
            feature="natal",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="test-obs-3",
        trace_id="trace-obs-3",
    )

    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="Prompt",
    )

    from app.llm_orchestration.models import ResolvedExecutionPlan

    plan = ResolvedExecutionPlan(
        feature="natal",
        model_id="gpt-4o",
        model_source="config",
        provider="openai",
        requested_provider="openai",
        rendered_developer_prompt="Prompt with context quality instructions",
        system_core="System core",
        interaction_mode="structured",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=1000,
        max_output_tokens_source="unset",
        context_quality="partial",
        context_quality_instruction_injected=True,
    )

    mock_response = GatewayResult(
        use_case="natal",
        request_id="test-obs-3",
        trace_id="trace-obs-3",
        raw_output='{"ok": true}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch.object(LLMGateway, "_resolve_legacy_compat_config", return_value=mock_config):
        with patch.object(LLMGateway, "_resolve_plan", return_value=(plan, None)):
            with patch.object(LLMGateway, "_call_provider", return_value=mock_response):
                result = await gateway.execute_request(request)

                obs = result.meta.obs_snapshot
                assert obs.context_compensation_status == ContextCompensationStatus.INJECTOR_APPLIED


@pytest.mark.asyncio
async def test_observability_snapshot_template_handled(gateway):
    """
    Vérifie le statut TEMPLATE_HANDLED quand l'injecteur n'est pas utilisé
    mais que le contexte est dégradé.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal",
            feature="natal",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="test-obs-4",
        trace_id="trace-obs-4",
    )

    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="Prompt",
    )

    from app.llm_orchestration.models import ResolvedExecutionPlan

    plan = ResolvedExecutionPlan(
        feature="natal",
        model_id="gpt-4o",
        model_source="config",
        provider="openai",
        requested_provider="openai",
        rendered_developer_prompt="Prompt",
        system_core="System core",
        interaction_mode="structured",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=1000,
        max_output_tokens_source="unset",
        context_quality="minimal",
        context_quality_instruction_injected=False,
        context_quality_handled_by_template=True,
    )

    mock_response = GatewayResult(
        use_case="natal",
        request_id="test-obs-4",
        trace_id="trace-obs-4",
        raw_output='{"ok": true}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch.object(LLMGateway, "_resolve_legacy_compat_config", return_value=mock_config):
        with patch.object(LLMGateway, "_resolve_plan", return_value=(plan, None)):
            with patch.object(LLMGateway, "_call_provider", return_value=mock_response):
                result = await gateway.execute_request(request)

                obs = result.meta.obs_snapshot
                assert obs.context_quality == "minimal"
                assert obs.context_compensation_status == ContextCompensationStatus.TEMPLATE_HANDLED


@pytest.mark.asyncio
async def test_observability_snapshot_legacy_path_length_budget(gateway):
    """
    Vérifie que le chemin legacy utilise la bonne taxonomie pour max_output_tokens_source.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="legacy_case",
            feature="legacy_feat",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="test-obs-6",
        trace_id="trace-obs-6",
    )

    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="Prompt",
    )

    from app.llm_orchestration.models import ResolvedExecutionPlan

    # Plan representing a legacy resolution with length_budget_global
    plan = ResolvedExecutionPlan(
        feature="legacy_feat",
        model_id="gpt-4o",
        model_source="config",
        provider="openai",
        requested_provider="openai",
        rendered_developer_prompt="Prompt",
        system_core="System core",
        interaction_mode="structured",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=500,
        max_output_tokens_source="length_budget_global",  # Correct label now
        context_quality="full",
    )

    mock_response = GatewayResult(
        use_case="legacy_case",
        request_id="test-obs-6",
        trace_id="trace-obs-6",
        raw_output='{"ok": true}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch.object(LLMGateway, "_resolve_legacy_compat_config", return_value=mock_config):
        with patch.object(LLMGateway, "_resolve_plan", return_value=(plan, None)):
            with patch.object(LLMGateway, "_call_provider", return_value=mock_response):
                result = await gateway.execute_request(request)

                obs = result.meta.obs_snapshot
                assert obs.max_output_tokens_source == MaxTokensSource.LENGTH_BUDGET_GLOBAL
                assert obs.max_output_tokens_final == 500
