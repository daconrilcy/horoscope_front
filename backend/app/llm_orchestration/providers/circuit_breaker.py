import time
from enum import Enum
from typing import Dict


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Sliding window Circuit Breaker implementation.
    States:
    - CLOSED: Requests are allowed. Failures within a time window increment a counter.
    - OPEN: Requests are blocked for a cooldown period.
    - HALF_OPEN: A single probe request is allowed to check if the upstream is healthy.
    """

    def __init__(self, failure_threshold: int, recovery_timeout_sec: int, window_sec: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.window_sec = window_sec
        self.state = CircuitBreakerState.CLOSED
        self.failure_timestamps: list[float] = []
        self.last_failure_time = 0.0
        self._probe_in_flight = False

    def _clean_old_failures(self) -> None:
        """Remove failures older than the sliding window."""
        now = time.monotonic()
        self.failure_timestamps = [
            ts for ts in self.failure_timestamps if now - ts <= self.window_sec
        ]

    def allow_request(self) -> bool:
        """Check if a request should be allowed based on the breaker state."""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if time.monotonic() - self.last_failure_time > self.recovery_timeout_sec:
                self.state = CircuitBreakerState.HALF_OPEN
                self._probe_in_flight = True
                return True
            return False

        if self.state == CircuitBreakerState.HALF_OPEN:
            # If a probe is already in flight, block others to avoid flooding
            if self._probe_in_flight:
                return False
            self._probe_in_flight = True
            return True

        return False

    def record_success(self) -> None:
        """Reset failures and close the breaker on success."""
        self.failure_timestamps = []
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = 0.0
        self._probe_in_flight = False

    def record_failure(self) -> None:
        """Increment failures and open the breaker if threshold reached within window."""
        now = time.monotonic()
        self.failure_timestamps.append(now)
        self._clean_old_failures()
        self._probe_in_flight = False

        if len(self.failure_timestamps) >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_failure_time = now


_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    provider: str, family: str, failure_threshold: int, recovery_timeout_sec: int
) -> CircuitBreaker:
    """Get or create a circuit breaker for the given provider and family."""
    key = f"{provider}:{family}"
    if key not in _breakers:
        _breakers[key] = CircuitBreaker(failure_threshold, recovery_timeout_sec)
    return _breakers[key]
