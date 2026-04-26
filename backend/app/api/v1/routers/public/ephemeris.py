"""Endpoint de statut Swiss Ephemeris.

Expose l'état du bootstrap Swiss Ephemeris pour le diagnostic et les tests
d'intégration. Aucune authentification requise (information de configuration
non sensible — le path brut n'est jamais exposé).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.core import ephemeris
from app.core.config import settings
from app.core.ephemeris import EphemerisDataMissingError
from app.core.request_id import resolve_request_id

router = APIRouter()


@router.get("/v1/ephemeris/status", tags=["ephemeris"])
def ephemeris_status(request: Request) -> JSONResponse:
    """Retourne l'état du bootstrap Swiss Ephemeris.

    - ``200 {"status": "disabled"}`` : SWISSEPH_ENABLED=false (défaut en dev)
    - ``200 {"status": "ok", "path_version": "..."}`` : bootstrap réussi
    - ``503 {"error": {"code": "ephemeris_data_missing", ...}}`` : path absent/invalide
    - ``503 {"error": {"code": "swisseph_init_failed", ...}}`` : init runtime échouée
    - ``503 {"error": {"code": "swisseph_not_initialized", ...}}`` : activé mais bootstrap
      non encore appelé (ne devrait pas se produire en production)
    """
    request_id = resolve_request_id(request)

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
                    "details": {},
                    "request_id": request_id,
                }
            },
        )

    if result.success:
        return JSONResponse(
            content={
                "status": "ok",
                "path_version": result.path_version,
                "path_hash": result.path_hash or None,
            }
        )

    err = result.error
    code = err.code if err is not None else "swisseph_init_failed"
    message = err.message if err is not None else "Swiss Ephemeris initialization failed"
    details: dict[str, Any] = {}
    if isinstance(err, EphemerisDataMissingError) and getattr(err, "missing_file", None):
        details["missing_file"] = err.missing_file
    return JSONResponse(
        status_code=HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )
