# Validation smoke opt-in du provider theme astral.
"""Valide le smoke provider theme astral sans execution implicite en CI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

from app.core.llm_settings import ai_engine_settings
from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_SCHEMA,
)
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.infra.providers.llm.openai_responses_client import ResponsesClient

RUN_PROVIDER_SMOKE_ENV = "RUN_THEME_ASTRAL_PROVIDER_SMOKE"
PROVIDER_SMOKE_MODEL_ENV = "THEME_ASTRAL_PROVIDER_SMOKE_MODEL"
PROVIDER_SMOKE_TIMEOUT_SECONDS = 60
REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_PAYLOAD_PATH = (
    REPO_ROOT
    / "_condamad"
    / "examples"
    / "prompt-generation-cartography"
    / "1973-04-24-1100-paris-theme-astral-v1"
    / "basic-provider-payload.json"
)


def _provider_smoke_is_enabled() -> bool:
    """Indique si l'appel provider reel a ete explicitement autorise."""
    return os.getenv(RUN_PROVIDER_SMOKE_ENV) == "1"


def _skip_without_provider_smoke_prerequisites() -> None:
    """Ignore proprement le smoke si l'opt-in ou les identifiants manquent."""
    if not _provider_smoke_is_enabled():
        pytest.skip(f"{RUN_PROVIDER_SMOKE_ENV}=1 is required for provider smoke.")
    if not ai_engine_settings.is_openai_configured:
        pytest.skip("OpenAI provider credentials are required for provider smoke.")


def _load_example_payload() -> dict[str, Any]:
    """Charge le payload provider cartographie sans le dupliquer dans le test."""
    return json.loads(EXAMPLE_PAYLOAD_PATH.read_text(encoding="utf-8"))


def _provider_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Construit le message minimal envoye au provider smoke."""
    return [
        {
            "role": "user",
            "content": (
                f"{THEME_ASTRAL_INPUT_CONTRACT_ID}: "
                + json.dumps(payload, ensure_ascii=False, sort_keys=True)
            ),
        }
    ]


async def _call_theme_astral_provider_once(client: Any, payload: dict[str, Any]) -> GatewayResult:
    """Execute exactement une tentative provider avec le schema de reponse canonique."""
    model = os.getenv(PROVIDER_SMOKE_MODEL_ENV, ai_engine_settings.openai_model_default)
    result = await client.execute(
        messages=_provider_messages(payload),
        model=model,
        timeout_seconds=PROVIDER_SMOKE_TIMEOUT_SECONDS,
        request_id="theme-astral-provider-smoke",
        trace_id="theme-astral-provider-smoke",
        use_case="theme_astral",
        max_output_tokens=payload["delivery_profile"]["output_length_policy"]["max_output_tokens"],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": THEME_ASTRAL_RESPONSE_CONTRACT_ID,
                "schema": THEME_ASTRAL_RESPONSE_SCHEMA,
                "strict": True,
            },
        },
    )
    if isinstance(result, tuple):
        return result[0]
    return result


def _decode_provider_document(result: GatewayResult) -> dict[str, Any]:
    """Decode la reponse provider sans conserver le texte brut dans les preuves."""
    if result.structured_output:
        return result.structured_output
    decoded = json.loads(result.raw_output)
    assert isinstance(decoded, dict)
    return decoded


def _schema_errors(document: dict[str, Any]) -> list[str]:
    """Retourne les erreurs du schema canonique sous forme stable."""
    validator = Draft7Validator(THEME_ASTRAL_RESPONSE_SCHEMA)
    return sorted(error.message for error in validator.iter_errors(document))


def _safe_metadata(result: GatewayResult, document: dict[str, Any]) -> dict[str, Any]:
    """Produit une preuve metadata-only sans contenu provider ni secret."""
    return {
        "schema_valid": not _schema_errors(document),
        "model": result.meta.model,
        "total_tokens": result.usage.total_tokens,
        "estimated_cost_usd": result.usage.estimated_cost_usd,
        "contract_trace": document.get("contract_trace", {}),
        "raw_output_persisted": False,
    }


def _valid_response_document() -> dict[str, Any]:
    """Fournit une reponse minimale conforme au contrat canonique."""
    return {
        "title": "Theme astral de validation",
        "summary": "Validation controlee du contrat de reponse theme astral.",
        "sections": [
            {
                "key": "synthese",
                "heading": "Synthese",
                "content": "Le payload respecte le contrat attendu pour la validation smoke.",
            }
        ],
        "evidence": ["payload-example-basic", "schema-theme-astral-response-v1"],
        "contract_trace": {
            "prompt_contract_id": THEME_ASTRAL_PROMPT_CONTRACT_ID,
            "input_contract_id": THEME_ASTRAL_INPUT_CONTRACT_ID,
            "response_contract_id": THEME_ASTRAL_RESPONSE_CONTRACT_ID,
            "delivery_profile_id": "expanded",
        },
    }


class RecordingProviderClient:
    """Client instrumente pour prouver l'appel unique sans provider reel."""

    def __init__(self, document: dict[str, Any]) -> None:
        self.document = document
        self.calls: list[dict[str, Any]] = []

    async def execute(self, **kwargs: Any) -> GatewayResult:
        """Capture les arguments puis renvoie une reponse contractuelle."""
        self.calls.append(kwargs)
        return GatewayResult(
            use_case=kwargs["use_case"],
            request_id=kwargs["request_id"],
            trace_id=kwargs["trace_id"],
            raw_output=json.dumps(self.document, ensure_ascii=False),
            structured_output=self.document,
            usage=UsageInfo(input_tokens=120, output_tokens=80, total_tokens=200),
            meta=GatewayMeta(latency_ms=1, model=kwargs["model"], provider="openai"),
        )


def test_missing_provider_smoke_opt_in_keeps_runtime_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'absence d'opt-in laisse le smoke provider desactive par defaut."""
    monkeypatch.delenv(RUN_PROVIDER_SMOKE_ENV, raising=False)

    assert not _provider_smoke_is_enabled()


@pytest.mark.asyncio
async def test_opt_in_provider_path_performs_one_contractual_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le chemin opt-in execute un seul appel et transmet le schema canonique."""
    monkeypatch.setenv(RUN_PROVIDER_SMOKE_ENV, "1")
    payload = _load_example_payload()
    client = RecordingProviderClient(_valid_response_document())

    result = await _call_theme_astral_provider_once(client, payload)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["timeout_seconds"] == PROVIDER_SMOKE_TIMEOUT_SECONDS
    assert call["response_format"]["json_schema"]["schema"] is THEME_ASTRAL_RESPONSE_SCHEMA
    assert THEME_ASTRAL_INPUT_CONTRACT_ID in call["messages"][0]["content"]
    assert _schema_errors(_decode_provider_document(result)) == []


def test_safe_metadata_does_not_persist_provider_content() -> None:
    """La preuve conserve uniquement des metadonnees non sensibles."""
    document = _valid_response_document()
    result = GatewayResult(
        use_case="theme_astral",
        request_id="theme-astral-provider-smoke",
        trace_id="theme-astral-provider-smoke",
        raw_output=json.dumps(document, ensure_ascii=False),
        structured_output=document,
        usage=UsageInfo(
            input_tokens=10, output_tokens=20, total_tokens=30, estimated_cost_usd=0.001
        ),
        meta=GatewayMeta(latency_ms=1, model="test-model", provider="openai"),
    )

    metadata = _safe_metadata(result, document)

    assert metadata == {
        "schema_valid": True,
        "model": "test-model",
        "total_tokens": 30,
        "estimated_cost_usd": 0.001,
        "contract_trace": document["contract_trace"],
        "raw_output_persisted": False,
    }
    assert "raw_output" not in metadata
    assert "messages" not in metadata


@pytest.mark.provider_smoke
@pytest.mark.asyncio
async def test_theme_astral_provider_smoke_validates_response_contract() -> None:
    """Le smoke reel valide la reponse provider seulement sur opt-in explicite."""
    _skip_without_provider_smoke_prerequisites()
    payload = _load_example_payload()
    result = await _call_theme_astral_provider_once(ResponsesClient(), payload)
    document = _decode_provider_document(result)

    assert _schema_errors(document) == []
    assert _safe_metadata(result, document)["raw_output_persisted"] is False
