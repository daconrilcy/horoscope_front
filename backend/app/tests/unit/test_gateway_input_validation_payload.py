from app.domain.llm.runtime.contracts import ExecutionContext, UseCaseConfig
from app.domain.llm.runtime.gateway import LLMGateway


def test_build_validation_payload_uses_natal_data_for_chart_json_object() -> None:
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

    assert payload["chart_json"] == {"meta": {"chart_json_version": "1"}}


def test_build_validation_payload_parses_chart_json_string_when_natal_data_is_absent() -> None:
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

    assert payload["chart_json"] == {"meta": {"chart_json_version": "1"}}
