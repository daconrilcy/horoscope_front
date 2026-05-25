# Route publique unique pour la projection client transit proof-gated.
"""Expose transit_client_projection_v1 sans publier le runtime interne."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.services.api_contracts.public.transit_projection import TransitProjectionResponse
from app.services.transit_projection.access_gate import (
    TransitProjectionAccessDenied,
    TransitProjectionAccessResolver,
    TransitProjectionQuotaDenied,
    get_transit_projection_access_resolver,
)
from app.services.transit_projection.client_projection import TransitClientProjectionService
from app.services.transit_projection.proof_gate import (
    TransitProjectionProofGate,
    TransitProjectionProofGateUnavailable,
)

router = APIRouter(prefix="/v1/transit", tags=["transit"])


def get_transit_projection_proof_gate() -> TransitProjectionProofGate:
    """Retourne le proof gate canonique de la projection transit."""
    return TransitProjectionProofGate()


def get_transit_client_projection_service() -> TransitClientProjectionService:
    """Retourne l'assembleur canonique de projection transit client."""
    return TransitClientProjectionService()


@router.get(
    "/projection",
    response_model=TransitProjectionResponse,
    responses={200: {}, 403: {}, 409: {}, 503: {}},
)
def get_transit_projection(
    request: Request,
    response: Response,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    access_resolver: TransitProjectionAccessResolver = Depends(
        get_transit_projection_access_resolver
    ),
    proof_gate: TransitProjectionProofGate = Depends(get_transit_projection_proof_gate),
    projection_service: TransitClientProjectionService = Depends(
        get_transit_client_projection_service
    ),
) -> TransitProjectionResponse:
    """Expose la projection transit uniquement apres preuve et gate B2C."""
    del request
    if current_user.role not in {"user", "admin"}:
        response.status_code = 403
        return projection_service.unavailable(
            plan_code="free",
            reason="unauthorized_role",
        ).model_copy(update={"status": "unauthorized"})

    try:
        proof_result = proof_gate.validate()
    except TransitProjectionProofGateUnavailable as exc:
        response.status_code = 503
        return projection_service.unavailable(
            plan_code="free",
            reason=exc.reason_code,
        )
    if not proof_result.is_valid:
        response.status_code = 409
        return projection_service.unavailable(
            plan_code="free",
            reason="proof_gate_missing_evidence",
        ).model_copy(update={"status": "proof_blocked"})

    try:
        access = access_resolver.resolve(current_user)
    except TransitProjectionAccessDenied as exc:
        response.status_code = 403
        return projection_service.unavailable(
            plan_code=exc.plan_code,
            reason=exc.reason_code or exc.reason,
        ).model_copy(update={"status": "unauthorized"})
    except TransitProjectionQuotaDenied as exc:
        response.status_code = 403
        return projection_service.unavailable(
            plan_code="free",
            reason=f"quota_exhausted:{exc.quota_key}",
        ).model_copy(update={"status": "unauthorized"})

    return projection_service.build(
        plan_code=access.plan_code,
        proof_refs=proof_result.public_refs,
    )
