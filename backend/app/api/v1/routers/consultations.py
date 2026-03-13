from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.schemas.consultation import (
    ConsultationPrecheckRequest,
    ConsultationPrecheckResponse,
    ConsultationPrecheckMeta,
    ConsultationGenerateRequest,
    ConsultationGenerateResponse
)
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session as get_db
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.services.consultation_generation_service import ConsultationGenerationService

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

@router.post("/generate", response_model=ConsultationGenerateResponse)
async def generate_consultation(
    request: Request,
    payload: ConsultationGenerateRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """
    Génère le contenu complet d'une consultation.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    data = await ConsultationGenerationService.generate(db, current_user.id, payload, request_id)
    
    return ConsultationGenerateResponse(
        data=data,
        meta=ConsultationPrecheckMeta(
            request_id=request_id
        )
    )
