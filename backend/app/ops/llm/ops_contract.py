"""
Artefact contractuel canonique pour l'observabilité d'exploitation LLM (Story 66.37).

Cette couche centralise:
- les états ``unknown`` tolérés ;
- les combinaisons impossibles ;
- les seuils gouvernés d'alerte ;
- la représentation canonique des labels persona côté ops.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.domain.llm.runtime.contracts import ExecutionPathKind, FallbackType

PERMITTED_UNKNOWN_PATHS: set[str] = {
    "transitional_governance:unknown",
}

IMPOSSIBLE_COMBINATIONS = [
    {
        "pipeline_kind": "nominal_canonical",
        "execution_path_kind": ExecutionPathKind.LEGACY_USE_CASE_FALLBACK,
    },
    {
        "pipeline_kind": "nominal_canonical",
        "execution_path_kind": ExecutionPathKind.LEGACY_EXECUTION_PROFILE_FALLBACK,
    },
    {
        "pipeline_kind": "nominal_canonical",
        "fallback_kind": FallbackType.LEGACY_WRAPPER,
    },
    {
        "pipeline_kind": "nominal_canonical",
        "fallback_kind": FallbackType.USE_CASE_FIRST,
    },
]

REPAIR_RATE_THRESHOLD = 0.05
REPAIR_MIN_OCCURRENCES = 10
REPAIR_RATE_BASELINE_MULTIPLIER = 2.0
REPAIR_RATE_MIN_DELTA = 0.05

NOMINAL_FAMILIES = {"chat", "guidance", "natal", "horoscope_daily"}
PERSONA_LABEL_SENTINELS = {"unknown", "ungoverned"}


def canonical_persona_label(persona_id: Any) -> str:
    """
    Produit le label ops canonique d'un persona.

    Les labels d'alerte restent bornés et ne dépendent jamais d'un libellé éditorial.
    """
    if persona_id is None:
        return "unknown"
    if isinstance(persona_id, uuid.UUID):
        return str(persona_id)
    raw_value = str(persona_id).strip()
    if not raw_value:
        return "unknown"
    return raw_value


def is_persona_governed(persona_label: str | None) -> bool:
    """
    Vérifie qu'un label persona est canonique et sûr pour l'alerting.
    """
    if persona_label is None:
        return True
    if persona_label in PERSONA_LABEL_SENTINELS:
        return True
    try:
        uuid.UUID(str(persona_label))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def is_impossible_state(
    pipeline_kind: str | None,
    execution_path_kind: str | None,
    fallback_kind: str | None,
    requested_provider: str | None = None,
    executed_provider: str | None = None,
) -> bool:
    """
    Vérifie si l'état runtime observé viole explicitement le contrat canonique.
    """
    if not pipeline_kind:
        return False

    for combo in IMPOSSIBLE_COMBINATIONS:
        match = True
        if combo.get("pipeline_kind") != pipeline_kind:
            match = False
        if "execution_path_kind" in combo:
            expected_path = combo["execution_path_kind"].value
            if execution_path_kind != expected_path:
                match = False
        if "fallback_kind" in combo:
            expected_fallback = combo["fallback_kind"].value
            if fallback_kind != expected_fallback:
                match = False
        if match:
            return True

    if (
        pipeline_kind == "nominal_canonical"
        and execution_path_kind == ExecutionPathKind.CANONICAL_ASSEMBLY.value
        and fallback_kind not in (None, "")
    ):
        return True

    if (
        pipeline_kind == "nominal_canonical"
        and execution_path_kind == ExecutionPathKind.CANONICAL_ASSEMBLY.value
        and requested_provider
        and executed_provider
        and requested_provider != executed_provider
        and fallback_kind in (None, "")
    ):
        return True

    return False


def is_unknown_allowed(pipeline_kind: str, execution_path_kind: str) -> bool:
    """Vérifie si le couple ``pipeline_kind``/``execution_path_kind`` tolère ``unknown``."""
    return f"{pipeline_kind}:{execution_path_kind}" in PERMITTED_UNKNOWN_PATHS


__all__ = [
    "NOMINAL_FAMILIES",
    "PERSONA_LABEL_SENTINELS",
    "PERMITTED_UNKNOWN_PATHS",
    "IMPOSSIBLE_COMBINATIONS",
    "REPAIR_MIN_OCCURRENCES",
    "REPAIR_RATE_BASELINE_MULTIPLIER",
    "REPAIR_RATE_MIN_DELTA",
    "REPAIR_RATE_THRESHOLD",
    "canonical_persona_label",
    "is_persona_governed",
    "is_impossible_state",
    "is_unknown_allowed",
]
