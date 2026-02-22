"""
Service de réconciliation B2B.

Ce module gère la réconciliation entre les données d'usage et de facturation
des comptes entreprise, détectant et permettant de résoudre les écarts.
"""

from __future__ import annotations

from datetime import date, timedelta
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_billing import EnterpriseBillingCycleModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.services.b2b_billing_service import B2BBillingService


class B2BReconciliationServiceError(Exception):
    """Exception levée lors d'erreurs de réconciliation B2B."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de réconciliation.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ReconciliationSeverity(StrEnum):
    """Niveaux de gravité des écarts de réconciliation."""

    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"


class ReconciliationStatus(StrEnum):
    """Statuts possibles d'un problème de réconciliation."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class ReconciliationActionCode(StrEnum):
    """Actions disponibles pour résoudre un problème de réconciliation."""

    RECALCULATE = "recalculate"
    RESYNC = "resync"
    MARK_INVESTIGATED = "mark_investigated"
    ANNOTATE = "annotate"


class ReconciliationActionHint(BaseModel):
    """Suggestion d'action de réconciliation avec description."""

    code: ReconciliationActionCode
    label: str
    description: str


class ReconciliationLastAction(BaseModel):
    """Dernière action effectuée sur un problème de réconciliation."""

    action: ReconciliationActionCode
    at: str
    actor_user_id: int | None
    note: str | None = None


class ReconciliationIssueData(BaseModel):
    """Données d'un problème de réconciliation détecté."""

    issue_id: str
    account_id: int
    period_start: date
    period_end: date
    mismatch_type: str
    severity: ReconciliationSeverity
    status: ReconciliationStatus
    usage_measured_units: int
    billing_consumed_units: int
    delta_units: int
    billing_cycle_id: int | None
    billable_units: int | None
    total_amount_cents: int | None
    source_trace: dict[str, Any]
    recommended_actions: list[ReconciliationActionHint]
    last_action: ReconciliationLastAction | None


class ReconciliationIssueListData(BaseModel):
    """Liste paginée de problèmes de réconciliation."""

    items: list[ReconciliationIssueData]
    total: int
    limit: int
    offset: int


class ReconciliationIssueDetailData(BaseModel):
    """Détails complets d'un problème avec historique des actions."""

    issue: ReconciliationIssueData
    action_log: list[ReconciliationLastAction]


class ReconciliationActionResultData(BaseModel):
    """Résultat de l'exécution d'une action de réconciliation."""

    issue_id: str
    action: ReconciliationActionCode
    status: str
    message: str
    correction_state: ReconciliationStatus


class ReconciliationActionPayload(BaseModel):
    """Payload pour exécuter une action de réconciliation."""

    action: ReconciliationActionCode
    note: str | None = None


class B2BReconciliationService:
    """
    Service de réconciliation usage/facturation B2B.

    Détecte les écarts entre les données d'usage mesurées et les montants
    facturés, et fournit des outils pour investiguer et corriger ces écarts.
    """

    _TARGET_TYPE = "enterprise_billing_reconciliation"
    _ACTION_HINTS = [
        ReconciliationActionHint(
            code=ReconciliationActionCode.RECALCULATE,
            label="Recalculer le cycle",
            description="Rejoue le calcul de cycle facture pour la periode.",
        ),
        ReconciliationActionHint(
            code=ReconciliationActionCode.RESYNC,
            label="Resynchroniser",
            description="Relance la synchronisation usage/facturation.",
        ),
        ReconciliationActionHint(
            code=ReconciliationActionCode.MARK_INVESTIGATED,
            label="Marquer investigue",
            description="Indique que le cas est pris en charge par les operations.",
        ),
        ReconciliationActionHint(
            code=ReconciliationActionCode.ANNOTATE,
            label="Ajouter une note",
            description="Ajoute un commentaire de suivi au dossier de reconciliation.",
        ),
    ]

    @staticmethod
    def _month_bounds(day: date) -> tuple[date, date]:
        """Calcule les bornes du mois contenant la date donnée."""
        month_start = day.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        return month_start, month_end

    @staticmethod
    def _normalize_period_bounds(
        period_start: date | None, period_end: date | None
    ) -> tuple[date | None, date | None]:
        """Normalise les bornes de période aux limites de mois."""
        normalized_start: date | None = None
        normalized_end: date | None = None
        if period_start is not None:
            normalized_start, _ = B2BReconciliationService._month_bounds(period_start)
        if period_end is not None:
            _, normalized_end = B2BReconciliationService._month_bounds(period_end)
        return normalized_start, normalized_end

    @staticmethod
    def _issue_id(*, account_id: int, period_start: date, period_end: date) -> str:
        """Génère un identifiant unique pour un problème de réconciliation."""
        return f"{account_id}:{period_start.isoformat()}:{period_end.isoformat()}"

    @staticmethod
    def parse_issue_id(issue_id: str) -> tuple[int, date, date]:
        """
        Parse un identifiant de problème de réconciliation.

        Args:
            issue_id: Identifiant au format "account_id:start:end".

        Returns:
            Tuple (account_id, period_start, period_end).

        Raises:
            B2BReconciliationServiceError: Si le format est invalide.
        """
        parts = issue_id.split(":")
        if len(parts) != 3:
            raise B2BReconciliationServiceError(
                code="invalid_issue_id",
                message="reconciliation issue id is invalid",
                details={"issue_id": issue_id},
            )
        account_raw, start_raw, end_raw = parts
        if not account_raw.isdigit():
            raise B2BReconciliationServiceError(
                code="invalid_issue_id",
                message="reconciliation issue id is invalid",
                details={"issue_id": issue_id},
            )
        try:
            period_start = date.fromisoformat(start_raw)
            period_end = date.fromisoformat(end_raw)
        except ValueError as error:
            raise B2BReconciliationServiceError(
                code="invalid_issue_id",
                message="reconciliation issue id is invalid",
                details={"issue_id": issue_id},
            ) from error
        if period_start > period_end:
            raise B2BReconciliationServiceError(
                code="invalid_issue_id",
                message="reconciliation issue id is invalid",
                details={"issue_id": issue_id},
            )
        return int(account_raw), period_start, period_end

    @staticmethod
    def _severity(
        usage_units: int, billed_units: int, cycle_exists: bool
    ) -> ReconciliationSeverity:
        """Détermine la gravité d'un écart entre usage et facturation."""
        delta = abs(usage_units - billed_units)
        if delta == 0:
            return ReconciliationSeverity.NONE
        if not cycle_exists:
            return ReconciliationSeverity.MAJOR
        if delta <= 5:
            return ReconciliationSeverity.MINOR
        return ReconciliationSeverity.MAJOR

    @staticmethod
    def _mismatch_type(usage_units: int, billed_units: int, cycle_exists: bool) -> str:
        """Classifie le type d'écart détecté."""
        if not cycle_exists and usage_units > 0:
            return "missing_billing_cycle"
        if cycle_exists and usage_units == 0 and billed_units > 0:
            return "missing_usage_data"
        if usage_units != billed_units:
            return "usage_vs_billing_mismatch"
        return "coherent"

    @staticmethod
    def _status(
        *,
        severity: ReconciliationSeverity,
        last_action: ReconciliationLastAction | None,
    ) -> ReconciliationStatus:
        """Détermine le statut du problème selon sa gravité et les actions."""
        if severity == ReconciliationSeverity.NONE:
            return ReconciliationStatus.RESOLVED
        if last_action is None:
            return ReconciliationStatus.OPEN
        if last_action.action in {
            ReconciliationActionCode.MARK_INVESTIGATED,
            ReconciliationActionCode.ANNOTATE,
            ReconciliationActionCode.RECALCULATE,
            ReconciliationActionCode.RESYNC,
        }:
            return ReconciliationStatus.INVESTIGATING
        return ReconciliationStatus.OPEN

    @staticmethod
    def _usage_by_period(
        db: Session,
        *,
        account_id: int | None,
        period_start: date | None,
        period_end: date | None,
    ) -> dict[tuple[int, date, date], dict[str, int]]:
        """Agrège les données d'usage par période mensuelle."""
        query = select(
            EnterpriseDailyUsageModel.enterprise_account_id,
            EnterpriseDailyUsageModel.usage_date,
            EnterpriseDailyUsageModel.used_count,
        )
        if account_id is not None:
            query = query.where(EnterpriseDailyUsageModel.enterprise_account_id == account_id)
        if period_start is not None:
            query = query.where(EnterpriseDailyUsageModel.usage_date >= period_start)
        if period_end is not None:
            query = query.where(EnterpriseDailyUsageModel.usage_date <= period_end)

        rows = db.execute(query).all()
        grouped: dict[tuple[int, date, date], dict[str, int]] = {}
        for row in rows:
            month_start, month_end = B2BReconciliationService._month_bounds(row.usage_date)
            key = (row.enterprise_account_id, month_start, month_end)
            bucket = grouped.setdefault(key, {"usage_units": 0, "usage_rows": 0})
            bucket["usage_units"] += max(0, int(row.used_count))
            bucket["usage_rows"] += 1
        return grouped

    @staticmethod
    def _billing_by_period(
        db: Session,
        *,
        account_id: int | None,
        period_start: date | None,
        period_end: date | None,
    ) -> dict[tuple[int, date, date], EnterpriseBillingCycleModel]:
        """Récupère les cycles de facturation par période."""
        query = select(EnterpriseBillingCycleModel)
        if account_id is not None:
            query = query.where(EnterpriseBillingCycleModel.enterprise_account_id == account_id)
        if period_start is not None:
            query = query.where(EnterpriseBillingCycleModel.period_start >= period_start)
        if period_end is not None:
            query = query.where(EnterpriseBillingCycleModel.period_end <= period_end)
        rows = db.scalars(query).all()
        return {(row.enterprise_account_id, row.period_start, row.period_end): row for row in rows}

    @staticmethod
    def _latest_actions(
        db: Session,
        *,
        issue_ids: set[str],
    ) -> dict[str, ReconciliationLastAction]:
        """Récupère la dernière action pour chaque problème."""
        if not issue_ids:
            return {}
        rows = db.scalars(
            select(AuditEventModel)
            .where(
                AuditEventModel.target_type == B2BReconciliationService._TARGET_TYPE,
                AuditEventModel.target_id.in_(issue_ids),
            )
            .order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
        ).all()
        output: dict[str, ReconciliationLastAction] = {}
        for row in rows:
            target_id = row.target_id or ""
            if target_id in output:
                continue
            action_code = row.details.get("action_code")
            if not isinstance(action_code, str):
                continue
            if action_code not in {code.value for code in ReconciliationActionCode}:
                continue
            note_value = row.details.get("note")
            output[target_id] = ReconciliationLastAction(
                action=ReconciliationActionCode(action_code),
                at=row.created_at.isoformat(),
                actor_user_id=row.actor_user_id,
                note=note_value if isinstance(note_value, str) and note_value else None,
            )
        return output

    @staticmethod
    def _build_issue(
        *,
        account_id: int,
        period_start: date,
        period_end: date,
        usage_units: int,
        usage_rows: int,
        cycle: EnterpriseBillingCycleModel | None,
        last_action: ReconciliationLastAction | None,
    ) -> ReconciliationIssueData:
        """Construit un objet problème de réconciliation."""
        billed_units = cycle.consumed_units if cycle is not None else 0
        severity = B2BReconciliationService._severity(
            usage_units=usage_units,
            billed_units=billed_units,
            cycle_exists=cycle is not None,
        )
        mismatch_type = B2BReconciliationService._mismatch_type(
            usage_units=usage_units,
            billed_units=billed_units,
            cycle_exists=cycle is not None,
        )
        status = B2BReconciliationService._status(severity=severity, last_action=last_action)
        return ReconciliationIssueData(
            issue_id=B2BReconciliationService._issue_id(
                account_id=account_id,
                period_start=period_start,
                period_end=period_end,
            ),
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            mismatch_type=mismatch_type,
            severity=severity,
            status=status,
            usage_measured_units=usage_units,
            billing_consumed_units=billed_units,
            delta_units=usage_units - billed_units,
            billing_cycle_id=cycle.id if cycle is not None else None,
            billable_units=cycle.billable_units if cycle is not None else None,
            total_amount_cents=cycle.total_amount_cents if cycle is not None else None,
            source_trace={
                "usage_rows": usage_rows,
                "billing_cycle_id": cycle.id if cycle is not None else None,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            },
            recommended_actions=B2BReconciliationService._ACTION_HINTS,
            last_action=last_action,
        )

    @staticmethod
    def list_issues(
        db: Session,
        *,
        account_id: int | None = None,
        period_start: date | None = None,
        period_end: date | None = None,
        severity: ReconciliationSeverity | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ReconciliationIssueListData:
        """
        Liste les problèmes de réconciliation avec filtres optionnels.

        Args:
            db: Session de base de données.
            account_id: Filtrer par compte (optionnel).
            period_start: Début de période (optionnel).
            period_end: Fin de période (optionnel).
            severity: Filtrer par gravité (optionnel).
            limit: Nombre maximum de résultats.
            offset: Décalage pour la pagination.

        Returns:
            Liste paginée des problèmes détectés.

        Raises:
            B2BReconciliationServiceError: Si la pagination est invalide.
        """
        if limit <= 0 or limit > 100:
            raise B2BReconciliationServiceError(
                code="invalid_reconciliation_pagination",
                message="reconciliation pagination is invalid",
                details={"field": "limit"},
            )
        if offset < 0:
            raise B2BReconciliationServiceError(
                code="invalid_reconciliation_pagination",
                message="reconciliation pagination is invalid",
                details={"field": "offset"},
            )
        if period_start is not None and period_end is not None and period_start > period_end:
            raise B2BReconciliationServiceError(
                code="invalid_reconciliation_period",
                message="reconciliation period is invalid",
                details={},
            )
        normalized_period_start, normalized_period_end = (
            B2BReconciliationService._normalize_period_bounds(period_start, period_end)
        )

        usage_map = B2BReconciliationService._usage_by_period(
            db,
            account_id=account_id,
            period_start=normalized_period_start,
            period_end=normalized_period_end,
        )
        billing_map = B2BReconciliationService._billing_by_period(
            db,
            account_id=account_id,
            period_start=normalized_period_start,
            period_end=normalized_period_end,
        )
        keys = set(usage_map.keys()) | set(billing_map.keys())
        issue_ids = {
            B2BReconciliationService._issue_id(
                account_id=account, period_start=start, period_end=end
            )
            for account, start, end in keys
        }
        latest_actions = B2BReconciliationService._latest_actions(db, issue_ids=issue_ids)

        issues: list[ReconciliationIssueData] = []
        for account, start, end in sorted(keys, key=lambda item: (item[0], item[1], item[2])):
            usage_bucket = usage_map.get((account, start, end), {"usage_units": 0, "usage_rows": 0})
            cycle = billing_map.get((account, start, end))
            issue_id = B2BReconciliationService._issue_id(
                account_id=account,
                period_start=start,
                period_end=end,
            )
            issue = B2BReconciliationService._build_issue(
                account_id=account,
                period_start=start,
                period_end=end,
                usage_units=usage_bucket["usage_units"],
                usage_rows=usage_bucket["usage_rows"],
                cycle=cycle,
                last_action=latest_actions.get(issue_id),
            )
            if severity is not None and issue.severity != severity:
                continue
            issues.append(issue)

        total = len(issues)
        return ReconciliationIssueListData(
            items=issues[offset : offset + limit],
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get_issue_detail(db: Session, *, issue_id: str) -> ReconciliationIssueDetailData:
        """
        Récupère les détails d'un problème avec l'historique des actions.

        Args:
            db: Session de base de données.
            issue_id: Identifiant du problème.

        Returns:
            Détails complets du problème.

        Raises:
            B2BReconciliationServiceError: Si le problème n'existe pas.
        """
        account_id, period_start, period_end = B2BReconciliationService.parse_issue_id(issue_id)
        listed = B2BReconciliationService.list_issues(
            db,
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            limit=100,
            offset=0,
        )
        issue = next((item for item in listed.items if item.issue_id == issue_id), None)
        if issue is None:
            raise B2BReconciliationServiceError(
                code="reconciliation_issue_not_found",
                message="reconciliation issue was not found",
                details={"issue_id": issue_id},
            )
        rows = db.scalars(
            select(AuditEventModel)
            .where(
                AuditEventModel.target_type == B2BReconciliationService._TARGET_TYPE,
                AuditEventModel.target_id == issue_id,
            )
            .order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
            .limit(20)
        ).all()
        action_log: list[ReconciliationLastAction] = []
        for row in rows:
            action_code = row.details.get("action_code")
            if not isinstance(action_code, str):
                continue
            if action_code not in {code.value for code in ReconciliationActionCode}:
                continue
            note_value = row.details.get("note")
            action_log.append(
                ReconciliationLastAction(
                    action=ReconciliationActionCode(action_code),
                    at=row.created_at.isoformat(),
                    actor_user_id=row.actor_user_id,
                    note=note_value if isinstance(note_value, str) and note_value else None,
                )
            )
        return ReconciliationIssueDetailData(issue=issue, action_log=action_log)

    @staticmethod
    def execute_action(
        db: Session,
        *,
        issue_id: str,
        payload: ReconciliationActionPayload,
    ) -> ReconciliationActionResultData:
        """
        Exécute une action de réconciliation sur un problème.

        Args:
            db: Session de base de données.
            issue_id: Identifiant du problème.
            payload: Action à exécuter avec note optionnelle.

        Returns:
            Résultat de l'exécution de l'action.
        """
        account_id, period_start, period_end = B2BReconciliationService.parse_issue_id(issue_id)
        if payload.action in {
            ReconciliationActionCode.RECALCULATE,
            ReconciliationActionCode.RESYNC,
        }:
            # Idempotent by design: close_cycle returns existing cycle if already closed.
            B2BBillingService.close_cycle(
                db,
                account_id=account_id,
                period_start=period_start,
                period_end=period_end,
                closed_by_user_id=None,
            )

        detail = B2BReconciliationService.get_issue_detail(db, issue_id=issue_id)
        correction_state = detail.issue.status
        if payload.action in {
            ReconciliationActionCode.MARK_INVESTIGATED,
            ReconciliationActionCode.ANNOTATE,
        }:
            correction_state = ReconciliationStatus.INVESTIGATING
        elif (
            payload.action
            in {
                ReconciliationActionCode.RECALCULATE,
                ReconciliationActionCode.RESYNC,
            }
            and detail.issue.severity != ReconciliationSeverity.NONE
        ):
            correction_state = ReconciliationStatus.INVESTIGATING
        return ReconciliationActionResultData(
            issue_id=issue_id,
            action=payload.action,
            status="accepted",
            message="reconciliation action executed",
            correction_state=correction_state,
        )
