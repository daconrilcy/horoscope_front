"""Temporary compatibility alias; canonical renderer is prompt_renderer."""

from app.domain.llm.prompting.prompt_renderer import PromptRenderer

__all__ = ["PromptRenderer"]
