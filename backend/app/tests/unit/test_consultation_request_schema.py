"""Vérifie la normalisation canonique des types de consultation à l'entrée API."""

from app.api.v1.schemas.consultation import (
    ConsultationGenerateRequest,
    ConsultationPrecheckRequest,
)


def test_precheck_request_normalizes_legacy_consultation_type() -> None:
    """Les aliases legacy doivent être convertis dès la validation du schéma."""
    request = ConsultationPrecheckRequest(consultation_type="work")

    assert request.consultation_type == "career"


def test_generate_request_normalizes_legacy_consultation_type() -> None:
    """La route generate doit consommer la clé canonique dès l'entrée."""
    request = ConsultationGenerateRequest(
        consultation_type="relation",
        question="Que comprendre de cette relation ?",
    )

    assert request.consultation_type == "relationship"
