from __future__ import annotations

import logging
from app.infra.db.models.llm_persona import LlmPersonaModel

logger = logging.getLogger(__name__)

TONE_MAPPINGS = {
    "warm": "chaleureux et empathique",
    "direct": "direct et factuel",
    "mystical": "mystique et inspirant",
    "rational": "rationnel et analytique",
}

VERBOSITY_MAPPINGS = {
    "short": "courte (1-2 paragraphes)",
    "medium": "modérée (3-5 paragraphes)",
    "long": "détaillée (plus de 5 paragraphes)",
}

STYLE_MARKER_MAP = {
    "tutoiement": "Tutoie l'utilisateur.",
    "vouvoiement": "Vouvoie l'utilisateur.",
}


def _sanitize_string(s: str | None) -> str:
    """
    Cleans string fields: removes newlines/tabs, strips whitespace,
    and escapes Jinja2 brackets to prevent prompt injection.
    """
    if not s:
        return ""
    # Remove newlines and tabs to keep the block structure clean
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # Escape Jinja2 brackets
    s = s.replace("{{", "\\{\\{").replace("}}", "\\}\\}")
    return s.strip()


def compose_persona_block(persona: LlmPersonaModel) -> str:
    """
    Composes a structured persona block for the LLM.
    """
    lines = []

    # Header
    persona_name = _sanitize_string(persona.name)
    header = f"## Directives de persona : {persona_name}"
    if persona.description:
        header += f" ({_sanitize_string(persona.description)})"
    lines.append(header)

    # Tone and direct markers
    tone_val = persona.tone.value if hasattr(persona.tone, "value") else persona.tone
    tone_label = TONE_MAPPINGS.get(tone_val, tone_val)
    tone_line = f"Adopte un ton {tone_label}."

    # Special handling for common style markers to make them more natural
    markers = []
    for marker in persona.style_markers:
        sanitized_marker = _sanitize_string(marker)
        if sanitized_marker.lower() in STYLE_MARKER_MAP:
            tone_line += f" {STYLE_MARKER_MAP[sanitized_marker.lower()]}"
        else:
            markers.append(sanitized_marker)

    lines.append(tone_line)

    # Verbosity
    verb_val = persona.verbosity.value if hasattr(persona.verbosity, "value") else persona.verbosity
    verbosity_label = VERBOSITY_MAPPINGS.get(verb_val, verb_val)
    lines.append(f"Longueur de réponse : {verbosity_label}.")

    # Style markers (remaining)
    if markers:
        lines.append(f"Style : {', '.join(markers)}.")

    # Boundaries
    if persona.boundaries:
        lines.append("Contraintes éditoriales :")
        for boundary in persona.boundaries:
            lines.append(f"- {_sanitize_string(boundary)}")

    # Topics
    if persona.allowed_topics:
        sanitized_allowed = [_sanitize_string(t) for t in persona.allowed_topics]
        lines.append(f"Topics autorisés : {', '.join(sanitized_allowed)}.")
    else:
        # Default: all topics are allowed if not specified
        pass

    if persona.disallowed_topics:
        sanitized_disallowed = [_sanitize_string(t) for t in persona.disallowed_topics]
        lines.append(f"Topics exclus (ne jamais aborder) : {', '.join(sanitized_disallowed)}.")

    # Formatting
    f = persona.formatting
    formatting_parts = []
    if f.get("sections"):
        formatting_parts.append("Structure les réponses en sections claires.")
    if f.get("bullets"):
        formatting_parts.append("Utilise des listes à puces.")
    if f.get("emojis"):
        formatting_parts.append("Incorpore des emojis de manière appropriée.")

    if formatting_parts:
        lines.append(" ".join(formatting_parts))

    block = "\n".join(lines)

    # Security: check size
    block_len = len(block)
    if block_len > 1500:
        logger.warning(
            "persona_block_large_warning persona_id=%s length=%d",
            str(persona.id), block_len
        )

    if block_len > 2000:
        raise ValueError(f"Persona block too large: {block_len} characters (max 2000)")

    return block
