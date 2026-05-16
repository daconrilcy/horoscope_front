"""Résout les libellés astrologiques localisés depuis les référentiels DB."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import (
    AspectModel,
    AstralSignModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
)
from app.infra.db.models.translation_reference import (
    AstralAspectTranslationModel,
    AstralHouseTranslationModel,
    AstralPlanetTranslationModel,
    AstralSignTranslationModel,
)
from app.infra.db.models.user import UserModel

SYSTEM_LANGUAGE_CODE = "fr"


@dataclass(frozen=True)
class AstrologyLabels:
    """Contrat immuable de libellés astrologiques déjà résolus."""

    sign_labels: dict[str, str]
    effective_language_code: str
    planet_labels: dict[str, str] = field(default_factory=dict)
    aspect_labels: dict[str, str] = field(default_factory=dict)
    house_labels: dict[str, str] = field(default_factory=dict)

    @classmethod
    def technical_fallback(cls) -> "AstrologyLabels":
        """Construit un contrat qui retourne les codes canoniques."""
        return cls(
            sign_labels={},
            planet_labels={},
            aspect_labels={},
            house_labels={},
            effective_language_code=SYSTEM_LANGUAGE_CODE,
        )

    def sign_label(self, sign_code: str | None) -> str:
        """Retourne le libellé localisé d'un signe ou son code canonique."""
        if not sign_code:
            return ""
        return self.sign_labels.get(sign_code, sign_code)

    def planet_label(self, planet_code: str | None) -> str:
        """Retourne le libellé localisé d'une planète ou son code canonique."""
        if not planet_code:
            return ""
        return self.planet_labels.get(planet_code, planet_code)

    def aspect_label(self, aspect_code: str | None) -> str:
        """Retourne le libellé localisé d'un aspect ou son code canonique."""
        if not aspect_code:
            return ""
        return self.aspect_labels.get(aspect_code, aspect_code)

    def house_label(self, house_number: int | str | None) -> str:
        """Retourne le libellé localisé d'une maison ou son numéro canonique."""
        if house_number is None:
            return ""
        code = str(house_number)
        return self.house_labels.get(code, code)


class AstrologyTranslationResolver:
    """Résout les libellés de signes selon la langue demandée et l'utilisateur."""

    def __init__(self, db: Session) -> None:
        """Initialise le resolver avec la session SQLAlchemy appelante."""
        self._db = db

    def resolve_labels(
        self,
        *,
        language_code: str | None = None,
        user_id: int | None = None,
    ) -> AstrologyLabels:
        """Résout les libellés en respectant l'ordre explicite, utilisateur, système."""
        requested_codes = self._language_preference_codes(
            language_code=language_code,
            user_id=user_id,
        )
        sign_labels, effective_language_code = self._resolve_sign_labels(requested_codes)
        planet_labels, planet_language_code = self._resolve_planet_labels(requested_codes)
        aspect_labels, aspect_language_code = self._resolve_aspect_labels(requested_codes)
        house_labels, house_language_code = self._resolve_house_labels(requested_codes)
        return AstrologyLabels(
            sign_labels=sign_labels,
            planet_labels=planet_labels,
            aspect_labels=aspect_labels,
            house_labels=house_labels,
            effective_language_code=(
                effective_language_code
                or planet_language_code
                or aspect_language_code
                or house_language_code
                or SYSTEM_LANGUAGE_CODE
            ),
        )

    def _resolve_sign_labels(self, requested_codes: list[str]) -> tuple[dict[str, str], str | None]:
        """Résout les labels de signes depuis la table canonique."""
        rows = self._db.execute(
            select(
                AstralSignModel.code, LanguageModel.code, AstralSignTranslationModel.translated_name
            )
            .join(
                AstralSignTranslationModel,
                AstralSignTranslationModel.astral_sign_id == AstralSignModel.id,
            )
            .join(LanguageModel, LanguageModel.id == AstralSignTranslationModel.language_id)
            .where(LanguageModel.code.in_(requested_codes))
        ).all()
        return self._labels_by_preference(rows, requested_codes)

    def _resolve_planet_labels(
        self, requested_codes: list[str]
    ) -> tuple[dict[str, str], str | None]:
        """Résout les labels de planètes depuis la table canonique."""
        rows = self._db.execute(
            select(
                PlanetModel.code, LanguageModel.code, AstralPlanetTranslationModel.translated_name
            )
            .join(
                AstralPlanetTranslationModel,
                AstralPlanetTranslationModel.planet_id == PlanetModel.id,
            )
            .join(LanguageModel, LanguageModel.id == AstralPlanetTranslationModel.language_id)
            .where(LanguageModel.code.in_(requested_codes))
        ).all()
        return self._labels_by_preference(rows, requested_codes)

    def _resolve_aspect_labels(
        self, requested_codes: list[str]
    ) -> tuple[dict[str, str], str | None]:
        """Résout les labels d'aspects depuis la table canonique."""
        rows = self._db.execute(
            select(
                AspectModel.code, LanguageModel.code, AstralAspectTranslationModel.translated_name
            )
            .join(
                AstralAspectTranslationModel,
                AstralAspectTranslationModel.aspect_id == AspectModel.id,
            )
            .join(LanguageModel, LanguageModel.id == AstralAspectTranslationModel.language_id)
            .where(LanguageModel.code.in_(requested_codes))
        ).all()
        return self._labels_by_preference(rows, requested_codes)

    def _resolve_house_labels(
        self, requested_codes: list[str]
    ) -> tuple[dict[str, str], str | None]:
        """Résout les labels de maisons depuis la table canonique."""
        rows = self._db.execute(
            select(
                HouseModel.number, LanguageModel.code, AstralHouseTranslationModel.translated_name
            )
            .join(
                AstralHouseTranslationModel, AstralHouseTranslationModel.house_id == HouseModel.id
            )
            .join(LanguageModel, LanguageModel.id == AstralHouseTranslationModel.language_id)
            .where(LanguageModel.code.in_(requested_codes))
        ).all()
        return self._labels_by_preference(rows, requested_codes)

    @staticmethod
    def _labels_by_preference(
        rows: list[tuple[object, object, object]],
        requested_codes: list[str],
    ) -> tuple[dict[str, str], str | None]:
        """Conserve le premier libellé disponible selon la priorité de langue."""
        labels: dict[str, str] = {}
        effective_language_code: str | None = None
        for preferred_code in requested_codes:
            for item_code, row_language_code, translated_name in rows:
                code = str(item_code)
                if row_language_code == preferred_code and code not in labels:
                    labels[code] = str(translated_name)
                    if effective_language_code is None:
                        effective_language_code = preferred_code
        return labels, effective_language_code

    def _language_preference_codes(
        self,
        *,
        language_code: str | None,
        user_id: int | None,
    ) -> list[str]:
        """Construit la priorité de langues sans doublon."""
        codes: list[str] = []
        self._append_code(codes, self._normalize_language_code(language_code))

        user_language_code = self._user_default_language_code(user_id)
        self._append_code(codes, user_language_code)
        self._append_code(codes, SYSTEM_LANGUAGE_CODE)
        return codes

    def _user_default_language_code(self, user_id: int | None) -> str | None:
        """Retourne la langue préférée utilisateur si elle existe."""
        if user_id is None:
            return None
        row = self._db.execute(
            select(LanguageModel.code)
            .select_from(UserModel)
            .join(LanguageModel, LanguageModel.id == UserModel.default_language_id)
            .where(UserModel.id == user_id)
        ).first()
        return str(row[0]) if row else None

    @staticmethod
    def _normalize_language_code(language_code: str | None) -> str | None:
        """Normalise un code de langue API en code référentiel."""
        if not language_code:
            return None
        normalized = language_code.strip().lower().replace("_", "-")
        return normalized.split("-", maxsplit=1)[0] or None

    @staticmethod
    def _append_code(codes: list[str], code: str | None) -> None:
        """Ajoute un code de langue uniquement s'il est exploitable et nouveau."""
        if code and code not in codes:
            codes.append(code)
