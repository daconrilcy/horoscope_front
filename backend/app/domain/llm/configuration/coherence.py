"""Canonical coherence validation entrypoint."""

from app.domain.llm.configuration.config_coherence_validator import (
    CoherenceError,
    ConfigCoherenceValidator,
    validate_execution_profile,
)

__all__ = ["CoherenceError", "ConfigCoherenceValidator", "validate_execution_profile"]
