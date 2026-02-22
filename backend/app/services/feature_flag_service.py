"""
Service de gestion des feature flags.

Ce module gère les drapeaux de fonctionnalités pour le déploiement progressif
et le contrôle d'accès aux modules (tarot, runes, etc.).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import monotonic

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.persona_config_service import PersonaConfigService

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


class ModuleAvailabilityData(BaseModel):
    """Disponibilité d'un module pour un utilisateur."""

    module: str
    flag_key: str
    status: str
    available: bool
    reason: str


class ModuleAvailabilityListData(BaseModel):
    """Liste de disponibilité de tous les modules."""

    modules: list[ModuleAvailabilityData]
    total: int
    available_count: int


class ModuleExecutionPayload(BaseModel):
    """Payload pour exécuter un module."""

    question: str
    situation: str | None = None
    conversation_id: int | None = None


class ModuleExecutionData(BaseModel):
    """Résultat de l'exécution d'un module."""

    module: str
    status: str
    interpretation: str
    persona_profile_code: str
    conversation_id: int | None


class FeatureFlagService:
    """
    Service de gestion des feature flags et modules.

    Permet le déploiement progressif de fonctionnalités avec ciblage
    par rôle ou par utilisateur spécifique.
    """

    _KNOWN_FLAGS: dict[str, str] = {
        "tarot_enabled": "Activation module Tarot",
        "runes_enabled": "Activation module Runes",
    }
    _MODULE_TO_FLAG = {
        "tarot": "tarot_enabled",
        "runes": "runes_enabled",
    }
    _ALLOWED_ROLES = {"user", "support", "ops", "enterprise_admin"}

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
        model.updated_at = datetime.now(timezone.utc)
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

    @staticmethod
    def _resolve_module_flag(module: str) -> str:
        """Résout la clé de flag associée à un module."""
        normalized = module.strip().lower()
        if normalized not in FeatureFlagService._MODULE_TO_FLAG:
            raise FeatureFlagServiceError(
                code="module_not_supported",
                message="module is not supported",
                details={"module": module},
            )
        return FeatureFlagService._MODULE_TO_FLAG[normalized]

    @staticmethod
    def get_module_availability(
        db: Session,
        *,
        module: str,
        user_id: int,
        user_role: str,
    ) -> ModuleAvailabilityData:
        """
        Vérifie la disponibilité d'un module pour un utilisateur.

        Args:
            db: Session de base de données.
            module: Nom du module.
            user_id: Identifiant de l'utilisateur.
            user_role: Rôle de l'utilisateur.

        Returns:
            Statut de disponibilité avec raison.
        """
        FeatureFlagService._ensure_seeded(db)
        normalized_module = module.strip().lower()
        flag_key = FeatureFlagService._resolve_module_flag(normalized_module)
        model = db.scalar(select(FeatureFlagModel).where(FeatureFlagModel.key == flag_key).limit(1))
        if model is None:
            raise FeatureFlagServiceError(
                code="feature_flag_not_found",
                message="feature flag was not found",
                details={"key": flag_key},
            )
        if not model.enabled:
            status = ModuleAvailabilityData(
                module=normalized_module,
                flag_key=flag_key,
                status="module-locked",
                available=False,
                reason="feature_disabled",
            )
        else:
            target_roles = FeatureFlagService._parse_roles(model.target_roles_csv)
            target_user_ids = FeatureFlagService._parse_user_ids(model.target_user_ids_csv)
            if target_user_ids:
                if user_id in target_user_ids:
                    status = ModuleAvailabilityData(
                        module=normalized_module,
                        flag_key=flag_key,
                        status="module-ready",
                        available=True,
                        reason="segment_match",
                    )
                else:
                    status = ModuleAvailabilityData(
                        module=normalized_module,
                        flag_key=flag_key,
                        status="module-locked",
                        available=False,
                        reason="segment_mismatch",
                    )
            elif target_roles and user_role in target_roles:
                status = ModuleAvailabilityData(
                    module=normalized_module,
                    flag_key=flag_key,
                    status="module-ready",
                    available=True,
                    reason="segment_match",
                )
            elif not target_roles:
                status = ModuleAvailabilityData(
                    module=normalized_module,
                    flag_key=flag_key,
                    status="module-ready",
                    available=True,
                    reason="segment_match",
                )
            else:
                status = ModuleAvailabilityData(
                    module=normalized_module,
                    flag_key=flag_key,
                    status="module-locked",
                    available=False,
                    reason="segment_mismatch",
                )

        increment_counter(
            f"module_feature_exposure_total|module={normalized_module}|status={status.status}",
            1.0,
        )
        return status

    @staticmethod
    def list_modules_availability(
        db: Session,
        *,
        user_id: int,
        user_role: str,
    ) -> ModuleAvailabilityListData:
        """Liste la disponibilité de tous les modules pour un utilisateur."""
        modules = [
            FeatureFlagService.get_module_availability(
                db,
                module=module,
                user_id=user_id,
                user_role=user_role,
            )
            for module in sorted(FeatureFlagService._MODULE_TO_FLAG.keys())
        ]
        available_count = sum(1 for module in modules if module.available)
        return ModuleAvailabilityListData(
            modules=modules,
            total=len(modules),
            available_count=available_count,
        )

    @staticmethod
    def execute_module(
        db: Session,
        *,
        module: str,
        user_id: int,
        user_role: str,
        payload: ModuleExecutionPayload,
        skip_availability_check: bool = False,
    ) -> ModuleExecutionData:
        """
        Exécute un module (tarot, runes) pour un utilisateur.

        Args:
            db: Session de base de données.
            module: Nom du module à exécuter.
            user_id: Identifiant de l'utilisateur.
            user_role: Rôle de l'utilisateur.
            payload: Données d'entrée pour le module.
            skip_availability_check: Ignorer la vérification d'accès.

        Returns:
            Résultat de l'interprétation du module.

        Raises:
            FeatureFlagServiceError: Si le module n'est pas disponible.
        """
        normalized_module = module.strip().lower()
        if skip_availability_check:
            FeatureFlagService._resolve_module_flag(normalized_module)
        else:
            availability = FeatureFlagService.get_module_availability(
                db,
                module=normalized_module,
                user_id=user_id,
                user_role=user_role,
            )
            if not availability.available:
                increment_counter(
                    f"module_errors_total|module={normalized_module}|code=module_locked", 1.0
                )
                raise FeatureFlagServiceError(
                    code="module_locked",
                    message="module is not available for this user",
                    details={"module": normalized_module, "reason": availability.reason},
                )
        question = payload.question.strip()
        if not question:
            increment_counter(
                f"module_errors_total|module={normalized_module}|code=invalid_module_input", 1.0
            )
            raise FeatureFlagServiceError(
                code="invalid_module_input",
                message="question is required",
                details={"field": "question"},
            )
        started = monotonic()
        increment_counter(f"module_activation_total|module={normalized_module}", 1.0)

        persona = PersonaConfigService.get_active(db)
        if normalized_module == "tarot":
            interpretation = (
                "Tirage tarot (3 cartes):\n"
                f"- Contexte: {payload.situation.strip() if payload.situation else 'non precise'}\n"
                f"- Message central: {question}\n"
                "- Lecture: avancez par petites decisions concretes, verifiez vos priorites "
                "avant tout engagement important."
            )
        else:
            interpretation = (
                "Lecture runique:\n"
                f"- Intention: {question}\n"
                "- Lecture: phase de clarification; posez un cadre simple, puis agissez "
                "de facon progressive et mesurable."
            )

        conversation_id = payload.conversation_id
        if conversation_id is not None:
            repo = ChatRepository(db)
            conversation = repo.get_conversation_by_id(conversation_id)
            if conversation is None:
                increment_counter(
                    f"module_errors_total|module={normalized_module}|code=conversation_not_found",
                    1.0,
                )
                raise FeatureFlagServiceError(
                    code="conversation_not_found",
                    message="conversation was not found",
                    details={"conversation_id": str(conversation_id)},
                )
            if conversation.user_id != user_id:
                increment_counter(
                    f"module_errors_total|module={normalized_module}|code=conversation_forbidden",
                    1.0,
                )
                raise FeatureFlagServiceError(
                    code="conversation_forbidden",
                    message="conversation does not belong to user",
                    details={"conversation_id": str(conversation_id)},
                )
            repo.create_message(
                conversation_id=conversation.id,
                role="assistant",
                content=interpretation,
                metadata_payload={
                    "module": normalized_module,
                    "module_status": "completed",
                    "persona_profile_code": persona.profile_code,
                },
            )

        elapsed = monotonic() - started
        observe_duration(f"module_latency_seconds|module={normalized_module}", elapsed)
        return ModuleExecutionData(
            module=normalized_module,
            status="completed",
            interpretation=interpretation,
            persona_profile_code=persona.profile_code,
            conversation_id=conversation_id,
        )
