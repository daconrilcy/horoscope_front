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


def test_startup_validation_strict_ok_logs_success(caplog: pytest.LogCaptureFixture) -> None:
    with patch(VALIDATE_PATH):
        with caplog.at_level("INFO"):
            run_feature_scope_startup_validation("strict")

    assert "feature_scope_registry_startup_validation_ok" in caplog.text


def test_startup_validation_strict_fails(caplog: pytest.LogCaptureFixture) -> None:
    """Mode strict with failure: error is raised, blocking startup."""
    with patch(
        VALIDATE_PATH, side_effect=FeatureRegistryConsistencyError(["test error"])
    ) as mock_validate:
        with caplog.at_level("ERROR"):
            with pytest.raises(FeatureRegistryConsistencyError):
                run_feature_scope_startup_validation("strict")
        mock_validate.assert_called_once()

    assert "feature_scope_registry_startup_validation_failed" in caplog.text
    assert "test error" in caplog.text


def test_startup_validation_warn_does_not_block(caplog: pytest.LogCaptureFixture) -> None:
    """Mode warn with failure: error is logged but not raised."""
    with patch(
        VALIDATE_PATH, side_effect=FeatureRegistryConsistencyError(["test error"])
    ) as mock_validate:
        with caplog.at_level("ERROR"):
            run_feature_scope_startup_validation("warn")
        mock_validate.assert_called_once()

    assert "feature_scope_registry_startup_validation_failed" in caplog.text


def test_startup_validation_off_skips_validator(caplog: pytest.LogCaptureFixture) -> None:
    """Mode off: validator is not even called."""
    with patch(VALIDATE_PATH) as mock_validate:
        with caplog.at_level("WARNING"):
            run_feature_scope_startup_validation("off")
        mock_validate.assert_not_called()

    assert "feature_scope_registry_startup_validation_disabled" in caplog.text


def test_startup_validation_invalid_mode_falls_back_to_strict(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Invalid mode: fallback to strict (failure blocks)."""
    with patch(
        VALIDATE_PATH, side_effect=FeatureRegistryConsistencyError(["test error"])
    ) as mock_validate:
        with caplog.at_level("WARNING"):
            with pytest.raises(FeatureRegistryConsistencyError):
                run_feature_scope_startup_validation("invalid_mode")
        mock_validate.assert_called_once()

    assert "feature_scope_registry_startup_validation_invalid_mode" in caplog.text
