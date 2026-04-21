"""Schéma JSON de sortie narrateur horoscope quotidien (seed / contrats)."""

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
