from __future__ import annotations

import logging

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.api.v1.router_logic.public.email import (
    _get_confirmation_html,
)
from app.core.config import settings
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session

router = APIRouter(prefix="/email", tags=["email"])
logger = logging.getLogger(__name__)


@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(token: str = Query(...), db: Session = Depends(get_db_session)) -> str:
    """
    AC2: Endpoint to unsubscribe a user via a token.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")
        email_type = payload.get("email_type")

        marketing_types = {
            "marketing",
            "onboarding_j1_education",
            "onboarding_j3_social_proof",
            "onboarding_j5_objections",
            "onboarding_j7_upgrade",
        }

        if not user_id or email_type not in marketing_types:
            raise HTTPException(status_code=400, detail="Lien de désabonnement non valide")

        # AC2: Check if user exists and update
        result = db.execute(
            update(UserModel).where(UserModel.id == user_id).values(email_unsubscribed=True)
        )
        db.commit()

        if result.rowcount == 0:
            # If the user doesn't exist, we don't want to leak that info too much,
            # but for a link like this, a 400 is fine.
            raise HTTPException(status_code=400, detail="Utilisateur non trouvé")

        return _get_confirmation_html(
            success=True, message="Vous avez bien été désabonné de nos emails marketing."
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Le lien de désabonnement a expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Lien de désabonnement invalide")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unsubscribe error: {str(e)}")
        raise HTTPException(status_code=400, detail="Une erreur est survenue lors du désabonnement")
