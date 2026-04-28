"""Route publique de désabonnement email à token signé."""

from __future__ import annotations

import logging

import jwt
from fastapi import APIRouter, Query, Response
from fastapi.responses import HTMLResponse

from app.api.errors import raise_api_error
from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.services.email.public_email import (
    _get_confirmation_html,
)
from app.services.email.service import EmailService

router = APIRouter(prefix="/email", tags=["email"])
logger = logging.getLogger(__name__)

NO_STORE_HEADERS = {"Cache-Control": "no-store"}


@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(
    response: Response,
    token: str = Query(...),
) -> str:
    """Désabonne un utilisateur marketing depuis un lien email signé et non authentifié."""
    response.headers.update(NO_STORE_HEADERS)
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
            raise_api_error(
                status_code=400,
                message="Lien de désabonnement non valide",
                headers=NO_STORE_HEADERS,
            )

        if not EmailService.mark_user_unsubscribed(user_id):
            raise_api_error(
                status_code=400,
                message="Utilisateur non trouvé",
                headers=NO_STORE_HEADERS,
            )
        return _get_confirmation_html(
            success=True, message="Vous avez bien été désabonné de nos emails marketing."
        )

    except jwt.ExpiredSignatureError:
        raise_api_error(
            status_code=400,
            message="Le lien de désabonnement a expiré",
            headers=NO_STORE_HEADERS,
        )
    except jwt.InvalidTokenError:
        raise_api_error(
            status_code=400,
            message="Lien de désabonnement invalide",
            headers=NO_STORE_HEADERS,
        )
    except ApplicationError:
        raise
    except Exception:
        logger.exception("unsubscribe_failed")
        raise_api_error(
            status_code=400,
            message="Une erreur est survenue lors du désabonnement",
            headers=NO_STORE_HEADERS,
        )
