import json
from pathlib import Path

import pytest

from app.llm_orchestration.seeds.use_cases_seed import ASTRO_RESPONSE_V3_JSON_SCHEMA
from app.llm_orchestration.services.output_validator import validate_schema


@pytest.mark.evaluation
@pytest.mark.parametrize(
    "feature,plan,quality",
    [
        ("natal", "premium", "full"),
        ("natal", "premium", "minimal"),
        ("natal", "free", "minimal"),
        ("horoscope_daily", "premium", "full"),
        ("horoscope_daily", "premium", "minimal"),
        ("horoscope_daily", "free", "partial"),
        ("horoscope_daily", "free", "minimal"),
    ],
)
def test_output_contract_validation(feature, plan, quality):
    """
    Validates pre-recorded LLM responses against the real JSON Schema used at runtime.
    (Story 66.24: extended to daily paths, free plans and degraded modes)
    """
    from app.llm_orchestration.narrator_contract import NARRATOR_OUTPUT_SCHEMA

    # Schema selection logic based on feature and plan
    if feature == "natal":
        if plan == "premium":
            schema = ASTRO_RESPONSE_V3_JSON_SCHEMA
        else:
            # For free natal, we use AstroFreeResponseV1 schema (Story 64.3)
            # We fetch it from app.llm_orchestration.schemas as it might not be in seeds
            from app.llm_orchestration.schemas import AstroFreeResponseV1

            schema = AstroFreeResponseV1.model_json_schema()
    else:
        # daily paths currently share the same narrator schema
        schema = NARRATOR_OUTPUT_SCHEMA

    fixture_name = f"{feature}_{plan}_{quality}.json"
    fixture_path = Path(__file__).parent / "fixtures" / "llm_responses" / fixture_name
    assert fixture_path.exists(), f"Missing evaluation fixture: {fixture_path}"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = validate_schema(data, schema)
    assert result.valid, (
        f"LLM response fixture for {feature}/{plan}/{quality} "
        f"does not match runtime contract: {result.errors}"
    )


@pytest.mark.evaluation
def test_output_contract_invalid_fixture():
    """Checks that validation fails for corrupted fixtures against the real schema."""
    invalid_data = {"wrong_key": "oops"}
    result = validate_schema(invalid_data, ASTRO_RESPONSE_V3_JSON_SCHEMA)
    assert not result.valid
    assert result.errors
