"""
Service de calcul du profil astrologique utilisateur.

Ce module calcule le signe solaire et l'ascendant à partir du profil natal,
en appliquant la règle null-time : si l'heure de naissance est absente,
l'ascendant n'est pas calculé et missing_birth_time vaut True.
"""

from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_calculation import NatalCalculationError
from app.domain.astrology.natal_preparation import BirthInput
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


class UserAstroProfileServiceError(Exception):
    """Exception levée lors d'erreurs du profil astrologique."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class UserAstroProfileData(BaseModel):
    """Données du profil astrologique calculé."""

    sun_sign_code: str | None
    ascendant_sign_code: str | None
    missing_birth_time: bool


ZODIAC_ORDER = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]


def _sign_from_longitude(longitude: float) -> str:
    normalized = longitude % 360.0
    sign_index = int(normalized // 30.0) % 12
    return ZODIAC_ORDER[sign_index]


class UserAstroProfileService:
    """
    Service de calcul du profil astrologique.

    Calcule le signe solaire et l'ascendant en cohérence avec le moteur
    astrologique existant. Applique la règle null-time stricte :
    ascendant non calculé si l'heure de naissance est absente.
    """

    @staticmethod
    def get_for_user(db: Session, user_id: int) -> UserAstroProfileData:
        """
        Calcule le profil astrologique d'un utilisateur.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            Profil astrologique avec signe solaire, ascendant et indicateur null-time.

        Raises:
            UserAstroProfileServiceError: Si le profil natal est introuvable.
        """
        try:
            profile = UserBirthProfileService.get_for_user(db, user_id)
        except UserBirthProfileServiceError as error:
            raise UserAstroProfileServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        birth_input = BirthInput(
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_place=profile.birth_place,
            birth_timezone=profile.birth_timezone,
        )

        try:
            natal_result = NatalCalculationService.calculate(db, birth_input=birth_input)
        except NatalCalculationError as error:
            should_auto_seed = (
                error.code == "reference_version_not_found"
                and settings.active_reference_version
            )
            if should_auto_seed:
                ReferenceDataService.seed_reference_version(
                    db, version=settings.active_reference_version
                )
                natal_result = NatalCalculationService.calculate(db, birth_input=birth_input)
            else:
                raise UserAstroProfileServiceError(
                    code=error.code,
                    message=error.message,
                    details=error.details,
                ) from error

        sun_position = next(
            (planet for planet in natal_result.planet_positions if planet.planet_code == "sun"),
            None,
        )
        sun_sign_code = (
            _sign_from_longitude(sun_position.longitude) if sun_position is not None else None
        )

        if profile.birth_time is None:
            return UserAstroProfileData(
                sun_sign_code=sun_sign_code,
                ascendant_sign_code=None,
                missing_birth_time=True,
            )

        first_house = next(
            (house for house in natal_result.houses if house.number == 1),
            None,
        )
        ascendant_sign_code = (
            _sign_from_longitude(first_house.cusp_longitude) if first_house is not None else None
        )
        return UserAstroProfileData(
            sun_sign_code=sun_sign_code,
            ascendant_sign_code=ascendant_sign_code,
            missing_birth_time=False,
        )
