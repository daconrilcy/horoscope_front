"""Bootstrap entrypoint for LLM chat prompt seed."""

from __future__ import annotations


def seed() -> None:
    # Lazy import keeps startup modules decoupled from script paths.
    from scripts.seed_30_14_chat_prompt import seed as _seed

    _seed()
