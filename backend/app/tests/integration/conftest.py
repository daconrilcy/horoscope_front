from __future__ import annotations

import pytest

from app.core.rate_limit import reset_rate_limits


@pytest.fixture(autouse=True)
def reset_rate_limits_fixture() -> None:
    reset_rate_limits()
