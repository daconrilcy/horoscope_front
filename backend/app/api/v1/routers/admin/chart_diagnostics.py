# Commentaire global: ce routeur expose le diagnostic de calcul astrologique aux administrateurs.
"""Route admin protegee pour `admin_chart_diagnostics_v1`."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_admin_user,
    require_authenticated_user,
)
from app.api.errors import raise_api_error
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.admin.chart_diagnostics import (
    AdminChartDiagnosticsResponse,
)
from app.services.ops.admin_chart_diagnostics import (
    AdminChartDiagnosticsService,
    AdminChartDiagnosticsSourceMissingError,
)

router = APIRouter(prefix="/v1/admin/audit", tags=["admin-audit"])


def require_admin_user_with_audit(
    chart_reference: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> AuthenticatedUser:
    """Controle le role admin et journalise les refus authentifies."""
    if user.role != "admin":
        AdminChartDiagnosticsService.record_failed_consultation(
            db,
            chart_reference=chart_reference,
            request_id=resolve_request_id(request),
            current_user=user,
            decision="denied",
            error_code="insufficient_role",
        )
        db.commit()
    return require_admin_user(user)


@router.get(
    "/admin_chart_diagnostics_v1/{chart_reference}",
    response_model=AdminChartDiagnosticsResponse,
)
def get_admin_chart_diagnostics(
    chart_reference: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user_with_audit),
    db: Session = Depends(get_db_session),
) -> AdminChartDiagnosticsResponse:
    """Consulte un diagnostic de calcul masque et journalise l'acces admin."""
    try:
        response = AdminChartDiagnosticsService.get_chart_diagnostics(
            db,
            chart_reference=chart_reference,
            request_id=resolve_request_id(request),
            current_user=current_user,
        )
        db.commit()
        return response
    except AdminChartDiagnosticsSourceMissingError as error:
        db.commit()
        raise_api_error(
            status_code=404,
            code="admin_chart_diagnostics_source_missing",
            message="Chart diagnostic source not found",
            details={"chart_reference": error.chart_reference},
        )
