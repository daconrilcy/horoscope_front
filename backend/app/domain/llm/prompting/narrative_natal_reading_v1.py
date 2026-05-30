# Commentaire global: contrat public de lecture narrative natale versionnee.
"""Schemas Pydantic pour `narrative_natal_reading_v1` expose au client."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

NARRATIVE_NATAL_READING_V1_CONTRACT_VERSION = "narrative_natal_reading_v1"
NARRATIVE_NATAL_READING_PAYLOAD_KEY = "narrative_natal_reading_v1"

NarrativeChapterKey = Literal[
    "personality",
    "emotional_world",
    "relationships",
    "vocation",
    "evolution_path",
]

NARRATIVE_CHAPTER_ORDER: tuple[NarrativeChapterKey, ...] = (
    "personality",
    "emotional_world",
    "relationships",
    "vocation",
    "evolution_path",
)


class NarrativeNatalReadingChapterV1(BaseModel):
    """Chapitre narratif grand public d'une lecture natale."""

    model_config = ConfigDict(extra="forbid")

    key: NarrativeChapterKey
    title: str = Field(..., min_length=1, max_length=120)
    narrative: str = Field(..., min_length=80, max_length=8000)
    key_points: list[str] = Field(default_factory=list, max_length=6)


class UsedAstrologicalElementV1(BaseModel):
    """Justification astrologique vulgarisee sans score ni identifiant technique."""

    model_config = ConfigDict(extra="forbid")

    astrological_label: str = Field(..., min_length=3, max_length=200)
    consequence: str = Field(..., min_length=10, max_length=500)


class NarrativeNatalReadingV1(BaseModel):
    """Lecture natale structuree en cinq chapitres et justifications de fin."""

    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["narrative_natal_reading_v1"] = (
        NARRATIVE_NATAL_READING_V1_CONTRACT_VERSION
    )
    editorial_profile: Literal["free", "basic", "premium"] = "premium"
    chapters: list[NarrativeNatalReadingChapterV1] = Field(..., min_length=5, max_length=5)
    used_astrological_elements: list[UsedAstrologicalElementV1] = Field(
        default_factory=list,
        max_length=12,
    )

    def ordered_chapters(self) -> list[NarrativeNatalReadingChapterV1]:
        """Retourne les chapitres dans l'ordre produit attendu."""
        by_key = {chapter.key: chapter for chapter in self.chapters}
        return [by_key[key] for key in NARRATIVE_CHAPTER_ORDER]


__all__ = [
    "NARRATIVE_CHAPTER_ORDER",
    "NARRATIVE_NATAL_READING_PAYLOAD_KEY",
    "NARRATIVE_NATAL_READING_V1_CONTRACT_VERSION",
    "NarrativeChapterKey",
    "NarrativeNatalReadingChapterV1",
    "NarrativeNatalReadingV1",
    "UsedAstrologicalElementV1",
]
