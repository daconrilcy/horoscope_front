from __future__ import annotations

import logging

import pytest


@pytest.fixture(autouse=True)
def _reset_global_logging_disable() -> None:
    # Some tests may globally disable logging; restore default behavior.
    logging.disable(logging.NOTSET)
