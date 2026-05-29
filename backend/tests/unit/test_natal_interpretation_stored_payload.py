# Commentaire global: tests du contrat de stockage accepted/rejected des interpretations natales.
"""Verifie la separation entre payloads acceptes et rejets LLM persistes."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.domain.llm.prompting.schemas import AstroFreeResponseV1, AstroResponseV1
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.services.llm_generation.natal.stored_interpretation_payload import (
    NatalInterpretationRejectedStoredPayload,
    extract_accepted_interpretation_payload,
    is_rejected_interpretation,
    is_rejected_stored_payload,
    parse_rejected_stored_payload,
)

_ACCEPTED_FREE_PAYLOAD = {
    "title": "Mon theme",
    "summary": "Resume valide pour le plan free.",
    "sections": [],
    "highlights": [],
    "advice": [],
    "evidence": [],
}

_ACCEPTED_PREMIUM_PAYLOAD = {
    "title": "Theme complet",
    "summary": "Resume premium valide avec assez de contenu.",
    "sections": [
        {"key": "overall", "heading": "Vue d'ensemble", "content": "Contenu principal."},
        {"key": "strengths", "heading": "Forces", "content": "Contenu complementaire."},
    ],
    "highlights": ["Point A", "Point B", "Point C"],
    "advice": ["Conseil A", "Conseil B", "Conseil C"],
    "evidence": [],
}

_REJECTED_PAYLOAD = {
    "status": "rejected",
    "rejection_reason": {
        "code": "natal_output_policy_violation",
        "failed_sections": ["unsupported_claims"],
        "validation_errors": ["unsupported_generated_claim"],
    },
    "validation_context": [
        {
            "section_id": "unsupported_claims",
            "requires_evidence": True,
            "section_status": "ungrounded",
            "evidence_refs": [
                {
                    "validation_state": "unsupported_source_type",
                    "validation_errors": ["unsupported_generated_claim"],
                    "claims": ["saturne", "vénus"],
                }
            ],
        }
    ],
    "raw_answer_storage": {
        "structured_output": {
            "title": "Titre",
            "summary": "L'astrologie n'est pas une science exacte.",
        }
    },
    "client_message": (
        "Nous n'avons pas assez de preuves fiables pour afficher cette interpretation."
    ),
    "retry_policy": "out_of_scope",
}


def _make_model(
    payload: dict[str, object],
    *,
    grounding_status: str = "grounded",
) -> UserNatalInterpretationModel:
    return UserNatalInterpretationModel(
        id=42,
        user_id=3,
        chart_id="chart-123",
        level=InterpretationLevel.SHORT,
        use_case="natal_interpretation_short",
        interpretation_payload=payload,
        grounding_status=grounding_status,
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )


def test_is_rejected_stored_payload_detects_rejection_contract() -> None:
    assert is_rejected_stored_payload(_REJECTED_PAYLOAD) is True
    assert is_rejected_stored_payload(_ACCEPTED_FREE_PAYLOAD) is False


def test_parse_rejected_stored_payload_validates_contract() -> None:
    parsed = parse_rejected_stored_payload(_REJECTED_PAYLOAD)
    assert isinstance(parsed, NatalInterpretationRejectedStoredPayload)
    assert parsed.status == "rejected"
    assert parsed.retry_policy == "out_of_scope"


def test_extract_accepted_interpretation_payload_rejects_rejected_payload() -> None:
    with pytest.raises(ValueError, match="rejected"):
        extract_accepted_interpretation_payload(_REJECTED_PAYLOAD)


def test_deserialize_accepted_free_interpretation_payload() -> None:
    model = _make_model(_ACCEPTED_FREE_PAYLOAD)
    model.level = InterpretationLevel.COMPLETE
    model.variant_code = "free_short"
    interpretation, schema_version = (
        NatalInterpretationService._deserialize_persisted_interpretation(
            model,
            level="complete",
            locale="fr-FR",
        )
    )
    assert schema_version == "v1"
    assert isinstance(interpretation, AstroFreeResponseV1)
    assert interpretation.summary == _ACCEPTED_FREE_PAYLOAD["summary"]


def test_deserialize_accepted_premium_interpretation_payload() -> None:
    model = _make_model(_ACCEPTED_PREMIUM_PAYLOAD)
    interpretation, schema_version = (
        NatalInterpretationService._deserialize_persisted_interpretation(
            model,
            level="short",
            locale="fr-FR",
        )
    )
    assert schema_version == "v1"
    assert isinstance(interpretation, AstroResponseV1)
    assert interpretation.title == _ACCEPTED_PREMIUM_PAYLOAD["title"]


def test_deserialize_rejected_interpretation_payload_raises_service_error() -> None:
    model = _make_model(_REJECTED_PAYLOAD, grounding_status="rejected")
    with pytest.raises(NatalInterpretationServiceError, match="rejected"):
        NatalInterpretationService._deserialize_persisted_interpretation(
            model,
            level="short",
            locale="fr-FR",
        )


def test_is_rejected_interpretation_uses_grounding_status() -> None:
    model = _make_model(_ACCEPTED_FREE_PAYLOAD, grounding_status="rejected")
    assert is_rejected_interpretation(model) is True


def test_purge_rejected_interpretation_deletes_row() -> None:
    db = MagicMock()
    model = _make_model(_REJECTED_PAYLOAD, grounding_status="rejected")
    deleted = NatalInterpretationService._purge_rejected_interpretation(db, model)
    assert deleted is True
    db.delete.assert_called_once_with(model)


def test_rejected_payload_cannot_be_instantiated_as_astro_response_v1() -> None:
    with pytest.raises(ValidationError):
        AstroResponseV1(**_REJECTED_PAYLOAD, disclaimers=[])


def test_rejected_payload_cannot_be_instantiated_as_astro_free_response_v1() -> None:
    with pytest.raises(ValidationError):
        AstroFreeResponseV1(**_REJECTED_PAYLOAD)
