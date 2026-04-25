from unittest.mock import MagicMock, patch

from app.services.canonical_entitlement.shared.db_consistency_validator import (
    CanonicalEntitlementDbConsistencyError,
)
from scripts.check_canonical_entitlement_db_consistency import main

VALIDATE_PATH_CLI = (
    "app.services.canonical_entitlement.shared.db_consistency_validator"
    ".CanonicalEntitlementDbConsistencyValidator.validate"
)


def test_cli_main_exit_0_on_consistent_db():
    mock_db = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_db)
    mock_ctx.__exit__ = MagicMock(return_value=False)

    with patch("app.infra.db.session.SessionLocal", return_value=mock_ctx):
        with patch(VALIDATE_PATH_CLI):
            assert main() == 0


def test_cli_main_exit_1_on_inconsistent_db():
    mock_db = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_db)
    mock_ctx.__exit__ = MagicMock(return_value=False)

    with patch("app.infra.db.session.SessionLocal", return_value=mock_ctx):
        with patch(
            VALIDATE_PATH_CLI,
            side_effect=CanonicalEntitlementDbConsistencyError("Inconsistent"),
        ):
            assert main() == 1


def test_cli_main_exit_2_on_unexpected_error():
    mock_db = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_db)
    mock_ctx.__exit__ = MagicMock(return_value=False)

    with patch("app.infra.db.session.SessionLocal", return_value=mock_ctx):
        with patch(VALIDATE_PATH_CLI, side_effect=RuntimeError("Unexpected")):
            assert main() == 2
