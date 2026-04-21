"""Canonical runtime policy entrypoint."""

from app.domain.llm.runtime.hard_policy import get_hard_policy

__all__ = ["get_hard_policy"]
