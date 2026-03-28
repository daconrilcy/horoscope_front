import logging

from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
    FeatureRegistryConsistencyValidator,
)

logger = logging.getLogger(__name__)

_VALID_MODES = frozenset({"strict", "warn", "off"})


def run_feature_scope_startup_validation(mode: str) -> None:
    """Run feature scope registry validation at application startup.

    strict -> failure blocks startup
    warn   -> failure is logged but startup continues
    off    -> validation skipped explicitly
    """
    if mode not in _VALID_MODES:
        logger.warning(
            "feature_scope_registry_startup_validation_invalid_mode mode=%s fallback=strict",
            mode,
        )
        mode = "strict"

    if mode == "off":
        logger.warning("feature_scope_registry_startup_validation_disabled")
        return

    try:
        FeatureRegistryConsistencyValidator.validate()
        logger.info("feature_scope_registry_startup_validation_ok")
    except FeatureRegistryConsistencyError as exc:
        logger.error(
            "feature_scope_registry_startup_validation_failed errors=%s",
            exc,
        )
        if mode == "strict":
            raise
