from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


@pytest.mark.asyncio
async def test_gateway_model_override_from_env():
    """Vérifie que la variable d'environnement LLM_MODEL_OVERRIDE_{UC} outrepasse le modèle."""
    # Arrange
    use_case = "chat"
    env_key = f"LLM_MODEL_OVERRIDE_{use_case.upper()}"
    override_model = "gpt-overriden-model"

    mock_client = MagicMock()
    # On mock le retour du client pour inclure le modèle surchargé
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case=use_case,
            request_id="req1",
            trace_id="tr1",
            raw_output="hello",
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=10, model=override_model, prompt_version_id="v1"),
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    # Act
    # On utilise patch.dict pour simuler la variable d'environnement sans polluer le vrai os.environ
    with patch.dict(os.environ, {env_key: override_model}):
        result = await gateway.execute(
            use_case=use_case,
            user_input={"last_user_msg": "hi"},
            context={"locale": "fr", "use_case": use_case},
            request_id="req1",
            trace_id="tr1",
        )

    # Assert
    # Vérifier que le client a été appelé avec le modèle surchargé
    _, kwargs = mock_client.execute.call_args
    assert kwargs["model"] == override_model
    assert result.meta.model_override_active is True


@pytest.mark.asyncio
async def test_gateway_uses_default_model_when_no_env_override():
    """Vérifie que le modèle par défaut est utilisé si aucune variable d'env n'est définie."""
    # Arrange
    use_case = "chat"
    # Le modèle par défaut dans USE_CASE_STUBS pour 'chat' est 'gpt-4o-mini'
    default_model = "gpt-4o-mini"

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case=use_case,
            request_id="req1",
            trace_id="tr1",
            raw_output="hello",
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=10, model=default_model, prompt_version_id="v1"),
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    # Act
    # On s'assure que la variable d'env est absente de manière chirurgicale
    # sans vider tout l'environnement système (comme PATH)
    with patch.dict(os.environ, values={}, clear=False):
        env_key = f"LLM_MODEL_OVERRIDE_{use_case.upper()}"
        os.environ.pop(env_key, None)

        result = await gateway.execute(
            use_case=use_case,
            user_input={"last_user_msg": "hi"},
            context={"locale": "fr", "use_case": use_case},
            request_id="req1",
            trace_id="tr1",
        )

    # Assert
    _, kwargs = mock_client.execute.call_args
    assert kwargs["model"] == default_model
    assert result.meta.model_override_active is False


@pytest.mark.asyncio
async def test_gateway_model_override_with_robust_normalization():
    """Vérifie que la surcharge fonctionne même si le use_case a des caractères spéciaux."""
    # Arrange
    use_case = "natal-v2.extra"
    # Normalisé en LLM_MODEL_OVERRIDE_NATAL_V2_EXTRA
    env_key = "LLM_MODEL_OVERRIDE_NATAL_V2_EXTRA"
    override_model = "gpt-robust-model"

    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case=use_case,
            request_id="req1",
            trace_id="tr1",
            raw_output="hello",
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=10, model=override_model, prompt_version_id="v1"),
        )
    )

    from app.llm_orchestration.models import UseCaseConfig
    stub_config = UseCaseConfig(
        model="gpt-default",
        developer_prompt="test",
        required_prompt_placeholders=[]
    )

    with patch("app.llm_orchestration.gateway.USE_CASE_STUBS", {use_case: stub_config}):
        gateway = LLMGateway(responses_client=mock_client)

        # Act
        with patch.dict(os.environ, {env_key: override_model}):
            result = await gateway.execute(
                use_case=use_case,
                user_input={"last_user_msg": "hi"},
                context={"locale": "fr", "use_case": use_case},
                request_id="req1",
                trace_id="tr1",
            )

    # Assert
    _, kwargs = mock_client.execute.call_args
    assert kwargs["model"] == override_model
    assert result.meta.model_override_active is True
