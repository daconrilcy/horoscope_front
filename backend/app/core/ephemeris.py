"""Swiss Ephemeris bootstrap and initialization module.

Central initialization point for pyswisseph. State is set once at application
startup (lifespan) and is read-only thereafter — no mutable state per request.

Usage::

    # At app startup (lifespan), if SWISSEPH_ENABLED:
    from app.core import ephemeris
    ephemeris.bootstrap_swisseph(data_path=..., path_version=...)

    # In request handlers:
    result = ephemeris.get_bootstrap_result()
    if result is None or not result.success:
        raise SwissEphInitError(...)
"""

from __future__ import annotations

import logging
import os
import threading

from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

# Global lock to synchronize access to pyswisseph's global state (set_topo, set_sid_mode, etc.)
# Swiss Ephemeris is NOT thread-safe for calls that change the internal engine context.
SWISSEPH_LOCK = threading.Lock()

METRIC_INIT_ERRORS = "swisseph_init_errors_total"
METRIC_DATA_MISSING = "swisseph_data_missing_total"


class EphemerisDataMissingError(Exception):
    """Raised when the Swiss Ephemeris data path is empty or not a valid directory."""

    code = "ephemeris_data_missing"

    def __init__(
        self, message: str = "Swiss Ephemeris data path is not configured or invalid"
    ) -> None:
        self.message = message
        super().__init__(message)


class SwissEphInitError(Exception):
    """Raised when pyswisseph runtime initialization fails."""

    code = "swisseph_init_failed"

    def __init__(
        self, message: str = "Swiss Ephemeris runtime initialization failed"
    ) -> None:
        self.message = message
        super().__init__(message)


class _BootstrapResult:
    __slots__ = ("success", "path_version", "error")

    def __init__(
        self,
        *,
        success: bool,
        path_version: str,
        error: EphemerisDataMissingError | SwissEphInitError | None = None,
    ) -> None:
        self.success = success
        self.path_version = path_version
        self.error = error


_result: _BootstrapResult | None = None


def bootstrap_swisseph(*, data_path: str, path_version: str) -> None:
    """Initialize Swiss Ephemeris and store the result in module state.

    Validates the ephemeris data directory, calls ``swe.set_ephe_path``, and
    records the outcome so request handlers can check it without re-running
    initialization.  Intended to be called exactly once during application
    startup.

    Args:
        data_path: Filesystem path to the Swiss Ephemeris data files directory.
        path_version: Human-readable dataset version identifier (e.g. "se-2024-v1").
                      This value is published in response metadata; the raw path
                      is *never* surfaced to callers.

    Raises:
        EphemerisDataMissingError: ``data_path`` is empty or not a valid directory.
        SwissEphInitError: pyswisseph is not installed or ``swe`` initialization fails.
    """
    global _result  # noqa: PLW0603

    if not path_version or not path_version.strip():
        increment_counter(METRIC_INIT_ERRORS)
        logger.error("swisseph_bootstrap_failed reason=path_version_empty")
        err = SwissEphInitError("Swiss Ephemeris path_version is empty")
        _result = _BootstrapResult(success=False, path_version="", error=err)
        raise err

    if not data_path:
        increment_counter(METRIC_DATA_MISSING)
        logger.error(
            "swisseph_bootstrap_failed reason=data_path_empty path_version=%s",
            path_version,
        )
        err = EphemerisDataMissingError("Swiss Ephemeris data path is empty")
        _result = _BootstrapResult(success=False, path_version=path_version, error=err)
        raise err

    if not os.path.isdir(data_path):
        increment_counter(METRIC_DATA_MISSING)
        logger.error(
            "swisseph_bootstrap_failed reason=data_path_not_found path_version=%s",
            path_version,
        )
        err = EphemerisDataMissingError(
            "Swiss Ephemeris data path does not exist or is not a directory"
        )
        _result = _BootstrapResult(success=False, path_version=path_version, error=err)
        raise err

    try:
        import swisseph as swe  # type: ignore[import-untyped]

        swe.set_ephe_path(data_path)
    except ImportError as exc:
        increment_counter(METRIC_INIT_ERRORS)
        logger.error(
            "swisseph_init_failed reason=module_not_installed path_version=%s",
            path_version,
        )
        err = SwissEphInitError("pyswisseph module is not installed")
        _result = _BootstrapResult(success=False, path_version=path_version, error=err)
        raise err from exc
    except Exception as exc:
        increment_counter(METRIC_INIT_ERRORS)
        logger.error(
            "swisseph_init_failed error_type=%s path_version=%s",
            type(exc).__name__,
            path_version,
        )
        err = SwissEphInitError(
            f"Swiss Ephemeris initialization failed: {type(exc).__name__}"
        )
        _result = _BootstrapResult(success=False, path_version=path_version, error=err)
        raise err from exc

    _result = _BootstrapResult(success=True, path_version=path_version)
    logger.info(
        "swisseph_bootstrap_success path_version=%s",
        path_version,
    )


def get_bootstrap_result() -> _BootstrapResult | None:
    """Return the current bootstrap result, or ``None`` if bootstrap was not called."""
    return _result


def reset_bootstrap_state() -> None:
    """Reset bootstrap state to ``None``.  For testing only."""
    global _result  # noqa: PLW0603
    _result = None
