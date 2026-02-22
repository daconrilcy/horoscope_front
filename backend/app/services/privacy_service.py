"""
Service de conformité vie privée (RGPD).

Ce module gère les demandes d'export et de suppression de données
utilisateur conformément aux obligations RGPD.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import monotonic
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import (
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.observability.metrics import increment_counter, observe_duration

logger = logging.getLogger(__name__)


class PrivacyServiceError(Exception):
    """Exception levée lors d'erreurs de traitement vie privée."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de vie privée.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class PrivacyRequestData(BaseModel):
    """Données d'une demande de vie privée (export ou suppression)."""

    request_id: int
    request_kind: str
    status: str
    requested_at: datetime
    completed_at: datetime | None
    result_data: dict[str, object]
    error_reason: str | None


class PrivacyEvidenceRequestSummary(BaseModel):
    """Résumé d'une demande pour les preuves de conformité."""

    request_id: int
    request_kind: str
    status: str
    requested_at: datetime
    completed_at: datetime | None
    error_reason: str | None
    result_summary: dict[str, object]


class PrivacyEvidenceAuditSummary(BaseModel):
    """Résumé d'un événement d'audit pour les preuves de conformité."""

    event_id: int
    request_id: str
    action: str
    status: str
    target_type: str
    target_id: str | None
    details: dict[str, object]
    created_at: datetime


class PrivacyComplianceEvidenceData(BaseModel):
    """Preuves de conformité RGPD complètes pour un utilisateur."""

    schema_version: str
    user_id: int
    export_request: PrivacyEvidenceRequestSummary
    delete_request: PrivacyEvidenceRequestSummary
    audit_events: list[PrivacyEvidenceAuditSummary]
    collected_at: datetime


class PrivacyService:
    """
    Service de conformité vie privée RGPD.

    Gère les demandes d'export et de suppression de données utilisateur
    avec traçabilité complète pour la conformité réglementaire.
    """

    @staticmethod
    def _summarize_result_data(
        request_kind: str, result_data: dict[str, object]
    ) -> dict[str, object]:
        """Résume les données de résultat pour les preuves de conformité."""
        if request_kind == "export":
            return {
                "contains_user_data": isinstance(result_data.get("user"), dict),
                "birth_profile_present": result_data.get("birth_profile") is not None,
                "chart_results_count": int(result_data.get("chart_results_count", 0)),
                "conversations_count": int(result_data.get("conversations_count", 0)),
                "messages_count": int(result_data.get("messages_count", 0)),
                "subscriptions_count": int(result_data.get("subscriptions_count", 0)),
                "payment_attempts_count": int(result_data.get("payment_attempts_count", 0)),
                "quota_usage_count": int(result_data.get("quota_usage_count", 0)),
            }
        if request_kind == "delete":
            deleted_entities = result_data.get("deleted_entities")
            deleted_list = deleted_entities if isinstance(deleted_entities, list) else []
            return {
                "account_anonymized": bool(result_data.get("account_anonymized", False)),
                "deleted_entities_count": len(deleted_list),
                "deleted_entities": [str(item) for item in deleted_list],
            }
        return {
            "result_keys": sorted(str(key) for key in result_data.keys()),
        }

    @staticmethod
    def _to_evidence_request_summary(
        request: UserPrivacyRequestModel,
    ) -> PrivacyEvidenceRequestSummary:
        """Convertit une demande en résumé pour les preuves."""
        return PrivacyEvidenceRequestSummary(
            request_id=request.id,
            request_kind=request.request_kind,
            status=request.status,
            requested_at=request.requested_at,
            completed_at=request.completed_at,
            error_reason=request.error_reason,
            result_summary=PrivacyService._summarize_result_data(
                request.request_kind, request.result_data
            ),
        )

    @staticmethod
    def _extract_request_correlation_id(request: UserPrivacyRequestModel) -> str | None:
        """Extrait l'identifiant de corrélation d'une demande."""
        value = request.request_data.get("request_id")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @staticmethod
    def _mark_failed(
        request: UserPrivacyRequestModel,
        *,
        reason: str,
    ) -> None:
        """Marque une demande comme échouée avec la raison."""
        request.status = "failed"
        request.error_reason = reason[:255]
        request.completed_at = datetime.now(timezone.utc)

    @staticmethod
    def _to_request_data(request: UserPrivacyRequestModel) -> PrivacyRequestData:
        """Convertit un modèle de demande en DTO."""
        return PrivacyRequestData(
            request_id=request.id,
            request_kind=request.request_kind,
            status=request.status,
            requested_at=request.requested_at,
            completed_at=request.completed_at,
            result_data=request.result_data,
            error_reason=request.error_reason,
        )

    @staticmethod
    def _get_latest_request(
        db: Session,
        *,
        user_id: int,
        request_kind: str,
    ) -> UserPrivacyRequestModel | None:
        """Récupère la dernière demande d'un type donné pour un utilisateur."""
        return db.scalar(
            select(UserPrivacyRequestModel)
            .where(
                UserPrivacyRequestModel.user_id == user_id,
                UserPrivacyRequestModel.request_kind == request_kind,
            )
            .order_by(
                UserPrivacyRequestModel.requested_at.desc(),
                UserPrivacyRequestModel.id.desc(),
            )
            .limit(1)
        )

    @staticmethod
    def get_latest_export_status(db: Session, *, user_id: int) -> PrivacyRequestData:
        """Récupère le statut de la dernière demande d'export."""
        request = PrivacyService._get_latest_request(db, user_id=user_id, request_kind="export")
        if request is None:
            raise PrivacyServiceError(
                code="privacy_not_found",
                message="privacy export request was not found",
                details={"request_kind": "export"},
            )
        return PrivacyService._to_request_data(request)

    @staticmethod
    def get_latest_delete_status(db: Session, *, user_id: int) -> PrivacyRequestData:
        """Récupère le statut de la dernière demande de suppression."""
        request = PrivacyService._get_latest_request(db, user_id=user_id, request_kind="delete")
        if request is None:
            raise PrivacyServiceError(
                code="privacy_not_found",
                message="privacy delete request was not found",
                details={"request_kind": "delete"},
            )
        return PrivacyService._to_request_data(request)

    @staticmethod
    def request_export(db: Session, *, user_id: int, request_id: str) -> PrivacyRequestData:
        """
        Exécute une demande d'export de données RGPD.

        Opération idempotente : retourne l'export existant si déjà complété.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            request_id: Identifiant de corrélation de la requête.

        Returns:
            Données de la demande d'export.

        Raises:
            PrivacyServiceError: Si un export est déjà en cours.
        """
        start = monotonic()
        latest = PrivacyService._get_latest_request(db, user_id=user_id, request_kind="export")
        if latest is not None and latest.status == "completed":
            logger.info(
                "privacy_export_idempotent_reuse request_id=%s user_id=%s privacy_request_id=%s",
                request_id,
                user_id,
                latest.id,
            )
            return PrivacyService._to_request_data(latest)
        if latest is not None and latest.status in {"requested", "processing"}:
            increment_counter("privacy_request_failures_total", 1.0)
            raise PrivacyServiceError(
                code="privacy_request_conflict",
                message="an export request is already in progress",
                details={"request_kind": "export"},
            )

        request = UserPrivacyRequestModel(
            user_id=user_id,
            request_kind="export",
            status="requested",
            request_data={"request_id": request_id},
            result_data={},
            error_reason=None,
        )
        db.add(request)
        db.flush()
        request.status = "processing"
        db.flush()
        try:
            user = db.get(UserModel, user_id)
            if user is None:
                raise PrivacyServiceError(
                    code="privacy_request_invalid",
                    message="user does not exist",
                    details={"user_id": str(user_id)},
                )

            birth_profile = db.scalar(
                select(UserBirthProfileModel)
                .where(UserBirthProfileModel.user_id == user_id)
                .limit(1)
            )
            chart_results = db.scalars(
                select(ChartResultModel).where(ChartResultModel.user_id == user_id)
            ).all()
            conversations = db.scalars(
                select(ChatConversationModel).where(ChatConversationModel.user_id == user_id)
            ).all()
            conversation_ids = [conversation.id for conversation in conversations]
            messages = []
            if conversation_ids:
                messages = db.scalars(
                    select(ChatMessageModel).where(
                        ChatMessageModel.conversation_id.in_(conversation_ids)
                    )
                ).all()

            subscriptions = db.scalars(
                select(UserSubscriptionModel).where(UserSubscriptionModel.user_id == user_id)
            ).all()
            payment_attempts = db.scalars(
                select(PaymentAttemptModel).where(PaymentAttemptModel.user_id == user_id)
            ).all()
            quota_usage = db.scalars(
                select(UserDailyQuotaUsageModel).where(UserDailyQuotaUsageModel.user_id == user_id)
            ).all()

            request.status = "completed"
            request.completed_at = datetime.now(timezone.utc)
            request.result_data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at.isoformat(),
                },
                "birth_profile": (
                    {
                        "birth_date": birth_profile.birth_date.isoformat(),
                        "birth_time": birth_profile.birth_time,
                        "birth_place": birth_profile.birth_place,
                        "birth_timezone": birth_profile.birth_timezone,
                    }
                    if birth_profile is not None
                    else None
                ),
                "chart_results_count": len(chart_results),
                "conversations_count": len(conversations),
                "messages_count": len(messages),
                "subscriptions_count": len(subscriptions),
                "payment_attempts_count": len(payment_attempts),
                "quota_usage_count": len(quota_usage),
            }
            db.flush()
        except PrivacyServiceError as error:
            increment_counter("privacy_request_failures_total", 1.0)
            PrivacyService._mark_failed(request, reason=error.code)
            db.flush()
            raise
        except Exception as error:
            increment_counter("privacy_request_failures_total", 1.0)
            PrivacyService._mark_failed(request, reason="privacy_request_failed")
            db.flush()
            raise PrivacyServiceError(
                code="privacy_request_failed",
                message="privacy export request failed",
                details={},
            ) from error

        increment_counter("privacy_export_requests_total", 1.0)
        observe_duration("privacy_export_seconds", monotonic() - start)
        logger.info(
            "privacy_export_completed request_id=%s user_id=%s privacy_request_id=%s",
            request_id,
            user_id,
            request.id,
        )
        return PrivacyService._to_request_data(request)

    @staticmethod
    def request_delete(db: Session, *, user_id: int, request_id: str) -> PrivacyRequestData:
        """
        Exécute une demande de suppression de données RGPD.

        Supprime toutes les données utilisateur et anonymise le compte.
        Opération idempotente : retourne la suppression existante si déjà complétée.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            request_id: Identifiant de corrélation de la requête.

        Returns:
            Données de la demande de suppression.

        Raises:
            PrivacyServiceError: Si une suppression est déjà en cours.
        """
        start = monotonic()
        latest = PrivacyService._get_latest_request(db, user_id=user_id, request_kind="delete")
        if latest is not None and latest.status == "completed":
            logger.info(
                "privacy_delete_idempotent_reuse request_id=%s user_id=%s privacy_request_id=%s",
                request_id,
                user_id,
                latest.id,
            )
            return PrivacyService._to_request_data(latest)
        if latest is not None and latest.status in {"requested", "processing"}:
            increment_counter("privacy_request_failures_total", 1.0)
            raise PrivacyServiceError(
                code="privacy_request_conflict",
                message="a delete request is already in progress",
                details={"request_kind": "delete"},
            )

        request = UserPrivacyRequestModel(
            user_id=user_id,
            request_kind="delete",
            status="requested",
            request_data={"request_id": request_id},
            result_data={},
            error_reason=None,
        )
        db.add(request)
        db.flush()
        request.status = "processing"
        db.flush()
        try:
            user = db.get(UserModel, user_id)
            if user is None:
                raise PrivacyServiceError(
                    code="privacy_request_invalid",
                    message="user does not exist",
                    details={"user_id": str(user_id)},
                )

            conversation_ids = db.scalars(
                select(ChatConversationModel.id).where(ChatConversationModel.user_id == user_id)
            ).all()
            if conversation_ids:
                db.execute(
                    delete(ChatMessageModel).where(
                        ChatMessageModel.conversation_id.in_(conversation_ids)
                    )
                )
            db.execute(
                delete(ChatConversationModel).where(ChatConversationModel.user_id == user_id)
            )
            db.execute(
                delete(UserBirthProfileModel).where(UserBirthProfileModel.user_id == user_id)
            )
            db.execute(delete(ChartResultModel).where(ChartResultModel.user_id == user_id))
            db.execute(
                delete(UserDailyQuotaUsageModel).where(UserDailyQuotaUsageModel.user_id == user_id)
            )
            db.execute(delete(PaymentAttemptModel).where(PaymentAttemptModel.user_id == user_id))
            db.execute(
                delete(SubscriptionPlanChangeModel).where(
                    SubscriptionPlanChangeModel.user_id == user_id
                )
            )
            db.execute(
                delete(UserSubscriptionModel).where(UserSubscriptionModel.user_id == user_id)
            )

            deleted_timestamp = int(datetime.now(timezone.utc).timestamp())
            anonymized_email = f"deleted-user-{user_id}-{deleted_timestamp}@deleted.local"
            user.email = anonymized_email
            user.password_hash = hash_password(uuid4().hex)
            user.role = "user"

            request.status = "completed"
            request.completed_at = datetime.now(timezone.utc)
            request.result_data = {
                "account_anonymized": True,
                "deleted_entities": [
                    "user_birth_profiles",
                    "chart_results",
                    "chat_conversations",
                    "chat_messages",
                    "user_daily_quota_usages",
                    "payment_attempts",
                    "subscription_plan_changes",
                    "user_subscriptions",
                ],
            }
            db.flush()
        except PrivacyServiceError as error:
            increment_counter("privacy_request_failures_total", 1.0)
            PrivacyService._mark_failed(request, reason=error.code)
            db.flush()
            raise
        except Exception as error:
            increment_counter("privacy_request_failures_total", 1.0)
            PrivacyService._mark_failed(request, reason="privacy_request_failed")
            db.flush()
            raise PrivacyServiceError(
                code="privacy_request_failed",
                message="privacy delete request failed",
                details={},
            ) from error

        increment_counter("privacy_delete_requests_total", 1.0)
        observe_duration("privacy_delete_seconds", monotonic() - start)
        logger.info(
            "privacy_delete_completed request_id=%s user_id=%s privacy_request_id=%s",
            request_id,
            user_id,
            request.id,
        )
        return PrivacyService._to_request_data(request)

    @staticmethod
    def get_compliance_evidence(
        db: Session, *, user_id: int, max_audit_events: int = 50
    ) -> PrivacyComplianceEvidenceData:
        """
        Génère les preuves de conformité RGPD pour un utilisateur.

        Agrège les demandes d'export/suppression et les événements d'audit
        pour constituer un dossier de conformité.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            max_audit_events: Nombre maximum d'événements d'audit à inclure.

        Returns:
            Preuves de conformité complètes.

        Raises:
            PrivacyServiceError: Si les preuves sont incomplètes.
        """
        if max_audit_events <= 0 or max_audit_events > 200:
            raise PrivacyServiceError(
                code="privacy_request_invalid",
                message="privacy evidence pagination is invalid",
                details={"field": "max_audit_events"},
            )

        user = db.get(UserModel, user_id)
        if user is None:
            raise PrivacyServiceError(
                code="privacy_request_invalid",
                message="user does not exist",
                details={"user_id": str(user_id)},
            )

        export_request = PrivacyService._get_latest_request(
            db, user_id=user_id, request_kind="export"
        )
        delete_request = PrivacyService._get_latest_request(
            db, user_id=user_id, request_kind="delete"
        )

        missing_artifacts: list[str] = []
        if export_request is None:
            missing_artifacts.append("export")
        elif export_request.status != "completed":
            missing_artifacts.append("export_completed")
        if delete_request is None:
            missing_artifacts.append("delete")
        elif delete_request.status != "completed":
            missing_artifacts.append("delete_completed")

        export_correlation_id: str | None = None
        delete_correlation_id: str | None = None
        if export_request is not None and export_request.status == "completed":
            export_correlation_id = PrivacyService._extract_request_correlation_id(export_request)
            if export_correlation_id is None:
                missing_artifacts.append("export_request_id")
        if delete_request is not None and delete_request.status == "completed":
            delete_correlation_id = PrivacyService._extract_request_correlation_id(delete_request)
            if delete_correlation_id is None:
                missing_artifacts.append("delete_request_id")

        audit_events: list[AuditEventModel] = []
        if (
            not missing_artifacts
            and export_correlation_id is not None
            and delete_correlation_id is not None
        ):
            correlation_ids = sorted({export_correlation_id, delete_correlation_id})
            audit_events = db.scalars(
                select(AuditEventModel)
                .where(
                    AuditEventModel.target_type == "user",
                    AuditEventModel.target_id == str(user_id),
                    AuditEventModel.action.in_(("privacy_export", "privacy_delete")),
                    AuditEventModel.request_id.in_(correlation_ids),
                )
                .order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
                .limit(max_audit_events)
            ).all()

            has_export_audit = any(
                event.action == "privacy_export"
                and event.request_id == export_correlation_id
                and event.status == "success"
                for event in audit_events
            )
            has_delete_audit = any(
                event.action == "privacy_delete"
                and event.request_id == delete_correlation_id
                and event.status == "success"
                for event in audit_events
            )
            if not has_export_audit:
                missing_artifacts.append("audit_export")
            if not has_delete_audit:
                missing_artifacts.append("audit_delete")

        if missing_artifacts:
            raise PrivacyServiceError(
                code="privacy_evidence_incomplete",
                message="privacy evidence is incomplete",
                details={"missing_artifacts": ",".join(missing_artifacts)},
            )

        assert export_request is not None
        assert delete_request is not None

        collected_at_candidates = [export_request.requested_at, delete_request.requested_at]
        collected_at_candidates.extend(event.created_at for event in audit_events)
        collected_at = max(collected_at_candidates)

        return PrivacyComplianceEvidenceData(
            schema_version="1.0",
            user_id=user_id,
            export_request=PrivacyService._to_evidence_request_summary(export_request),
            delete_request=PrivacyService._to_evidence_request_summary(delete_request),
            audit_events=[
                PrivacyEvidenceAuditSummary(
                    event_id=event.id,
                    request_id=event.request_id,
                    action=event.action,
                    status=event.status,
                    target_type=event.target_type,
                    target_id=event.target_id,
                    details=event.details,
                    created_at=event.created_at,
                )
                for event in audit_events
            ],
            collected_at=collected_at,
        )
