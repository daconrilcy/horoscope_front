from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.infra.db.models.llm.llm_persona import LlmPersonaModel

logger = logging.getLogger(__name__)

TONE_MAPPINGS = {
    "warm": "chaleureux et empathique",
    "calm": "chaleureux et empathique",  # Legacy mapping (calm -> warm)
    "direct": "direct et factuel",
    "mystical": "mystique et inspirant",
    "rational": "rationnel et analytique",
}

VERBOSITY_MAPPINGS = {
    "short": "synthétique",
    "medium": "équilibrée",
    "long": "approfondie",
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
    Uses the dedicated prompt profile if available, otherwise falls back to legacy fields.
    """
    # 1. Try to find the active dedicated prompt profile
    # We look for the first active one. In theory there should only be one active per persona.
    prompt_profiles = getattr(persona, "prompt_profiles", []) or []
    active_prompts = [prompt for prompt in prompt_profiles if prompt.is_active]
    active_prompts.sort(
        key=lambda prompt: (
            getattr(prompt, "updated_at", None) or datetime.min.replace(tzinfo=timezone.utc)
        ),
        reverse=True,
    )
    active_prompt = active_prompts[0] if active_prompts else None

    if active_prompt:
        persona_name = _sanitize_string(persona.name)
        prompt_content = _sanitize_string(active_prompt.prompt_content)
        # We still add a header for structure
        block = f"## Directives de persona : {persona_name}\n{prompt_content}"

        # 3. Boundary validation (Story 66.10 AC2, AC3, AC4)
        try:
            from app.domain.llm.prompting.persona_boundary import validate_persona_block

            violations = validate_persona_block(block, str(persona.id))
            for v in violations:
                msg = (
                    f"persona_boundary_violation: {v.dimension} detected in persona block "
                    f"id={v.persona_id}. Severity={v.severity}. Excerpt: {v.excerpt}"
                )
                if v.severity == "ERROR":
                    logger.error(msg)
                else:
                    logger.warning(msg)
        except Exception as e:
            logger.debug("persona_boundary_validation_skipped: %s", e)

        # Security: check size
        block_len = len(block)
        if block_len > 3000:
            raise ValueError(f"Persona block too large: {block_len} characters (max 3000)")

        return block

    # 2. Legacy fallback
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
    boundaries = persona.boundaries
    if isinstance(boundaries, str):
        boundaries = [b.strip() for b in boundaries.splitlines() if b.strip()]
    if boundaries:
        lines.append("Contraintes éditoriales :")
        for boundary in boundaries:
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
    f = persona.formatting if isinstance(persona.formatting, dict) else {}
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

    # 3. Boundary validation (Story 66.10 AC2, AC3, AC4)
    try:
        from app.domain.llm.prompting.persona_boundary import validate_persona_block

        violations = validate_persona_block(block, str(persona.id))
        for v in violations:
            msg = (
                f"persona_boundary_violation: {v.dimension} detected in persona block "
                f"id={v.persona_id}. Severity={v.severity}. Excerpt: {v.excerpt}"
            )
            if v.severity == "ERROR":
                logger.error(msg)
            else:
                logger.warning(msg)
    except Exception as e:
        logger.debug("persona_boundary_validation_skipped: %s", e)

    # Security: check size
    block_len = len(block)
    if block_len > 1500:
        logger.warning(
            "persona_block_large_warning persona_id=%s length=%d", str(persona.id), block_len
        )

    if block_len > 2000:
        raise ValueError(f"Persona block too large: {block_len} characters (max 2000)")

    return block
