"""Canonical prompt catalog.

Transitional source for use-case metadata while legacy compatibility
data remains required by bounded fallback paths.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.domain.llm.prompting import legacy_prompt_runtime as legacy_bridge


class PromptEntry(BaseModel):
    name: str
    description: str
    use_case_key: str
    engine_env_key: str
    max_tokens: int
    temperature: float
    output_schema: dict[str, Any] | None = None
    deprecated: bool = False
    deprecation_note: str | None = None


PROMPT_CATALOG: dict[str, PromptEntry] = {
    key: PromptEntry(use_case_key=key, **entry)
    for key, entry in legacy_bridge.LEGACY_PROMPT_RUNTIME_DATA.items()
}
DEPRECATED_USE_CASE_MAPPING = legacy_bridge.DEPRECATED_USE_CASE_MAPPING
CHAT_RESPONSE_V1 = legacy_bridge.CHAT_RESPONSE_V1
ASTRO_RESPONSE_V1 = legacy_bridge.ASTRO_RESPONSE_V1
ASTRO_RESPONSE_V3 = legacy_bridge.ASTRO_RESPONSE_V3
HOROSCOPE_FREE_OUTPUT_SCHEMA = legacy_bridge.HOROSCOPE_FREE_OUTPUT_SCHEMA
NATAL_FREE_SHORT_SCHEMA = legacy_bridge.NATAL_FREE_SHORT_SCHEMA


def validate_catalog() -> None:
    names = set()
    for key, entry in PROMPT_CATALOG.items():
        if entry.use_case_key != key:
            raise ValueError(
                f"Catalog key '{key}' does not match use_case_key '{entry.use_case_key}'"
            )
        if entry.name in names:
            raise ValueError(f"Duplicate prompt name found: {entry.name}")
        names.add(entry.name)


validate_catalog()


def resolve_model(use_case_key: str, fallback_model: str | None = None) -> str:
    return legacy_bridge.resolve_legacy_model(use_case_key, fallback_model=fallback_model)


def get_legacy_max_tokens(use_case_key: str, *, default_use_case: str | None = None) -> int | None:
    return legacy_bridge.get_legacy_max_tokens(use_case_key, default_use_case=default_use_case)


def get_legacy_prompt_runtime_entry(use_case_key: str) -> dict[str, Any] | None:
    return legacy_bridge.get_legacy_prompt_runtime_entry(use_case_key)


def get_legacy_output_schema(use_case_key: str) -> dict[str, Any] | None:
    return legacy_bridge.get_legacy_output_schema(use_case_key)


def build_legacy_compat_use_case_config(use_case_key: str):
    return legacy_bridge.build_legacy_compat_use_case_config(use_case_key)


__all__ = [
    "ASTRO_RESPONSE_V1",
    "ASTRO_RESPONSE_V3",
    "CHAT_RESPONSE_V1",
    "DEPRECATED_USE_CASE_MAPPING",
    "HOROSCOPE_FREE_OUTPUT_SCHEMA",
    "NATAL_FREE_SHORT_SCHEMA",
    "PROMPT_CATALOG",
    "PromptEntry",
    "build_legacy_compat_use_case_config",
    "get_legacy_output_schema",
    "get_legacy_max_tokens",
    "get_legacy_prompt_runtime_entry",
    "resolve_model",
]
