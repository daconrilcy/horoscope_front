"""Bootstrap entrypoint for LLM prompt seed 29."""

from __future__ import annotations


def seed_prompts() -> None:
    # Lazy import keeps startup modules decoupled from script paths.
    from scripts.seed_29_prompts import seed_prompts as _seed_prompts

    _seed_prompts()
