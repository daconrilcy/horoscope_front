# Commentaire global: construction de narrative_natal_reading_v1 depuis AstroResponseV3.
"""Projette une lecture narrative publique sans exposer les carriers techniques."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from app.domain.llm.prompting.narrative_natal_reading_v1 import (
    NARRATIVE_CHAPTER_ORDER,
    NarrativeChapterKey,
    NarrativeNatalReadingChapterV1,
    NarrativeNatalReadingV1,
    UsedAstrologicalElementV1,
)
from app.domain.llm.prompting.schemas import AstroResponseV3

_CHAPTER_SECTION_PRIORITY: dict[NarrativeChapterKey, tuple[str, ...]] = {
    "personality": ("self_image", "overall", "strengths"),
    "emotional_world": ("emotions", "inner_life", "daily_life"),
    "relationships": ("relationships", "needs_in_love", "romance_vibe"),
    "vocation": ("career", "work_environment", "leadership_signature"),
    "evolution_path": ("growth_levers", "growth_direction", "integration_path", "integration"),
}

_CHAPTER_DEFAULT_TITLES: dict[NarrativeChapterKey, str] = {
    "personality": "Votre personnalite",
    "emotional_world": "Votre monde emotionnel",
    "relationships": "Vos relations",
    "vocation": "Votre vocation",
    "evolution_path": "Votre chemin d'evolution",
}


def _section_content_by_key(response: AstroResponseV3, section_key: str) -> str | None:
    for section in response.sections:
        if section.key == section_key:
            return section.content
    return None


def _pick_section_content(response: AstroResponseV3, priority: Sequence[str]) -> tuple[str, str]:
    for key in priority:
        content = _section_content_by_key(response, key)
        if content:
            for section in response.sections:
                if section.key == key:
                    return section.heading or key, content
    fallback = response.sections[0]
    return fallback.heading, fallback.content


def _editorial_profile(level: str, variant_code: str | None) -> Literal["free", "basic", "premium"]:
    if level == "short" or variant_code == "free_short":
        return "free"
    if variant_code == "single_astrologer":
        return "basic"
    return "premium"


def build_used_astrological_elements(
    llm_astrology_input_v1: Mapping[str, Any] | None,
    *,
    limit: int,
) -> list[UsedAstrologicalElementV1]:
    """Construit des justifications lisibles depuis le shaping autorise."""
    if not isinstance(llm_astrology_input_v1, dict):
        return []
    shaping = llm_astrology_input_v1.get("shaping")
    if not isinstance(shaping, dict):
        return []
    support = shaping.get("support_elements")
    if not isinstance(support, list):
        return []
    elements: list[UsedAstrologicalElementV1] = []
    for item in support:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code", "")).strip()
        value = str(item.get("value", "")).strip()
        if not value or code in {"confidence_wording"}:
            continue
        if code == "source_label":
            label = value
            consequence = "Ce repere structure une partie de votre lecture."
        elif code == "highlight":
            label = value
            consequence = "Ce theme ressort comme un fil directeur du theme."
        elif code == "personalization_note":
            label = "Personnalisation du theme"
            consequence = value
        else:
            label = value.replace("_", " ").strip().capitalize()
            consequence = "Ce repere soutient la coherence de la lecture."
        elements.append(
            UsedAstrologicalElementV1(
                astrological_label=label[:200],
                consequence=consequence[:500],
            )
        )
        if len(elements) >= limit:
            break
    return elements


def build_narrative_natal_reading_v1(
    *,
    response: AstroResponseV3,
    llm_astrology_input_v1: Mapping[str, Any] | None,
    level: str,
    variant_code: str | None,
) -> NarrativeNatalReadingV1:
    """Assemble le contrat narratif public depuis une interpretation V3 acceptee."""
    profile = _editorial_profile(level, variant_code)
    limits = {"free": 3, "basic": 6, "premium": 10}[profile]
    chapters: list[NarrativeNatalReadingChapterV1] = []
    for chapter_key in NARRATIVE_CHAPTER_ORDER:
        heading, content = _pick_section_content(response, _CHAPTER_SECTION_PRIORITY[chapter_key])
        title = heading if heading else _CHAPTER_DEFAULT_TITLES[chapter_key]
        highlights = [
            str(item).strip() for item in (response.highlights or [])[:2] if str(item).strip()
        ]
        chapters.append(
            NarrativeNatalReadingChapterV1(
                key=chapter_key,
                title=title[:120],
                narrative=content,
                key_points=highlights[:2] if chapter_key == "personality" else [],
            )
        )
    return NarrativeNatalReadingV1(
        editorial_profile=profile,
        chapters=chapters,
        used_astrological_elements=build_used_astrological_elements(
            llm_astrology_input_v1,
            limit=limits,
        ),
    )
