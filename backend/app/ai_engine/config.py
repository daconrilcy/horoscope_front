"""AI Engine specific configuration."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def _get_int_env(name: str, default: int) -> int:
    """Get integer from environment variable with fallback on parse error."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("invalid_env_var name=%s value=%s using_default=%d", name, value, default)
        return default


def _get_float_env(name: str, default: float) -> float:
    """Get float from environment variable with fallback on parse error."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logger.warning("invalid_env_var name=%s value=%s using_default=%f", name, value, default)
        return default


class AIEngineSettings:
    """Configuration settings for the AI Engine module."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model_default = os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini").strip()
        self.timeout_seconds = _get_int_env("AI_ENGINE_TIMEOUT_SECONDS", 30)
        self.max_retries = _get_int_env("AI_ENGINE_MAX_RETRIES", 2)
        self.context_max_tokens = _get_int_env("AI_ENGINE_CONTEXT_MAX_TOKENS", 4000)
        self.retry_base_delay_ms = _get_int_env("AI_ENGINE_RETRY_BASE_DELAY_MS", 500)
        self.retry_max_delay_ms = _get_int_env("AI_ENGINE_RETRY_MAX_DELAY_MS", 5000)
        self.cost_per_1k_input_tokens = _get_float_env(
            "AI_ENGINE_COST_PER_1K_INPUT_TOKENS", 0.00015
        )
        self.cost_per_1k_output_tokens = _get_float_env(
            "AI_ENGINE_COST_PER_1K_OUTPUT_TOKENS", 0.0006
        )

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)


ai_engine_settings = AIEngineSettings()
