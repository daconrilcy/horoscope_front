"""Contrats de sortie editoriale deterministe pour les aspects.

Ces structures portent l'assemblage lisible issu des profils, sans appeler de
runtime LLM et sans redefinir les axes semantiques.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AspectEditorialInterpretation:
    """Interpretation editoriale structuree d'un aspect."""

    summary: str
    psychological_meaning: tuple[str, ...]
    relationship_expression: tuple[str, ...]
    shadow_expression: tuple[str, ...]
    growth_path: tuple[str, ...]
    source_profile_code: str | None = None
