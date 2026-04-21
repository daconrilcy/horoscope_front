import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.llm.runtime.contracts import (
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    RecoveryResult,
    ResolvedExecutionPlan,
    UsageInfo,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.llm.runtime.output_validator import ValidationResult


@pytest.mark.asyncio
async def test_pipeline_nominal_flow(db):
    gateway = LLMGateway()
    use_case = "test_uc"

    # Story 66.29 bypass: use non-supported feature
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=use_case, feature="test_family"),
        request_id="req-test",
        trace_id="trace-test",
    )

    # Seed a minimal config
    from app.infra.db.models.llm_prompt import LlmPromptVersionModel, LlmUseCaseConfigModel

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key=use_case,
        developer_prompt="Hello",
        status="published",
        model="m",
        created_by="t",
    )
    uc_config = LlmUseCaseConfigModel(
        key=use_case,
        persona_strategy="optional",
        display_name="Test UC",
        description="Test description",
    )
    db.add(prompt)
    db.add(uc_config)
    db.commit()

    # 1. Mock Stage 3 (Provider)
    mock_provider_res = GatewayResult(
        use_case=use_case,
        request_id="req-test",
        trace_id="trace-test",
        raw_output="ok",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    with patch.object(
        gateway.runtime_manager, "execute_with_resilience", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = mock_provider_res

        # Execute pipeline
        result = await gateway.execute_request(request, db=db)

        assert result.use_case == use_case
        assert result.meta.validation_status == "valid"
        assert result.meta.repair_attempted is False
        assert mock_exec.called


@pytest.mark.asyncio
async def test_pipeline_repair_flow(db):
    gateway = LLMGateway()
    use_case = "test_uc_repair"
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=use_case, feature="test_family"),
        request_id="req-repair",
        trace_id="trace-repair",
    )

    # Seed a minimal config
    from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
    from app.infra.db.models.llm_prompt import LlmPromptVersionModel, LlmUseCaseConfigModel

    schema_id = uuid.uuid4()
    schema = LlmOutputSchemaModel(id=schema_id, name="Test Schema", json_schema={"type": "object"})
    db.add(schema)

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key=use_case,
        developer_prompt="Hello",
        status="published",
        model="m",
        created_by="t",
    )
    uc_config = LlmUseCaseConfigModel(
        key=use_case,
        persona_strategy="optional",
        display_name="Test UC Repair",
        description="Test description",
        output_schema_id=str(schema_id),
    )
    db.add(prompt)
    db.add(uc_config)
    db.commit()

    # 1. First call returns invalid JSON
    bad_output = "INVALID JSON"
    # 2. Second call (repair) returns valid JSON
    good_output = '{"ok": true}'

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
    # let's mock _call_provider and validate_output instead.
    with patch.object(gateway, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = [mock_res_bad, mock_res_good]

        with patch("app.domain.llm.runtime.gateway.validate_output") as mock_val:
            mock_val.side_effect = [
                ValidationResult(valid=False, parsed={}, errors=["err"]),
                ValidationResult(valid=True, parsed={"ok": True}, errors=[]),
            ]

            # Act
            result = await gateway.execute_request(request, db=db)

            # Assert
            assert result.raw_output == good_output
            assert result.meta.repair_attempted is True
            assert result.meta.validation_status == "repair_success"
            assert mock_call.call_count == 2


@pytest.mark.asyncio
async def test_pipeline_anti_loop(db):
    gateway = LLMGateway()
    # Request with use_case already in visited
    from app.domain.llm.runtime.contracts import ExecutionFlags

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat"),
        flags=ExecutionFlags(visited_use_cases=["chat"], is_repair_call=False),
        request_id="r",
        trace_id="t",
    )

    from app.domain.llm.runtime.contracts import GatewayError

    with pytest.raises(GatewayError) as exc:
        await gateway.execute_request(request, db=db)
    assert "removed" in str(exc.value).lower()


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
