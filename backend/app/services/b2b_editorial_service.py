"""
Service de configuration éditoriale B2B.

Ce module gère les configurations éditoriales des comptes entreprise,
permettant de personnaliser le ton, le style et le format du contenu généré.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
from app.infra.observability.metrics import increment_counter

_VALID_TONES = {"neutral", "friendly", "premium"}
_VALID_LENGTHS = {"short", "medium", "long"}
_VALID_FORMATS = {"paragraph", "bullet"}


class B2BEditorialServiceError(Exception):
    """Exception levée lors d'erreurs de configuration éditoriale B2B."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de configuration éditoriale.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class B2BEditorialConfigUpdatePayload(BaseModel):
    """Payload pour la mise à jour d'une configuration éditoriale."""

    tone: str = "neutral"
    length_style: str = "medium"
    output_format: str = "paragraph"
    preferred_terms: list[str] = Field(default_factory=list)
    avoided_terms: list[str] = Field(default_factory=list)

    @field_validator("tone")
    @classmethod
    def _validate_tone(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in _VALID_TONES:
            raise ValueError("tone is invalid")
        return normalized

    @field_validator("length_style")
    @classmethod
    def _validate_length_style(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in _VALID_LENGTHS:
            raise ValueError("length_style is invalid")
        return normalized

    @field_validator("output_format")
    @classmethod
    def _validate_output_format(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in _VALID_FORMATS:
            raise ValueError("output_format is invalid")
        return normalized

    @field_validator("preferred_terms", "avoided_terms")
    @classmethod
    def _validate_terms(cls, values: list[str]) -> list[str]:
        if len(values) > 12:
            raise ValueError("too many terms")
        normalized: list[str] = []
        seen: set[str] = set()
        for raw in values:
            term = raw.strip()
            if not term:
                continue
            if len(term) > 32:
                raise ValueError("term is too long")
            key = term.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(term)
        return normalized


class B2BEditorialConfigData(BaseModel):
    """Données d'une configuration éditoriale B2B."""

    config_id: int | None
    account_id: int
    version_number: int
    is_active: bool
    tone: str
    length_style: str
    output_format: str
    preferred_terms: list[str]
    avoided_terms: list[str]
    created_by_credential_id: int | None
    created_at: datetime | None
    updated_at: datetime | None


class B2BEditorialService:
    """
    Service de gestion des configurations éditoriales B2B.

    Permet aux comptes entreprise de personnaliser le ton, le style
    et le vocabulaire utilisés dans le contenu astrologique généré.
    """

    @staticmethod
    def _default_for_account(account_id: int) -> B2BEditorialConfigData:
        """Retourne la configuration éditoriale par défaut pour un compte."""
        return B2BEditorialConfigData(
            config_id=None,
            account_id=account_id,
            version_number=0,
            is_active=True,
            tone="neutral",
            length_style="medium",
            output_format="paragraph",
            preferred_terms=[],
            avoided_terms=[],
            created_by_credential_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def default_config(*, account_id: int) -> B2BEditorialConfigData:
        """
        Retourne la configuration éditoriale par défaut.

        Args:
            account_id: Identifiant du compte entreprise.

        Returns:
            Configuration avec les valeurs par défaut.
        """
        return B2BEditorialService._default_for_account(account_id)

    @staticmethod
    def _to_data(model: EnterpriseEditorialConfigModel) -> B2BEditorialConfigData:
        """Convertit un modèle de configuration en DTO."""
        return B2BEditorialConfigData(
            config_id=model.id,
            account_id=model.enterprise_account_id,
            version_number=model.version_number,
            is_active=model.is_active,
            tone=model.tone,
            length_style=model.length_style,
            output_format=model.output_format,
            preferred_terms=list(model.preferred_terms),
            avoided_terms=list(model.avoided_terms),
            created_by_credential_id=model.created_by_credential_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _ensure_active_account(db: Session, *, account_id: int) -> EnterpriseAccountModel:
        """Vérifie qu'un compte entreprise existe et est actif."""
        account = db.scalar(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.id == account_id).limit(1)
        )
        if account is None:
            raise B2BEditorialServiceError(
                code="enterprise_account_not_found",
                message="enterprise account was not found",
                details={"account_id": str(account_id)},
            )
        if account.status != "active":
            raise B2BEditorialServiceError(
                code="enterprise_account_inactive",
                message="enterprise account is inactive",
                details={"account_id": str(account_id), "status": account.status},
            )
        return account

    @staticmethod
    def _get_active_model(db: Session, *, account_id: int) -> EnterpriseEditorialConfigModel | None:
        return db.scalar(
            select(EnterpriseEditorialConfigModel)
            .where(
                EnterpriseEditorialConfigModel.enterprise_account_id == account_id,
                EnterpriseEditorialConfigModel.is_active.is_(True),
            )
            .order_by(
                desc(EnterpriseEditorialConfigModel.version_number),
                desc(EnterpriseEditorialConfigModel.id),
            )
            .limit(1)
        )

    @staticmethod
    def get_active_config(db: Session, *, account_id: int) -> B2BEditorialConfigData:
        """
        Récupère la configuration éditoriale active d'un compte.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.

        Returns:
            Configuration active ou configuration par défaut si aucune.

        Raises:
            B2BEditorialServiceError: Si le compte n'existe pas ou est inactif.
        """
        B2BEditorialService._ensure_active_account(db, account_id=account_id)
        active = B2BEditorialService._get_active_model(db, account_id=account_id)
        if active is None:
            return B2BEditorialService._default_for_account(account_id)
        return B2BEditorialService._to_data(active)

    @staticmethod
    def upsert_config(
        db: Session,
        *,
        account_id: int,
        credential_id: int,
        payload: B2BEditorialConfigUpdatePayload,
    ) -> B2BEditorialConfigData:
        """
        Crée ou met à jour la configuration éditoriale d'un compte.

        Crée une nouvelle version si la configuration a changé.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.
            credential_id: Identifiant du credential effectuant la modification.
            payload: Nouvelles valeurs de configuration.

        Returns:
            Configuration mise à jour.

        Raises:
            B2BEditorialServiceError: Si le compte n'existe pas ou est inactif.
        """
        B2BEditorialService._ensure_active_account(db, account_id=account_id)
        active = B2BEditorialService._get_active_model(db, account_id=account_id)
        if active is not None:
            same_config = (
                active.tone == payload.tone
                and active.length_style == payload.length_style
                and active.output_format == payload.output_format
                and list(active.preferred_terms) == payload.preferred_terms
                and list(active.avoided_terms) == payload.avoided_terms
            )
            if same_config:
                return B2BEditorialService._to_data(active)
            active.is_active = False
            next_version = active.version_number + 1
        else:
            next_version = 1

        created = EnterpriseEditorialConfigModel(
            enterprise_account_id=account_id,
            version_number=next_version,
            is_active=True,
            tone=payload.tone,
            length_style=payload.length_style,
            output_format=payload.output_format,
            preferred_terms=payload.preferred_terms,
            avoided_terms=payload.avoided_terms,
            created_by_credential_id=credential_id,
        )
        db.add(created)
        db.flush()
        increment_counter("b2b_editorial_updates_total", 1.0)
        return B2BEditorialService._to_data(created)

    @staticmethod
    def _compose_base_body(*, sign_name: str, length_style: str) -> str:
        """Compose le corps de base du résumé selon le style de longueur."""
        if length_style == "short":
            return f"Semaine de {sign_name}: avancez pas a pas."
        if length_style == "long":
            return (
                f"Semaine de {sign_name}: avancez pas a pas, priorisez les actions concretes, "
                "et prenez le temps de valider les decisions importantes avec serenite."
            )
        return f"Semaine de {sign_name}: avancez pas a pas et priorisez les decisions progressives."

    @staticmethod
    def _apply_avoided_terms(text: str, avoided_terms: list[str]) -> str:
        """Supprime les termes à éviter du texte."""
        output = text
        for term in avoided_terms:
            pattern = re.compile(re.escape(term), flags=re.IGNORECASE)
            output = pattern.sub("", output)
        return re.sub(r"\s{2,}", " ", output).strip()

    @staticmethod
    def render_weekly_summary(
        *,
        sign_name: str,
        config: B2BEditorialConfigData,
    ) -> str:
        """
        Génère un résumé hebdomadaire pour un signe avec la configuration donnée.

        Args:
            sign_name: Nom du signe astrologique.
            config: Configuration éditoriale à appliquer.

        Returns:
            Texte du résumé formaté selon la configuration.
        """
        tone_prefix = {
            "neutral": "Tendance",
            "friendly": "Conseil",
            "premium": "Perspective",
        }.get(config.tone, "Tendance")
        body = B2BEditorialService._compose_base_body(
            sign_name=sign_name,
            length_style=config.length_style,
        )
        if config.preferred_terms:
            body = f"{body} Mots-cles: {', '.join(config.preferred_terms[:3])}."
        body = B2BEditorialService._apply_avoided_terms(body, config.avoided_terms)
        if config.output_format == "bullet":
            return f"- {tone_prefix} {sign_name}: {body}"
        return f"{tone_prefix} pour {sign_name}: {body}"
