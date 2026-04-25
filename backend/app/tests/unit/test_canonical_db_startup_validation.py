from unittest.mock import MagicMock, patch

import pytest

from app.services.canonical_entitlement.shared.db_consistency_validator import (
    CanonicalEntitlementDbConsistencyError,
)
from app.startup.canonical_db_validation import run_canonical_db_startup_validation

VALIDATE_PATH = (
    "app.startup.canonical_db_validation.CanonicalEntitlementDbConsistencyValidator.validate"
)


def test_startup_db_validation_strict_ok():
    db = MagicMock()
    with patch(VALIDATE_PATH) as mock_validate:
        run_canonical_db_startup_validation("strict", db)
        mock_validate.assert_called_once_with(db)


def test_startup_db_validation_strict_fails():
    db = MagicMock()
    with patch(
        VALIDATE_PATH,
        side_effect=CanonicalEntitlementDbConsistencyError("Fail"),
    ):
        with pytest.raises(CanonicalEntitlementDbConsistencyError):
            run_canonical_db_startup_validation("strict", db)


def test_startup_db_validation_warn_does_not_block():
    db = MagicMock()
    with patch(
        VALIDATE_PATH,
        side_effect=CanonicalEntitlementDbConsistencyError("Fail"),
    ):
        run_canonical_db_startup_validation("warn", db)


def test_startup_db_validation_off_skips_validator():
    db = MagicMock()
    with patch(VALIDATE_PATH) as mock_validate:
        run_canonical_db_startup_validation("off", db)
        mock_validate.assert_not_called()


def test_startup_db_validation_invalid_mode_falls_back_to_strict():
    db = MagicMock()
    with patch(VALIDATE_PATH) as mock_validate:
        run_canonical_db_startup_validation("invalid", db)
        mock_validate.assert_called_once_with(db)
