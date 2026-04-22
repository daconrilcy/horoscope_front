"""Canonical prompt catalog and bounded fallback registry."""

from __future__ import annotations

import os
import re
from typing import Any

from pydantic import BaseModel

from app.domain.llm.governance import prompt_governance_registry as _prompt_governance_registry
from app.domain.llm.runtime.contracts import UseCaseConfig


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


DEPRECATED_USE_CASE_MAPPING: dict[str, dict[str, str]] = (
    _prompt_governance_registry.DEPRECATED_USE_CASE_MAPPING
)

CHAT_RESPONSE_V1 = {
    "type": "object",
    "required": ["message"],
    "additionalProperties": False,
    "properties": {"message": {"type": "string"}},
}
ASTRO_RESPONSE_V1 = {
    "type": "object",
    "required": ["summary", "key_points", "advice"],
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
        "advice": {"type": "string"},
    },
}
ASTRO_RESPONSE_V3 = {
    "type": "object",
    "required": ["summary", "sections", "highlights"],
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "content"],
                "additionalProperties": False,
                "properties": {"title": {"type": "string"}, "content": {"type": "string"}},
            },
        },
        "highlights": {"type": "array", "items": {"type": "string"}},
    },
}
HOROSCOPE_FREE_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["day_climate"],
    "properties": {
        "day_climate": {
            "type": "object",
            "additionalProperties": False,
            "required": ["summary"],
            "properties": {"summary": {"type": "string"}},
        }
    },
}
NATAL_FREE_SHORT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "accordion_titles"],
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "accordion_titles": {"type": "array", "items": {"type": "string"}},
    },
}

PROMPT_RUNTIME_DATA: dict[str, dict[str, Any]] = {
    "horoscope_daily": {
        "name": "horoscope-daily-canonical-v1",
        "description": "Horoscope du jour canonique resolu via feature/plan assembly",
        "engine_env_key": "OPENAI_ENGINE_HOROSCOPE_DAILY_FULL",
        "max_tokens": 3000,
        "temperature": 0.7,
        "output_schema": None,
    },
    "natal_long_free": {
        "name": "natal-long-free-v1",
        "description": "Interpretation natale restreinte (plan free)",
        "engine_env_key": "OPENAI_ENGINE_NATAL_LONG_FREE",
        "max_tokens": 1000,
        "temperature": 0.7,
        "output_schema": NATAL_FREE_SHORT_SCHEMA,
    },
    "guidance_daily": {
        "name": "guidance-daily-v1",
        "description": "Daily astrological guidance",
        "engine_env_key": "OPENAI_ENGINE_GUIDANCE_DAILY",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V1,
    },
    "guidance_weekly": {
        "name": "guidance-weekly-v1",
        "description": "Weekly astrological guidance",
        "engine_env_key": "OPENAI_ENGINE_GUIDANCE_WEEKLY",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V1,
    },
    "guidance_contextual": {
        "name": "guidance-contextual-v1",
        "description": "Contextual guidance for a specific situation",
        "engine_env_key": "OPENAI_ENGINE_GUIDANCE_CONTEXTUAL",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V1,
    },
    "natal_interpretation": {
        "name": "natal-interpretation-v3",
        "description": "Deep dive natal chart analysis",
        "engine_env_key": "OPENAI_ENGINE_NATAL_INTERPRETATION",
        "max_tokens": 4000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V3,
    },
    "natal_interpretation_short": {
        "name": "natal-interpretation-short-v1",
        "description": "Fast/concise natal analysis",
        "engine_env_key": "OPENAI_ENGINE_NATAL_SHORT",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V1,
    },
    "chat_astrologer": {
        "name": "chat-astrologer-v1",
        "description": "Interactive conversation with the virtual astrologer",
        "engine_env_key": "OPENAI_ENGINE_CHAT",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": CHAT_RESPONSE_V1,
    },
    "chat": {
        "name": "chat-legacy-v1",
        "description": "Legacy chat compatibility key",
        "engine_env_key": "OPENAI_ENGINE_CHAT",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": CHAT_RESPONSE_V1,
    },
    "astrologer_selection_help": {
        "name": "astrologer-selection-v1",
        "description": "Support for choosing an expert",
        "engine_env_key": "OPENAI_ENGINE_SUPPORT",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": CHAT_RESPONSE_V1,
    },
    "event_guidance": {
        "name": "event-guidance-v1",
        "description": "Guidance for a specific life event",
        "engine_env_key": "OPENAI_ENGINE_EVENT_GUIDANCE",
        "max_tokens": 4000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V1,
    },
    "test_natal": {
        "name": "test-natal-v1",
        "description": "Synthetic natal use case for gateway/orchestration tests",
        "engine_env_key": "OPENAI_ENGINE_TEST_NATAL",
        "max_tokens": 1000,
        "temperature": 0.7,
        "output_schema": CHAT_RESPONSE_V1,
    },
    "test_guidance": {
        "name": "test-guidance-v1",
        "description": "Synthetic guidance use case for gateway/orchestration tests",
        "engine_env_key": "OPENAI_ENGINE_TEST_GUIDANCE",
        "max_tokens": 2000,
        "temperature": 0.7,
        "output_schema": ASTRO_RESPONSE_V1,
    },
}

PROMPT_FALLBACK_CONFIGS: dict[str, dict[str, Any]] = {
    "natal_long_free": {
        "developer_prompt": (
            "Langue de reponse : francais ({{locale}}). Contexte : use_case={{use_case}}.\n\n"
            "Interpretez le theme natal fourni de facon claire, chaleureuse et non fataliste, "
            "strictement a partir des donnees techniques suivantes :\n{{chart_json}}"
        ),
        "required_prompt_placeholders": ["chart_json", "locale", "use_case"],
        "interaction_mode": "structured",
        "user_question_policy": "none",
    },
    "natal_interpretation": {
        "developer_prompt": (
            "Analyse le theme natal pour un utilisateur ne le {{birth_date}}. "
            "Donnees: {{chart_json}}."
        ),
        "required_prompt_placeholders": ["birth_date", "chart_json"],
        "interaction_mode": "structured",
        "user_question_policy": "none",
    },
    "natal_interpretation_short": {
        "developer_prompt": "Analyse rapide du theme natal.",
        "required_prompt_placeholders": [],
        "interaction_mode": "structured",
        "user_question_policy": "optional",
    },
    "chat_astrologer": {
        "developer_prompt": "Reponds a la conversation suivante: {{last_user_msg}}.",
        "required_prompt_placeholders": ["last_user_msg"],
        "interaction_mode": "chat",
        "user_question_policy": "required",
    },
    "chat": {
        "developer_prompt": "Reponds a la conversation suivante: {{last_user_msg}}.",
        "required_prompt_placeholders": ["last_user_msg"],
        "interaction_mode": "chat",
        "user_question_policy": "required",
    },
    "guidance_daily": {
        "developer_prompt": "Genere une guidance quotidienne basee sur le contexte: {{situation}}.",
        "required_prompt_placeholders": ["situation"],
        "interaction_mode": "structured",
        "user_question_policy": "none",
    },
    "horoscope_daily": {
        "developer_prompt": "Genere un horoscope quotidien. Question: {{question}}",
        "required_prompt_placeholders": ["question"],
        "interaction_mode": "structured",
        "user_question_policy": "none",
    },
    "guidance_weekly": {
        "developer_prompt": "Genere une guidance hebdomadaire.",
        "required_prompt_placeholders": [],
        "interaction_mode": "chat",
        "user_question_policy": "none",
    },
    "guidance_contextual": {
        "developer_prompt": "Genere une guidance contextuelle pour: {{situation}}.",
        "required_prompt_placeholders": ["situation"],
        "interaction_mode": "chat",
        "user_question_policy": "required",
    },
    "event_guidance": {
        "developer_prompt": "Guidance pour un evenement: {{event_description}}.",
        "required_prompt_placeholders": ["event_description"],
        "interaction_mode": "chat",
        "user_question_policy": "required",
    },
    "astrologer_selection_help": {
        "developer_prompt": "Aide l'utilisateur a choisir un astrologue.",
        "required_prompt_placeholders": [],
        "interaction_mode": "chat",
        "user_question_policy": "optional",
    },
    "test_natal": {
        "developer_prompt": "Synthetic test natal (locale {{locale}}).",
        "required_prompt_placeholders": [],
        "interaction_mode": "structured",
        "user_question_policy": "none",
    },
    "test_guidance": {
        "developer_prompt": "Synthetic test guidance: situation={{situation}}.",
        "required_prompt_placeholders": [],
        "interaction_mode": "structured",
        "user_question_policy": "none",
    },
}

PROMPT_CATALOG: dict[str, PromptEntry] = {
    key: PromptEntry(use_case_key=key, **entry) for key, entry in PROMPT_RUNTIME_DATA.items()
}


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
    from app.core.config import settings

    entry = PROMPT_RUNTIME_DATA.get(use_case_key)
    if entry:
        model = os.environ.get(str(entry["engine_env_key"]))
        if model:
            return model

    safe_uc_key = re.sub(r"[^a-zA-Z0-9_]", "_", use_case_key).upper()
    legacy_key = f"LLM_MODEL_OVERRIDE_{safe_uc_key}"
    legacy_model = os.environ.get(legacy_key)
    if legacy_model:
        return legacy_model

    if fallback_model:
        return fallback_model

    return getattr(settings, "openai_model_default", "gpt-4o-mini")


def get_max_tokens(use_case_key: str, *, default_use_case: str | None = None) -> int | None:
    entry = PROMPT_RUNTIME_DATA.get(use_case_key)
    if entry is None and default_use_case is not None:
        entry = PROMPT_RUNTIME_DATA.get(default_use_case)
    if entry is None:
        return None
    return int(entry["max_tokens"])


def get_prompt_runtime_entry(use_case_key: str) -> dict[str, Any] | None:
    entry = PROMPT_RUNTIME_DATA.get(use_case_key)
    if entry is None:
        return None
    return dict(entry)


def get_output_schema(use_case_key: str) -> dict[str, Any] | None:
    entry = PROMPT_RUNTIME_DATA.get(use_case_key)
    if entry is None:
        return None
    schema = entry.get("output_schema")
    return dict(schema) if schema is not None else None


def build_fallback_use_case_config(use_case_key: str) -> UseCaseConfig | None:
    runtime_entry = PROMPT_RUNTIME_DATA.get(use_case_key)
    prompt_entry = PROMPT_FALLBACK_CONFIGS.get(use_case_key)
    if runtime_entry is None or prompt_entry is None:
        return None

    from app.core.config import settings

    return UseCaseConfig(
        model=getattr(settings, "openai_model_default", "gpt-4o-mini"),
        temperature=float(runtime_entry.get("temperature", 0.7)),
        max_output_tokens=int(runtime_entry.get("max_tokens", 1000)),
        system_core_key="default_v1",
        developer_prompt=str(prompt_entry["developer_prompt"]),
        required_prompt_placeholders=list(prompt_entry.get("required_prompt_placeholders", [])),
        interaction_mode=str(prompt_entry.get("interaction_mode", "structured")),
        user_question_policy=str(prompt_entry.get("user_question_policy", "none")),
    )


__all__ = [
    "ASTRO_RESPONSE_V1",
    "ASTRO_RESPONSE_V3",
    "CHAT_RESPONSE_V1",
    "DEPRECATED_USE_CASE_MAPPING",
    "HOROSCOPE_FREE_OUTPUT_SCHEMA",
    "NATAL_FREE_SHORT_SCHEMA",
    "PROMPT_FALLBACK_CONFIGS",
    "PROMPT_CATALOG",
    "PROMPT_RUNTIME_DATA",
    "PromptEntry",
    "build_fallback_use_case_config",
    "get_output_schema",
    "get_max_tokens",
    "get_prompt_runtime_entry",
    "resolve_model",
]
