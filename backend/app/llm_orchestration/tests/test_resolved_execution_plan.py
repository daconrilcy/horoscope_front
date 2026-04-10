import json
import os
from unittest.mock import patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionOverrides,
    ExecutionUserInput,
    LLMExecutionRequest,
    ResolvedExecutionPlan,
)


@pytest.mark.asyncio
async def test_resolve_plan_source_config(db):
    gateway = LLMGateway()
    # Use a generic use case not in DEPRECATED_USE_CASE_MAPPING
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="astrologer_selection_help"),
        request_id="r",
        trace_id="t",
    )

    # Ensure no environment overrides
    with patch.dict(os.environ, {}, clear=True):
        plan, qctx = await gateway._resolve_plan(request, db)
        assert plan.model_source in ["config", "stub"]


@pytest.mark.asyncio
async def test_resolve_plan_source_os_granular(db):
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="natal_long_free"), request_id="r", trace_id="t"
    )

    with patch.dict(os.environ, {"OPENAI_ENGINE_NATAL_LONG_FREE": "gpt-override"}):
        plan, qctx = await gateway._resolve_plan(request, db)
        assert plan.model_id == "gpt-override"
        assert plan.model_source == "os_granular"


@pytest.mark.asyncio
async def test_resolve_plan_source_os_legacy(db):
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", message="hello"),
        request_id="r",
        trace_id="t",
    )

    with patch.dict(os.environ, {"LLM_MODEL_OVERRIDE_CHAT": "gpt-legacy"}):
        plan, qctx = await gateway._resolve_plan(request, db)
        assert plan.model_id == "gpt-legacy"
        assert plan.model_source == "os_legacy"


def test_plan_to_log_dict_filtering():
    plan = ResolvedExecutionPlan(
        model_id="gpt-4o",
        model_source="config",
        rendered_developer_prompt="VERY LONG PROMPT",
        system_core="HARD POLICY",
        persona_block="PERSONA",
        output_schema={"type": "object"},
        interaction_mode="chat",
        user_question_policy="required",
        temperature=0.7,
        max_output_tokens=1000,
    )

    log_dict = plan.to_log_dict()
    assert "rendered_developer_prompt" not in log_dict
    assert "system_core" not in log_dict
    assert "persona_block" not in log_dict
    assert "output_schema" not in log_dict
    assert log_dict["model_id"] == "gpt-4o"

    # Verify serializable
    json.dumps(log_dict)


@pytest.mark.asyncio
async def test_resolve_plan_overrides(db):
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="natal_long_free"),
        overrides=ExecutionOverrides(interaction_mode="chat"),
        request_id="r",
        trace_id="t",
    )

    plan, qctx = await gateway._resolve_plan(request, db)
    assert plan.interaction_mode == "chat"
    assert plan.overrides_applied["interaction_mode"] == "chat"


@pytest.mark.asyncio
async def test_resolve_plan_repair_short_circuit(db):
    gateway = LLMGateway()
    request = LLMGateway._legacy_dicts_to_request(
        use_case="natal_long_free",
        user_input={},
        context={},
        request_id="r",
        trace_id="t",
        is_repair_call=True,
    )

    plan, qctx = await gateway._resolve_plan(request, db)
    assert "Ta seule mission est de corriger le format JSON" in plan.rendered_developer_prompt
