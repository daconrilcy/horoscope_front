from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm_orchestration.providers.responses_client import ResponsesClient


def _build_raw_response(
    mock_response: MagicMock,
    headers: dict[str, str] | None = None,
) -> MagicMock:
    raw_response = MagicMock()
    raw_response.parse.return_value = mock_response
    raw_response.headers = headers or {}
    return raw_response

# ---------------------------------------------------------------------------
# Tests _to_typed_content_blocks
# ---------------------------------------------------------------------------


def test_to_typed_content_blocks_converts_strings():
    """Vérifie la conversion en blocs de contenu typés pour GPT-5."""
    messages = [
        {"role": "system", "content": "Instruction"},
        {"role": "user", "content": "Question"},
        {"role": "assistant", "content": "Reponse precedente"},
    ]
    typed = ResponsesClient._to_typed_content_blocks(messages)

    assert len(typed) == 3
    assert typed[0]["role"] == "system"
    assert typed[0]["content"] == [{"type": "input_text", "text": "Instruction"}]
    assert typed[1]["role"] == "user"
    assert typed[1]["content"] == [{"type": "input_text", "text": "Question"}]
    assert typed[2]["role"] == "assistant"
    assert typed[2]["content"] == [{"type": "output_text", "text": "Reponse precedente"}]


def test_to_typed_content_blocks_idempotent():
    """Si content est déjà une liste de typed blocks, il n'est pas re-converti."""
    already_typed = [
        {"role": "assistant", "content": [{"type": "output_text", "text": "Already typed"}]}
    ]
    result = ResponsesClient._to_typed_content_blocks(already_typed)
    assert result[0]["content"] == [{"type": "output_text", "text": "Already typed"}]


def test_to_typed_content_blocks_preserves_extra_fields():
    """Tous les champs du message original sont préservés (pas uniquement role/content)."""
    messages = [{"role": "user", "content": "Hello", "extra_field": "keep_me"}]
    result = ResponsesClient._to_typed_content_blocks(messages)
    assert result[0]["extra_field"] == "keep_me"
    assert result[0]["role"] == "user"
    assert result[0]["content"] == [{"type": "input_text", "text": "Hello"}]


def test_to_typed_content_blocks_handles_missing_content():
    """Un message sans clé 'content' produit un bloc vide sans KeyError."""
    messages = [{"role": "system"}]
    result = ResponsesClient._to_typed_content_blocks(messages)
    assert result[0]["content"] == [{"type": "input_text", "text": ""}]


def test_to_typed_content_blocks_preserves_roles():
    """Le rôle de chaque message est préservé."""
    messages = [
        {"role": "system", "content": "Hard policy."},
        {"role": "developer", "content": "Developer prompt."},
        {"role": "user", "content": "User data."},
    ]
    result = ResponsesClient._to_typed_content_blocks(messages)
    assert [m["role"] for m in result] == ["system", "developer", "user"]


# ---------------------------------------------------------------------------
# Tests execute() — paramètres GPT-5
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_gpt5_params():
    """Vérifie que les paramètres GPT-5 sont transmis et temperature omise."""
    client = ResponsesClient()
    mock_openai = AsyncMock()
    client._async_client = mock_openai
    client._ensure_configured = MagicMock()

    messages = [{"role": "user", "content": "Hello"}]

    mock_response = MagicMock()
    mock_response.model = "gpt-5"
    mock_response.output_text = "{}"
    mock_response.usage = MagicMock()
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 20
    mock_response.usage.total_tokens = 30
    mock_openai.with_raw_response.responses.create.return_value = _build_raw_response(mock_response)

    await client.execute(
        messages=messages,
        model="gpt-5",
        reasoning_effort="low",
        verbosity="high",
        temperature=0.7,
        request_id="req_123",
        trace_id="trace_456",
        use_case="natal_interpretation",
    )

    _, kwargs = mock_openai.with_raw_response.responses.create.call_args
    assert kwargs["model"] == "gpt-5"
    assert "temperature" not in kwargs
    assert kwargs["reasoning"]["effort"] == "low"
    assert kwargs["text"]["verbosity"] == "high"
    assert kwargs["extra_headers"] == {
        "x-request-id": "req_123",
        "x-trace-id": "trace_456",
        "x-use-case": "natal_interpretation",
    }
    # Input doit être en typed content blocks
    assert isinstance(kwargs["input"][0]["content"], list)
    assert kwargs["input"][0]["content"][0]["type"] == "input_text"


@pytest.mark.asyncio
async def test_execute_non_reasoning_params():
    """Vérifie que temperature est présente et reasoning absent pour gpt-4o-mini."""
    client = ResponsesClient()
    mock_openai = AsyncMock()
    client._async_client = mock_openai
    client._ensure_configured = MagicMock()

    messages = [{"role": "user", "content": "Hello"}]

    mock_response = MagicMock()
    mock_response.model = "gpt-4o-mini"
    mock_response.output_text = "{}"
    mock_response.usage = MagicMock()
    mock_response.usage.input_tokens = 5
    mock_response.usage.output_tokens = 5
    mock_response.usage.total_tokens = 10
    mock_openai.with_raw_response.responses.create.return_value = _build_raw_response(mock_response)

    await client.execute(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.5,
    )

    _, kwargs = mock_openai.with_raw_response.responses.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["temperature"] == 0.5
    assert "reasoning" not in kwargs
    assert "text" not in kwargs
    # Input doit rester en format string (pas de typed blocks)
    assert kwargs["input"][0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_execute_o4_reasoning_no_temperature():
    """Un modèle o4- est traité comme reasoning model : temperature omise."""
    client = ResponsesClient()
    mock_openai = AsyncMock()
    client._async_client = mock_openai
    client._ensure_configured = MagicMock()

    mock_response = MagicMock()
    mock_response.model = "o4-mini"
    mock_response.output_text = "{}"
    mock_response.usage = MagicMock(input_tokens=5, output_tokens=5, total_tokens=10)
    mock_openai.with_raw_response.responses.create.return_value = _build_raw_response(mock_response)

    await client.execute(
        messages=[{"role": "user", "content": "Test"}],
        model="o4-mini",
        temperature=0.7,
        reasoning_effort="medium",
    )

    _, kwargs = mock_openai.with_raw_response.responses.create.call_args
    assert "temperature" not in kwargs
    assert kwargs["reasoning"]["effort"] == "medium"


@pytest.mark.asyncio
async def test_execute_gpt5_no_verbosity_when_none():
    """verbosity n'est pas ajouté au payload si None."""
    client = ResponsesClient()
    mock_openai = AsyncMock()
    client._async_client = mock_openai
    client._ensure_configured = MagicMock()

    mock_response = MagicMock()
    mock_response.model = "gpt-5"
    mock_response.output_text = "{}"
    mock_response.usage = MagicMock(input_tokens=5, output_tokens=5, total_tokens=10)
    mock_openai.with_raw_response.responses.create.return_value = _build_raw_response(mock_response)

    await client.execute(
        messages=[{"role": "user", "content": "Test"}],
        model="gpt-5",
        reasoning_effort="low",
        verbosity=None,
    )

    _, kwargs = mock_openai.with_raw_response.responses.create.call_args
    assert "text" not in kwargs


@pytest.mark.asyncio
async def test_structured_output_populated_when_response_format_set():
    """Vérifie que structured_output est peuplé si response_format est fourni."""
    client = ResponsesClient()
    mock_openai = AsyncMock()
    client._async_client = mock_openai
    client._ensure_configured = MagicMock()

    mock_response = MagicMock()
    mock_response.model = "gpt-5"
    mock_response.output_text = '{"result": "success"}'
    mock_response.usage = MagicMock(input_tokens=5, output_tokens=5, total_tokens=10)
    mock_openai.with_raw_response.responses.create.return_value = _build_raw_response(mock_response)

    result, headers = await client.execute(
        messages=[{"role": "user", "content": "Test"}],
        model="gpt-5",
        response_format={"type": "json_object"},
    )

    assert headers == {}
    assert result.structured_output == {"result": "success"}


@pytest.mark.asyncio
async def test_structured_output_none_when_no_response_format():
    """Vérifie que structured_output est None si pas de response_format."""
    client = ResponsesClient()
    mock_openai = AsyncMock()
    client._async_client = mock_openai
    client._ensure_configured = MagicMock()

    mock_response = MagicMock()
    mock_response.model = "gpt-5"
    mock_response.output_text = '{"result": "success"}'
    mock_response.usage = MagicMock(input_tokens=5, output_tokens=5, total_tokens=10)
    mock_openai.with_raw_response.responses.create.return_value = _build_raw_response(mock_response)

    result, headers = await client.execute(
        messages=[{"role": "user", "content": "Test"}],
        model="gpt-5",
        response_format=None,
    )

    assert headers == {}
    assert result.structured_output is None
