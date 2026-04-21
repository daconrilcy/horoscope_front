"""Legacy shim for prompt renderer; canonical implementation lives in domain."""

from app.domain.llm.prompting.prompt_renderer import PromptRenderer

__all__ = ["PromptRenderer"]
