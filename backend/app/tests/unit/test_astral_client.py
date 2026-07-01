# Commentaire global: tests du proxy Mercure du client Astral.
"""Couvre le comportement du proxy SSE Mercure du client Astral."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

import pytest

from app.infra.astral.client import AstralClient, AstralClientConfig


class _FakeMercureResponse:
    """Simule une réponse Mercure avec statut HTTP configurable."""

    def __init__(self, *, status_code: int, chunks: list[bytes] | None = None) -> None:
        self.status_code = status_code
        self._chunks = chunks or []

    async def __aenter__(self) -> "_FakeMercureResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        """Expose les morceaux du flux SSE simulé."""
        for chunk in self._chunks:
            yield chunk


class _FakeMercureStream:
    """Expose un gestionnaire de contexte compatible avec httpx.AsyncClient.stream."""

    def __init__(self, response: _FakeMercureResponse) -> None:
        self._response = response

    async def __aenter__(self) -> _FakeMercureResponse:
        return self._response

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeMercureAsyncClient:
    """Simule le client HTTP utilisé par le proxy Mercure."""

    def __init__(self, *, response: _FakeMercureResponse) -> None:
        self._response = response

    async def __aenter__(self) -> "_FakeMercureAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def stream(self, method: str, url: str, **kwargs) -> _FakeMercureStream:
        """Retourne la réponse Mercure simulée."""
        return _FakeMercureStream(self._response)


@pytest.mark.asyncio
async def test_stream_mercure_events_returns_controlled_error_event_on_unauthorized(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Un 401 Mercure ne doit pas remonter en traceback non contrôlé."""
    response = _FakeMercureResponse(status_code=401)
    monkeypatch.setattr(
        "app.infra.astral.client.httpx.AsyncClient",
        lambda timeout=None: _FakeMercureAsyncClient(response=response),
    )

    client = AstralClient(
        AstralClientConfig(
            jobs_api_url="http://astral.local",
            gateway_url="http://gateway.local",
            mercure_url="http://mercure.local/.well-known/mercure",
            api_key="secret",
            timeout_seconds=5,
        )
    )

    with caplog.at_level(logging.WARNING, logger="app.infra.astral.client"):
        chunks = [
            chunk
            async for chunk in client.stream_mercure_events(
                topic="tenants/14/jobs/run-123",
                is_disconnected=lambda: _never_disconnected(),
            )
        ]

    assert len(chunks) == 1
    payload = chunks[0].decode("utf-8")
    assert "event: error" in payload
    assert "astral_mercure_unavailable" in payload

    warning_records = [record for record in caplog.records if record.levelno == logging.WARNING]
    assert warning_records
    assert all(record.exc_info is None for record in warning_records)
    assert any(
        "astral_mercure_stream_rejected" in record.message for record in warning_records
    )


async def _never_disconnected() -> bool:
    """Indique que le client reste connecté pendant le test."""
    return False
