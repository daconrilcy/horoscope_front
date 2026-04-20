"""Single explicit nominal -> legacy bridge."""

from app.llm_orchestration.legacy_prompt_runtime import (
    DEPRECATED_USE_CASE_MAPPING,
    build_legacy_compat_use_case_config,
    get_legacy_max_tokens,
    get_legacy_output_schema,
    get_legacy_prompt_runtime_entry,
    get_legacy_use_case_name,
    resolve_legacy_model,
)

__all__ = [
    "DEPRECATED_USE_CASE_MAPPING",
    "build_legacy_compat_use_case_config",
    "get_legacy_max_tokens",
    "get_legacy_output_schema",
    "get_legacy_prompt_runtime_entry",
    "get_legacy_use_case_name",
    "resolve_legacy_model",
]
