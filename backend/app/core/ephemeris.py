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
from hashlib import sha256
from pathlib import Path

from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

# Global lock to synchronize access to pyswisseph's global state (set_topo, set_sid_mode, etc.)
# Swiss Ephemeris is NOT thread-safe for calls that change the internal engine context.
SWISSEPH_LOCK = threading.Lock()

METRIC_INIT_ERRORS = "swisseph_init_errors_total"
METRIC_DATA_MISSING = "swisseph_data_missing_total"
METRIC_ERRORS = "swisseph_errors_total"


class EphemerisDataMissingError(Exception):
    """Raised when the Swiss Ephemeris data path is empty or not a valid directory."""

    code = "ephemeris_data_missing"

    def __init__(
        self,
        message: str = "Swiss Ephemeris data path is not configured or invalid",
        missing_file: str | None = None,
    ) -> None:
        self.message = message
        self.missing_file = missing_file
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
    __slots__ = ("success", "path_version", "path_hash", "error")

    def __init__(
        self,
        *,
        success: bool,
        path_version: str,
        path_hash: str = "",
        error: EphemerisDataMissingError | SwissEphInitError | None = None,
    ) -> None:
        self.success = success
        self.path_version = path_version
        self.path_hash = path_hash
        self.error = error


_result: _BootstrapResult | None = None

DEFAULT_REQUIRED_FILES: tuple[str, ...] = (
    "seas_18.se1",
    "semo_18.se1",
    "sepl_18.se1",
    "seas_24.se1",
    "semo_24.se1",
    "sepl_24.se1",
)


def _compute_file_sha256(file_path: Path) -> str:
    digest = sha256()
    with file_path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _compute_ephemeris_path_hash(*, data_path: str, required_files: list[str]) -> str:
    """Compute a deterministic hash from required ephemeris files only."""
    digest = sha256()
    base_path = Path(data_path)

    for filename in sorted(required_files):
        file_path = base_path / filename
        if not file_path.is_file():
            raise EphemerisDataMissingError(
                f"Swiss Ephemeris required file is missing: {filename}",
                missing_file=filename,
            )
        file_hash = _compute_file_sha256(file_path)
        stat = file_path.stat()
        digest.update(filename.encode("utf-8"))
        digest.update(b":")
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(b":")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")

    return digest.hexdigest()


def _resolve_required_files(
    *,
    required_files: list[str] | None,
) -> list[str]:
    if required_files:
        return [item.strip() for item in required_files if item and item.strip()]
    return list(DEFAULT_REQUIRED_FILES)


def bootstrap_swisseph(
    *,
    data_path: str,
    path_version: str,
    expected_path_hash: str = "",
    required_files: list[str] | None = None,
    validate_required_files: bool = False,
) -> None:
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
        increment_counter(f"{METRIC_ERRORS}|code=swisseph_init_failed")
        logger.error("swisseph_bootstrap_failed reason=path_version_empty")
        err = SwissEphInitError("Swiss Ephemeris path_version is empty")
        _result = _BootstrapResult(success=False, path_version="", path_hash="", error=err)
        raise err

    normalized_data_path = data_path.strip()
    normalized_expected_hash = expected_path_hash.strip().lower()

    if not normalized_data_path:
        increment_counter(METRIC_DATA_MISSING)
        increment_counter(f"{METRIC_ERRORS}|code=ephemeris_data_missing")
        logger.error(
            "swisseph_bootstrap_failed reason=data_path_empty path_version=%s",
            path_version,
        )
        err = EphemerisDataMissingError("Swiss Ephemeris data path is empty")
        _result = _BootstrapResult(
            success=False,
            path_version=path_version,
            path_hash="",
            error=err,
        )
        raise err

    if not os.path.isdir(normalized_data_path):
        increment_counter(METRIC_DATA_MISSING)
        increment_counter(f"{METRIC_ERRORS}|code=ephemeris_data_missing")
        logger.error(
            "swisseph_bootstrap_failed reason=data_path_not_found path_version=%s",
            path_version,
        )
        err = EphemerisDataMissingError(
            "Swiss Ephemeris data path does not exist or is not a directory"
        )
        _result = _BootstrapResult(
            success=False,
            path_version=path_version,
            path_hash="",
            error=err,
        )
        raise err

    resolved_required_files = _resolve_required_files(required_files=required_files)
    computed_path_hash = ""

    if validate_required_files:
        try:
            computed_path_hash = _compute_ephemeris_path_hash(
                data_path=normalized_data_path,
                required_files=resolved_required_files,
            )
        except EphemerisDataMissingError as err:
            increment_counter(METRIC_DATA_MISSING)
            increment_counter(f"{METRIC_ERRORS}|code=ephemeris_data_missing")
            logger.error(
                "swisseph_bootstrap_failed reason=required_files_missing path_version=%s",
                path_version,
            )
            _result = _BootstrapResult(
                success=False, path_version=path_version, path_hash="", error=err
            )
            raise

        if normalized_expected_hash and computed_path_hash != normalized_expected_hash:
            increment_counter(METRIC_INIT_ERRORS)
            increment_counter(f"{METRIC_ERRORS}|code=swisseph_init_failed")
            logger.error(
                "swisseph_bootstrap_failed reason=path_hash_mismatch path_version=%s",
                path_version,
            )
            err = SwissEphInitError("Swiss Ephemeris path hash mismatch")
            _result = _BootstrapResult(
                success=False, path_version=path_version, path_hash=computed_path_hash, error=err
            )
            raise err
    elif normalized_expected_hash:
        computed_path_hash = normalized_expected_hash

    try:
        import swisseph as swe  # type: ignore[import-untyped]

        swe.set_ephe_path(normalized_data_path)
    except ImportError as exc:
        increment_counter(METRIC_INIT_ERRORS)
        increment_counter(f"{METRIC_ERRORS}|code=swisseph_init_failed")
        logger.error(
            "swisseph_init_failed reason=module_not_installed path_version=%s",
            path_version,
        )
        err = SwissEphInitError("pyswisseph module is not installed")
        _result = _BootstrapResult(
            success=False, path_version=path_version, path_hash=computed_path_hash, error=err
        )
        raise err from exc
    except Exception as exc:
        increment_counter(METRIC_INIT_ERRORS)
        increment_counter(f"{METRIC_ERRORS}|code=swisseph_init_failed")
        logger.error(
            "swisseph_init_failed error_type=%s path_version=%s",
            type(exc).__name__,
            path_version,
        )
        err = SwissEphInitError(
            f"Swiss Ephemeris initialization failed: {type(exc).__name__}"
        )
        _result = _BootstrapResult(
            success=False, path_version=path_version, path_hash=computed_path_hash, error=err
        )
        raise err from exc

    _result = _BootstrapResult(
        success=True,
        path_version=path_version,
        path_hash=computed_path_hash,
    )
    logger.info(
        "swisseph_bootstrap_success path_version=%s path_hash=%s",
        path_version,
        computed_path_hash or "unset",
    )


def get_bootstrap_result() -> _BootstrapResult | None:
    """Return the current bootstrap result, or ``None`` if bootstrap was not called."""
    return _result


def reset_bootstrap_state() -> None:
    """Reset bootstrap state to ``None``.  For testing only."""
    global _result  # noqa: PLW0603
    _result = None
