"""Backward-compatible wrapper toward canonical ops path."""

from app.ops.llm.bootstrap.seed_30_14_chat_prompt import (  # noqa: F401
    CHAT_ASTROLOGER_PROMPT_V3,
    seed,
)

if __name__ == "__main__":
    seed()
