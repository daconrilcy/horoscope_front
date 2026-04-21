"""Canonical active prompt version lookup entrypoint."""

from app.domain.llm.configuration.prompt_version_lookup import get_active_prompt_version

__all__ = ["get_active_prompt_version"]
