from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.schemas.consultation import (
    ConsultationPrecheckRequest,
    ConsultationPrecheckResponse,
    ConsultationPrecheckMeta,
)
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session as get_db
from app.services.consultation_precheck_service import ConsultationPrecheckService

router = APIRouter()

@router.post("/precheck", response_model=ConsultationPrecheckResponse)
def precheck_consultation(
    request: Request,
    payload: ConsultationPrecheckRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """
    Exécute un précheck de complétude et d'éligibilité pour une consultation.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    data = ConsultationPrecheckService.precheck(db, current_user.id, payload)
    
    return ConsultationPrecheckResponse(
        data=data,
        meta=ConsultationPrecheckMeta(
            request_id=request_id
        )
    )
