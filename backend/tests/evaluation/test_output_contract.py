import json
from pathlib import Path

import pytest

from app.llm_orchestration.seeds.use_cases_seed import ASTRO_RESPONSE_V3_JSON_SCHEMA
from app.llm_orchestration.services.output_validator import validate_schema


@pytest.mark.evaluation
@pytest.mark.parametrize("feature", ["natal", "horoscope_daily", "daily_prediction"])
@pytest.mark.parametrize("quality", ["full", "minimal"])
def test_output_contract_validation(feature, quality):
    """
    Validates pre-recorded LLM responses against the real JSON Schema used at runtime.
    (Story 66.24: extended to daily paths and both qualities)
    """
    from app.llm_orchestration.narrator_contract import NARRATOR_OUTPUT_SCHEMA

    schema = ASTRO_RESPONSE_V3_JSON_SCHEMA if feature == "natal" else NARRATOR_OUTPUT_SCHEMA
    fixture_name = f"{feature}_premium_{quality}.json"
    fixture_path = Path(__file__).parent / "fixtures" / "llm_responses" / fixture_name
    assert fixture_path.exists(), f"Missing evaluation fixture: {fixture_path}"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = validate_schema(data, schema)
    assert result.valid, f"LLM response fixture for {feature}/{quality} does not match runtime contract: {result.errors}"


@pytest.mark.evaluation
def test_output_contract_invalid_fixture():
    """Checks that validation fails for corrupted fixtures against the real schema."""
    invalid_data = {"wrong_key": "oops"}
    result = validate_schema(invalid_data, ASTRO_RESPONSE_V3_JSON_SCHEMA)
    assert not result.valid
    assert result.errors
