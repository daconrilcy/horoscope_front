"""
Service d'astrologie B2B.

Ce module fournit les fonctionnalités d'astrologie pour les partenaires B2B,
notamment la génération de résumés hebdomadaires par signe.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.reference import SignModel
from app.services.b2b_editorial_service import B2BEditorialConfigData, B2BEditorialService


class B2BAstrologyServiceError(Exception):
    """Exception levée lors d'erreurs du service d'astrologie B2B."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur d'astrologie B2B.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class WeeklyBySignItem(BaseModel):
    """Résumé hebdomadaire pour un signe astrologique."""

    sign_code: str
    sign_name: str
    weekly_summary: str


class WeeklyBySignData(BaseModel):
    """Données complètes des résumés hebdomadaires par signe."""

    api_version: str
    reference_version: str
    generated_at: datetime
    items: list[WeeklyBySignItem]


class B2BAstrologyService:
    """
    Service d'astrologie pour partenaires B2B.

    Génère du contenu astrologique personnalisé selon la configuration
    éditoriale du compte entreprise.
    """
    @staticmethod
    def get_weekly_by_sign(
        db: Session,
        *,
        editorial_config: B2BEditorialConfigData | None = None,
    ) -> WeeklyBySignData:
        """
        Génère les résumés hebdomadaires pour tous les signes astrologiques.

        Args:
            db: Session de base de données.
            editorial_config: Configuration éditoriale optionnelle pour personnaliser
                le ton et le style du contenu.

        Returns:
            WeeklyBySignData contenant les résumés pour chaque signe.

        Raises:
            B2BAstrologyServiceError: Si les données de référence sont indisponibles.
        """
        signs = db.scalars(
            select(SignModel)
            .where(SignModel.reference_version_id.is_not(None))
            .order_by(SignModel.id.asc())
        ).all()
        if not signs:
            raise B2BAstrologyServiceError(
                code="reference_data_unavailable",
                message="reference data is unavailable",
                details={},
            )

        config = editorial_config or B2BEditorialService.default_config(account_id=0)
        items = [
            WeeklyBySignItem(
                sign_code=sign.code,
                sign_name=sign.name,
                weekly_summary=B2BEditorialService.render_weekly_summary(
                    sign_name=sign.name,
                    config=config,
                ),
            )
            for sign in signs
        ]
        return WeeklyBySignData(
            api_version="v1",
            reference_version=settings.active_reference_version,
            generated_at=datetime.now(timezone.utc),
            items=items,
        )
