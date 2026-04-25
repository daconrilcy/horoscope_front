"""Centralise le format texte partage entre generation guidance et rendu consultation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class StructuredTextBlock:
    """Represente un bloc de texte structure utilisable par plusieurs consumers."""

    kind: Literal["title", "subtitle", "paragraph", "bullet_list"]
    text: str | None = None
    items: list[str] | None = None


_INLINE_FORMATTING_PATTERN = re.compile(r"\*\*(?P<bold>[^*]+)\*\*")
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s*(.+)$")
_NUMBERED_HEADING_PATTERN = re.compile(r"^\d+[\).\s]+(.+)$")
_BULLET_PATTERN = re.compile(r"^[-*•]\s+(.+)$")
_BLANK_LINE_PATTERN = re.compile(r"^\s*$")


def compose_structured_guidance_full_text(
    summary_raw: str,
    key_points: list[str],
    advice: list[str],
) -> str:
    """Assemble le texte canonique d une guidance structuree."""
    sections: list[str] = []
    summary = summary_raw.strip()
    if summary:
        sections.append(summary)
    if key_points:
        sections.append("Points cles :\n" + "\n".join(f"- {item}" for item in key_points))
    if advice:
        sections.append("Conseils :\n" + "\n".join(f"- {item}" for item in advice))
    return "\n\n".join(section for section in sections if section.strip())


def normalize_structured_string_list(raw_value: Any) -> list[str]:
    """Normalise une sortie structuree LLM potentiellement mal typee."""
    if raw_value is None:
        return []
    if isinstance(raw_value, str):
        normalized = raw_value.strip()
        return [normalized] if normalized else []
    if isinstance(raw_value, (list, tuple)):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    normalized = str(raw_value).strip()
    return [normalized] if normalized else []


def parse_structured_guidance_blocks(content: str) -> list[StructuredTextBlock]:
    """Transforme le texte guidance canonique en blocs structurels stables."""
    blocks: list[StructuredTextBlock] = []
    paragraph_lines: list[str] = []
    bullet_items: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        paragraph = " ".join(line.strip() for line in paragraph_lines if line.strip()).strip()
        if paragraph:
            blocks.append(StructuredTextBlock(kind="paragraph", text=paragraph))
        paragraph_lines.clear()

    def flush_bullets() -> None:
        if not bullet_items:
            return
        blocks.append(StructuredTextBlock(kind="bullet_list", items=bullet_items.copy()))
        bullet_items.clear()

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if _BLANK_LINE_PATTERN.match(line):
            flush_paragraph()
            flush_bullets()
            continue

        heading_match = _HEADING_PATTERN.match(line)
        if heading_match:
            flush_paragraph()
            flush_bullets()
            heading_text = _clean_inline_formatting(heading_match.group(2))
            heading_level = len(heading_match.group(1))
            blocks.append(
                StructuredTextBlock(
                    kind="title" if heading_level <= 2 else "subtitle",
                    text=heading_text,
                )
            )
            continue

        bullet_match = _BULLET_PATTERN.match(line)
        if bullet_match:
            flush_paragraph()
            bullet_items.append(_clean_inline_formatting(bullet_match.group(1)))
            continue

        numbered_heading_match = _NUMBERED_HEADING_PATTERN.match(line)
        if numbered_heading_match and not line.lower().startswith("http"):
            flush_paragraph()
            flush_bullets()
            blocks.append(
                StructuredTextBlock(
                    kind="subtitle",
                    text=_clean_inline_formatting(numbered_heading_match.group(1)),
                )
            )
            continue

        paragraph_lines.append(_clean_inline_formatting(line))

    flush_paragraph()
    flush_bullets()
    return blocks


def _clean_inline_formatting(text: str) -> str:
    """Retire le markdown inline non desire avant exposition dans les DTO."""
    cleaned = text.strip()
    cleaned = _INLINE_FORMATTING_PATTERN.sub(
        lambda match: match.group("bold").strip(),
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" :.-")
