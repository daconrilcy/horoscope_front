"""Bootstrap entrypoint for LLM natal v3 prompt seed."""

from __future__ import annotations


def seed() -> None:
    # Lazy import keeps startup modules decoupled from script paths.
    from scripts.seed_30_8_v3_prompts import seed as _seed

    _seed()
