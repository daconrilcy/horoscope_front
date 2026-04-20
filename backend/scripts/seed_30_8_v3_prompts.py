"""Backward-compatible wrapper toward canonical ops path."""

from app.ops.llm.bootstrap.seed_30_8_v3_prompts import (  # noqa: F401
    ALL_PROMPT_CONFIGS,
    GPT5_V3_CONFIG,
    LINT_REQUIRED_PLACEHOLDERS,
    NATAL_COMPLETE_PROMPT_V3,
    THEMATIC_PROMPT_CONFIGS,
    seed,
)

if __name__ == "__main__":
    seed()
