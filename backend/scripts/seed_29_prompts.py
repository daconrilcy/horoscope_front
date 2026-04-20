"""Backward-compatible wrapper toward canonical ops path."""

from app.ops.llm.bootstrap.seed_29_prompts import (  # noqa: F401
    NATAL_COMPLETE_PROMPT,
    NATAL_SHORT_PROMPT,
    PROMPTS_TO_SEED,
    seed_prompts,
)

if __name__ == "__main__":
    seed_prompts()
