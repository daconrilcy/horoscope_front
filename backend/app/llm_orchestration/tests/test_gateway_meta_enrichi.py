import pytest
from unittest.mock import MagicMock
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    LLMExecutionRequest, 
    ExecutionUserInput, 
    ResolvedExecutionPlan,
    GatewayResult,
    UsageInfo,
    GatewayMeta,
    RecoveryResult,
    ExecutionFlags
)
from app.llm_orchestration.services.output_validator import ValidationResult

def test_build_result_enriched_telemetry():
    gateway = LLMGateway()
    plan = ResolvedExecutionPlan(
        model_id="gpt-4o", model_source="config", rendered_developer_prompt="...",
        system_core="...", interaction_mode="chat", user_question_policy="none",
        temperature=0.7, max_output_tokens=100, context_quality="partial"
    )
    provider_res = GatewayResult(
        use_case="uc", request_id="r", trace_id="t", raw_output="...",
        usage=UsageInfo(), meta=GatewayMeta(latency_ms=0, model="gpt-4o")
    )
    recovery = RecoveryResult(result=provider_res, repair_attempts=1)
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="uc"),
        request_id="r", trace_id="t", flags=ExecutionFlags()
    )
    
    validation = ValidationResult(valid=True, parsed={}, normalizations_applied=["tag1"])
    
    from app.prompts.common_context import QualifiedContext, PromptCommonContext
    qualified_ctx = QualifiedContext(
        payload=PromptCommonContext(
            precision_level="p", astrologer_profile={}, period_covered="p", 
            today_date="d", use_case_name="n", use_case_key="uc"
        ),
        source="db",
        missing_fields=["field1"]
    )
    
    final = gateway._build_result(
        validation, plan, recovery, 150, request, qualified_ctx
    )
    
    assert final.meta.execution_path == "repaired"
    assert final.meta.context_quality == "partial"
    assert final.meta.missing_context_fields == ["field1"]
    assert final.meta.normalizations_applied == ["tag1"]
    assert final.meta.repair_attempts == 1
    assert final.meta.repair_attempted is True # Sync check
    assert final.meta.latency_ms == 150

def test_build_result_test_fallback_path():
    gateway = LLMGateway()
    # Use real objects instead of mocks to avoid attribute errors
    plan = ResolvedExecutionPlan(
        model_id="m", model_source="config", rendered_developer_prompt="...",
        system_core="...", interaction_mode="chat", user_question_policy="none",
        temperature=0.7, max_output_tokens=100, context_quality="full"
    )
    provider_res = GatewayResult(
        use_case="uc", request_id="r", trace_id="t", raw_output="...",
        usage=UsageInfo(), meta=GatewayMeta(latency_ms=0, model="m")
    )
    recovery = RecoveryResult(result=provider_res)
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="uc"),
        request_id="r", trace_id="t", flags=ExecutionFlags(test_fallback_active=True)
    )
    
    validation = ValidationResult(valid=True, parsed={}, normalizations_applied=[])
    
    final = gateway._build_result(
        validation, plan, recovery, 10, request
    )
    
    assert final.meta.execution_path == "test_fallback"

def test_build_result_fallback_path():
    gateway = LLMGateway()
    plan = ResolvedExecutionPlan(
        model_id="m", model_source="config", rendered_developer_prompt="...",
        system_core="...", interaction_mode="chat", user_question_policy="none",
        temperature=0.7, max_output_tokens=100, context_quality="full"
    )
    provider_res = GatewayResult(
        use_case="uc", request_id="r", trace_id="t", raw_output="...",
        usage=UsageInfo(), meta=GatewayMeta(latency_ms=0, model="m")
    )
    # Simulated fallback
    fallback_res = GatewayResult(
        use_case="uc-fallback", request_id="r-f", trace_id="t", raw_output="...",
        usage=UsageInfo(), meta=GatewayMeta(latency_ms=0, model="m")
    )
    recovery = RecoveryResult(result=fallback_res, fallback_reason="schema_error")
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="uc"),
        request_id="r", trace_id="t", flags=ExecutionFlags()
    )
    
    validation = ValidationResult(valid=False, errors=["err"], normalizations_applied=[])
    
    final = gateway._build_result(
        validation, plan, recovery, 10, request
    )
    
    assert final.meta.execution_path == "fallback_use_case"
    assert final.meta.fallback_reason == "schema_error"
    assert final.meta.fallback_triggered is True
