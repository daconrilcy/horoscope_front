# Commentaire global: contrat de stockage accepted/rejected des interpretations natales.
"""Distingue les payloads acceptes des rejets LLM persistes pour audit interne."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.domain.astrology.reading.basic_natal_contracts import (
    BASIC_NATAL_DEGRADED_BASELINE_TOKENS,
    BASIC_NATAL_MIN_EDITORIAL_CONTRACT_VERSION,
    BasicNatalInterpretationV2,
)
from app.domain.llm.prompting.narrative_natal_reading_v1 import (
    NARRATIVE_NATAL_READING_PAYLOAD_KEY,
    NarrativeNatalReadingV1,
)
from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel

NARRATIVE_ANSWER_AUDIT_USE_CASE = "narrative_answer_audit_v1"
CORRECTIVE_REGENERATION_PENDING_USE_CASE = "natal_corrective_regeneration_pending"
BASIC_NATAL_INTERPRETATION_V2_PAYLOAD_KEY = "basic_natal_interpretation_v2"

REJECTED_PAYLOAD_MARKER_KEYS = frozenset(
    {
        "rejection_reason",
        "validation_context",
        "raw_answer_storage",
        "retry_policy",
    }
)


class NatalInterpretationRejectedStoredPayload(BaseModel):
    """Contrat interne d'un rejet LLM stocke pour audit et non expose comme interpretation."""

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
    if model.use_case in {
        NARRATIVE_ANSWER_AUDIT_USE_CASE,
        CORRECTIVE_REGENERATION_PENDING_USE_CASE,
    }:
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
    excluded = set(REJECTED_PAYLOAD_MARKER_KEYS) | {NARRATIVE_NATAL_READING_PAYLOAD_KEY}
    return {key: value for key, value in payload.items() if key not in excluded}


def extract_narrative_reading_payload(payload: dict[str, object]) -> dict[str, object] | None:
    """Lit le fragment narratif public stocke a cote du schema AstroResponse."""
    nested = payload.get(NARRATIVE_NATAL_READING_PAYLOAD_KEY)
    return nested if isinstance(nested, dict) else None


def load_narrative_reading_from_payload(
    payload: dict[str, object],
) -> NarrativeNatalReadingV1 | None:
    """Deserialise la lecture narrative publique si elle est presente et valide."""
    nested = extract_narrative_reading_payload(payload)
    if nested is None:
        return None
    try:
        reading = NarrativeNatalReadingV1.model_validate(nested)
    except ValidationError:
        return None
    from app.services.llm_generation.natal.narrative_natal_reading_validator import (
        validate_narrative_reading_public_text,
    )

    if validate_narrative_reading_public_text(reading):
        return None
    return reading


def load_basic_natal_interpretation_v2_from_payload(
    payload: dict[str, object],
) -> BasicNatalInterpretationV2 | None:
    """Deserialise la lecture Basic V2 compatible depuis le payload accepte."""
    if contains_degraded_basic_natal_baseline_token(payload):
        return None
    nested = payload.get(BASIC_NATAL_INTERPRETATION_V2_PAYLOAD_KEY)
    if not isinstance(nested, dict):
        return None
    if nested.get("basic_editorial_contract_version") != BASIC_NATAL_MIN_EDITORIAL_CONTRACT_VERSION:
        return None
    try:
        return BasicNatalInterpretationV2.model_validate(nested)
    except ValidationError:
        return None


def contains_degraded_basic_natal_baseline_token(value: object) -> bool:
    """Detecte les fragments publics Basic issus des anciennes sorties degradees."""
    if isinstance(value, str):
        normalized = value.casefold()
        return any(token.casefold() in normalized for token in BASIC_NATAL_DEGRADED_BASELINE_TOKENS)
    if isinstance(value, dict):
        return any(contains_degraded_basic_natal_baseline_token(item) for item in value.values())
    if isinstance(value, list | tuple):
        return any(contains_degraded_basic_natal_baseline_token(item) for item in value)
    return False


def has_compatible_basic_natal_interpretation_v2(payload: dict[str, object]) -> bool:
    """Indique si le cache Basic porte les versions publiques V2 attendues."""
    return load_basic_natal_interpretation_v2_from_payload(payload) is not None
