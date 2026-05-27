# Tests du renderer de prompts LLM.
"""Verifie les substitutions finales et les variables requises du renderer."""

import json

import pytest

from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.domain.llm.runtime.contracts import PromptRenderError
from app.domain.llm.runtime.gateway import LLM_ASTROLOGY_INPUT_V1_KEY


def test_render_success():
    renderer = PromptRenderer()
    template = "Hello {{name}}, you are {{age}} years old."
    variables = {"name": "Alice", "age": 30}
    result = renderer.render(template, variables)
    assert result == "Hello Alice, you are 30 years old."


def test_render_with_extra_variables():
    renderer = PromptRenderer()
    template = "Hello {{name}}."
    variables = {"name": "Alice", "extra": "ignored"}
    result = renderer.render(template, variables)
    assert result == "Hello Alice."


def test_render_missing_non_required_variable():
    renderer = PromptRenderer()
    template = "Hello {{name}}."
    variables = {}
    result = renderer.render(template, variables)
    # Story 66.13: Unknown placeholders are now stripped (replaced by empty string)
    assert result == "Hello ."


def test_render_raises_error_for_missing_required_variable():
    renderer = PromptRenderer()
    template = "Hello {{name}}."
    variables = {}
    with pytest.raises(PromptRenderError) as exc:
        renderer.render(template, variables, required_variables=["name"])
    assert "name" in str(exc.value)


def test_render_snake_case_only():
    renderer = PromptRenderer()
    template = "Hello {{first name}} and {{last_name}}."
    variables = {"first name": "Alice", "last_name": "Smith"}
    result = renderer.render(template, variables)
    # {{first name}} should not be replaced if we only match snake_case
    # Our current regex is r'\{\{([a-zA-Z0-9_]+)\}\}' which doesn't match space.
    assert result == "Hello {{first name}} and Smith."


def test_render_modern_natal_payload_consumes_llm_astrology_input_v1() -> None:
    """Le prompt final natal consomme la cle riche sans carrier legacy."""

    payload = {
        "contract_id": "llm_astrology_input_v1",
        "facts": {"positions": [{"body": "moon", "sign": "taurus"}]},
    }

    result = PromptRenderer.render(
        "Payload: {{llm_astrology_input_v1}}",
        {LLM_ASTROLOGY_INPUT_V1_KEY: json.dumps(payload, sort_keys=True)},
        required_variables=[LLM_ASTROLOGY_INPUT_V1_KEY],
        feature="natal",
    )

    assert "llm_astrology_input_v1" in result
    assert "taurus" in result
    assert "chart_json" not in result
    assert "natal_data" not in result
