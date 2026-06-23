# Commentaire global: routeur public des données de référence non astrologiques.
"""Expose les données de référence applicatives conservées après externalisation Astral."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.errors import build_error_response
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.public.reference_data import LanguagesApiResponse
from app.services.reference_data.language_service import (
    ReferenceLanguageService,
    ReferenceLanguageServiceError,
)

router = APIRouter(prefix="/v1/reference-data", tags=["reference-data"])
logger = logging.getLogger(__name__)


@router.get(
    "/languages",
    response_model=LanguagesApiResponse,
)
def list_languages(
    request: Request,
    db: Session = Depends(get_db_session),
) -> dict[str, object] | JSONResponse:
    """Retourne les langues canoniques disponibles dans la table `languages`."""
    request_id = resolve_request_id(request)
    try:
        languages = ReferenceLanguageService.list_languages(db)
    except ReferenceLanguageServiceError as error:
        logger.exception(
            "reference languages lookup failed",
            extra={"request_id": request_id},
        )
        return build_error_response(
            status_code=500,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return {
        "data": languages,
        "meta": {"request_id": request_id},
    }
