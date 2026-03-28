import logging

from sqlalchemy.orm import Session

from app.services.canonical_entitlement_db_consistency_validator import (
    CanonicalEntitlementDbConsistencyError,
    CanonicalEntitlementDbConsistencyValidator,
)

logger = logging.getLogger(__name__)
_VALID_MODES = frozenset({"strict", "warn", "off"})


def run_canonical_db_startup_validation(mode: str, db: Session) -> None:
    if mode not in _VALID_MODES:
        logger.warning("canonical_db_startup_validation_invalid_mode mode=%s fallback=strict", mode)
        mode = "strict"

    if mode == "off":
        logger.warning("canonical_db_startup_validation_disabled")
        return

    try:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
        logger.info("canonical_db_startup_validation_ok")
    except CanonicalEntitlementDbConsistencyError as exc:
        logger.error("canonical_db_startup_validation_failed errors=%s", exc)
        if mode == "strict":
            raise
