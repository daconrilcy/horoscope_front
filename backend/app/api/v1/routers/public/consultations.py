from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.router_logic.public.consultations import (
    _build_consultation_quota_info,
)
from app.api.v1.schemas.consultation import (
    ConsultationCatalogueResponse,
    ConsultationGenerateRequest,
    ConsultationGenerateResponse,
    ConsultationPrecheckMeta,
    ConsultationPrecheckRequest,
    ConsultationPrecheckResponse,
    ConsultationTemplateSchema,
    ConsultationThirdPartyListMeta,
    ConsultationThirdPartyListResponse,
    ConsultationThirdPartyProfile,
    ConsultationThirdPartyProfileCreate,
)
from app.infra.db.session import get_db_session as get_db
from app.services.consultation.catalogue_service import ConsultationCatalogueService
from app.services.consultation.precheck_service import ConsultationPrecheckService
from app.services.consultation.third_party_service import ConsultationThirdPartyService
from app.services.entitlement.thematic_consultation_entitlement_gate import (
    ConsultationAccessDeniedError,
    ConsultationQuotaExceededError,
    ThematicConsultationEntitlementGate,
)
from app.services.llm_generation.consultation_generation_service import (
    ConsultationGenerationService,
)

router = APIRouter()


@router.get("/catalogue", response_model=ConsultationCatalogueResponse)
def get_catalogue(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """
    Récupère le catalogue public des consultations types piloté par la base.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    templates = ConsultationCatalogueService.get_catalogue(db)

    # Conversion en schémas
    items = [ConsultationTemplateSchema.model_validate(t) for t in templates]

    return ConsultationCatalogueResponse(
        items=items, meta={"request_id": request_id, "total": len(items)}
    )


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
        data=data, meta=ConsultationPrecheckMeta(request_id=request_id)
    )


@router.post(
    "/generate",
    response_model=ConsultationGenerateResponse,
    responses={403: {"description": "Accès refusé"}, 429: {"description": "Quota épuisé"}},
)
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

    try:
        entitlement_result = ThematicConsultationEntitlementGate.check_access(
            db, user_id=current_user.id
        )
    except ConsultationQuotaExceededError as error:
        db.rollback()
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "consultation_quota_exceeded",
                    "message": "quota de consultations thématiques épuisé",
                    "details": {
                        "quota_key": error.quota_key,
                        "used": error.used,
                        "limit": error.limit,
                        "reason_code": "quota_exhausted",
                        "window_end": error.window_end.isoformat() if error.window_end else None,
                    },
                    "request_id": request_id,
                }
            },
        )
    except ConsultationAccessDeniedError as error:
        db.rollback()
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "consultation_access_denied",
                    "message": "accès aux consultations thématiques refusé",
                    "details": {
                        "reason": error.reason,
                        "reason_code": error.reason_code,
                        "billing_status": error.billing_status,
                    },
                    "request_id": request_id,
                }
            },
        )

    quota_info = _build_consultation_quota_info(entitlement_result)

    data = await ConsultationGenerationService.generate(
        db, current_user.id, payload, request_id, entitlement_result=entitlement_result
    )
    db.commit()

    return ConsultationGenerateResponse(
        data=data,
        meta=ConsultationPrecheckMeta(request_id=request_id),
        quota_info=quota_info,
    )


@router.get("/third-parties", response_model=ConsultationThirdPartyListResponse)
def list_third_parties(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """
    Liste les profils tiers enregistrés de l'utilisateur.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    items = ConsultationThirdPartyService.list_third_parties(db, current_user.id)

    return ConsultationThirdPartyListResponse(
        items=items, meta=ConsultationThirdPartyListMeta(request_id=request_id)
    )


@router.post("/third-parties", response_model=ConsultationThirdPartyProfile)
def create_third_party(
    payload: ConsultationThirdPartyProfileCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """
    Crée un nouveau profil tiers.
    """
    return ConsultationThirdPartyService.create_third_party(db, current_user.id, payload)
