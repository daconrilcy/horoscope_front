"""Expose la surface publique nominale du runtime LLM sans forcer les imports lourds."""

from __future__ import annotations

from typing import Any

__all__ = ["AIEngineAdapter", "AIEngineAdapterError"]


def __getattr__(name: str) -> Any:
    """Charge paresseusement la facade publique pour eviter les cycles de package."""
    if name == "AIEngineAdapter":
        from app.domain.llm.runtime.adapter import AIEngineAdapter

        return AIEngineAdapter
    if name == "AIEngineAdapterError":
        from app.domain.llm.runtime.adapter_errors import AIEngineAdapterError

        return AIEngineAdapterError
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
