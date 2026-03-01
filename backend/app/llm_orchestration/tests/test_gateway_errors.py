import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import PromptRenderError, UnknownUseCaseError


@pytest.mark.asyncio
async def test_raises_unknown_use_case_error():
    gateway = LLMGateway()
    with pytest.raises(UnknownUseCaseError) as exc:
        await gateway.execute(
            use_case="unknown_case",
            user_input={"locale": "fr-FR", "use_case": "unknown_case"},
            context={},
            request_id="r",
            trace_id="t",
        )
    assert "unknown_case" in str(exc.value)


@pytest.mark.asyncio
async def test_raises_prompt_render_error_if_var_missing():
    # Use natal_interpretation which needs {{birth_date}} and {{chart_json}}
    gateway = LLMGateway()
    with pytest.raises(PromptRenderError) as exc:
        await gateway.execute(
            use_case="natal_interpretation",
            user_input={"locale": "fr-FR", "use_case": "natal_interpretation"},
            context={},  # Missing birth_date and chart_json
            request_id="r",
            trace_id="t",
        )
    assert "birth_date" in str(exc.value)
    assert "chart_json" in str(exc.value)


@pytest.mark.asyncio
async def test_renderer_raises_error_when_required_variable_missing():
    from app.llm_orchestration.services.prompt_renderer import PromptRenderer

    renderer = PromptRenderer()
    with pytest.raises(PromptRenderError) as exc:
        renderer.render("Hello {{name}}", {"age": 20}, required_variables=["name"])
    assert "name" in str(exc.value)
