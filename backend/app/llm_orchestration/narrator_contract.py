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
            "additionalProperties": {"type": "string"},
        },
        "turning_point_narratives": {
            "type": "array",
            "items": {"type": "string"},
        },
        "main_turning_point_narrative": {"type": ["string", "null"]},
        "daily_advice": {
            "type": ["object", "null"],
            "required": ["advice", "emphasis"],
            "additionalProperties": False,
            "properties": {
                "advice": {"type": "string"},
                "emphasis": {"type": "string"},
            },
        },
    },
}
