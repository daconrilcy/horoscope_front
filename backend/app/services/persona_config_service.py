"""
Service de configuration des personas.

Ce module gère les profils de persona de l'assistant astrologique : création,
activation, archivage et rollback des configurations.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.persona_config import PersonaConfigModel

logger = logging.getLogger(__name__)

ALLOWED_TONES = {"calm", "direct", "empathetic"}
ALLOWED_PRUDENCE_LEVELS = {"standard", "high"}
ALLOWED_SCOPE_POLICIES = {"strict", "balanced"}
ALLOWED_RESPONSE_STYLES = {"concise", "detailed"}
ALLOWED_FALLBACK_POLICIES = {"safe_fallback", "retry_once_then_safe"}
PROFILE_CODE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")

DEFAULT_PERSONA_CONFIG = {
    "profile_code": "legacy-default",
    "display_name": "Astrologue Principal",
    "tone": "calm",
    "prudence_level": "high",
    "scope_policy": "strict",
    "response_style": "concise",
    "fallback_policy": "safe_fallback",
}


class PersonaConfigServiceError(Exception):
    """Exception levée lors d'erreurs de configuration persona."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de configuration persona.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class PersonaConfigData(BaseModel):
    """Données d'une configuration persona."""

    id: int | None
    version: int
    profile_code: str
    display_name: str
    tone: str
    prudence_level: str
    scope_policy: str
    response_style: str
    fallback_policy: str
    status: str
    rollback_from_id: int | None
    created_by_user_id: int | None
    created_at: datetime | None
    is_default: bool

    def to_prompt_line(self) -> str:
        """Génère la ligne de prompt pour cette configuration persona."""
        return (
            "Persona policy: "
            f"profile={self.profile_code}; "
            f"tone={self.tone}; prudence={self.prudence_level}; "
            f"scope={self.scope_policy}; style={self.response_style}; "
            f"fallback={self.fallback_policy}"
        )


class PersonaConfigUpdatePayload(BaseModel):
    """Payload pour mettre à jour la configuration active."""

    tone: str
    prudence_level: str
    scope_policy: str
    response_style: str
    profile_code: str | None = None
    display_name: str | None = None
    fallback_policy: str = "safe_fallback"


class PersonaProfileCreatePayload(BaseModel):
    """Payload pour créer un nouveau profil persona."""

    profile_code: str
    display_name: str
    tone: str
    prudence_level: str
    scope_policy: str
    response_style: str
    fallback_policy: str = "safe_fallback"
    activate: bool = False


class PersonaRollbackData(BaseModel):
    """Résultat d'un rollback de configuration persona."""

    active: PersonaConfigData
    rolled_back_version: int


class PersonaProfileListData(BaseModel):
    """Liste des profils persona."""

    items: list[PersonaConfigData]
    total: int


class PersonaConfigService:
    """
    Service de gestion des configurations persona.

    Gère le cycle de vie des profils persona avec versioning,
    activation/désactivation et capacité de rollback.
    """
    @staticmethod
    def _to_data(model: PersonaConfigModel) -> PersonaConfigData:
        """Convertit un modèle de configuration en DTO."""
        return PersonaConfigData(
            id=model.id,
            version=model.version,
            profile_code=model.profile_code,
            display_name=model.display_name,
            tone=model.tone,
            prudence_level=model.prudence_level,
            scope_policy=model.scope_policy,
            response_style=model.response_style,
            fallback_policy=model.fallback_policy,
            status=model.status,
            rollback_from_id=model.rollback_from_id,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
            is_default=False,
        )

    @staticmethod
    def _default_data() -> PersonaConfigData:
        """Retourne la configuration persona par défaut."""
        return PersonaConfigData(
            id=None,
            version=0,
            profile_code=DEFAULT_PERSONA_CONFIG["profile_code"],
            display_name=DEFAULT_PERSONA_CONFIG["display_name"],
            tone=DEFAULT_PERSONA_CONFIG["tone"],
            prudence_level=DEFAULT_PERSONA_CONFIG["prudence_level"],
            scope_policy=DEFAULT_PERSONA_CONFIG["scope_policy"],
            response_style=DEFAULT_PERSONA_CONFIG["response_style"],
            fallback_policy=DEFAULT_PERSONA_CONFIG["fallback_policy"],
            status="active",
            rollback_from_id=None,
            created_by_user_id=None,
            created_at=None,
            is_default=True,
        )

    @staticmethod
    def _validate_profile_code(profile_code: str) -> str:
        """Valide et normalise un code de profil."""
        normalized = profile_code.strip().lower()
        if not PROFILE_CODE_PATTERN.match(normalized):
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "profile_code"},
            )
        return normalized

    @staticmethod
    def _validate_payload(payload: PersonaConfigUpdatePayload) -> PersonaConfigUpdatePayload:
        """Valide les champs d'un payload de mise à jour."""
        if payload.tone not in ALLOWED_TONES:
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "tone"},
            )
        if payload.prudence_level not in ALLOWED_PRUDENCE_LEVELS:
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "prudence_level"},
            )
        if payload.scope_policy not in ALLOWED_SCOPE_POLICIES:
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "scope_policy"},
            )
        if payload.response_style not in ALLOWED_RESPONSE_STYLES:
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "response_style"},
            )
        if payload.fallback_policy not in ALLOWED_FALLBACK_POLICIES:
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "fallback_policy"},
            )
        if payload.profile_code is not None:
            PersonaConfigService._validate_profile_code(payload.profile_code)
        if payload.display_name is not None and not payload.display_name.strip():
            raise PersonaConfigServiceError(
                code="invalid_persona_config",
                message="persona config is invalid",
                details={"field": "display_name"},
            )
        return payload

    @staticmethod
    def _validate_create_payload(
        payload: PersonaProfileCreatePayload,
    ) -> PersonaProfileCreatePayload:
        """Valide un payload de création de profil."""
        PersonaConfigService._validate_payload(
            PersonaConfigUpdatePayload(
                tone=payload.tone,
                prudence_level=payload.prudence_level,
                scope_policy=payload.scope_policy,
                response_style=payload.response_style,
                profile_code=payload.profile_code,
                display_name=payload.display_name,
                fallback_policy=payload.fallback_policy,
            )
        )
        return payload

    @staticmethod
    def _next_version(db: Session) -> int:
        """Calcule le prochain numéro de version."""
        latest = db.scalar(
            select(PersonaConfigModel).order_by(desc(PersonaConfigModel.version)).limit(1)
        )
        return (latest.version + 1) if latest is not None else 1

    @staticmethod
    def _get_active_model(db: Session, *, for_update: bool = False) -> PersonaConfigModel | None:
        """Récupère le modèle de configuration actif."""
        query = (
            select(PersonaConfigModel)
            .where(PersonaConfigModel.status == "active")
            .order_by(desc(PersonaConfigModel.version), desc(PersonaConfigModel.id))
            .limit(1)
        )
        if for_update:
            query = query.with_for_update()
        return db.scalar(query)

    @staticmethod
    def _get_profile_by_id(
        db: Session,
        *,
        profile_id: int,
        for_update: bool = False,
    ) -> PersonaConfigModel | None:
        """Récupère un profil par son identifiant."""
        query = select(PersonaConfigModel).where(PersonaConfigModel.id == profile_id).limit(1)
        if for_update:
            query = query.with_for_update()
        return db.scalar(query)

    @staticmethod
    def get_active(db: Session) -> PersonaConfigData:
        """Récupère la configuration persona active."""
        active = PersonaConfigService._get_active_model(db)
        if active is None:
            return PersonaConfigService._default_data()
        return PersonaConfigService._to_data(active)

    @staticmethod
    def list_profiles(db: Session) -> PersonaProfileListData:
        """Liste tous les profils persona triés par version."""
        rows = list(
            db.scalars(
                select(PersonaConfigModel).order_by(
                    desc(PersonaConfigModel.version),
                    desc(PersonaConfigModel.id),
                )
            )
        )
        return PersonaProfileListData(
            items=[PersonaConfigService._to_data(row) for row in rows],
            total=len(rows),
        )

    @staticmethod
    def create_profile(
        db: Session,
        *,
        user_id: int,
        payload: PersonaProfileCreatePayload,
    ) -> PersonaConfigData:
        """
        Crée un nouveau profil persona.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur créateur.
            payload: Données du nouveau profil.

        Returns:
            Profil créé.
        """
        validated = PersonaConfigService._validate_create_payload(payload)
        current_active = PersonaConfigService._get_active_model(db, for_update=True)
        if validated.activate and current_active is not None:
            current_active.status = "inactive"
            db.flush()

        model = PersonaConfigModel(
            version=PersonaConfigService._next_version(db),
            profile_code=PersonaConfigService._validate_profile_code(validated.profile_code),
            display_name=validated.display_name.strip(),
            tone=validated.tone,
            prudence_level=validated.prudence_level,
            scope_policy=validated.scope_policy,
            response_style=validated.response_style,
            fallback_policy=validated.fallback_policy,
            status="active" if validated.activate else "inactive",
            rollback_from_id=current_active.id if validated.activate and current_active else None,
            created_by_user_id=user_id,
        )
        db.add(model)
        db.flush()
        logger.info(
            "persona_profile_created user_id=%s profile_id=%s profile_code=%s active=%s version=%s",
            user_id,
            model.id,
            model.profile_code,
            validated.activate,
            model.version,
        )
        return PersonaConfigService._to_data(model)

    @staticmethod
    def activate_profile(
        db: Session,
        *,
        user_id: int,
        profile_id: int,
    ) -> PersonaConfigData:
        """
        Active un profil persona existant.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            profile_id: Identifiant du profil à activer.

        Returns:
            Profil activé.

        Raises:
            PersonaConfigServiceError: Si le profil n'existe pas ou est archivé.
        """
        target = PersonaConfigService._get_profile_by_id(db, profile_id=profile_id, for_update=True)
        if target is None:
            raise PersonaConfigServiceError(
                code="persona_profile_not_found",
                message="persona profile was not found",
                details={"profile_id": str(profile_id)},
            )
        if target.status == "archived":
            raise PersonaConfigServiceError(
                code="persona_profile_archived",
                message="persona profile is archived",
                details={"profile_id": str(profile_id)},
            )
        current_active = PersonaConfigService._get_active_model(db, for_update=True)
        if current_active is not None and current_active.id == target.id:
            return PersonaConfigService._to_data(target)
        if current_active is not None:
            current_active.status = "inactive"
            db.flush()
        target.status = "active"
        target.rollback_from_id = current_active.id if current_active is not None else None
        db.flush()
        logger.info(
            "persona_profile_activated user_id=%s profile_id=%s "
            "profile_code=%s rollback_from_id=%s",
            user_id,
            target.id,
            target.profile_code,
            target.rollback_from_id,
        )
        return PersonaConfigService._to_data(target)

    @staticmethod
    def archive_profile(
        db: Session,
        *,
        user_id: int,
        profile_id: int,
    ) -> PersonaConfigData:
        """
        Archive un profil persona inactif.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            profile_id: Identifiant du profil à archiver.

        Returns:
            Profil archivé.

        Raises:
            PersonaConfigServiceError: Si le profil est actif ou n'existe pas.
        """
        target = PersonaConfigService._get_profile_by_id(db, profile_id=profile_id, for_update=True)
        if target is None:
            raise PersonaConfigServiceError(
                code="persona_profile_not_found",
                message="persona profile was not found",
                details={"profile_id": str(profile_id)},
            )
        if target.status == "active":
            raise PersonaConfigServiceError(
                code="persona_profile_archive_forbidden",
                message="active persona profile cannot be archived",
                details={"profile_id": str(profile_id)},
            )
        target.status = "archived"
        db.flush()
        logger.info(
            "persona_profile_archived user_id=%s profile_id=%s profile_code=%s",
            user_id,
            target.id,
            target.profile_code,
        )
        return PersonaConfigService._to_data(target)

    @staticmethod
    def restore_profile(
        db: Session,
        *,
        user_id: int,
        profile_id: int,
    ) -> PersonaConfigData:
        """
        Restaure un profil persona archivé.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            profile_id: Identifiant du profil à restaurer.

        Returns:
            Profil restauré (statut inactif).
        """
        target = PersonaConfigService._get_profile_by_id(db, profile_id=profile_id, for_update=True)
        if target is None:
            raise PersonaConfigServiceError(
                code="persona_profile_not_found",
                message="persona profile was not found",
                details={"profile_id": str(profile_id)},
            )
        if target.status == "archived":
            target.status = "inactive"
            db.flush()
        logger.info(
            "persona_profile_restored user_id=%s profile_id=%s profile_code=%s",
            user_id,
            target.id,
            target.profile_code,
        )
        return PersonaConfigService._to_data(target)

    @staticmethod
    def update_active(
        db: Session,
        *,
        user_id: int,
        payload: PersonaConfigUpdatePayload,
    ) -> PersonaConfigData:
        """
        Met à jour la configuration active en créant une nouvelle version.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            payload: Nouvelles valeurs de configuration.

        Returns:
            Nouvelle configuration active.
        """
        validated = PersonaConfigService._validate_payload(payload)
        current_active = PersonaConfigService._get_active_model(db, for_update=True)
        current = (
            PersonaConfigService._to_data(current_active)
            if current_active is not None
            else PersonaConfigService._default_data()
        )
        target_profile_code = validated.profile_code or current.profile_code
        target_display_name = (validated.display_name or current.display_name).strip()
        if (
            current_active is not None
            and current.profile_code == target_profile_code
            and current.display_name == target_display_name
            and current.tone == validated.tone
            and current.prudence_level == validated.prudence_level
            and current.scope_policy == validated.scope_policy
            and current.response_style == validated.response_style
            and current.fallback_policy == validated.fallback_policy
        ):
            logger.info(
                "persona_config_update_noop user_id=%s profile_id=%s profile_code=%s version=%s",
                user_id,
                current_active.id,
                current_active.profile_code,
                current_active.version,
            )
            return PersonaConfigService._to_data(current_active)
        create_payload = PersonaProfileCreatePayload(
            profile_code=target_profile_code,
            display_name=target_display_name,
            tone=validated.tone,
            prudence_level=validated.prudence_level,
            scope_policy=validated.scope_policy,
            response_style=validated.response_style,
            fallback_policy=validated.fallback_policy,
            activate=True,
        )
        return PersonaConfigService.create_profile(
            db,
            user_id=user_id,
            payload=create_payload,
        )

    @staticmethod
    def rollback_active(
        db: Session,
        *,
        user_id: int,
    ) -> PersonaRollbackData:
        """
        Effectue un rollback vers la version précédente.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            Données du rollback avec la nouvelle configuration active.

        Raises:
            PersonaConfigServiceError: Si aucun rollback n'est disponible.
        """
        current_active = PersonaConfigService._get_active_model(db, for_update=True)
        if current_active is None:
            raise PersonaConfigServiceError(
                code="persona_rollback_unavailable",
                message="persona rollback is unavailable",
                details={},
            )

        previous: PersonaConfigModel | None = None
        if current_active.rollback_from_id is not None:
            previous = PersonaConfigService._get_profile_by_id(
                db,
                profile_id=current_active.rollback_from_id,
                for_update=True,
            )
            if previous is not None and previous.status == "archived":
                previous = None

        if previous is None:
            previous = db.scalar(
                select(PersonaConfigModel)
                .where(
                    PersonaConfigModel.version < current_active.version,
                    PersonaConfigModel.status.in_(["inactive", "rolled_back"]),
                )
                .order_by(desc(PersonaConfigModel.version), desc(PersonaConfigModel.id))
                .limit(1)
                .with_for_update()
            )
        if previous is None:
            raise PersonaConfigServiceError(
                code="persona_rollback_unavailable",
                message="persona rollback is unavailable",
                details={},
            )

        current_active.status = "rolled_back"
        db.flush()
        previous.status = "active"
        previous.rollback_from_id = current_active.id
        db.flush()
        logger.info(
            "persona_config_rolled_back user_id=%s rolled_back_id=%s rolled_back_version=%s "
            "reactivated_id=%s reactivated_version=%s",
            user_id,
            current_active.id,
            current_active.version,
            previous.id,
            previous.version,
        )
        return PersonaRollbackData(
            active=PersonaConfigService._to_data(previous),
            rolled_back_version=current_active.version,
        )
