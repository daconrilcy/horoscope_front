"""Unit tests for the prompt catalog."""

from unittest.mock import MagicMock

import pytest

from app.prompts.catalog import PROMPT_CATALOG, PromptEntry
from app.prompts.exceptions import ConfigurationError
from app.prompts.validators import validate_catalog_vs_db


def test_catalog_contains_expected_use_cases() -> None:
    """Test that PROMPT_CATALOG contains the core required use cases."""
    expected_keys = {
        "guidance_daily",
        "guidance_weekly",
        "guidance_contextual",
        "natal_interpretation",
        "chat_astrologer",
    }
    for key in expected_keys:
        assert key in PROMPT_CATALOG
        assert isinstance(PROMPT_CATALOG[key], PromptEntry)

def test_catalog_names_are_unique() -> None:
    """Test that all prompt names in the catalog are unique."""
    names = [entry.name for entry in PROMPT_CATALOG.values()]
    assert len(names) == len(set(names))

def test_validate_catalog_vs_db_success() -> None:
    """Test that validation passes when all DB use cases are in catalog."""
    mock_db = MagicMock()
    # Mock db.execute(stmt).scalars().all()
    mock_uc1 = MagicMock()
    mock_uc1.key = "guidance_daily"
    mock_uc2 = MagicMock()
    mock_uc2.key = "chat_astrologer"
    
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_uc1, mock_uc2]
    
    # Should not raise
    validate_catalog_vs_db(mock_db)

def test_validate_catalog_vs_db_failure() -> None:
    """Test that validation fails when a DB use case is missing from catalog."""
    mock_db = MagicMock()
    mock_uc = MagicMock()
    mock_uc.key = "non_existent_use_case"
    
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_uc]
    
    with pytest.raises(ConfigurationError) as exc_info:
        validate_catalog_vs_db(mock_db)
    
    assert "Database use cases missing from Python catalog" in str(exc_info.value)
    assert "non_existent_use_case" in str(exc_info.value)
