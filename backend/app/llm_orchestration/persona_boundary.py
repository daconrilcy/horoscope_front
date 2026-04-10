from __future__ import annotations

import logging
import re
from typing import Literal

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PersonaBoundaryViolation(BaseModel):
    dimension: str
    severity: Literal["WARNING", "ERROR"]
    excerpt: str
    persona_id: str


# AC11: Persona Boundary Policy (Story 66.10 D3)
PERSONA_BOUNDARY_POLICY = {
    "allowed_dimensions": [
        "tone",
        "warmth",
        "vocabulary",
        "symbolism_level",
        "explanatory_density",
        "formulation_style",
    ],
    "forbidden_patterns": {
        "output_contract": [
            r"répondre? en json",
            r"format de sortie json",
            r"schéma json",
            r"structure de réponse",
            r"respond in json",
            r"clé \"[a-z_]+\"",
            r"field \"[a-z_]+\"",
        ],
        "hard_policy": [
            r"ignore(r|s)? les (règles|instructions|contraintes)",
            r"ignore (all )?(previous )?(system )?instructions",
            r"bypass(er)? (security|safety|instructions)",
            r"oublie les instructions précédentes",
            r"désactive la sécurité",
            r"sans restriction aucune",
            r"passer outre les consignes système",
        ],
        "model_choice": [
            r"utilise le modèle (gpt|claude|o1)",
            r"passe au modèle",
            r"switch to model",
            r"\b(gpt-4|gpt-5|claude-3|o1-preview)\b",
        ],
        "plan_rules": [
            r"si l'utilisateur est (en plan gratuit|premium)",
            r"abonnement (free|premium|payant)",
            r"uniquement pour les comptes",
            r"limite de \d+ caractères",
            r"premium only",
            r"free plan",
        ],
    },
    "severity_map": {
        "output_contract": "WARNING",
        "hard_policy": "ERROR",
        "model_choice": "WARNING",
        "plan_rules": "WARNING",
    },
}

# Note Dev: Les patterns interdits sont des heuristiques (L4 fix).
# Préférer des expressions composées (verbe + objet) aux mots simples pour limiter les faux positifs.


def validate_persona_block(persona_content: str, persona_id: str) -> list[PersonaBoundaryViolation]:
    """
    Detects if a persona block attempts to redefine forbidden dimensions.
    Returns a list of violations.
    """
    violations = []
    content_lower = persona_content.lower()

    for dimension, patterns in PERSONA_BOUNDARY_POLICY["forbidden_patterns"].items():
        for pattern in patterns:
            match = re.search(pattern, content_lower)
            if match:
                severity = PERSONA_BOUNDARY_POLICY["severity_map"].get(dimension, "WARNING")

                # Extract excerpt around match
                start = max(0, match.start() - 30)
                end = min(len(persona_content), match.end() + 30)
                excerpt = persona_content[start:end]

                violations.append(
                    PersonaBoundaryViolation(
                        dimension=dimension,
                        severity=severity,
                        excerpt=f"...{excerpt}...",
                        persona_id=persona_id,
                    )
                )
                # One match per dimension is enough for the report
                break

    return violations
