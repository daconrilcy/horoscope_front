from __future__ import annotations

from typing import Any, List


def build_repair_prompt(raw_output: str, errors: List[str], json_schema: dict[str, Any]) -> str:
    """
    Builds a prompt to ask the LLM to fix its previous invalid output.
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

    prompt = (
        "La réponse précédente n'est pas conforme au format attendu.\n\n"
        f"Erreurs détectées :\n{error_list}\n\n"
        f"Champs requis et formats :\n{schema_summary}\n\n"
        f"Réponse originale (à corriger) :\n{raw_output}\n\n"
        "CONSIGNE : Corrige uniquement le format en produisant un JSON valide conforme au schéma. "
        "Ne modifie pas le contenu métier sauf pour satisfaire les contraintes de format (types, longueurs, énumérations). "  # noqa: E501
        "Réponds EXCLUSIVEMENT avec le bloc JSON."
    )

    return prompt
