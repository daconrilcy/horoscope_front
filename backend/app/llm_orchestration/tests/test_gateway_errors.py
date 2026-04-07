import pytest
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import PromptRenderError

@pytest.mark.asyncio
async def test_raises_prompt_render_error_if_var_missing():
    # Use natal_interpretation which needs {{birth_date}} and {{chart_json}}
    gateway = LLMGateway()
    
    # Renderer raises on FIRST missing variable (order depends on required_prompt_placeholders)
    with pytest.raises(PromptRenderError) as exc:
        await gateway.execute(
            use_case="natal_interpretation",
            user_input={"locale": "fr-FR", "use_case": "natal_interpretation"},
            context={},  # Missing birth_date and chart_json
            request_id="r",
            trace_id="t",
        )
    
    # Check that at least one of the missing ones is mentioned
    msg = str(exc.value)
    assert "birth_date" in msg or "chart_json" in msg
