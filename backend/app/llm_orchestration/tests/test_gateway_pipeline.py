import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    RecoveryResult,
    ResolvedExecutionPlan,
    UsageInfo,
)
from app.llm_orchestration.services.output_validator import ValidationResult


@pytest.mark.asyncio
async def test_pipeline_nominal_flow(db):
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="natal_long_free"),
        request_id="req-test",
        trace_id="trace-test",
    )

    # Story 66.20: Seed assembly for natal family to satisfy mandatory enforcement
    from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
    from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus

    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="natal_long_free",
        developer_prompt="P",
        status=PromptStatus.PUBLISHED,
        model="m",
        created_by="t",
    )
    db.add(fv)
    asm = PromptAssemblyConfigModel(
        feature="natal",
        subfeature="interpretation",
        plan="free",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_config={"model": "m"},
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )

    db.add(asm)
    db.commit()

    # 1. Mock Stage 3 (Provider)
    mock_provider_res = GatewayResult(
        use_case="natal_long_free",
        request_id="req-test",
        trace_id="trace-test",
        raw_output='{"title": "ok", "summary": "ok", "accordion_titles": ["a"]}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    with patch.object(gateway.client, "execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_provider_res

        # Execute pipeline
        result = await gateway.execute_request(request, db=db)

        assert result.use_case == "natal_long_free"
        assert result.meta.validation_status == "valid"
        assert result.meta.repair_attempted is False
        assert mock_exec.called


@pytest.mark.asyncio
async def test_pipeline_repair_flow(db):
    gateway = LLMGateway()
    # Need a use case with a schema to trigger repair
    use_case = "natal_long_free"
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=use_case),
        request_id="req-repair",
        trace_id="trace-repair",
    )

    # Story 66.20: Seed assembly for natal family to satisfy mandatory enforcement
    from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
    from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus

    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="natal_long_free",
        developer_prompt="P",
        status=PromptStatus.PUBLISHED,
        model="m",
        created_by="t",
    )
    db.add(fv)
    asm = PromptAssemblyConfigModel(
        feature="natal",
        subfeature="interpretation",
        plan="free",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_config={"model": "m"},
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )

    db.add(asm)
    db.commit()

    # 1. First call returns invalid JSON
    bad_output = "INVALID JSON"
    # 2. Second call (repair) returns valid JSON
    good_output = '{"title": "fixed", "summary": "fixed", "accordion_titles": ["a"]}'

    mock_res_bad = GatewayResult(
        use_case=use_case,
        request_id="req-repair",
        trace_id="trace-repair",
        raw_output=bad_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=5, model="m"),
    )
    mock_res_good = GatewayResult(
        use_case=use_case,
        request_id="req-repair-repair",
        trace_id="trace-repair",
        raw_output=good_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=5, model="m"),
    )

    # Mocking execute_request for the recursive call is tricky,
    # let's mock _call_provider instead.
    with patch.object(gateway, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = [mock_res_bad, mock_res_good]

        result = await gateway.execute_request(request, db=db)

        assert result.raw_output == good_output
        assert result.meta.repair_attempted is True
        assert result.meta.validation_status == "repair_success"
        assert mock_call.call_count == 2


@pytest.mark.asyncio
async def test_pipeline_anti_loop(db):
    gateway = LLMGateway()
    # Request with use_case already in visited
    from app.llm_orchestration.models import ExecutionFlags

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat"),
        flags=ExecutionFlags(visited_use_cases=["chat"], is_repair_call=False),
        request_id="r",
        trace_id="t",
    )

    from app.llm_orchestration.models import GatewayError

    with pytest.raises(GatewayError) as exc:
        await gateway.execute_request(request, db=db)
    assert "Infinite fallback loop" in str(exc.value)


def test_build_result_metadata_preservation():
    gateway = LLMGateway()
    plan = ResolvedExecutionPlan(
        model_id="plan-model",
        model_source="config",
        rendered_developer_prompt="...",
        system_core="...",
        interaction_mode="chat",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=100,
        output_schema_id="schema-123",
    )
    provider_res = GatewayResult(
        use_case="uc",
        request_id="r",
        trace_id="t",
        raw_output="...",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=0, model="old-model"),
    )
    recovery = RecoveryResult(result=provider_res, repair_attempts=1)

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="uc", locale="fr"),
        request_id="r",
        trace_id="t",
        user_id=1,
    )

    final = gateway._build_result(
        ValidationResult(valid=True, parsed={}, errors=[]), plan, recovery, 500, request
    )

    assert final.meta.latency_ms == 500
    assert final.meta.model == "plan-model"
    assert final.meta.repair_attempted is True
    assert final.meta.output_schema_id == "schema-123"
