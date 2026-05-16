"""Service applicatif des préférences publiques utilisateur."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infra.db.models.reference import LanguageModel
from app.infra.db.models.user import UserModel
from app.services.api_contracts.public.users import UserSettingsPatchRequest

COUNTRY_CODE_PATTERN = re.compile(r"^[A-Z]{2}$")


class UserSettingsServiceError(Exception):
    """Erreur contrôlée lors de la lecture ou mise à jour des préférences utilisateur."""

    def __init__(self, code: str, message: str, details: dict[str, object] | None = None) -> None:
        """Initialise une erreur métier exposable par le routeur HTTP."""
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def normalize_optional_text(value: str | None) -> str | None:
    """Nettoie une valeur optionnelle issue du navigateur sans inventer de fallback."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def normalize_country_code(value: str | None) -> str | None:
    """Normalise un code pays ISO alpha-2 optionnel."""
    normalized = normalize_optional_text(value)
    return normalized.upper() if normalized is not None else None


def settings_payload(user: UserModel) -> dict[str, object]:
    """Construit la réponse settings sans dupliquer la forme entre GET et PATCH."""
    return {
        "astrologer_profile": user.astrologer_profile,
        "default_astrologer_id": user.default_astrologer_id,
        "default_language_code": (
            user.default_language.code if user.default_language is not None else None
        ),
        "detected_locale": user.detected_locale,
        "detected_country_code": user.detected_country_code,
        "detected_timezone": user.detected_timezone,
    }


class UserSettingsService:
    """Orchestre la persistance des préférences utilisateur hors de la couche HTTP."""

    @staticmethod
    def get_for_user(db: Session, user_id: int) -> dict[str, object]:
        """Retourne les préférences publiques d'un utilisateur."""
        user = db.get(UserModel, user_id)
        if not user:
            raise UserSettingsServiceError("user_not_found", "user not found")
        return settings_payload(user)

    @staticmethod
    def patch_for_user(
        db: Session,
        user_id: int,
        payload: UserSettingsPatchRequest,
        valid_astrologer_profiles: set[str],
    ) -> dict[str, object]:
        """Applique une mise à jour partielle des préférences utilisateur."""
        if (
            payload.astrologer_profile is not None
            and payload.astrologer_profile not in valid_astrologer_profiles
        ):
            raise UserSettingsServiceError(
                "invalid_astrologer_profile",
                f"profile must be one of {valid_astrologer_profiles}",
                {"allowed_values": list(valid_astrologer_profiles)},
            )

        user = db.get(UserModel, user_id)
        if not user:
            raise UserSettingsServiceError("user_not_found", "user not found")

        update_data = payload.model_dump(exclude_unset=True)
        if "astrologer_profile" in update_data:
            user.astrologer_profile = update_data["astrologer_profile"]
        if "default_astrologer_id" in update_data:
            user.default_astrologer_id = update_data["default_astrologer_id"]
        if "default_language_code" in update_data:
            language_code = update_data["default_language_code"]
            if language_code is None:
                user.default_language_id = None
            else:
                language = db.scalar(
                    select(LanguageModel).where(LanguageModel.code == language_code)
                )
                if language is None:
                    raise UserSettingsServiceError(
                        "invalid_default_language",
                        "language code is not supported",
                        {"language_code": language_code},
                    )
                user.default_language_id = language.id
        if "detected_locale" in update_data:
            user.detected_locale = normalize_optional_text(update_data["detected_locale"])
        if "detected_country_code" in update_data:
            detected_country_code = normalize_country_code(update_data["detected_country_code"])
            if detected_country_code is not None and not COUNTRY_CODE_PATTERN.fullmatch(
                detected_country_code
            ):
                raise UserSettingsServiceError(
                    "invalid_detected_country_code",
                    "detected country code must be an ISO alpha-2 code",
                    {"detected_country_code": update_data["detected_country_code"]},
                )
            user.detected_country_code = detected_country_code
        if "detected_timezone" in update_data:
            user.detected_timezone = normalize_optional_text(update_data["detected_timezone"])

        try:
            db.commit()
            db.refresh(user)
        except SQLAlchemyError as error:
            db.rollback()
            raise UserSettingsServiceError(
                "user_settings_persistence_error",
                "user settings could not be persisted",
            ) from error
        return settings_payload(user)
