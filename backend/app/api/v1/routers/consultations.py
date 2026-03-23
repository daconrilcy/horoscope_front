from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
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
from app.services.consultation_catalogue_service import ConsultationCatalogueService
from app.services.consultation_generation_service import ConsultationGenerationService
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.services.consultation_third_party_service import ConsultationThirdPartyService

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
    items = [ConsultationTemplateSchema.from_orm(t) for t in templates]

    return ConsultationCatalogueResponse(
        items=items,
        meta={
            "request_id": request_id,
            "total": len(items)
        }
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
    Gère la compatibilité legacy des clés.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # AC2: Normalisation des clés legacy
    payload.consultation_type = ConsultationCatalogueService.map_legacy_key(payload.consultation_type)

    data = ConsultationPrecheckService.precheck(db, current_user.id, payload)

    return ConsultationPrecheckResponse(
        data=data, meta=ConsultationPrecheckMeta(request_id=request_id)
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
    Gère la compatibilité legacy des clés.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # AC2: Normalisation des clés legacy
    payload.consultation_type = ConsultationCatalogueService.map_legacy_key(payload.consultation_type)

    data = await ConsultationGenerationService.generate(db, current_user.id, payload, request_id)

    return ConsultationGenerateResponse(
        data=data, meta=ConsultationPrecheckMeta(request_id=request_id)
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
