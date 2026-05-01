"""Contrats narratifs canoniques pour la narration horoscope quotidienne."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NarratorAdvice:
    """Représente le conseil actionnable retourné par la narration quotidienne."""

    advice: str
    emphasis: str


@dataclass
class NarratorResult:
    """Porte la sortie narrative structurée consommée par la projection publique."""

    daily_synthesis: str
    astro_events_intro: str
    time_window_narratives: dict[str, str]
    turning_point_narratives: list[str]
    daily_advice: NarratorAdvice | None = None
    main_turning_point_narrative: str | None = None


NARRATOR_OUTPUT_SCHEMA = {
    "type": "object",
    "required": [
        "daily_synthesis",
        "astro_events_intro",
        "time_window_narratives",
        "turning_point_narratives",
        "main_turning_point_narrative",
        "daily_advice",
    ],
    "additionalProperties": False,
    "properties": {
        "daily_synthesis": {"type": "string"},
        "astro_events_intro": {"type": "string"},
        "time_window_narratives": {
            "type": "object",
            "required": ["nuit", "matin", "apres_midi", "soiree"],
            "additionalProperties": False,
            "properties": {
                "nuit": {"type": "string"},
                "matin": {"type": "string"},
                "apres_midi": {"type": "string"},
                "soiree": {"type": "string"},
            },
        },
        "turning_point_narratives": {
            "type": "array",
            "items": {"type": "string"},
        },
        "main_turning_point_narrative": {"type": "string"},
        "daily_advice": {
            "type": "object",
            "required": ["advice", "emphasis"],
            "additionalProperties": False,
            "properties": {
                "advice": {"type": "string"},
                "emphasis": {"type": "string"},
            },
        },
    },
}
