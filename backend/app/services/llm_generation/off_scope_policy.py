"""Porte les règles partagées de détection hors-scope pour les services LLM métier."""

from __future__ import annotations


def assess_off_scope(content: str) -> tuple[bool, float, str | None]:
    """Évalue si une réponse paraît hors périmètre et retourne un score de confiance."""
    normalized = content.strip().lower()
    if not normalized:
        return True, 1.0, "empty_response"
    if "[off_scope]" in normalized:
        return True, 0.95, "explicit_marker"
    if normalized.startswith("hors_scope:"):
        return True, 0.9, "explicit_prefix"
    return False, 0.0, None
