"""Centralized prompt catalog."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.domain.llm.legacy import bridge as legacy_bridge


class PromptEntry(BaseModel):
    """Metadata for a prompt use case."""

    name: str  # Unique human-readable name
    description: str  # Short description
    use_case_key: str  # Use case identifier (key in PROMPT_CATALOG)
    engine_env_key: str  # .env key for the engine/model
    max_tokens: int
    temperature: float
    output_schema: dict[str, Any] | None = None  # None = text output, no JSON schema
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
    """Validate that the catalog is internally consistent."""
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
    """Compatibility wrapper kept for legacy tests and admin tooling."""
    return legacy_bridge.resolve_legacy_model(use_case_key, fallback_model=fallback_model)
