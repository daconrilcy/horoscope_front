"""Endpoint de statut Swiss Ephemeris.

Expose l'état du bootstrap Swiss Ephemeris pour le diagnostic et les tests
d'intégration. Aucune authentification requise (information de configuration
non sensible — le path brut n'est jamais exposé).
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.core import ephemeris
from app.core.config import settings

router = APIRouter()


@router.get("/v1/ephemeris/status", tags=["ephemeris"])
def ephemeris_status() -> JSONResponse:
    """Retourne l'état du bootstrap Swiss Ephemeris.

    - ``200 {"status": "disabled"}`` : SWISSEPH_ENABLED=false (défaut en dev)
    - ``200 {"status": "ok", "path_version": "..."}`` : bootstrap réussi
    - ``503 {"error": {"code": "ephemeris_data_missing", ...}}`` : path absent/invalide
    - ``503 {"error": {"code": "swisseph_init_failed", ...}}`` : init runtime échouée
    - ``503 {"error": {"code": "swisseph_not_initialized", ...}}`` : activé mais bootstrap
      non encore appelé (ne devrait pas se produire en production)
    """
    if not settings.swisseph_enabled:
        return JSONResponse(content={"status": "disabled"})

    result = ephemeris.get_bootstrap_result()

    if result is None:
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "swisseph_not_initialized",
                    "message": "Swiss Ephemeris is enabled but bootstrap has not run",
                }
            },
        )

    if result.success:
        return JSONResponse(
            content={
                "status": "ok",
                "path_version": result.path_version,
            }
        )

    err = result.error
    code = err.code if err is not None else "swisseph_init_failed"
    message = err.message if err is not None else "Swiss Ephemeris initialization failed"
    return JSONResponse(
        status_code=HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )
