# Commentaire global: couvre le mapping HTTP stable de la façade publique Astral.
"""Tests du routeur public Astral et de son mapping d'erreurs."""

from __future__ import annotations

from app.api.v1.routers.public.astral import _resolve_astral_error_status
from app.services.astral.integration_service import AstralIntegrationServiceError


def test_resolve_astral_error_status_preserves_upstream_http_status() -> None:
    """Préserve le statut upstream quand Astral a déjà qualifié l'erreur."""
    error = AstralIntegrationServiceError(
        "astral_upstream_error",
        "Astral service returned an error",
        details={"upstream_http_status": 401},
    )

    assert _resolve_astral_error_status(error) == 401


def test_resolve_astral_error_status_falls_back_to_catalog_when_missing() -> None:
    """Revient au catalogue applicatif si le statut upstream n'est pas exploitable."""
    error = AstralIntegrationServiceError(
        "unsupported_astral_product_plan",
        "unsupported Astral product and plan combination",
        details={"upstream_http_status": "401"},
    )

    assert _resolve_astral_error_status(error) == 422
