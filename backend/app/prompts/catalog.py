"""Centralized prompt catalog."""

from __future__ import annotations

import os
import re
from typing import Any

from pydantic import BaseModel


class PromptEntry(BaseModel):
    """Metadata for a prompt use case."""

    name: str  # Unique human-readable name
    description: str  # Short description
    use_case_key: str  # Use case identifier (key in PROMPT_CATALOG)
    engine_env_key: str  # .env key for the engine/model
    max_tokens: int
    temperature: float
    output_schema: dict[str, Any] | None = None  # None = text output, no JSON schema


# Canonical Output Schemas (simplified for metadata)
CHAT_RESPONSE_V1 = {"type": "object", "required": ["message"]}
ASTRO_RESPONSE_V1 = {"type": "object", "required": ["summary", "key_points", "advice"]}
ASTRO_RESPONSE_V3 = {"type": "object", "required": ["summary", "sections", "highlights"]}

PROMPT_CATALOG: dict[str, PromptEntry] = {
    "guidance_daily": PromptEntry(
        name="guidance-daily-v1",
        description="Daily astrological guidance",
        use_case_key="guidance_daily",
        engine_env_key="OPENAI_ENGINE_GUIDANCE_DAILY",
        max_tokens=2000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V1,
    ),
    "guidance_weekly": PromptEntry(
        name="guidance-weekly-v1",
        description="Weekly astrological guidance",
        use_case_key="guidance_weekly",
        engine_env_key="OPENAI_ENGINE_GUIDANCE_WEEKLY",
        max_tokens=2000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V1,
    ),
    "guidance_contextual": PromptEntry(
        name="guidance-contextual-v1",
        description="Contextual guidance for a specific situation",
        use_case_key="guidance_contextual",
        engine_env_key="OPENAI_ENGINE_GUIDANCE_CONTEXTUAL",
        max_tokens=2000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V1,
    ),
    "natal_interpretation": PromptEntry(
        name="natal-interpretation-v3",
        description="Deep dive natal chart analysis",
        use_case_key="natal_interpretation",
        engine_env_key="OPENAI_ENGINE_NATAL_INTERPRETATION",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_interpretation_short": PromptEntry(
        name="natal-interpretation-short-v1",
        description="Fast/concise natal analysis",
        use_case_key="natal_interpretation_short",
        engine_env_key="OPENAI_ENGINE_NATAL_SHORT",
        max_tokens=2000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V1,
    ),
    "chat_astrologer": PromptEntry(
        name="chat-astrologer-v1",
        description="Interactive conversation with the virtual astrologer",
        use_case_key="chat_astrologer",
        engine_env_key="OPENAI_ENGINE_CHAT",
        max_tokens=2000,
        temperature=0.7,
        output_schema=CHAT_RESPONSE_V1,
    ),
    "chat": PromptEntry(
        name="chat-v1-legacy",
        description="Legacy chat use case",
        use_case_key="chat",
        engine_env_key="OPENAI_ENGINE_CHAT",
        max_tokens=2000,
        temperature=0.7,
        output_schema=CHAT_RESPONSE_V1,
    ),
    "event_guidance": PromptEntry(
        name="event-guidance-v1",
        description="Guidance for a specific life event",
        use_case_key="event_guidance",
        engine_env_key="OPENAI_ENGINE_EVENT_GUIDANCE",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V1,
    ),
    "daily_prediction": PromptEntry(
        name="daily-prediction-narrator-v1",
        description="LLM narration of daily horoscope sections (Story 60.16)",
        use_case_key="daily_prediction",
        engine_env_key="OPENAI_MODEL_DEFAULT",
        max_tokens=800,
        temperature=0.7,
    ),
    "natal_psy_profile": PromptEntry(
        name="natal-psy-profile-v3",
        description="Psychological portrait",
        use_case_key="natal_psy_profile",
        engine_env_key="OPENAI_ENGINE_NATAL_PSY",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_shadow_integration": PromptEntry(
        name="natal-shadow-integration-v3",
        description="Shadow work and integration",
        use_case_key="natal_shadow_integration",
        engine_env_key="OPENAI_ENGINE_NATAL_SHADOW",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_leadership_workstyle": PromptEntry(
        name="natal-leadership-workstyle-v3",
        description="Work and leadership style",
        use_case_key="natal_leadership_workstyle",
        engine_env_key="OPENAI_ENGINE_NATAL_WORK",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_creativity_joy": PromptEntry(
        name="natal-creativity-joy-v3",
        description="Creativity and resourcing",
        use_case_key="natal_creativity_joy",
        engine_env_key="OPENAI_ENGINE_NATAL_JOY",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_relationship_style": PromptEntry(
        name="natal-relationship-style-v3",
        description="Relationship and attachment style",
        use_case_key="natal_relationship_style",
        engine_env_key="OPENAI_ENGINE_NATAL_RELATIONSHIP",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_community_networks": PromptEntry(
        name="natal-community-networks-v3",
        description="Social energy and collaboration",
        use_case_key="natal_community_networks",
        engine_env_key="OPENAI_ENGINE_NATAL_COMMUNITY",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_values_security": PromptEntry(
        name="natal-values-security-v3",
        description="Personal values and security",
        use_case_key="natal_values_security",
        engine_env_key="OPENAI_ENGINE_NATAL_VALUES",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "natal_evolution_path": PromptEntry(
        name="natal-evolution-path-v3",
        description="Growth and evolution axis",
        use_case_key="natal_evolution_path",
        engine_env_key="OPENAI_ENGINE_NATAL_EVOLUTION",
        max_tokens=4000,
        temperature=0.7,
        output_schema=ASTRO_RESPONSE_V3,
    ),
    "astrologer_selection_help": PromptEntry(
        name="astrologer-selection-v1",
        description="Support for choosing an expert",
        use_case_key="astrologer_selection_help",
        engine_env_key="OPENAI_ENGINE_SUPPORT",
        max_tokens=2000,
        temperature=0.7,
        output_schema=CHAT_RESPONSE_V1,
    ),
    "account_support": PromptEntry(
        name="account-support-v1",
        description="Technical account support",
        use_case_key="account_support",
        engine_env_key="OPENAI_ENGINE_SUPPORT",
        max_tokens=2000,
        temperature=0.0,
        output_schema=None,
    ),
}


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
    """
    Resolve the OpenAI model to use for a specific use case.

    Order of resolution:
    1. OS environment variable (OPENAI_ENGINE_{UC})
    2. Legacy model override (LLM_MODEL_OVERRIDE_{UC})
    3. fallback_model (usually from DB config or stub)
    4. settings.OPENAI_MODEL_DEFAULT

    Returns:
        The model name (e.g., 'gpt-4o-mini').
    """
    # Lazy import to avoid circular dependency at module load time
    from app.core.config import settings

    # 1. New granular override
    entry = PROMPT_CATALOG.get(use_case_key)
    if entry:
        model = os.environ.get(entry.engine_env_key)
        if model:
            return model

    # 2. Legacy override
    safe_uc_key = re.sub(r"[^a-zA-Z0-9_]", "_", use_case_key).upper()
    legacy_key = f"LLM_MODEL_OVERRIDE_{safe_uc_key}"
    legacy_model = os.environ.get(legacy_key)
    if legacy_model:
        return legacy_model

    # 3. Use provided fallback (from DB or stub)
    if fallback_model:
        return fallback_model

    return getattr(settings, "openai_model_default", "gpt-4o-mini")
