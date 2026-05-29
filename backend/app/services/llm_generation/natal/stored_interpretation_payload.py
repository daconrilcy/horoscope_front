# Commentaire global: contrat de stockage accepted/rejected des interpretations natales.
"""Distingue les payloads acceptes des rejets LLM persistes pour audit interne."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel

NARRATIVE_ANSWER_AUDIT_USE_CASE = "narrative_answer_audit_v1"

REJECTED_PAYLOAD_MARKER_KEYS = frozenset(
    {
        "rejection_reason",
        "validation_context",
        "raw_answer_storage",
        "retry_policy",
    }
)


class NatalInterpretationRejectedStoredPayload(BaseModel):
    """Contrat interne d'un rejet LLM stocke pour audit, jamais expose comme interpretation."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["rejected"] = "rejected"
    rejection_reason: dict[str, object]
    validation_context: list[dict[str, object]]
    raw_answer_storage: dict[str, object]
    client_message: str = Field(..., min_length=1)
    retry_policy: Literal["retryable", "out_of_scope", "manual_review"] = "out_of_scope"


def is_rejected_stored_payload(payload: object) -> bool:
    """Indique si un payload JSON correspond au contrat de rejet interne."""
    if not isinstance(payload, dict):
        return False
    if payload.get("status") == "rejected":
        return True
    return any(key in payload for key in REJECTED_PAYLOAD_MARKER_KEYS)


def is_rejected_interpretation(model: UserNatalInterpretationModel) -> bool:
    """Detecte une ligne d'interpretation rejetee via l'audit ou le payload."""
    if model.grounding_status == "rejected":
        return True
    return is_rejected_stored_payload(model.interpretation_payload)


def is_public_natal_interpretation(model: UserNatalInterpretationModel) -> bool:
    """Indique si une ligne peut etre exposee comme interpretation utilisateur."""
    if model.use_case == NARRATIVE_ANSWER_AUDIT_USE_CASE:
        return False
    return not is_rejected_interpretation(model)


def parse_rejected_stored_payload(
    payload: dict[str, object],
) -> NatalInterpretationRejectedStoredPayload:
    """Valide strictement un payload de rejet avant usage interne."""
    return NatalInterpretationRejectedStoredPayload.model_validate(payload)


def extract_accepted_interpretation_payload(payload: dict[str, object]) -> dict[str, object]:
    """Retire les metadonnees de rejet avant instanciation AstroResponseV1/V2/V3."""
    if is_rejected_stored_payload(payload):
        raise ValueError("Cannot extract accepted payload from rejected stored interpretation")
    return {key: value for key, value in payload.items() if key not in REJECTED_PAYLOAD_MARKER_KEYS}
