"""Tests des codes d'erreur applicatifs de l'observabilité admin LLM."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from app.core.exceptions import ApplicationError
from app.services.api_contracts.admin.llm.prompts import ReplayPayload
from app.services.llm_observability import admin_observability


@pytest.mark.asyncio
async def test_replay_request_preserves_disabled_replay_error_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie que la désactivation garde le code historique avec statut 403."""

    async def _disabled_replay(**_kwargs: Any) -> None:
        raise RuntimeError("Replay tool is disabled in production environments.")

    monkeypatch.setattr(admin_observability, "replay", _disabled_replay)

    with pytest.raises(ApplicationError) as raised:
        await admin_observability.replay_request(
            request_id="req-review-disabled",
            payload=ReplayPayload(request_id="source-request", prompt_version_id="prompt-version"),
            current_user=SimpleNamespace(id="admin"),
            db=SimpleNamespace(),
        )

    assert raised.value.code == "replay_failed"
    assert raised.value.http_status_code == 403


@pytest.mark.asyncio
async def test_replay_request_raises_generic_replay_failure_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Vérifie que les autres échecs replay gardent le code applicatif historique."""

    async def _failing_replay(**_kwargs: Any) -> None:
        raise RuntimeError("Call log not found for request_id: source-request")

    monkeypatch.setattr(admin_observability, "replay", _failing_replay)

    with pytest.raises(ApplicationError) as raised:
        await admin_observability.replay_request(
            request_id="req-review-failed",
            payload=ReplayPayload(request_id="source-request", prompt_version_id="prompt-version"),
            current_user=SimpleNamespace(id="admin"),
            db=SimpleNamespace(),
        )

    assert raised.value.code == "replay_failed"
    assert raised.value.http_status_code == 400
