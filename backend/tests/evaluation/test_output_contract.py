import json
from pathlib import Path

import pytest

from app.llm_orchestration.seeds.use_cases_seed import ASTRO_RESPONSE_V3_JSON_SCHEMA
from app.llm_orchestration.services.output_validator import validate_schema


@pytest.mark.evaluation
def test_output_contract_validation():
    """
    Validates pre-recorded LLM responses against the real JSON Schema used at runtime.
    """
    fixture_path = Path(__file__).parent / "fixtures" / "llm_responses" / "natal_premium_full.json"
    assert fixture_path.exists(), f"Missing evaluation fixture: {fixture_path}"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = validate_schema(data, ASTRO_RESPONSE_V3_JSON_SCHEMA)
    assert result.valid, f"LLM response fixture does not match runtime contract: {result.errors}"

@pytest.mark.evaluation
def test_output_contract_invalid_fixture():
    """Checks that validation fails for corrupted fixtures against the real schema."""
    invalid_data = {"wrong_key": "oops"}
    result = validate_schema(invalid_data, ASTRO_RESPONSE_V3_JSON_SCHEMA)
    assert not result.valid
    assert result.errors
