from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# AC3, AC4: Context Quality Instructions (Story 66.14 D3)
CONTEXT_QUALITY_INSTRUCTIONS: dict[str, dict[str, str]] = {
    "generic": {
        "partial": "[CONTEXTE PARTIEL] Certaines informations sont manquantes. Compense les trous en restant cohérent avec les données disponibles.",
        "minimal": "[CONTEXTE LIMITÉ] Les données disponibles sont incomplètes. Formule tes interprétations avec prudence et pédagogie, en évitant les affirmations trop catégoriques.",
    },
    "natal": {
        "partial": "[CONTEXTE NATAL PARTIEL] Les données de naissance sont incomplètes. Concentre-toi sur les aspects disponibles et évite de conclure sur les maisons si l'heure est absente.",
        "minimal": "[CONTEXTE NATAL LIMITÉ] Tu ne disposes que de données minimales. Ne fais pas d'affirmations définitives. Explique que l'analyse est partielle et encourage l'utilisateur à compléter son profil.",
    },
    "guidance": {
        "partial": "[CONTEXTE GUIDANCE PARTIEL] La situation de l'utilisateur n'est que partiellement connue. Reste nuancé dans tes conseils.",
        "minimal": "[CONTEXTE GUIDANCE MINIMAL] Tu ignores presque tout de la situation actuelle. Pose des questions ouvertes et reste très général dans tes prédictions.",
    },
}


class ContextQualityInjector:
    """
    Injects compensation instructions based on context quality (Story 66.14 D1, D3).
    """

    @staticmethod
    def inject(developer_prompt: str, feature: str, context_quality: str) -> tuple[str, bool]:
        """
        Returns the augmented prompt and a boolean indicating if an injection was made.
        """
        if context_quality == "full":
            return developer_prompt, False

        # Check if the template already handles context_quality explicitly
        if f"{{{{#context_quality:{context_quality}}}}}" in developer_prompt:
            # Explicitly handled by template, no automatic injection
            return developer_prompt, False

        # Get specific or generic instruction
        # Normalize feature key
        feat_key = feature.split("_")[0] if "_" in feature else feature
        instructions = CONTEXT_QUALITY_INSTRUCTIONS.get(
            feat_key, CONTEXT_QUALITY_INSTRUCTIONS["generic"]
        )

        instruction = instructions.get(context_quality)
        if not instruction:
            # Try generic if feature-specific didn't have the level
            instruction = CONTEXT_QUALITY_INSTRUCTIONS["generic"].get(context_quality)

        if not instruction:
            return developer_prompt, False

        augmented = f"{developer_prompt}\n\n{instruction}"
        return augmented, True
