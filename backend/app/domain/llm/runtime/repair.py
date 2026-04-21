"""Canonical runtime repair entrypoint."""

from app.domain.llm.runtime.repair_prompter import build_repair_prompt

__all__ = ["build_repair_prompt"]
