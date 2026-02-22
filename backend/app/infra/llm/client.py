"""
DEPRECATED: Ce module est déprécié et sera supprimé dans une version future.

Utilisez le nouveau module AI Engine à la place:
- Pour le chat: app.ai_engine.services.chat_service
- Pour les guidances: app.ai_engine.services.generate_service avec les use_cases guidance_*
- Pour l'intégration dans les services existants: app.services.ai_engine_adapter

Le AI Engine offre:
- De vrais appels OpenAI au lieu de simples échos
- Rate limiting et cache
- Logs structurés et métriques
- Prompts centralisés via le Prompt Registry
"""

from __future__ import annotations

import warnings


class LLMClient:
    """
    DEPRECATED: Utilisez AIEngineAdapter ou les services du module ai_engine.

    Ce stub est conservé uniquement pour la rétrocompatibilité pendant la migration.
    Il sera supprimé dans une version future.
    """

    def __init__(self) -> None:
        """Initialize LLMClient with deprecation warning."""
        warnings.warn(
            "LLMClient is deprecated. Use AIEngineAdapter or ai_engine services instead. "
            "See app.services.ai_engine_adapter for migration guide.",
            DeprecationWarning,
            stacklevel=2,
        )

    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        """
        DEPRECATED: Generate a reply (stub implementation).

        Args:
            prompt: The prompt to send to the LLM.
            timeout_seconds: Timeout in seconds (unused in stub).

        Returns:
            Echo of the prompt (stub behavior).

        Raises:
            TimeoutError: If prompt contains 'simulate_timeout'.
            ConnectionError: If prompt contains 'simulate_unavailable'.
        """
        lowered = prompt.lower()
        if "simulate_timeout" in lowered:
            raise TimeoutError("llm timeout")
        if "simulate_unavailable" in lowered:
            raise ConnectionError("llm unavailable")
        return f"Guidance astrologique: {prompt.strip()}"
