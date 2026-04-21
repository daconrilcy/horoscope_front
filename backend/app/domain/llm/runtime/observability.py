"""Canonical runtime observability entrypoint."""

from app.domain.llm.runtime.observability_service import (
    compute_input_hash,
    log_call,
    log_governance_event,
    log_legacy_residual_activation,
    log_legacy_residual_blocked_attempt,
    purge_expired_logs,
)

__all__ = [
    "compute_input_hash",
    "log_call",
    "log_governance_event",
    "log_legacy_residual_activation",
    "log_legacy_residual_blocked_attempt",
    "purge_expired_logs",
]
