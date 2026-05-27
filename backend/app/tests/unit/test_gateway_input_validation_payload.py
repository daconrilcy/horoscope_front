from app.domain.llm.runtime.contracts import ExecutionContext, UseCaseConfig
from app.domain.llm.runtime.gateway import LLMGateway


def test_build_validation_payload_does_not_rebuild_chart_json_from_natal_data() -> None:
    gateway = LLMGateway()
    config = UseCaseConfig(
        model="gpt-5-nano",
        developer_prompt="Test {{chart_json}}",
        input_schema={
            "type": "object",
            "required": ["chart_json"],
            "properties": {
                "chart_json": {"type": "object"},
                "locale": {"type": "string"},
            },
        },
    )

    payload = gateway._build_validation_payload(
        config,
        {"use_case": "natal_interpretation_short", "locale": "fr-FR"},
        ExecutionContext(
            natal_data={"meta": {"chart_json_version": "1"}},
            chart_json='{"meta": {"chart_json_version": "legacy"}}',
        ),
    )

    assert "chart_json" not in payload


def test_build_validation_payload_does_not_parse_chart_json_string_from_context() -> None:
    gateway = LLMGateway()
    config = UseCaseConfig(
        model="gpt-5-nano",
        developer_prompt="Test {{chart_json}}",
        input_schema={
            "type": "object",
            "required": ["chart_json"],
            "properties": {"chart_json": {"type": "object"}},
        },
    )

    payload = gateway._build_validation_payload(
        config,
        {"use_case": "natal_interpretation_short"},
        ExecutionContext(chart_json='{"meta": {"chart_json_version": "1"}}'),
    )

    assert "chart_json" not in payload
