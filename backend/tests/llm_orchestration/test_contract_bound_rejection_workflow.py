# Commentaire global: preuves du workflow de rejet gateway pilote par contrat resolu.
"""Valide parsing strict, reparation de forme unique et rejets metier injectes."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import pytest

from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant

from .contract_bound_gateway_helpers import (
    RecordingContractClient,
    basic_prompt_data,
    raw_json,
    runtime_snapshot,
    valid_basic_raw_payload,
)


@pytest.mark.asyncio
async def test_invalid_json_gets_exactly_one_form_repair() -> None:
    """Un JSON invalide declenche une seule reparation de forme contractuelle."""
    snapshot = runtime_snapshot(ThemeNatalOutputVariant.BASIC_FULL_READING)
    client = RecordingContractClient(['{"schema_version":', raw_json(valid_basic_raw_payload())])

    result = await LLMGateway(responses_client=client).execute_resolved_snapshot(
        snapshot=snapshot,
        prompt_data=basic_prompt_data(),
        request_id="invalid-json",
        trace_id="trace-invalid-json",
    )

    assert result.accepted is True
    assert result.repair_attempts == 1
    assert len(client.calls) == 2
    assert client.calls[1]["request_id"] == "invalid-json-repair"


@pytest.mark.asyncio
async def test_schema_shape_error_gets_exactly_one_form_repair() -> None:
    """Un champ inconnu schema est repare une seule fois quand le contrat le permet."""
    invalid_payload = {**valid_basic_raw_payload(), "debug_trace": "interdit"}
    snapshot = runtime_snapshot(ThemeNatalOutputVariant.BASIC_FULL_READING)
    client = RecordingContractClient(
        [raw_json(invalid_payload), raw_json(valid_basic_raw_payload())]
    )

    result = await LLMGateway(responses_client=client).execute_resolved_snapshot(
        snapshot=snapshot,
        prompt_data=basic_prompt_data(),
        request_id="schema-shape",
        trace_id="trace-schema-shape",
    )

    assert result.accepted is True
    assert result.repair_attempts == 1
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_unknown_json_fields_are_rejected_when_repair_is_not_allowed() -> None:
    """Le schema strict rejette les champs inconnus sans fallback silencieux."""
    invalid_payload = {**valid_basic_raw_payload(), "debug_trace": "interdit"}
    snapshot = runtime_snapshot(
        ThemeNatalOutputVariant.BASIC_FULL_READING,
        form_repair_attempts=0,
    )
    client = RecordingContractClient([raw_json(invalid_payload)])

    result = await LLMGateway(responses_client=client).execute_resolved_snapshot(
        snapshot=snapshot,
        prompt_data=basic_prompt_data(),
        request_id="unknown-field",
        trace_id="trace-unknown-field",
    )

    assert result.accepted is False
    assert result.repair_attempts == 0
    assert result.rejection_reason == {
        "code": "contract_form_rejected",
        "category": "schema_error",
    }
    assert result.validation_errors[0]["code"] == "schema_error"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("marker", "expected_code"),
    [
        ("invented_fact_marker", "invented_fact"),
        ("astrological_contradiction_marker", "astrological_contradiction"),
        ("technical_leak_marker", "technical_leak"),
        ("mechanical_phrase_marker", "mechanical_text"),
        ("empty_text_marker", "empty_text"),
    ],
)
async def test_policy_rejections_do_not_trigger_content_repair(
    marker: str,
    expected_code: str,
) -> None:
    """Les validateurs injectes rejettent le contenu sans reparation narrative."""
    payload = valid_basic_raw_payload()
    first_section = payload["sections"][0]
    assert isinstance(first_section, dict)
    first_section["narrative"] = f"{first_section['narrative']} {marker}"
    snapshot = runtime_snapshot(
        ThemeNatalOutputVariant.BASIC_FULL_READING,
        validators=(_marker_policy_validator,),
    )
    client = RecordingContractClient([raw_json(payload)])

    result = await LLMGateway(responses_client=client).execute_resolved_snapshot(
        snapshot=snapshot,
        prompt_data=basic_prompt_data(),
        request_id=f"policy-{expected_code}",
        trace_id=f"trace-policy-{expected_code}",
    )

    assert result.accepted is False
    assert result.repair_attempts == 0
    assert len(client.calls) == 1
    assert result.rejection_reason == {
        "code": expected_code,
        "category": "contract_policy_rejection",
    }


def _marker_policy_validator(
    parsed_output: Mapping[str, Any],
    _prompt_data: Mapping[str, Any],
) -> list[dict[str, object]]:
    serialized = json.dumps(parsed_output, ensure_ascii=False, sort_keys=True)
    marker_to_code = {
        "invented_fact_marker": "invented_fact",
        "astrological_contradiction_marker": "astrological_contradiction",
        "technical_leak_marker": "technical_leak",
        "mechanical_phrase_marker": "mechanical_text",
        "empty_text_marker": "empty_text",
    }
    return [{"code": code} for marker, code in marker_to_code.items() if marker in serialized]
