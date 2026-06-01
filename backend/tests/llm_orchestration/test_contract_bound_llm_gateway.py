# Commentaire global: preuves d'orchestration du gateway LLM pilote par snapshot resolu.
"""Valide que le gateway execute un contrat resolu sans heuristique natal brute."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant

from .contract_bound_gateway_helpers import (
    RecordingContractClient,
    basic_prompt_data,
    premium_prompt_data_with_basic_payload,
    raw_json,
    runtime_snapshot,
    valid_basic_raw_payload,
)

GATEWAY_PATH = Path(__file__).resolve().parents[2] / "app/domain/llm/runtime/gateway.py"


@pytest.mark.asyncio
async def test_gateway_executes_engine_prompt_schema_and_data_from_snapshot() -> None:
    """Le provider recoit uniquement le profil moteur, le schema et le carrier du snapshot."""
    snapshot = runtime_snapshot(ThemeNatalOutputVariant.BASIC_FULL_READING)
    client = RecordingContractClient([raw_json(valid_basic_raw_payload())])

    result = await LLMGateway(responses_client=client).execute_resolved_snapshot(
        snapshot=snapshot,
        prompt_data=basic_prompt_data(),
        request_id="contract-bound-basic",
        trace_id="trace-contract-bound-basic",
    )

    assert result.accepted is True
    assert result.contract_metadata["generation_contract_hash"] == snapshot.generation_contract_hash
    assert result.contract_metadata["prompt_contract_version"] == snapshot.prompt_contract_version
    assert result.contract_metadata["data_contract_version"] == snapshot.data_contract_version

    call = client.calls[0]
    assert call["model"] == snapshot.engine_profile["model_family"]
    assert call["temperature"] == snapshot.engine_profile["runtime_parameters"]["temperature"]
    assert (
        call["max_output_tokens"]
        == snapshot.engine_profile["runtime_parameters"]["max_output_tokens"]
    )
    assert call["response_format"]["json_schema"]["schema"] == snapshot.output_schema
    assert snapshot.prompt_contract["prompt_policy_id"] in call["messages"][0]["content"]

    prompt_payload = json.loads(call["messages"][1]["content"])
    assert set(prompt_payload) == set(snapshot.data_contract["prompt_visible"])


@pytest.mark.asyncio
async def test_premium_contract_carrier_excludes_basic_prompt_payload() -> None:
    """Un payload Basic parasite ne traverse pas le carrier prompt Premium."""
    snapshot = runtime_snapshot(
        ThemeNatalOutputVariant.PREMIUM_FULL_READING,
        form_repair_attempts=0,
    )
    client = RecordingContractClient([raw_json(valid_basic_raw_payload())])

    await LLMGateway(responses_client=client).execute_resolved_snapshot(
        snapshot=snapshot,
        prompt_data=premium_prompt_data_with_basic_payload(),
        request_id="contract-bound-premium",
        trace_id="trace-contract-bound-premium",
    )

    prompt_payload = json.loads(client.calls[0]["messages"][1]["content"])
    serialized_prompt = json.dumps(prompt_payload, ensure_ascii=False, sort_keys=True)

    assert "basic_natal_prompt_payload" not in prompt_payload
    assert "basic_natal_prompt_payload" not in serialized_prompt
    assert set(prompt_payload) == set(snapshot.data_contract["prompt_visible"])


def test_gateway_contract_bound_ast_guard_keeps_raw_natal_use_case_out() -> None:
    """Le chemin snapshot ne prend pas de requete use_case et ne code aucune regle natal."""
    source = GATEWAY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    execute_node = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "execute_resolved_snapshot"
    )
    argument_names = {arg.arg for arg in execute_node.args.args + execute_node.args.kwonlyargs}

    forbidden_source_tokens = {"ThemeNatal", "natal_reading", "basic_full_reading"}

    assert "request" not in argument_names
    assert "use_case" not in argument_names
    assert forbidden_source_tokens.isdisjoint(source.split())
