"""Service de lecture du référentiel public des langues."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infra.db.models.reference import LanguageModel


class ReferenceLanguageServiceError(Exception):
    """Erreur contrôlée lors de la lecture des langues publiques."""

    def __init__(self, code: str, message: str, details: dict[str, object] | None = None) -> None:
        """Initialise une erreur métier exposable par le routeur HTTP."""
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ReferenceLanguageService:
    """Extrait la lecture des langues hors de la couche routeur."""

    @staticmethod
    def list_languages(db: Session) -> list[dict[str, str]]:
        """Retourne les langues disponibles triées par code stable."""
        try:
            languages = db.query(LanguageModel).order_by(LanguageModel.code.asc()).all()
        except SQLAlchemyError as error:
            raise ReferenceLanguageServiceError(
                "reference_languages_unavailable",
                "reference languages could not be loaded",
            ) from error
        return [{"code": item.code, "name": item.name} for item in languages]
