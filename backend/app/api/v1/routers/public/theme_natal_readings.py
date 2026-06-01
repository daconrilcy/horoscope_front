# Commentaire global: routeur public des commandes produit de lecture theme natal.
"""Expose la surface publique action-based pour les lectures theme natal."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.theme_natal_readings import (
    ThemeNatalReadingCommandRequest,
    ThemeNatalReadingCommandResponse,
)
from app.services.llm_generation.natal.theme_natal_product_actions import (
    execute_theme_natal_reading_product_action,
)

router = APIRouter(prefix="/v1/theme-natal", tags=["theme-natal-readings"])


@router.post(
    "/readings",
    response_model=ThemeNatalReadingCommandResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
async def create_theme_natal_reading(
    body: ThemeNatalReadingCommandRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> ThemeNatalReadingCommandResponse:
    """Transmet la commande publique au service produit canonique."""
    return execute_theme_natal_reading_product_action(
        db,
        user_id=current_user.id,
        command=body,
    )
