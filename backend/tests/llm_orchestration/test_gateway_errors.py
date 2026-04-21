import pytest

from app.domain.llm.runtime.contracts import PromptRenderError
from app.domain.llm.runtime.gateway import LLMGateway


@pytest.mark.asyncio
async def test_raises_prompt_render_error_if_var_missing(db):
    # Use a non-supported feature to avoid mandatory assembly check (Story 66.29)
    # We'll use 'dummy' feature.
    gateway = LLMGateway()

    # Seed a dummy config with a required variable
    from unittest.mock import patch

    from app.domain.llm.runtime.contracts import UseCaseConfig

    dummy_config = UseCaseConfig(
        model="m", developer_prompt="Hello {{name}}", required_prompt_placeholders=["name"]
    )

    with patch.object(gateway, "_resolve_legacy_compat_config", return_value=dummy_config):
        # Renderer raises on FIRST missing variable
        with pytest.raises(PromptRenderError) as exc:
            await gateway.execute(
                use_case="dummy_uc",
                user_input={"locale": "fr-FR", "use_case": "dummy_uc", "feature": "dummy"},
                context={},  # Missing 'name'
                request_id="r",
                trace_id="t",
            )

    msg = str(exc.value)
    assert "name" in msg
