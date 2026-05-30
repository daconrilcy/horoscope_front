# Commentaire global: integrite semantique des lectures narratives natales completes Basic/Premium.
"""Detecte le padding, les doublons et les sources vides avant persistance ou relecture publique."""

from __future__ import annotations

import re

from app.domain.llm.prompting.narrative_natal_reading_v1 import (
    NARRATIVE_CHAPTER_ORDER,
    NarrativeNatalReadingV1,
)


class NarrativeChapterSourceMissingError(ValueError):
    """Leve lorsqu'un chapitre requis ne possede aucune section source exploitable."""

    def __init__(self, chapter_key: str, priority: tuple[str, ...]) -> None:
        self.chapter_key = chapter_key
        self.priority = priority
        super().__init__(
            f"Missing narrative source section for chapter '{chapter_key}' "
            f"(priority={list(priority)})"
        )


def _normalize_narrative_text(text: str) -> str:
    """Normalise un texte narratif pour comparer titres et contenus."""
    collapsed = re.sub(r"\s+", " ", text.strip().casefold())
    return collapsed


def validate_narrative_semantic_integrity(reading: NarrativeNatalReadingV1) -> list[str]:
    """Retourne les violations semantiques d'une lecture complete acceptee."""
    violations: list[str] = []
    chapter_keys = [chapter.key for chapter in reading.chapters]
    if chapter_keys != list(NARRATIVE_CHAPTER_ORDER):
        violations.append("chapter_order_invalid")

    normalized_narratives: list[str] = []
    normalized_titles: list[str] = []
    for chapter in reading.chapters:
        narrative = _normalize_narrative_text(chapter.narrative)
        if not narrative:
            violations.append(f"chapter_empty:{chapter.key}")
            continue
        if narrative in normalized_narratives:
            violations.append("duplicate_chapter_narrative")
        normalized_narratives.append(narrative)

        title = _normalize_narrative_text(chapter.title)
        if title and title in normalized_titles:
            violations.append("duplicate_chapter_title")
        if title:
            normalized_titles.append(title)

    if reading.editorial_profile in {"basic", "premium"} and not reading.used_astrological_elements:
        violations.append("empty_used_astrological_elements")

    return sorted(set(violations))


def is_narratively_invalid_complete_payload(payload: dict[str, object]) -> bool:
    """Indique si un payload persiste ne doit pas etre expose comme lecture complete nominale."""
    from app.services.llm_generation.natal.stored_interpretation_payload import (
        load_narrative_reading_from_payload,
    )

    reading = load_narrative_reading_from_payload(payload)
    if reading is None:
        return True
    return bool(validate_narrative_semantic_integrity(reading))
