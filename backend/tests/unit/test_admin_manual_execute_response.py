"""Payload opérateur exécution manuelle catalogue LLM (story 69.2)."""

import uuid
from types import SimpleNamespace

from app.api.v1.routers.admin_llm import _build_admin_manual_execute_response_payload
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


def test_build_admin_manual_execute_response_redacts_structured_sensitive_keys() -> None:
    built = SimpleNamespace(
        use_case_key="uc_test",
        transformation_pipeline=SimpleNamespace(
            rendered_prompt="Instruction pour le chart_json suivant."
        ),
    )
    result = GatewayResult(
        use_case="uc_test",
        request_id="gw-req",
        trace_id="gw-tr",
        raw_output='{"title":"ok"}',
        structured_output={"provider": "openai", "chart_json": "SECRET"},
        usage=UsageInfo(input_tokens=1, output_tokens=2, total_tokens=3),
        meta=GatewayMeta(
            latency_ms=10,
            model="gpt-test",
            provider="openai",
            validation_status="valid",
        ),
    )
    payload = _build_admin_manual_execute_response_payload(
        built=built,  # type: ignore[arg-type]
        result=result,
        manifest_entry_id="f:s:p:l",
        sample_payload_id=uuid.uuid4(),
        request_id="req-1",
        trace_id="tr-1",
        use_case_key="uc_test",
    )
    assert payload.structured_output is not None
    assert payload.structured_output["provider"] == "openai"
    assert payload.structured_output["chart_json"] == "[REDACTED]"
    assert payload.structured_output_parseable is True
    assert isinstance(payload.prompt_sent, str)
    assert isinstance(payload.resolved_runtime_parameters, dict)


def test_build_admin_manual_execute_response_non_dict_structured_not_parseable() -> None:
    built = SimpleNamespace(
        use_case_key="uc_test",
        transformation_pipeline=SimpleNamespace(rendered_prompt="x"),
    )
    result = GatewayResult.model_construct(
        use_case="uc_test",
        request_id="gw-req",
        trace_id="gw-tr",
        raw_output="[]",
        structured_output=["not", "a", "dict"],
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=1,
            model="gpt-test",
            provider="openai",
            validation_status="valid",
        ),
    )
    payload = _build_admin_manual_execute_response_payload(
        built=built,  # type: ignore[arg-type]
        result=result,
        manifest_entry_id="f:s:p:l",
        sample_payload_id=uuid.uuid4(),
        request_id="req-1",
        trace_id="tr-1",
        use_case_key="uc_test",
    )
    assert payload.structured_output is None
    assert payload.structured_output_parseable is False
