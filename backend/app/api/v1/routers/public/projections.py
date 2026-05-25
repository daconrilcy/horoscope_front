# Route publique canonique des projections B2C natales.
"""Expose `POST /v1/astrology/projections` sans surface interne ou alternative."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors.raising import raise_api_error
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.projections import (
    ProjectionCommandRequest,
    ProjectionCommandResponse,
)
from app.services.projections.projection_endpoint_service import (
    ProjectionEndpointService,
    ProjectionEndpointServiceError,
)

router = APIRouter(prefix="/v1/astrology", tags=["astrology-projections"])
_PROJECTION_ERROR_STATUS_CODES = {
    "projection.invalid_chart_source": status.HTTP_400_BAD_REQUEST,
    "projection.unauthorized": status.HTTP_403_FORBIDDEN,
    "projection.chart_not_found": status.HTTP_404_NOT_FOUND,
    "projection.dependency_unavailable": status.HTTP_409_CONFLICT,
    "projection.invalid_payload": 422,
}


def get_projection_endpoint_service(
    db=Depends(get_db_session),
) -> ProjectionEndpointService:
    """Construit le service applicatif canonique pour la commande HTTP."""
    return ProjectionEndpointService(db)


@router.post(
    "/projections",
    response_model=ProjectionCommandResponse,
    responses={
        400: {"model": ErrorEnvelope},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def create_projection(
    request: Request,
    response: Response,
    payload: ProjectionCommandRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    service: ProjectionEndpointService = Depends(get_projection_endpoint_service),
) -> ProjectionCommandResponse:
    """Genere une projection B2C publique depuis chart_id ou birth_input."""
    try:
        result = service.generate(
            request=payload,
            current_user=current_user,
            request_id=resolve_request_id(request),
        )
    except ProjectionEndpointServiceError as exc:
        raise_api_error(
            status_code=_PROJECTION_ERROR_STATUS_CODES[exc.code],
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
    if result.persisted:
        response.status_code = 201
    return result
