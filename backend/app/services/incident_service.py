"""
Service de gestion des incidents support.

Ce module gère le cycle de vie des incidents support : création, mise à jour,
assignation et suivi des métriques de résolution.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.observability.metrics import increment_counter, observe_duration

logger = logging.getLogger(__name__)

VALID_INCIDENT_STATUS = {"open", "in_progress", "resolved", "closed"}
VALID_INCIDENT_PRIORITY = {"low", "medium", "high"}
VALID_INCIDENT_CATEGORY = {"account", "subscription", "content"}
ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "open": {"in_progress", "resolved", "closed"},
    "in_progress": {"resolved", "closed"},
    "resolved": {"closed"},
    "closed": set(),
}


class IncidentServiceError(Exception):
    """Exception levée lors d'erreurs de gestion d'incidents."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur d'incident.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class SupportIncidentData(BaseModel):
    """Données d'un incident support."""

    incident_id: int
    user_id: int
    created_by_user_id: int | None
    assigned_to_user_id: int | None
    category: str
    title: str
    description: str
    status: str
    priority: str
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SupportIncidentCreatePayload(BaseModel):
    """Payload pour créer un incident support."""

    user_id: int
    category: str
    title: str
    description: str
    priority: str = "medium"
    assigned_to_user_id: int | None = None


class SupportIncidentUpdatePayload(BaseModel):
    """Payload pour mettre à jour un incident."""

    status: str | None = None
    priority: str | None = None
    description: str | None = None
    assigned_to_user_id: int | None = None


class SupportIncidentListFilters(BaseModel):
    """Filtres pour lister les incidents."""

    user_id: int | None = None
    status: str | None = None
    priority: str | None = None
    limit: int = 50
    offset: int = 0


class SupportIncidentListData(BaseModel):
    """Liste paginée d'incidents support."""

    incidents: list[SupportIncidentData]
    total: int
    limit: int
    offset: int


class IncidentService:
    """
    Service de gestion des incidents support.

    Gère le cycle de vie complet des incidents avec validation des transitions
    d'état et suivi des métriques de temps de résolution.
    """

    @staticmethod
    def _coerce_utc(value: datetime) -> datetime:
        """Convertit une datetime en UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _to_data(model: SupportIncidentModel) -> SupportIncidentData:
        """Convertit un modèle d'incident en DTO."""
        return SupportIncidentData(
            incident_id=model.id,
            user_id=model.user_id,
            created_by_user_id=model.created_by_user_id,
            assigned_to_user_id=model.assigned_to_user_id,
            category=model.category,
            title=model.title,
            description=model.description,
            status=model.status,
            priority=model.priority,
            resolved_at=model.resolved_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _require_user_exists(db: Session, user_id: int, *, field: str) -> None:
        """Vérifie qu'un utilisateur existe en base."""
        user = db.get(UserModel, user_id)
        if user is None:
            raise IncidentServiceError(
                code="incident_user_not_found",
                message="user does not exist",
                details={field: str(user_id)},
            )

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        """Valide les paramètres de pagination."""
        if limit <= 0 or limit > 100:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident pagination is invalid",
                details={"field": "limit"},
            )
        if offset < 0:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident pagination is invalid",
                details={"field": "offset"},
            )

    @staticmethod
    def create_incident(
        db: Session,
        *,
        payload: SupportIncidentCreatePayload,
        actor_user_id: int | None,
        request_id: str,
    ) -> SupportIncidentData:
        """
        Crée un nouvel incident support.

        Args:
            db: Session de base de données.
            payload: Données de l'incident à créer.
            actor_user_id: Identifiant de l'utilisateur créant l'incident.
            request_id: Identifiant de requête pour le logging.

        Returns:
            Incident créé.

        Raises:
            IncidentServiceError: Si la validation échoue.
        """
        if payload.category not in VALID_INCIDENT_CATEGORY:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident category is invalid",
                details={"field": "category"},
            )
        if payload.priority not in VALID_INCIDENT_PRIORITY:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident priority is invalid",
                details={"field": "priority"},
            )
        title = payload.title.strip()
        description = payload.description.strip()
        if not title:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident title is required",
                details={"field": "title"},
            )
        if not description:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident description is required",
                details={"field": "description"},
            )
        IncidentService._require_user_exists(db, payload.user_id, field="user_id")
        if payload.assigned_to_user_id is not None:
            IncidentService._require_user_exists(
                db,
                payload.assigned_to_user_id,
                field="assigned_to_user_id",
            )

        model = SupportIncidentModel(
            user_id=payload.user_id,
            created_by_user_id=actor_user_id,
            assigned_to_user_id=payload.assigned_to_user_id,
            category=payload.category,
            title=title,
            description=description,
            status="open",
            priority=payload.priority,
            resolved_at=None,
        )
        db.add(model)
        db.flush()
        increment_counter("support_incidents_total", 1.0)
        increment_counter("support_incidents_open", 1.0)
        logger.info(
            (
                "support_incident_created request_id=%s incident_id=%s "
                "user_id=%s status=%s priority=%s"
            ),
            request_id,
            model.id,
            model.user_id,
            model.status,
            model.priority,
        )
        return IncidentService._to_data(model)

    @staticmethod
    def list_incidents(
        db: Session, *, filters: SupportIncidentListFilters
    ) -> SupportIncidentListData:
        """
        Liste les incidents avec filtres et pagination.

        Args:
            db: Session de base de données.
            filters: Filtres à appliquer (user_id, status, priority).

        Returns:
            Liste paginée des incidents.
        """
        IncidentService._validate_pagination(filters.limit, filters.offset)
        if filters.status is not None and filters.status not in VALID_INCIDENT_STATUS:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident status is invalid",
                details={"field": "status"},
            )
        if filters.priority is not None and filters.priority not in VALID_INCIDENT_PRIORITY:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="incident priority is invalid",
                details={"field": "priority"},
            )

        query = select(SupportIncidentModel)
        count_query = select(func.count(SupportIncidentModel.id))

        if filters.user_id is not None:
            query = query.where(SupportIncidentModel.user_id == filters.user_id)
            count_query = count_query.where(SupportIncidentModel.user_id == filters.user_id)
        if filters.status is not None:
            query = query.where(SupportIncidentModel.status == filters.status)
            count_query = count_query.where(SupportIncidentModel.status == filters.status)
        if filters.priority is not None:
            query = query.where(SupportIncidentModel.priority == filters.priority)
            count_query = count_query.where(SupportIncidentModel.priority == filters.priority)

        query = (
            query.order_by(desc(SupportIncidentModel.created_at), desc(SupportIncidentModel.id))
            .limit(filters.limit)
            .offset(filters.offset)
        )
        incidents = db.scalars(query).all()
        total = int(db.scalar(count_query) or 0)
        return SupportIncidentListData(
            incidents=[IncidentService._to_data(item) for item in incidents],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    @staticmethod
    def list_incidents_for_user(
        db: Session,
        *,
        user_id: int,
        limit: int = 20,
    ) -> list[SupportIncidentData]:
        """Liste les incidents d'un utilisateur spécifique."""
        IncidentService._validate_pagination(limit, 0)
        query = (
            select(SupportIncidentModel)
            .where(SupportIncidentModel.user_id == user_id)
            .order_by(desc(SupportIncidentModel.created_at), desc(SupportIncidentModel.id))
            .limit(limit)
        )
        incidents = db.scalars(query).all()
        return [IncidentService._to_data(item) for item in incidents]

    @staticmethod
    def update_incident(
        db: Session,
        *,
        incident_id: int,
        payload: SupportIncidentUpdatePayload,
        request_id: str,
    ) -> SupportIncidentData:
        """
        Met à jour un incident existant.

        Valide les transitions d'état et met à jour resolved_at si applicable.

        Args:
            db: Session de base de données.
            incident_id: Identifiant de l'incident.
            payload: Modifications à appliquer.
            request_id: Identifiant de requête pour le logging.

        Returns:
            Incident mis à jour.

        Raises:
            IncidentServiceError: Si l'incident n'existe pas ou transition invalide.
        """
        model = db.get(SupportIncidentModel, incident_id)
        if model is None:
            raise IncidentServiceError(
                code="incident_not_found",
                message="incident was not found",
                details={"incident_id": str(incident_id)},
            )

        previous_status = model.status
        has_changes = False

        if payload.priority is not None:
            if payload.priority not in VALID_INCIDENT_PRIORITY:
                raise IncidentServiceError(
                    code="incident_validation_error",
                    message="incident priority is invalid",
                    details={"field": "priority"},
                )
            model.priority = payload.priority
            has_changes = True

        if payload.description is not None:
            description = payload.description.strip()
            if not description:
                raise IncidentServiceError(
                    code="incident_validation_error",
                    message="incident description is required",
                    details={"field": "description"},
                )
            model.description = description
            has_changes = True

        if payload.assigned_to_user_id is not None:
            IncidentService._require_user_exists(
                db,
                payload.assigned_to_user_id,
                field="assigned_to_user_id",
            )
            model.assigned_to_user_id = payload.assigned_to_user_id
            has_changes = True

        if payload.status is not None:
            target_status = payload.status
            if target_status not in VALID_INCIDENT_STATUS:
                raise IncidentServiceError(
                    code="incident_validation_error",
                    message="incident status is invalid",
                    details={"field": "status"},
                )
            if (
                target_status != model.status
                and target_status not in ALLOWED_STATUS_TRANSITIONS.get(model.status, set())
            ):
                raise IncidentServiceError(
                    code="incident_invalid_transition",
                    message="incident status transition is not allowed",
                    details={"from_status": model.status, "to_status": target_status},
                )
            model.status = target_status
            has_changes = True

        if not has_changes:
            raise IncidentServiceError(
                code="incident_validation_error",
                message="no incident update field was provided",
                details={"field": "payload"},
            )

        if model.status in {"resolved", "closed"} and model.resolved_at is None:
            model.resolved_at = datetime.now(timezone.utc)
        if model.status in {"open", "in_progress"}:
            model.resolved_at = None

        db.flush()

        if previous_status in {"open", "in_progress"} and model.status in {"resolved", "closed"}:
            increment_counter("support_incidents_open", -1.0)
            if model.created_at is not None and model.resolved_at is not None:
                created_at = IncidentService._coerce_utc(model.created_at)
                resolved_at = IncidentService._coerce_utc(model.resolved_at)
                resolution_seconds = max(
                    0.0,
                    (resolved_at - created_at).total_seconds(),
                )
                observe_duration("support_incidents_resolution_seconds", resolution_seconds)
        logger.info(
            "support_incident_updated request_id=%s incident_id=%s status=%s priority=%s",
            request_id,
            model.id,
            model.status,
            model.priority,
        )
        return IncidentService._to_data(model)
