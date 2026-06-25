# Commentaire global: couvre le fallback SSE du client Astral quand Mercure est indisponible.
"""Tests du streaming d'evenements Astral cote backend."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from app.infra.astral.client import AstralClient, AstralClientConfig

last_stream_headers: dict[str, str] | None = None


class FailingMercureStream:
    """Flux Mercure factice qui refuse la souscription."""

    async def __aenter__(self) -> "FailingMercureStream":
        """Retourne la reponse factice."""
        return self

    async def __aexit__(self, *_args: object) -> None:
        """Ferme le contexte sans masquer l'erreur."""
        return None

    def raise_for_status(self) -> None:
        """Simule le 401 observe sur le hub Mercure local."""
        request = httpx.Request("GET", "http://mercure.local/.well-known/mercure")
        response = httpx.Response(401, request=request)
        raise httpx.HTTPStatusError("401 Unauthorized", request=request, response=response)

    async def aiter_bytes(self) -> Any:
        """Ne produit jamais de chunk car raise_for_status echoue avant."""
        if False:
            yield b""


class FakeAsyncClient:
    """Client httpx factice limite a l'API utilisee par le streaming Mercure."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Accepte la signature httpx.AsyncClient sans l'utiliser."""

    async def __aenter__(self) -> "FakeAsyncClient":
        """Retourne le client factice."""
        return self

    async def __aexit__(self, *_args: object) -> None:
        """Ferme le contexte sans effet."""
        return None

    def stream(self, *_args: object, **kwargs: object) -> FailingMercureStream:
        """Retourne un flux Mercure en erreur."""
        global last_stream_headers
        headers = kwargs.get("headers")
        last_stream_headers = dict(headers) if isinstance(headers, dict) else None
        return FailingMercureStream()


async def _connected() -> bool:
    """Simule un navigateur toujours connecte."""
    return False


@pytest.mark.asyncio
async def test_stream_mercure_events_falls_back_to_job_polling(monkeypatch) -> None:
    """Un 401 Mercure ne doit pas bloquer l'UI si le job est disponible par polling."""
    global last_stream_headers
    last_stream_headers = None
    client = AstralClient(
        AstralClientConfig(
            jobs_api_url="http://jobs.local",
            gateway_url="http://gateway.local",
            mercure_url="http://mercure.local/.well-known/mercure",
            api_key="secret",
            timeout_seconds=1,
        )
    )

    async def fake_get_job_status(run_id: str) -> dict[str, Any]:
        return {"run_id": run_id, "status": "completed", "result": {"reading": {"ok": True}}}

    monkeypatch.setattr("app.infra.astral.client.httpx.AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(client, "get_job_status", fake_get_job_status)

    chunks = [
        chunk
        async for chunk in client.stream_mercure_events(
            run_id="run-1",
            topic="tenants/1/jobs/run-1",
            is_disconnected=_connected,
        )
    ]

    assert len(chunks) == 1
    assert last_stream_headers == {"Accept": "text/event-stream"}
    raw = chunks[0].decode("utf-8")
    assert raw.startswith("event: message\n")
    payload = json.loads(raw.split("data:", 1)[1].strip())
    assert payload["run_id"] == "run-1"
    assert payload["status"] == "completed"
