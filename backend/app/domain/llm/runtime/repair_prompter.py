from __future__ import annotations

import re
from typing import Any, List

# Patterns indicating density violations in error messages (v3 schema)
_DENSITY_ERROR_PATTERNS = re.compile(
    r"too short|minLength|minItems|min_length|min_items|is too short",
    re.IGNORECASE,
)

_V3_DENSITY_GUIDANCE = (
    "\n\nCONTRAINTES DE DENSITÉ OBLIGATOIRES (schéma v3) :\n"
    "- summary : minimum 900 caractères (développe avec plus de détails astrologiques)\n"
    "- sections : minimum 5 sections, chaque content >= 280 caractères\n"
    "- highlights : minimum 5 éléments\n"
    "- advice : minimum 5 éléments\n"
    "IMPORTANT : Développe le contenu pour atteindre ces minimums — ne tronque pas."
)


def build_repair_prompt(raw_output: str, errors: List[str], json_schema: dict[str, Any]) -> str:
    """
    Builds a prompt to ask the LLM to fix its previous invalid output.

    For v3 density violations (minLength/minItems errors), adds targeted density guidance
    so the LLM knows exactly which constraints to satisfy.
    """
    # Extract schema summary (required fields and their types)
    required = json_schema.get("required", [])
    properties = json_schema.get("properties", {})

    schema_summary_parts = []
    for field in required:
        prop_info = properties.get(field, {})
        field_type = prop_info.get("type", "any")
        schema_summary_parts.append(f"- {field} ({field_type})")

    schema_summary = "\n".join(schema_summary_parts)

    error_list = "\n".join([f"- {e}" for e in errors])

    # Detect v3 density violations to add targeted guidance
    has_density_violations = any(_DENSITY_ERROR_PATTERNS.search(e) for e in errors)
    density_block = _V3_DENSITY_GUIDANCE if has_density_violations else ""

    prompt = (
        "La réponse précédente n'est pas conforme au format attendu.\n\n"
        f"Erreurs détectées :\n{error_list}\n\n"
        f"Champs requis et formats :\n{schema_summary}"
        f"{density_block}\n\n"
        f"Réponse originale (à corriger) :\n{raw_output}\n\n"
        "CONSIGNE : Corrige uniquement le format en produisant un JSON valide conforme au schéma. "
        "Ne modifie pas le contenu métier sauf pour satisfaire les contraintes de format (types, longueurs, énumérations). "  # noqa: E501
        "Réponds EXCLUSIVEMENT avec le bloc JSON."
    )

    return prompt
