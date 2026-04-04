from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai_engine.exceptions import UpstreamTimeoutError
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import PromptRenderError, UnknownUseCaseError


@pytest.mark.asyncio
async def test_catalog_free_natal_use_case_resolves_without_db_prompt(db):
    gateway = LLMGateway()

    config = await gateway._resolve_config(db, "natal_long_free", {})

    assert config.interaction_mode == "structured"
    assert config.user_question_policy == "none"
    assert '"title"' in config.developer_prompt
    assert "accordion_titles" in config.developer_prompt
    assert "chart_json" in config.required_prompt_placeholders


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


@pytest.mark.asyncio
async def test_propagates_upstream_timeout_error():
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(side_effect=UpstreamTimeoutError("timeout"))
    gateway = LLMGateway(responses_client=mock_client)

    with pytest.raises(UpstreamTimeoutError):
        await gateway.execute(
            use_case="natal_interpretation_short",
            user_input={},
            context={"locale": "fr-FR", "use_case": "natal_interpretation_short"},
            request_id="r",
            trace_id="t",
        )
