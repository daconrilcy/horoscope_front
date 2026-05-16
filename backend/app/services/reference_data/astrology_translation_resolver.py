"""Résout les libellés astrologiques localisés depuis les référentiels DB."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import AstralSignModel, LanguageModel
from app.infra.db.models.translation_reference import AstralSignTranslationModel
from app.infra.db.models.user import UserModel

SYSTEM_LANGUAGE_CODE = "fr"


@dataclass(frozen=True)
class AstrologyLabels:
    """Contrat immuable de libellés astrologiques déjà résolus."""

    sign_labels: dict[str, str]
    effective_language_code: str

    @classmethod
    def technical_fallback(cls) -> "AstrologyLabels":
        """Construit un contrat qui retourne les codes canoniques."""
        return cls(sign_labels={}, effective_language_code=SYSTEM_LANGUAGE_CODE)

    def sign_label(self, sign_code: str | None) -> str:
        """Retourne le libellé localisé d'un signe ou son code canonique."""
        if not sign_code:
            return ""
        return self.sign_labels.get(sign_code, sign_code)


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
        rows = self._db.execute(
            select(
                AstralSignModel.code,
                LanguageModel.code,
                AstralSignTranslationModel.translated_name,
            )
            .join(
                AstralSignTranslationModel,
                AstralSignTranslationModel.astral_sign_id == AstralSignModel.id,
            )
            .join(LanguageModel, LanguageModel.id == AstralSignTranslationModel.language_id)
            .where(LanguageModel.code.in_(requested_codes))
        ).all()

        labels: dict[str, str] = {}
        effective_language_code: str | None = None
        for preferred_code in requested_codes:
            for sign_code, row_language_code, translated_name in rows:
                if row_language_code == preferred_code and sign_code not in labels:
                    labels[str(sign_code)] = str(translated_name)
                    if effective_language_code is None:
                        effective_language_code = preferred_code

        return AstrologyLabels(
            sign_labels=labels,
            effective_language_code=effective_language_code or SYSTEM_LANGUAGE_CODE,
        )

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
