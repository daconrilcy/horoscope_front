# Tests du contrat de configuration des use cases natals modernes.
"""Verrouille la migration des entrees natales modernes vers llm_astrology_input_v1."""

from __future__ import annotations

import json

from app.domain.llm.configuration.canonical_use_case_registry import (
    list_canonical_use_case_contracts,
    list_modern_natal_use_case_contracts,
)
from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.domain.llm.runtime.gateway import LLM_ASTROLOGY_INPUT_V1_KEY

LEGACY_ASTROLOGY_INPUT_KEYS = {"chart_json", "natal_data"}


def test_modern_natal_use_cases_require_llm_astrology_input_v1() -> None:
    """Chaque use case natal moderne exige la cle astrologique canonique."""

    contracts = list_modern_natal_use_case_contracts()

    assert contracts
    for contract in contracts:
        assert LLM_ASTROLOGY_INPUT_V1_KEY in contract.required_prompt_placeholders


def test_modern_natal_use_case_schemas_declare_llm_astrology_input_v1() -> None:
    """Les schemas natals modernes exposent la cle riche comme entree obligatoire."""

    for contract in list_modern_natal_use_case_contracts():
        assert contract.input_schema is not None
        assert contract.input_schema["required"] == [LLM_ASTROLOGY_INPUT_V1_KEY]
        assert LLM_ASTROLOGY_INPUT_V1_KEY in contract.input_schema["properties"]


def test_modern_natal_use_case_placeholders_exclude_legacy_carriers() -> None:
    """Les anciens transporteurs restent hors des placeholders natals nominaux."""

    for contract in list_modern_natal_use_case_contracts():
        placeholders = set(contract.required_prompt_placeholders)
        schema_properties = set((contract.input_schema or {}).get("properties", {}))

        assert placeholders.isdisjoint(LEGACY_ASTROLOGY_INPUT_KEYS)
        assert schema_properties.isdisjoint(LEGACY_ASTROLOGY_INPUT_KEYS)


def test_no_natal_prefixed_contract_can_reintroduce_legacy_carriers_as_normal_input() -> None:
    """Un nouveau use case natal ne peut pas redevenir proprietaire des anciens carriers."""

    natal_prefixed_contracts = [
        contract
        for contract in list_canonical_use_case_contracts()
        if contract.key.startswith("natal_")
    ]

    assert natal_prefixed_contracts
    for contract in natal_prefixed_contracts:
        placeholders = set(contract.required_prompt_placeholders)
        schema_required = set((contract.input_schema or {}).get("required", []))

        assert placeholders.isdisjoint(LEGACY_ASTROLOGY_INPUT_KEYS)
        assert schema_required.isdisjoint(LEGACY_ASTROLOGY_INPUT_KEYS)


def test_modern_natal_prompt_rendering_uses_rich_payload_material() -> None:
    """Le rendu final materialise le payload moderne sans ancien transporteur."""

    contract = list_modern_natal_use_case_contracts()[0]
    rich_payload = {
        "contract_id": "llm_astrology_input_v1",
        "facts": {"positions": [{"body": "sun", "sign": "aries"}]},
    }

    rendered = PromptRenderer.render(
        "Astrology input: {{llm_astrology_input_v1}}. Persona: {{persona_name}}.",
        {
            LLM_ASTROLOGY_INPUT_V1_KEY: json.dumps(rich_payload, sort_keys=True),
            "persona_name": "Standard",
        },
        required_variables=contract.required_prompt_placeholders,
        feature="natal",
    )

    assert "llm_astrology_input_v1" in rendered
    assert "aries" in rendered
    assert "chart_json" not in rendered
    assert "natal_data" not in rendered
