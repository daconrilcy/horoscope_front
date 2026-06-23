# Commentaire global: client HTTP unique pour consommer les services Astral externalises.
"""Client HTTP unique pour consommer les services Astral externalises."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx


class AstralClientError(Exception):
    """Erreur controlee lors d'un appel au service Astral externe."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialise une erreur exposable par la facade backend."""
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class AstralClientConfig:
    """Configuration reseau minimale du client Astral."""

    jobs_api_url: str
    gateway_url: str
    mercure_url: str
    api_key: str | None
    timeout_seconds: float


class AstralClient:
    """Centralise les appels HTTP vers Astral et normalise leurs erreurs."""

    def __init__(self, config: AstralClientConfig) -> None:
        """Prepare un client sans ouvrir de connexion persistante globale."""
        self._config = config

    @property
    def mercure_url(self) -> str:
        """Retourne l'URL publique du hub Mercure configure."""
        return self._config.mercure_url.rstrip("/")

    async def submit_job(
        self,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Soumet un job asynchrone Astral via l'API integration."""
        return await self._post_json(
            f"{self._config.jobs_api_url.rstrip('/')}/v1/jobs",
            payload,
            extra_headers={"Idempotency-Key": idempotency_key},
        )

    async def get_job_status(self, run_id: str) -> dict[str, Any]:
        """Recupere l'etat courant d'un job Astral."""
        return await self._get_json(f"{self._config.jobs_api_url.rstrip('/')}/v1/jobs/{run_id}")

    async def get_services(self) -> dict[str, Any] | list[Any]:
        """Expose le catalogue des services Astral pour diagnostics internes."""
        async with self._client() as client:
            response = await client.get(
                f"{self._config.jobs_api_url.rstrip('/')}/v1/services",
                headers=self._headers(),
            )
        return self._decode_response(response)

    async def stream_mercure_events(
        self,
        *,
        topic: str,
        is_disconnected: Callable[[], Awaitable[bool]],
    ) -> AsyncIterator[bytes]:
        """Proxy le flux Mercure Astral en conservant les secrets cote backend."""
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "GET",
                    self.mercure_url,
                    params={"topic": topic},
                    headers=self._headers(accept="text/event-stream"),
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        if await is_disconnected():
                            break
                        yield chunk
        except httpx.HTTPError as error:
            payload = json.dumps(
                {
                    "code": "astral_mercure_unavailable",
                    "message": str(error),
                },
                ensure_ascii=False,
            )
            yield f"event: error\ndata: {payload}\n\n".encode("utf-8")

    async def _post_json(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Execute un POST JSON avec mapping d'erreur uniforme."""
        headers = self._headers()
        headers.update(extra_headers or {})
        try:
            async with self._client() as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException as error:
            raise AstralClientError(
                code="astral_upstream_timeout",
                message="Astral service timed out",
                status_code=504,
            ) from error
        except httpx.HTTPError as error:
            raise AstralClientError(
                code="astral_upstream_unreachable",
                message="Astral service is unreachable",
                status_code=503,
                details={"error": str(error)},
            ) from error
        decoded = self._decode_response(response)
        if not isinstance(decoded, dict):
            raise AstralClientError(
                code="astral_invalid_response",
                message="Astral response must be a JSON object",
                status_code=502,
            )
        return decoded

    async def _get_json(self, url: str) -> dict[str, Any]:
        """Execute un GET JSON avec mapping d'erreur uniforme."""
        try:
            async with self._client() as client:
                response = await client.get(url, headers=self._headers())
        except httpx.TimeoutException as error:
            raise AstralClientError(
                code="astral_upstream_timeout",
                message="Astral service timed out",
                status_code=504,
            ) from error
        except httpx.HTTPError as error:
            raise AstralClientError(
                code="astral_upstream_unreachable",
                message="Astral service is unreachable",
                status_code=503,
                details={"error": str(error)},
            ) from error
        decoded = self._decode_response(response)
        if not isinstance(decoded, dict):
            raise AstralClientError(
                code="astral_invalid_response",
                message="Astral response must be a JSON object",
                status_code=502,
            )
        return decoded

    def _decode_response(self, response: httpx.Response) -> Any:
        """Decode une reponse Astral et remonte son erreur HTTP si necessaire."""
        try:
            decoded = response.json()
        except ValueError as error:
            raise AstralClientError(
                code="astral_invalid_json",
                message="Astral response is not valid JSON",
                status_code=502,
            ) from error
        if response.status_code >= 400:
            error_payload = decoded.get("error") if isinstance(decoded, dict) else None
            code = "astral_upstream_error"
            message = "Astral service returned an error"
            details: dict[str, Any] = {"status_code": response.status_code}
            if isinstance(error_payload, dict):
                code = str(error_payload.get("code") or code)
                message = str(error_payload.get("message") or message)
                raw_details = error_payload.get("details")
                if isinstance(raw_details, dict):
                    details.update(raw_details)
            raise AstralClientError(
                code=code,
                message=message,
                status_code=response.status_code,
                details=details,
            )
        return decoded

    def _headers(self, *, accept: str = "application/json") -> dict[str, str]:
        """Construit les headers communs sans exposer le secret au frontend."""
        headers = {"Accept": accept}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
            headers["X-API-Key"] = self._config.api_key
        return headers

    def _client(self) -> httpx.AsyncClient:
        """Cree un client HTTP court-vivant avec timeout centralise."""
        return httpx.AsyncClient(timeout=self._config.timeout_seconds)
