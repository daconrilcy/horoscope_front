from __future__ import annotations

import os

import pytest

from app.core.rate_limit import reset_rate_limits

# Keep reference-data seed integration flows deterministic without manual shell exports.
os.environ.setdefault("REFERENCE_SEED_ADMIN_TOKEN", "test-seed-token")
os.environ.setdefault("ENABLE_REFERENCE_SEED_ADMIN_FALLBACK", "1")


@pytest.fixture(autouse=True)
def _reset_in_memory_rate_limits() -> None:
    # Integration tests share the same process-wide in-memory limiter.
    # Reset between tests to avoid cross-test 429 leakage.
    reset_rate_limits()
