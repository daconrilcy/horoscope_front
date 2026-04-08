from __future__ import annotations

import re
import logging
from typing import Literal, Optional
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
            r"json",
            r"format de sortie",
            r"schéma",
            r"structure de réponse",
            r"respond in json",
            r"clé",
            r"field",
        ],
        "hard_policy": [
            r"ignore",
            r"bypass",
            r"oublie",
            r"désactive",
            r"sans restriction",
            r"instruction système",
            r"passer outre",
        ],
        "model_choice": [
            r"utilise le modèle",
            r"passe à",
            r"switch to model",
            r"gpt-",
            r"claude-",
            r"o1-",
        ],
        "plan_rules": [
            r"plan gratuit",
            r"abonnement",
            r"premium only",
            r"payant",
            r"limite de caractères",
        ],
    },
    "severity_map": {
        "output_contract": "WARNING",
        "hard_policy": "ERROR",
        "model_choice": "WARNING",
        "plan_rules": "WARNING",
    },
}

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
                
                violations.append(PersonaBoundaryViolation(
                    dimension=dimension,
                    severity=severity,
                    excerpt=f"...{excerpt}...",
                    persona_id=persona_id
                ))
                # One match per dimension is enough for the report
                break

    return violations
