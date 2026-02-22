"""
Service de gestion des profils de naissance utilisateur.

Ce module gère les profils de naissance des utilisateurs : création,
mise à jour et récupération des données de naissance.
"""

from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.astrology.natal_preparation import BirthInput, prepare_birth_data
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.infra.db.repositories.user_repository import UserRepository


class UserBirthProfileServiceError(Exception):
    """Exception levée lors d'erreurs de profil de naissance."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de profil de naissance.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class UserBirthProfileData(BaseModel):
    """Données du profil de naissance d'un utilisateur."""

    birth_date: str
    birth_time: str
    birth_place: str
    birth_timezone: str


class UserBirthProfileService:
    """
    Service de gestion des profils de naissance.

    Gère les données de naissance des utilisateurs nécessaires
    aux calculs astrologiques.
    """
    @staticmethod
    def get_for_user(db: Session, user_id: int) -> UserBirthProfileData:
        """
        Récupère le profil de naissance d'un utilisateur.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            Données du profil de naissance.

        Raises:
            UserBirthProfileServiceError: Si le profil n'existe pas.
        """
        model = UserBirthProfileRepository(db).get_by_user_id(user_id)
        if model is None:
            raise UserBirthProfileServiceError(
                code="birth_profile_not_found",
                message="birth profile not found",
                details={"user_id": str(user_id)},
            )
        return UserBirthProfileData(
            birth_date=model.birth_date.isoformat(),
            birth_time=model.birth_time,
            birth_place=model.birth_place,
            birth_timezone=model.birth_timezone,
        )

    @staticmethod
    def upsert_for_user(db: Session, user_id: int, payload: BirthInput) -> UserBirthProfileData:
        """
        Crée ou met à jour le profil de naissance d'un utilisateur.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            payload: Données de naissance à enregistrer.

        Returns:
            Données du profil créé ou mis à jour.

        Raises:
            UserBirthProfileServiceError: Si l'utilisateur n'existe pas.
        """
        if UserRepository(db).get_by_id(user_id) is None:
            raise UserBirthProfileServiceError(
                code="user_not_found",
                message="user not found",
                details={"user_id": str(user_id)},
            )

        # Reuse existing preparation for deterministic birth-data validation.
        prepare_birth_data(payload)
        model = UserBirthProfileRepository(db).upsert(
            user_id=user_id,
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place,
            birth_timezone=payload.birth_timezone,
        )
        return UserBirthProfileData(
            birth_date=model.birth_date.isoformat(),
            birth_time=model.birth_time,
            birth_place=model.birth_place,
            birth_timezone=model.birth_timezone,
        )
