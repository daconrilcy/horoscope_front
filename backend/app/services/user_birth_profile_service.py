"""
Service de gestion des profils de naissance utilisateur.

Ce module gère les profils de naissance des utilisateurs : création,
mise à jour et récupération des données de naissance.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.astrology.natal_preparation import BirthInput, prepare_birth_data
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.repositories.geo_place_resolved_repository import GeoPlaceResolvedRepository
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


logger = logging.getLogger(__name__)


class UserBirthProfileData(BaseModel):
    """Données du profil de naissance d'un utilisateur."""

    birth_date: str
    birth_time: str | None
    # Kept for backward compatibility with existing clients.
    birth_place: str
    # Source UX canonical text for birth place.
    birth_place_text: str | None = None
    birth_timezone: str
    birth_city: str | None = None
    birth_country: str | None = None
    birth_lat: float | None = None
    birth_lon: float | None = None
    birth_place_resolved_id: int | None = None
    birth_place_resolved: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ResolvedBirthCoordinates:
    """Coordonnées de naissance résolues avec indication de source."""

    birth_lat: float | None
    birth_lon: float | None
    birth_place_resolved_id: int | None
    resolved_from_place: bool


def _resolved_place_to_dict(model: GeoPlaceResolvedModel) -> dict[str, Any]:
    return {
        "id": model.id,
        "provider": model.provider,
        "provider_place_id": model.provider_place_id,
        "display_name": model.display_name,
        "latitude": float(model.latitude),
        "longitude": float(model.longitude),
        "timezone_iana": model.timezone_iana,
    }


class UserBirthProfileService:
    """
    Service de gestion des profils de naissance.

    Gère les données de naissance des utilisateurs nécessaires
    aux calculs astrologiques.
    """

    @staticmethod
    def resolve_coordinates(
        db: Session,
        profile: UserBirthProfileData,
    ) -> ResolvedBirthCoordinates:
        """
        Résout les coordonnées de naissance de façon canonique.

        Priorité:
        1. `birth_place_resolved_id` valide et existant.
        2. Fallback legacy `birth_lat` / `birth_lon`.
        """
        resolved_fk = (
            profile.birth_place_resolved_id
            if isinstance(profile.birth_place_resolved_id, int)
            and profile.birth_place_resolved_id > 0
            else None
        )
        if resolved_fk is None:
            return ResolvedBirthCoordinates(
                birth_lat=profile.birth_lat,
                birth_lon=profile.birth_lon,
                birth_place_resolved_id=None,
                resolved_from_place=False,
            )

        resolved_place = GeoPlaceResolvedRepository(db).find_by_id(resolved_fk)
        if resolved_place is None:
            return ResolvedBirthCoordinates(
                birth_lat=profile.birth_lat,
                birth_lon=profile.birth_lon,
                birth_place_resolved_id=resolved_fk,
                resolved_from_place=False,
            )

        return ResolvedBirthCoordinates(
            birth_lat=float(resolved_place.latitude),
            birth_lon=float(resolved_place.longitude),
            birth_place_resolved_id=resolved_fk,
            resolved_from_place=True,
        )

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
        resolved_place = None
        if model.birth_place_resolved_id is not None:
            resolved_model = GeoPlaceResolvedRepository(db).find_by_id(
                model.birth_place_resolved_id
            )
            if resolved_model is not None:
                resolved_place = _resolved_place_to_dict(resolved_model)
            else:
                logger.warning(
                    "orphaned birth_place_resolved_id detected",
                    extra={
                        "user_id": user_id,
                        "birth_place_resolved_id": model.birth_place_resolved_id,
                    },
                )

        return UserBirthProfileData(
            birth_date=model.birth_date.isoformat(),
            birth_time=model.birth_time,
            birth_place=model.birth_place,
            birth_place_text=model.birth_place,
            birth_timezone=model.birth_timezone,
            birth_city=model.birth_city,
            birth_country=model.birth_country,
            birth_lat=model.birth_lat,
            birth_lon=model.birth_lon,
            birth_place_resolved_id=model.birth_place_resolved_id,
            birth_place_resolved=resolved_place,
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
        if payload.place_resolved_id is not None:
            resolved = GeoPlaceResolvedRepository(db).find_by_id(payload.place_resolved_id)
            if resolved is None:
                raise UserBirthProfileServiceError(
                    code="birth_place_resolved_not_found",
                    message="birth place resolved not found",
                    details={"place_resolved_id": str(payload.place_resolved_id)},
                )

        model = UserBirthProfileRepository(db).upsert(
            user_id=user_id,
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place,
            birth_timezone=payload.birth_timezone,
            birth_city=payload.birth_city,
            birth_country=payload.birth_country,
            birth_lat=payload.birth_lat,
            birth_lon=payload.birth_lon,
            birth_place_resolved_id=payload.place_resolved_id,
        )
        resolved_place = None
        if model.birth_place_resolved_id is not None:
            resolved_model = GeoPlaceResolvedRepository(db).find_by_id(
                model.birth_place_resolved_id
            )
            if resolved_model is not None:
                resolved_place = _resolved_place_to_dict(resolved_model)
            else:
                logger.warning(
                    "orphaned birth_place_resolved_id detected",
                    extra={
                        "user_id": user_id,
                        "birth_place_resolved_id": model.birth_place_resolved_id,
                    },
                )

        return UserBirthProfileData(
            birth_date=model.birth_date.isoformat(),
            birth_time=model.birth_time,
            birth_place=model.birth_place,
            birth_place_text=model.birth_place,
            birth_timezone=model.birth_timezone,
            birth_city=model.birth_city,
            birth_country=model.birth_country,
            birth_lat=model.birth_lat,
            birth_lon=model.birth_lon,
            birth_place_resolved_id=model.birth_place_resolved_id,
            birth_place_resolved=resolved_place,
        )
