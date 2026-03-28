from unittest.mock import patch

from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
)
from scripts.check_feature_scope_registry import main

VALIDATE_PATH_CLI = (
    "app.services.feature_registry_consistency_validator"
    ".FeatureRegistryConsistencyValidator.validate"
)


def test_cli_main_exit_0_on_consistent_registry():
    """Main should return 0 if validation passes."""
    with patch(VALIDATE_PATH_CLI):
        assert main() == 0


def test_cli_main_exit_1_on_inconsistent_registry():
    """Main should return 1 if validation fails."""
    with patch(
        VALIDATE_PATH_CLI,
        side_effect=FeatureRegistryConsistencyError(["test error"]),
    ):
        assert main() == 1
