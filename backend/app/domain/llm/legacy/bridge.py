"""Single explicit nominal -> legacy bridge."""

from app.llm_orchestration.legacy_prompt_runtime import (
    ASTRO_RESPONSE_V1,
    ASTRO_RESPONSE_V3,
    CHAT_RESPONSE_V1,
    DEPRECATED_USE_CASE_MAPPING,
    HOROSCOPE_FREE_OUTPUT_SCHEMA,
    LEGACY_PROMPT_RUNTIME_DATA,
    NATAL_FREE_SHORT_SCHEMA,
    build_legacy_compat_use_case_config,
    get_legacy_max_tokens,
    get_legacy_output_schema,
    get_legacy_prompt_runtime_entry,
    get_legacy_use_case_name,
    resolve_legacy_model,
)

__all__ = [
    "ASTRO_RESPONSE_V1",
    "ASTRO_RESPONSE_V3",
    "CHAT_RESPONSE_V1",
    "DEPRECATED_USE_CASE_MAPPING",
    "HOROSCOPE_FREE_OUTPUT_SCHEMA",
    "LEGACY_PROMPT_RUNTIME_DATA",
    "NATAL_FREE_SHORT_SCHEMA",
    "build_legacy_compat_use_case_config",
    "get_legacy_max_tokens",
    "get_legacy_output_schema",
    "get_legacy_prompt_runtime_entry",
    "get_legacy_use_case_name",
    "resolve_legacy_model",
]
