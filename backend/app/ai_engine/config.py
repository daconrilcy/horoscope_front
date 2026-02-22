"""AI Engine specific configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIEngineSettings(BaseSettings):
    """Configuration settings for the AI Engine module."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model_default: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL_DEFAULT")
    timeout_seconds: int = Field(default=30, alias="AI_ENGINE_TIMEOUT_SECONDS")
    max_retries: int = Field(default=2, alias="AI_ENGINE_MAX_RETRIES")
    context_max_tokens: int = Field(default=4000, alias="AI_ENGINE_CONTEXT_MAX_TOKENS")
    retry_base_delay_ms: int = Field(default=500, alias="AI_ENGINE_RETRY_BASE_DELAY_MS")
    retry_max_delay_ms: int = Field(default=5000, alias="AI_ENGINE_RETRY_MAX_DELAY_MS")
    cost_per_1k_input_tokens: float = Field(
        default=0.00015, alias="AI_ENGINE_COST_PER_1K_INPUT_TOKENS"
    )
    cost_per_1k_output_tokens: float = Field(
        default=0.0006, alias="AI_ENGINE_COST_PER_1K_OUTPUT_TOKENS"
    )

    rate_limit_per_min: int = Field(default=30, alias="AI_ENGINE_RATE_LIMIT_PER_MIN")
    rate_limit_enabled: bool = Field(default=True, alias="AI_ENGINE_RATE_LIMIT_ENABLED")

    cache_enabled: bool = Field(default=False, alias="AI_ENGINE_CACHE_ENABLED")
    cache_ttl_seconds: int = Field(default=3600, alias="AI_ENGINE_CACHE_TTL_SECONDS")

    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)

    @property
    def is_redis_configured(self) -> bool:
        """Check if Redis URL is configured."""
        return bool(self.redis_url)


@lru_cache
def get_ai_engine_settings() -> AIEngineSettings:
    """Get cached AI Engine settings instance."""
    return AIEngineSettings()


ai_engine_settings = get_ai_engine_settings()
