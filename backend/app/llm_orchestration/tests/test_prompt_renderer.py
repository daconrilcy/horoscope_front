import pytest

from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.llm_orchestration.models import PromptRenderError


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
