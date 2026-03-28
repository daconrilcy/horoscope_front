from unittest.mock import patch

import pytest

from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
)
from app.startup.feature_scope_validation import run_feature_scope_startup_validation

VALIDATE_PATH = (
    "app.startup.feature_scope_validation.FeatureRegistryConsistencyValidator.validate"
)


def test_startup_validation_strict_ok():
    """Mode strict with success: no error, startup continues."""
    with patch(VALIDATE_PATH) as mock_validate:
        run_feature_scope_startup_validation("strict")
        mock_validate.assert_called_once()


def test_startup_validation_strict_fails():
    """Mode strict with failure: error is raised, blocking startup."""
    with patch(
        VALIDATE_PATH, side_effect=FeatureRegistryConsistencyError(["test error"])
    ) as mock_validate:
        with pytest.raises(FeatureRegistryConsistencyError):
            run_feature_scope_startup_validation("strict")
        mock_validate.assert_called_once()


def test_startup_validation_warn_does_not_block():
    """Mode warn with failure: error is logged but not raised."""
    with patch(
        VALIDATE_PATH, side_effect=FeatureRegistryConsistencyError(["test error"])
    ) as mock_validate:
        # Should NOT raise
        run_feature_scope_startup_validation("warn")
        mock_validate.assert_called_once()


def test_startup_validation_off_skips_validator():
    """Mode off: validator is not even called."""
    with patch(VALIDATE_PATH) as mock_validate:
        run_feature_scope_startup_validation("off")
        mock_validate.assert_not_called()


def test_startup_validation_invalid_mode_falls_back_to_strict():
    """Invalid mode: fallback to strict (failure blocks)."""
    with patch(
        VALIDATE_PATH, side_effect=FeatureRegistryConsistencyError(["test error"])
    ) as mock_validate:
        with pytest.raises(FeatureRegistryConsistencyError):
            run_feature_scope_startup_validation("invalid_mode")
        mock_validate.assert_called_once()
