# Commentaire global: couvre le mapping HTTP stable de la façade publique Astral.
"""Tests du routeur public Astral et de son mapping d'erreurs."""

from __future__ import annotations

import logging

from app.api.v1.routers.public.astral import (
    PUBLIC_ASTRAL_ERROR_CODE,
    _log_failed_astral_job,
    _public_astral_error_payload,
    _public_astral_job_data,
    _resolve_astral_error_status,
)
from app.services.astral.integration_service import AstralIntegrationServiceError


def test_resolve_astral_error_status_hides_upstream_auth_status() -> None:
    """Ne transforme pas une erreur auth Astral en expiration de session utilisateur."""
    error = AstralIntegrationServiceError(
        "astral_upstream_error",
        "Astral service returned an error",
        details={"upstream_http_status": 401},
    )

    assert _resolve_astral_error_status(error) == 503


def test_resolve_astral_error_status_falls_back_to_catalog_when_missing() -> None:
    """Revient au catalogue applicatif si le statut upstream n'est pas exploitable."""
    error = AstralIntegrationServiceError(
        "unsupported_astral_product_plan",
        "unsupported Astral product and plan combination",
        details={"upstream_http_status": "401"},
    )

    assert _resolve_astral_error_status(error) == 422


def test_public_astral_error_payload_hides_upstream_details() -> None:
    """Masque les détails techniques Astral dans la réponse HTTP publique."""
    error = AstralIntegrationServiceError(
        "ASTRO_BASIS_INVALID",
        "chapter cites unknown astro fact_id",
        details={
            "upstream_http_status": 422,
            "fact_id": "placement:Milieu du Ciel:aries:house:10",
        },
    )

    code, message, details = _public_astral_error_payload(error)

    assert code == PUBLIC_ASTRAL_ERROR_CODE
    assert "fact_id" not in message
    assert details == {}


def test_public_astral_job_data_hides_terminal_error_details() -> None:
    """Masque les détails techniques d'un job failed avant retour au navigateur."""
    data = {
        "run_id": "run-failed",
        "status": "failed",
        "service_code": "natal_basic",
        "error": {
            "code": "ASTRO_BASIS_INVALID",
            "message": "chapter cites unknown astro fact_id",
            "details": {"fact_id": "placement:Milieu du Ciel:aries:house:10"},
        },
    }

    public_data = _public_astral_job_data(data)

    assert public_data["error"]["code"] == PUBLIC_ASTRAL_ERROR_CODE
    assert "fact_id" not in str(public_data["error"])
    assert data["error"]["code"] == "ASTRO_BASIS_INVALID"


def test_public_astral_job_data_hides_nested_reading_error_details() -> None:
    """Masque aussi les erreurs de lecture quand le job externe est completed."""
    data = {
        "run_id": "run-completed-failed-reading",
        "status": "completed",
        "service_code": "natal_basic",
        "result": {
            "reading": {
                "status": "failed",
                "error": {
                    "code": "ASTRO_BASIS_INVALID",
                    "message": "chapter cites unknown astro fact_id",
                    "details": {"fact_id": "placement:Milieu du Ciel:aries:house:10"},
                },
            },
        },
    }

    public_data = _public_astral_job_data(data)

    public_error = public_data["result"]["reading"]["error"]
    assert public_error["code"] == PUBLIC_ASTRAL_ERROR_CODE
    assert "fact_id" not in str(public_error)
    assert data["result"]["reading"]["error"]["code"] == "ASTRO_BASIS_INVALID"


def test_public_astral_error_payload_keeps_local_validation_details() -> None:
    """Conserve les erreurs applicatives locales non issues du module Astral."""
    error = AstralIntegrationServiceError(
        "unsupported_astral_product_plan",
        "unsupported Astral product and plan combination",
        details={"product": "unknown"},
    )

    code, message, details = _public_astral_error_payload(error)

    assert code == "unsupported_astral_product_plan"
    assert message == "unsupported Astral product and plan combination"
    assert details == {"product": "unknown"}


def test_public_astral_error_payload_keeps_local_astral_prefixed_error() -> None:
    """Ne masque pas une erreur locale dont le code commence par astral_."""
    error = AstralIntegrationServiceError(
        "astral_chart_calculation_required",
        "horoscope jobs require an Astral chart_calculation_id",
        details={"product": "horoscope_daily"},
    )

    code, message, details = _public_astral_error_payload(error)

    assert code == "astral_chart_calculation_required"
    assert "chart_calculation_id" in message
    assert details == {"product": "horoscope_daily"}


def test_failed_astral_job_logs_full_backend_detail(caplog) -> None:
    """Loggue le détail complet du job failed sans passer par l'UI."""
    caplog.set_level(logging.ERROR, logger="app.api.v1.routers.public.astral")

    _log_failed_astral_job(
        request_id="request-1",
        data={
            "run_id": "run-failed",
            "status": "failed",
            "service_code": "natal_basic",
            "error": {
                "code": "ASTRO_BASIS_INVALID",
                "details": {"fact_id": "placement:Milieu du Ciel:aries:house:10"},
            },
        },
        context={"run_id": "run-failed"},
    )

    assert "ASTRO_BASIS_INVALID" in caplog.text
    assert "placement:Milieu du Ciel:aries:house:10" in caplog.text


def test_nested_failed_astral_reading_logs_full_backend_detail(caplog) -> None:
    """Loggue aussi les échecs imbriqués dans result.reading."""
    caplog.set_level(logging.ERROR, logger="app.api.v1.routers.public.astral")

    _log_failed_astral_job(
        request_id="request-1",
        data={
            "run_id": "run-completed-failed-reading",
            "status": "completed",
            "service_code": "natal_basic",
            "result": {
                "reading": {
                    "status": "failed",
                    "error": {
                        "code": "ASTRO_BASIS_INVALID",
                        "details": {"fact_id": "placement:Milieu du Ciel:aries:house:10"},
                    },
                },
            },
        },
        context={"run_id": "run-completed-failed-reading"},
    )

    assert "ASTRO_BASIS_INVALID" in caplog.text
    assert "placement:Milieu du Ciel:aries:house:10" in caplog.text
