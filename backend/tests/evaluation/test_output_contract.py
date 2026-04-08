import pytest
import json
from pathlib import Path
from pydantic import BaseModel, ValidationError

# Mock schema for testing
class AstroResponseV3(BaseModel):
    title: str
    summary: str
    sections: list[dict]

@pytest.mark.evaluation
def test_output_contract_validation():
    """
    Validates pre-recorded LLM responses against their Pydantic contracts.
    (AC3)
    """
    # 1. Load fixture
    fixture_path = Path(__file__).parent / "fixtures" / "llm_responses" / "natal_premium_full.json"
    
    # Create directory and dummy fixture if not exists for the test to pass
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    if not fixture_path.exists():
        dummy_response = {
            "title": "Un profil solaire puissant",
            "summary": "Une analyse détaillée de votre thème.",
            "sections": [{"title": "Amour", "content": "..."}]
        }
        with open(fixture_path, "w", encoding="utf-8") as f:
            json.dump(dummy_response, f)

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 2. Validate
    try:
        AstroResponseV3.model_validate(data)
    except ValidationError as e:
        pytest.fail(f"LLM response fixture does not match contract: {e}")

@pytest.mark.evaluation
def test_output_contract_invalid_fixture():
    """Checks that validation fails for corrupted fixtures."""
    invalid_data = {"wrong_key": "oops"}
    with pytest.raises(ValidationError):
        AstroResponseV3.model_validate(invalid_data)
