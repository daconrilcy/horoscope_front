import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


@pytest.mark.asyncio
async def test_gateway_model_override_from_env():
    """Vérifie que la variable d'environnement LLM_MODEL_OVERRIDE_{UC} outrepasse le modèle."""
    use_case = "chat"
    env_key = f"LLM_MODEL_OVERRIDE_{use_case.upper()}"
    override_model = "gpt-overriden-model"

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case=use_case,
            request_id="req1",
            trace_id="tr1",
            raw_output='{"message": "hello"}',  # Valid JSON
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=10, model=override_model, prompt_version_id="v1"),
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    with patch.dict(os.environ, {env_key: override_model}):
        result = await gateway.execute(
            use_case=use_case,
            user_input={"last_user_msg": "hi"},
            context={"locale": "fr", "use_case": use_case},
            request_id="req1",
            trace_id="tr1",
        )
        assert result.meta.model == override_model
        assert result.meta.model_override_active is True


@pytest.mark.asyncio
async def test_gateway_uses_default_model_when_no_env_override():
    """Vérifie que le modèle par défaut est utilisé en l'absence de surcharge."""
    use_case = "chat"
    default_model = "gpt-4o-mini"

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case=use_case,
            request_id="req1",
            trace_id="tr1",
            raw_output='{"message": "hello"}',  # Valid JSON
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=10, model=default_model, prompt_version_id="v1"),
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    with patch.dict(os.environ, {}, clear=True):
        result = await gateway.execute(
            use_case=use_case,
            user_input={"last_user_msg": "hi"},
            context={"locale": "fr", "use_case": use_case},
            request_id="req1",
            trace_id="tr1",
        )
        assert result.meta.model_override_active is False


@pytest.mark.asyncio
async def test_gateway_model_override_with_robust_normalization():
    """Vérifie que la normalisation de la clé d'env est robuste (ex: natal-long-free)."""
    use_case = "natal-long-free"
    env_key = "LLM_MODEL_OVERRIDE_NATAL_LONG_FREE"
    override_model = "gpt-robust-model"

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case=use_case,
            request_id="req1",
            trace_id="tr1",
            raw_output='{"message": "hello"}',  # Valid JSON
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=10, model=override_model, prompt_version_id="v1"),
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    with patch.dict(os.environ, {env_key: override_model}):
        result = await gateway.execute(
            use_case=use_case,
            user_input={"last_user_msg": "hi"},
            context={"locale": "fr", "use_case": use_case},
            request_id="req1",
            trace_id="tr1",
        )
        assert result.meta.model_override_active is True
