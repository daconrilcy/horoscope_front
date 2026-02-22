"""AI Engine specific configuration."""

from __future__ import annotations

import os


class AIEngineSettings:
    """Configuration settings for the AI Engine module."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model_default = os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini").strip()
        self.timeout_seconds = int(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "30"))
        self.max_retries = int(os.getenv("AI_ENGINE_MAX_RETRIES", "2"))
        self.context_max_tokens = int(os.getenv("AI_ENGINE_CONTEXT_MAX_TOKENS", "4000"))
        self.retry_base_delay_ms = int(os.getenv("AI_ENGINE_RETRY_BASE_DELAY_MS", "500"))
        self.retry_max_delay_ms = int(os.getenv("AI_ENGINE_RETRY_MAX_DELAY_MS", "5000"))
        self.cost_per_1k_input_tokens = float(
            os.getenv("AI_ENGINE_COST_PER_1K_INPUT_TOKENS", "0.00015")
        )
        self.cost_per_1k_output_tokens = float(
            os.getenv("AI_ENGINE_COST_PER_1K_OUTPUT_TOKENS", "0.0006")
        )

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)


ai_engine_settings = AIEngineSettings()
