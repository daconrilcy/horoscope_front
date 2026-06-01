# Commentaire global: definit les schemas stricts raw et publics des generations theme natal.
"""Schemas de generation theme natal separes entre provider brut et projection publique."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant


class _StrictGenerationSchema(BaseModel):
    """Base stricte commune aux payloads contractuels de generation."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ThemeNatalEvidenceRef(_StrictGenerationSchema):
    """Reference non technique vers une source interpretative exploitable."""

    source_id: str = Field(min_length=1, max_length=80)
    source_kind: Literal["reading_plan", "astrological_fact", "safety_rule"]
    relevance: str = Field(min_length=1, max_length=320)


class ThemeNatalFreeRawHighlight(_StrictGenerationSchema):
    """Bloc provider brut pour la preview Free."""

    title: str = Field(min_length=1, max_length=90)
    narrative: str = Field(min_length=1, max_length=700)
    evidence_refs: tuple[ThemeNatalEvidenceRef, ...] = Field(min_length=1, max_length=4)


class ThemeNatalFreeRawProviderResponse(_StrictGenerationSchema):
    """Reponse provider brute attendue pour la preview Free."""

    schema_version: Literal["theme_natal_free_preview_raw_v1"]
    preview_title: str = Field(min_length=1, max_length=120)
    preview_summary: str = Field(min_length=1, max_length=900)
    highlights: tuple[ThemeNatalFreeRawHighlight, ...] = Field(min_length=2, max_length=4)
    safety_notes: tuple[str, ...] = Field(min_length=1, max_length=3)


class ThemeNatalBasicRawSection(_StrictGenerationSchema):
    """Section provider brute plan-backed pour la lecture Basic."""

    key: Literal["identity", "resources", "relationships", "growth"]
    heading: str = Field(min_length=1, max_length=120)
    narrative: str = Field(min_length=180, max_length=2600)
    source_refs: tuple[ThemeNatalEvidenceRef, ...] = Field(min_length=1, max_length=6)
    limitations: tuple[str, ...] = Field(default_factory=tuple, max_length=4)


class ThemeNatalBasicRawProviderResponse(_StrictGenerationSchema):
    """Reponse provider brute ciblee pour la lecture Basic complete."""

    schema_version: Literal["theme_natal_basic_full_raw_v1"]
    title: str = Field(min_length=1, max_length=140)
    introduction: str = Field(min_length=120, max_length=1200)
    sections: tuple[ThemeNatalBasicRawSection, ...] = Field(min_length=4, max_length=4)
    conclusion: str = Field(min_length=120, max_length=900)
    safety_notes: tuple[str, ...] = Field(min_length=1, max_length=4)


class ThemeNatalPremiumRawTimingWindow(_StrictGenerationSchema):
    """Fenetre temporelle provider brute autorisee pour Premium."""

    label: str = Field(min_length=1, max_length=80)
    narrative: str = Field(min_length=1, max_length=700)
    evidence_refs: tuple[ThemeNatalEvidenceRef, ...] = Field(min_length=1, max_length=5)


class ThemeNatalPremiumRawChapter(_StrictGenerationSchema):
    """Chapitre provider brut Premium avec approfondissements distincts de Basic."""

    key: Literal["identity", "resources", "relationships", "growth", "timing", "integration"]
    heading: str = Field(min_length=1, max_length=140)
    narrative: str = Field(min_length=220, max_length=3600)
    timing_windows: tuple[ThemeNatalPremiumRawTimingWindow, ...] = Field(
        default_factory=tuple, max_length=3
    )
    reflection_prompts: tuple[str, ...] = Field(min_length=1, max_length=4)
    source_refs: tuple[ThemeNatalEvidenceRef, ...] = Field(min_length=1, max_length=8)


class ThemeNatalPremiumRawProviderResponse(_StrictGenerationSchema):
    """Reponse provider brute ciblee pour la lecture Premium complete."""

    schema_version: Literal["theme_natal_premium_full_raw_v1"]
    title: str = Field(min_length=1, max_length=160)
    orientation: str = Field(min_length=160, max_length=1500)
    chapters: tuple[ThemeNatalPremiumRawChapter, ...] = Field(min_length=5, max_length=6)
    integration_summary: str = Field(min_length=160, max_length=1200)
    safety_notes: tuple[str, ...] = Field(min_length=1, max_length=4)


class ThemeNatalFreePublicReading(_StrictGenerationSchema):
    """Projection publique Free sans trace technique de generation."""

    schema_version: Literal["theme_natal_free_preview_public_v1"]
    title: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=900)
    highlights: tuple[str, ...] = Field(min_length=2, max_length=4)
    call_to_action: str = Field(min_length=1, max_length=220)


class ThemeNatalBasicPublicChapter(_StrictGenerationSchema):
    """Chapitre public Basic issu de la projection du provider brut."""

    key: Literal["identity", "resources", "relationships", "growth"]
    title: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=160, max_length=2400)
    source_annex: tuple[str, ...] = Field(default_factory=tuple, max_length=6)


class ThemeNatalBasicPublicReading(_StrictGenerationSchema):
    """Projection publique Basic distincte du schema provider brut."""

    schema_version: Literal["theme_natal_basic_full_public_v1"]
    title: str = Field(min_length=1, max_length=140)
    introduction: str = Field(min_length=100, max_length=1000)
    chapters: tuple[ThemeNatalBasicPublicChapter, ...] = Field(min_length=4, max_length=4)
    conclusion: str = Field(min_length=100, max_length=900)
    disclaimers: tuple[str, ...] = Field(min_length=1, max_length=3)


class ThemeNatalPremiumPublicTimingWindow(_StrictGenerationSchema):
    """Fenetre temporelle publique non technique pour Premium."""

    label: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=650)


class ThemeNatalPremiumPublicChapter(_StrictGenerationSchema):
    """Chapitre public Premium enrichi sans champs provider."""

    key: Literal["identity", "resources", "relationships", "growth", "timing", "integration"]
    title: str = Field(min_length=1, max_length=140)
    text: str = Field(min_length=180, max_length=3200)
    timing_windows: tuple[ThemeNatalPremiumPublicTimingWindow, ...] = Field(
        default_factory=tuple, max_length=3
    )
    reflection_prompts: tuple[str, ...] = Field(min_length=1, max_length=4)
    source_annex: tuple[str, ...] = Field(default_factory=tuple, max_length=8)


class ThemeNatalPremiumPublicReading(_StrictGenerationSchema):
    """Projection publique Premium distincte de Basic et du provider brut."""

    schema_version: Literal["theme_natal_premium_full_public_v1"]
    title: str = Field(min_length=1, max_length=160)
    orientation: str = Field(min_length=140, max_length=1300)
    chapters: tuple[ThemeNatalPremiumPublicChapter, ...] = Field(min_length=5, max_length=6)
    integration_summary: str = Field(min_length=140, max_length=1100)
    disclaimers: tuple[str, ...] = Field(min_length=1, max_length=3)


RAW_PROVIDER_MODELS: dict[ThemeNatalOutputVariant, type[BaseModel]] = {
    ThemeNatalOutputVariant.FREE_PREVIEW: ThemeNatalFreeRawProviderResponse,
    ThemeNatalOutputVariant.BASIC_FULL_READING: ThemeNatalBasicRawProviderResponse,
    ThemeNatalOutputVariant.PREMIUM_FULL_READING: ThemeNatalPremiumRawProviderResponse,
}

PUBLIC_PROJECTED_MODELS: dict[ThemeNatalOutputVariant, type[BaseModel]] = {
    ThemeNatalOutputVariant.FREE_PREVIEW: ThemeNatalFreePublicReading,
    ThemeNatalOutputVariant.BASIC_FULL_READING: ThemeNatalBasicPublicReading,
    ThemeNatalOutputVariant.PREMIUM_FULL_READING: ThemeNatalPremiumPublicReading,
}

RAW_PROVIDER_SCHEMA_NAMES: dict[ThemeNatalOutputVariant, str] = {
    ThemeNatalOutputVariant.FREE_PREVIEW: "theme_natal_free_preview_raw_v1",
    ThemeNatalOutputVariant.BASIC_FULL_READING: "theme_natal_basic_full_raw_v1",
    ThemeNatalOutputVariant.PREMIUM_FULL_READING: "theme_natal_premium_full_raw_v1",
}

PUBLIC_PROJECTED_SCHEMA_NAMES: dict[ThemeNatalOutputVariant, str] = {
    ThemeNatalOutputVariant.FREE_PREVIEW: "theme_natal_free_preview_public_v1",
    ThemeNatalOutputVariant.BASIC_FULL_READING: "theme_natal_basic_full_public_v1",
    ThemeNatalOutputVariant.PREMIUM_FULL_READING: "theme_natal_premium_full_public_v1",
}


def json_schema_for_model(model: type[BaseModel], *, schema_id: str) -> dict[str, Any]:
    """Construit un schema JSON ferme avec identifiant stable."""

    schema = model.model_json_schema()
    schema["$id"] = schema_id
    return schema


THEME_NATAL_RAW_PROVIDER_SCHEMAS: dict[ThemeNatalOutputVariant, dict[str, Any]] = {
    variant: json_schema_for_model(model, schema_id=RAW_PROVIDER_SCHEMA_NAMES[variant])
    for variant, model in RAW_PROVIDER_MODELS.items()
}

THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS: dict[ThemeNatalOutputVariant, dict[str, Any]] = {
    variant: json_schema_for_model(model, schema_id=PUBLIC_PROJECTED_SCHEMA_NAMES[variant])
    for variant, model in PUBLIC_PROJECTED_MODELS.items()
}

THEME_NATAL_PUBLIC_SCHEMA_REGISTRY: tuple[tuple[str, int, dict[str, Any]], ...] = tuple(
    (schema_name, 1, THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS[variant])
    for variant, schema_name in PUBLIC_PROJECTED_SCHEMA_NAMES.items()
)

__all__ = [
    "PUBLIC_PROJECTED_MODELS",
    "PUBLIC_PROJECTED_SCHEMA_NAMES",
    "RAW_PROVIDER_MODELS",
    "RAW_PROVIDER_SCHEMA_NAMES",
    "THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS",
    "THEME_NATAL_PUBLIC_SCHEMA_REGISTRY",
    "THEME_NATAL_RAW_PROVIDER_SCHEMAS",
    "ThemeNatalBasicPublicReading",
    "ThemeNatalBasicRawProviderResponse",
    "ThemeNatalFreePublicReading",
    "ThemeNatalFreeRawProviderResponse",
    "ThemeNatalPremiumPublicReading",
    "ThemeNatalPremiumRawProviderResponse",
    "json_schema_for_model",
]
