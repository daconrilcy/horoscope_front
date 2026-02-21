from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil
from threading import Lock
from time import monotonic


@dataclass
class RateLimitError(Exception):
    code: str
    message: str
    details: dict[str, str]
    status_code: int = 429


_WINDOWS: defaultdict[str, deque[float]] = defaultdict(deque)
_LOCK = Lock()


def _utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_rate_limit(*, key: str, limit: int, window_seconds: int) -> None:
    now = monotonic()
    with _LOCK:
        bucket = _WINDOWS[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            elapsed = now - bucket[0] if bucket else 0.0
            retry_after_seconds = max(1, ceil(window_seconds - elapsed))
            raise RateLimitError(
                code="rate_limit_exceeded",
                message="rate limit exceeded",
                details={
                    "key": key,
                    "limit": str(limit),
                    "window_seconds": str(window_seconds),
                    "retry_after": str(retry_after_seconds),
                    "timestamp": _utc_iso_now(),
                },
            )
        bucket.append(now)


def reset_rate_limits() -> None:
    with _LOCK:
        _WINDOWS.clear()
