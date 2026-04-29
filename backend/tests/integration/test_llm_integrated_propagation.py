from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.domain.llm.prompting.context import PromptCommonContext, QualifiedContext
from app.domain.llm.runtime.contracts import (
    ContextCompensationStatus,
    ExecutionContext,
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    UsageInfo,
)
from app.domain.llm.runtime.gateway import LLMGateway


@pytest.mark.asyncio
async def test_integrated_template_handled_propagation(db):
    """
    Reproduction test for Story 66.27.
    Tests that a template with {{#context_quality:partial}} results in TEMPLATE_HANDLED
    when passing through the real _resolve_plan logic.
    """
    gateway = LLMGateway()

    # Setup a request with a non-nominal feature to bypass governance
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation",
            feature="test_feature",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        user_id=1,
        request_id="test-66-27",
        trace_id="trace-66-27",
    )

    # We need to mock CommonContextBuilder.build to return partial quality
    mock_payload = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={},
        period_covered="daily",
        today_date="samedi 11 avril 2026",
        use_case_name="Natal",
        use_case_key="natal_interpretation",
    )
    mock_ctx = QualifiedContext(
        payload=mock_payload, source="db", missing_fields=["birth_time"], context_quality="partial"
    )

    # We need a developer prompt that handles partial quality
    # We'll mock the legacy compatibility resolver to return this prompt
    from app.domain.llm.runtime.contracts import UseCaseConfig

    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt=(
            "Base prompt. {{#context_quality:partial}}Partial handling here.{{/context_quality}}"
        ),
        required_prompt_placeholders=[],
    )

    # Mock provider call
    mock_response = GatewayResult(
        use_case="natal_interpretation",
        request_id="test-66-27",
        trace_id="trace-66-27",
        raw_output='{"response": "ok"}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch(
        "app.domain.llm.prompting.context.CommonContextBuilder.build", return_value=mock_ctx
    ):
        with patch.object(
            LLMGateway, "_resolve_fallback_use_case_config", return_value=mock_config
        ):
            with patch(
                "app.domain.llm.configuration.execution_profile_registry.ExecutionProfileRegistry.get_active_profile",
                return_value=None,
            ):
                with patch(
                    "app.domain.llm.configuration.execution_profile_registry.ExecutionProfileRegistry.get_profile_by_id",
                    return_value=None,
                ):
                    with patch(
                        "app.infra.providers.llm.openai_responses_client.ResponsesClient.execute",
                        new_callable=AsyncMock,
                    ) as mock_exec:
                        mock_exec.return_value = mock_response
                        result = await gateway.execute_request(request, db=db)

                # 1. Validate snapshot in result
                obs = result.meta.obs_snapshot
                assert obs.context_quality == "partial"
                assert obs.context_compensation_status == ContextCompensationStatus.TEMPLATE_HANDLED

                # 2. Validate real DB persistence (Story 66.27 AC4)
                from app.infra.db.models.llm.llm_observability import LlmCallLogModel

                stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == "test-66-27")
                log_entry = db.execute(stmt).scalar_one()
                assert log_entry.context_compensation_status == "template_handled"


@pytest.mark.asyncio
async def test_integrated_injector_applied_propagation(db):
    """Tests that a template without blocks results in INJECTOR_APPLIED when quality is degraded."""
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation", feature="test_feature", locale="fr-FR"
        ),
        context=ExecutionContext(),
        user_id=1,
        request_id="test-66-27-injected",
        trace_id="trace-66-27-injected",
    )

    mock_payload = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={},
        period_covered="daily",
        today_date="samedi 11 avril 2026",
        use_case_name="Natal",
        use_case_key="natal_interpretation",
    )
    mock_ctx = QualifiedContext(
        payload=mock_payload, source="db", missing_fields=["birth_time"], context_quality="partial"
    )

    from app.domain.llm.runtime.contracts import UseCaseConfig

    # No quality blocks here
    mock_config = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="Base prompt without blocks.",
        required_prompt_placeholders=[],
    )

    mock_response = GatewayResult(
        use_case="natal_interpretation",
        request_id="test-66-27-injected",
        trace_id="trace-66-27",
        raw_output='{"response": "ok"}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch(
        "app.domain.llm.prompting.context.CommonContextBuilder.build", return_value=mock_ctx
    ):
        with patch.object(
            LLMGateway, "_resolve_fallback_use_case_config", return_value=mock_config
        ):
            with patch(
                "app.domain.llm.configuration.execution_profile_registry.ExecutionProfileRegistry.get_active_profile",
                return_value=None,
            ):
                with patch(
                    "app.domain.llm.configuration.execution_profile_registry.ExecutionProfileRegistry.get_profile_by_id",
                    return_value=None,
                ):
                    with patch(
                        "app.infra.providers.llm.openai_responses_client.ResponsesClient.execute",
                        new_callable=AsyncMock,
                    ) as mock_exec:
                        mock_exec.return_value = mock_response
                        result = await gateway.execute_request(request, db=db)

                obs = result.meta.obs_snapshot
                assert obs.context_quality == "partial"
                assert obs.context_compensation_status == ContextCompensationStatus.INJECTOR_APPLIED

                # 2. Validate real DB persistence
                from app.infra.db.models.llm.llm_observability import LlmCallLogModel

                stmt = select(LlmCallLogModel).where(
                    LlmCallLogModel.request_id == "test-66-27-injected"
                )
                log_entry = db.execute(stmt).scalar_one()
                assert log_entry.context_compensation_status == "injector_applied"


@pytest.mark.asyncio
async def test_integrated_not_needed_propagation(db):
    """Tests that full quality results in NOT_NEEDED."""
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation", feature="test_feature", locale="fr-FR"
        ),
        context=ExecutionContext(),
        user_id=1,
        request_id="test-66-27-full",
        trace_id="trace-66-27-full",
    )

    mock_payload = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"name": "Astro"},
        period_covered="daily",
        today_date="samedi 11 avril 2026",
        use_case_name="Natal",
        use_case_key="natal_interpretation",
        natal_interpretation="Some interpretation",
        natal_data={"planets": {}},
    )
    # Context quality is FULL (with non-empty fields)
    mock_ctx = QualifiedContext(
        payload=mock_payload, source="db", missing_fields=[], context_quality="full"
    )

    from app.domain.llm.runtime.contracts import UseCaseConfig

    mock_config = UseCaseConfig(
        model="gpt-4o", developer_prompt="Base prompt.", required_prompt_placeholders=[]
    )

    mock_response = GatewayResult(
        use_case="natal_interpretation",
        request_id="test-66-27-full",
        trace_id="trace-66-27",
        raw_output='{"response": "ok"}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    with patch(
        "app.domain.llm.prompting.context.CommonContextBuilder.build", return_value=mock_ctx
    ):
        with patch.object(
            LLMGateway, "_resolve_fallback_use_case_config", return_value=mock_config
        ):
            with patch(
                "app.domain.llm.configuration.execution_profile_registry.ExecutionProfileRegistry.get_active_profile",
                return_value=None,
            ):
                with patch(
                    "app.domain.llm.configuration.execution_profile_registry.ExecutionProfileRegistry.get_profile_by_id",
                    return_value=None,
                ):
                    with patch(
                        "app.infra.providers.llm.openai_responses_client.ResponsesClient.execute",
                        new_callable=AsyncMock,
                    ) as mock_exec:
                        mock_exec.return_value = mock_response
                        result = await gateway.execute_request(request, db=db)

                obs = result.meta.obs_snapshot
                assert obs.context_quality == "full"
                assert obs.context_compensation_status == ContextCompensationStatus.NOT_NEEDED

                # 2. Validate real DB persistence
                from app.infra.db.models.llm.llm_observability import LlmCallLogModel

                stmt = select(LlmCallLogModel).where(
                    LlmCallLogModel.request_id == "test-66-27-full"
                )
                log_entry = db.execute(stmt).scalar_one()
                assert log_entry.context_compensation_status == "not_needed"
