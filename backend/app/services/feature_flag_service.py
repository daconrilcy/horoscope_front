"""
Service de gestion des feature flags.

Ce module gère les drapeaux de fonctionnalités pour le déploiement progressif.
Les modules hors périmètre historique ont été retirés.
"""

from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.feature_flag import FeatureFlagModel

logger = logging.getLogger(__name__)


class FeatureFlagServiceError(Exception):
    """Exception levée lors d'erreurs de feature flags."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de feature flag.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class FeatureFlagData(BaseModel):
    """Données d'un feature flag."""

    key: str
    description: str
    enabled: bool
    target_roles: list[str]
    target_user_ids: list[int]
    updated_by_user_id: int | None
    updated_at: datetime


class FeatureFlagListData(BaseModel):
    """Liste de tous les feature flags."""

    flags: list[FeatureFlagData]
    total: int


class FeatureFlagUpdatePayload(BaseModel):
    """Payload pour mettre à jour un feature flag."""

    enabled: bool
    target_roles: list[str] = Field(default_factory=list)
    target_user_ids: list[int] = Field(default_factory=list)


class FeatureFlagService:
    """
    Service de gestion des feature flags.

    Permet le déploiement progressif de fonctionnalités avec ciblage
    par rôle ou par utilisateur spécifique.
    """

    _KNOWN_FLAGS: dict[str, str] = {
        "test_flag": "Drapeau de test pour l'infrastructure",
        "paywall_experiment_copy": "Variante de wording paywall pour experimentation produit",
        "natal_premium_teaser": "Teaser premium sur la page theme astral complet",
        "llm_replay_enabled": "Autorise le rejeu manuel des appels LLM depuis l'admin",
    }
    _ALLOWED_ROLES = {"user", "support", "ops", "enterprise_admin", "admin"}

    @staticmethod
    def _parse_roles(csv_value: str | None) -> list[str]:
        """Parse une liste de rôles depuis une chaîne CSV."""
        if not csv_value:
            return []
        parsed = [item.strip().lower() for item in csv_value.split(",") if item.strip()]
        return sorted(set(item for item in parsed if item in FeatureFlagService._ALLOWED_ROLES))

    @staticmethod
    def _parse_user_ids(csv_value: str | None) -> list[int]:
        """Parse une liste d'IDs utilisateur depuis une chaîne CSV."""
        if not csv_value:
            return []
        values: list[int] = []
        for item in csv_value.split(","):
            normalized = item.strip()
            if normalized.isdigit():
                values.append(int(normalized))
        return sorted(set(values))

    @staticmethod
    def _serialize_roles(roles: list[str]) -> str | None:
        """Sérialise une liste de rôles en chaîne CSV."""
        cleaned = sorted(set(role.strip().lower() for role in roles if role.strip()))
        for role in cleaned:
            if role not in FeatureFlagService._ALLOWED_ROLES:
                raise FeatureFlagServiceError(
                    code="invalid_feature_flag_role",
                    message="feature flag role is invalid",
                    details={"role": role},
                )
        return ",".join(cleaned) if cleaned else None

    @staticmethod
    def _serialize_user_ids(user_ids: list[int]) -> str | None:
        """Sérialise une liste d'IDs utilisateur en chaîne CSV."""
        cleaned = sorted(set(user_id for user_id in user_ids if user_id > 0))
        return ",".join(str(user_id) for user_id in cleaned) if cleaned else None

    @staticmethod
    def _to_data(model: FeatureFlagModel) -> FeatureFlagData:
        """Convertit un modèle de feature flag en DTO."""
        return FeatureFlagData(
            key=model.key,
            description=model.description,
            enabled=model.enabled,
            target_roles=FeatureFlagService._parse_roles(model.target_roles_csv),
            target_user_ids=FeatureFlagService._parse_user_ids(model.target_user_ids_csv),
            updated_by_user_id=model.updated_by_user_id,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _ensure_seeded(db: Session) -> None:
        """S'assure que tous les flags connus existent en base."""
        keys = list(FeatureFlagService._KNOWN_FLAGS.keys())
        if not keys:
            return
        existing = {
            row.key: row
            for row in db.scalars(
                select(FeatureFlagModel).where(FeatureFlagModel.key.in_(keys))
            ).all()
        }
        for key, description in FeatureFlagService._KNOWN_FLAGS.items():
            if key in existing:
                continue
            db.add(
                FeatureFlagModel(
                    key=key,
                    description=description,
                    enabled=False,
                    target_roles_csv=None,
                    target_user_ids_csv=None,
                    updated_by_user_id=None,
                )
            )
        db.flush()

    @staticmethod
    def list_flags(db: Session) -> FeatureFlagListData:
        """Liste tous les feature flags."""
        FeatureFlagService._ensure_seeded(db)
        rows = list(db.scalars(select(FeatureFlagModel).order_by(FeatureFlagModel.key.asc())).all())
        data = [FeatureFlagService._to_data(row) for row in rows]
        return FeatureFlagListData(flags=data, total=len(data))

    @staticmethod
    def update_flag(
        db: Session,
        *,
        key: str,
        payload: FeatureFlagUpdatePayload,
        updated_by_user_id: int,
    ) -> FeatureFlagData:
        """
        Met à jour un feature flag.

        Args:
            db: Session de base de données.
            key: Clé du flag à mettre à jour.
            payload: Nouvelles valeurs.
            updated_by_user_id: Identifiant de l'utilisateur effectuant la modification.

        Returns:
            Flag mis à jour.

        Raises:
            FeatureFlagServiceError: Si le flag n'existe pas.
        """
        FeatureFlagService._ensure_seeded(db)
        if key not in FeatureFlagService._KNOWN_FLAGS:
            raise FeatureFlagServiceError(
                code="feature_flag_not_found",
                message="feature flag was not found",
                details={"key": key},
            )
        model = db.scalar(select(FeatureFlagModel).where(FeatureFlagModel.key == key).limit(1))
        if model is None:
            raise FeatureFlagServiceError(
                code="feature_flag_not_found",
                message="feature flag was not found",
                details={"key": key},
            )
        model.enabled = payload.enabled
        model.target_roles_csv = FeatureFlagService._serialize_roles(payload.target_roles)
        model.target_user_ids_csv = FeatureFlagService._serialize_user_ids(payload.target_user_ids)
        model.updated_by_user_id = updated_by_user_id
        model.updated_at = datetime_provider.utcnow()
        db.flush()
        logger.info(
            "feature_flag_updated key=%s enabled=%s target_roles=%s target_users=%s updated_by=%s",
            model.key,
            model.enabled,
            model.target_roles_csv or "",
            model.target_user_ids_csv or "",
            updated_by_user_id,
        )
        return FeatureFlagService._to_data(model)
