"""
Service de monitoring opérationnel LLM (Story 66.37).

Agrège les données persistées de ``llm_call_logs`` pour exposer une surface
ops gouvernée, sans dépendre des métriques instance-locales.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
    LlmCallLogOperationalMetadataModel,
    LlmValidationStatus,
)
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.ops.llm.ops_contract import (
    NOMINAL_FAMILIES,
    REPAIR_MIN_OCCURRENCES,
    REPAIR_RATE_BASELINE_MULTIPLIER,
    REPAIR_RATE_MIN_DELTA,
    REPAIR_RATE_THRESHOLD,
    canonical_persona_label,
    is_impossible_state,
    is_unknown_allowed,
)

WINDOWS: dict[str, timedelta] = {
    "1h": timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
}


class LlmOpsDashboardMetrics(BaseModel):
    """Métriques LLM agrégées par dimension canonique."""

    dimension: str
    value: str
    display_value: str | None = None
    request_count: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_count: int
    error_rate: float
    repair_count: int
    repair_rate: float
    fallback_count: int
    fallback_rate: float


class LlmOpsAlert(BaseModel):
    """Alerte d'exploitation LLM structurée."""

    code: str
    severity: str
    status: str
    message: str
    labels: dict[str, str]
    annotations: dict[str, str]
    timestamp: datetime


class LlmOpsMonitoringData(BaseModel):
    """Données d'exploitation LLM agrégées."""

    window: str
    dashboards: dict[str, list[LlmOpsDashboardMetrics]]
    alerts: list[LlmOpsAlert]


class _DimensionSpec(BaseModel):
    key: str
    column_name: str | None = None
    is_persona: bool = False


class LlmOpsMonitoringService:
    """
    Service d'exploitation LLM.

    Source de vérité: ``llm_call_logs`` en base persistante.
    """

    DIMENSION_SETS: dict[str, list[_DimensionSpec]] = {
        "family": [_DimensionSpec(key="feature", column_name="feature")],
        "plan": [_DimensionSpec(key="plan", column_name="plan")],
        "persona": [_DimensionSpec(key="persona", is_persona=True)],
        "pipeline_kind": [_DimensionSpec(key="pipeline_kind", column_name="pipeline_kind")],
        "release": [
            _DimensionSpec(key="active_snapshot_version", column_name="active_snapshot_version")
        ],
        "snapshot_id": [_DimensionSpec(key="active_snapshot_id", column_name="active_snapshot_id")],
        "manifest": [_DimensionSpec(key="manifest_entry_id", column_name="manifest_entry_id")],
        "family_execution_path": [
            _DimensionSpec(key="feature", column_name="feature"),
            _DimensionSpec(key="execution_path_kind", column_name="execution_path_kind"),
        ],
        "family_fallback": [
            _DimensionSpec(key="feature", column_name="feature"),
            _DimensionSpec(key="fallback_kind", column_name="fallback_kind"),
        ],
        "family_provider_triplet": [
            _DimensionSpec(key="feature", column_name="feature"),
            _DimensionSpec(key="requested_provider", column_name="requested_provider"),
            _DimensionSpec(key="resolved_provider", column_name="resolved_provider"),
            _DimensionSpec(key="executed_provider", column_name="executed_provider"),
        ],
        "family_context_quality": [
            _DimensionSpec(key="feature", column_name="feature"),
            _DimensionSpec(key="context_quality", column_name="context_quality"),
        ],
        "family_max_tokens_source": [
            _DimensionSpec(key="feature", column_name="feature"),
            _DimensionSpec(key="max_output_tokens_source", column_name="max_output_tokens_source"),
        ],
    }
    METADATA_DIMENSION_KEYS: frozenset[str] = frozenset(
        {
            "pipeline_kind",
            "active_snapshot_version",
            "active_snapshot_id",
            "manifest_entry_id",
            "execution_path_kind",
            "fallback_kind",
            "requested_provider",
            "resolved_provider",
            "executed_provider",
            "context_quality",
            "max_output_tokens_source",
        }
    )

    @staticmethod
    def get_llm_ops_data(db: Session, window: str = "24h") -> LlmOpsMonitoringData:
        """Récupère les dashboards et alertes LLM pour la fenêtre donnée."""
        selected_window = window.strip().lower()
        if selected_window not in WINDOWS:
            selected_window = "24h"

        duration = WINDOWS[selected_window]
        now = datetime_provider.utcnow()
        since = now - duration

        dashboards = {
            name: LlmOpsMonitoringService._get_aggregate(db, specs, since)
            for name, specs in LlmOpsMonitoringService.DIMENSION_SETS.items()
        }
        alerts = LlmOpsMonitoringService._generate_alerts(
            db=db,
            window=selected_window,
            since=since,
            duration=duration,
        )

        return LlmOpsMonitoringData(window=selected_window, dashboards=dashboards, alerts=alerts)

    @staticmethod
    def _dimension_column(spec: _DimensionSpec) -> Any:
        if spec.is_persona:
            return LlmCallLogModel.persona_id
        if spec.column_name is None:
            raise ValueError(f"Unsupported dimension without column: {spec.key}")
        if spec.key in LlmOpsMonitoringService.METADATA_DIMENSION_KEYS:
            return getattr(LlmCallLogOperationalMetadataModel, spec.column_name)
        return getattr(LlmCallLogModel, spec.column_name)

    @staticmethod
    def _get_aggregate(
        db: Session,
        dimensions: list[_DimensionSpec],
        since: datetime,
    ) -> list[LlmOpsDashboardMetrics]:
        """Agrège les logs par une ou plusieurs dimensions canoniques."""
        select_cols: list[Any] = []
        group_cols: list[Any] = []

        for index, spec in enumerate(dimensions):
            column = LlmOpsMonitoringService._dimension_column(spec)
            select_cols.append(column.label(f"dim_{index}"))
            group_cols.append(column)

        stmt = (
            select(
                *select_cols,
                func.max(LlmPersonaModel.name).label("persona_display"),
                func.count(LlmCallLogModel.id).label("count"),
                func.avg(LlmCallLogModel.latency_ms).label("avg_lat"),
                func.sum(
                    case(
                        (LlmCallLogModel.validation_status == LlmValidationStatus.ERROR, 1),
                        else_=0,
                    )
                ).label("error_count"),
                func.sum(case((LlmCallLogModel.repair_attempted.is_(True), 1), else_=0)).label(
                    "repair_count"
                ),
                func.sum(case((LlmCallLogModel.fallback_triggered.is_(True), 1), else_=0)).label(
                    "fallback_count"
                ),
            )
            .outerjoin(LlmPersonaModel, LlmCallLogModel.persona_id == LlmPersonaModel.id)
            .outerjoin(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(LlmCallLogModel.timestamp >= since)
            .group_by(*group_cols)
        )

        metrics: list[LlmOpsDashboardMetrics] = []
        dimension_label = " x ".join(spec.key for spec in dimensions)

        for row in db.execute(stmt).all():
            row_mapping = row._mapping
            raw_values = [row_mapping[f"dim_{index}"] for index in range(len(dimensions))]
            canonical_values = [
                LlmOpsMonitoringService._serialize_dimension_value(spec, raw_value)
                for spec, raw_value in zip(dimensions, raw_values, strict=True)
            ]
            display_value = None
            if len(dimensions) == 1 and dimensions[0].is_persona:
                display_value = row_mapping["persona_display"] or None

            count = int(row_mapping["count"] or 0)
            if count == 0:
                continue

            latencies = LlmOpsMonitoringService._get_latencies_for_group(
                db=db,
                dimensions=dimensions,
                raw_values=raw_values,
                since=since,
            )
            error_count = int(row_mapping["error_count"] or 0)
            repair_count = int(row_mapping["repair_count"] or 0)
            fallback_count = int(row_mapping["fallback_count"] or 0)

            metrics.append(
                LlmOpsDashboardMetrics(
                    dimension=dimension_label,
                    value=":".join(canonical_values),
                    display_value=display_value,
                    request_count=count,
                    avg_latency_ms=float(row_mapping["avg_lat"] or 0.0),
                    p50_latency_ms=LlmOpsMonitoringService._calculate_percentile(latencies, 0.50),
                    p95_latency_ms=LlmOpsMonitoringService._calculate_percentile(latencies, 0.95),
                    p99_latency_ms=LlmOpsMonitoringService._calculate_percentile(latencies, 0.99),
                    error_count=error_count,
                    error_rate=(error_count / count) if count else 0.0,
                    repair_count=repair_count,
                    repair_rate=(repair_count / count) if count else 0.0,
                    fallback_count=fallback_count,
                    fallback_rate=(fallback_count / count) if count else 0.0,
                )
            )

        return metrics

    @staticmethod
    def _serialize_dimension_value(spec: _DimensionSpec, raw_value: Any) -> str:
        if spec.is_persona:
            return canonical_persona_label(raw_value)
        if raw_value is None:
            return "unknown"
        return str(raw_value)

    @staticmethod
    def _get_latencies_for_group(
        *,
        db: Session,
        dimensions: list[_DimensionSpec],
        raw_values: list[Any],
        since: datetime,
    ) -> list[float]:
        filters = [LlmCallLogModel.timestamp >= since]
        for spec, raw_value in zip(dimensions, raw_values, strict=True):
            column = LlmOpsMonitoringService._dimension_column(spec)
            if raw_value is None:
                filters.append(column.is_(None))
            else:
                filters.append(column == raw_value)

        stmt = (
            select(LlmCallLogModel.latency_ms)
            .outerjoin(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(and_(*filters))
            .order_by(LlmCallLogModel.latency_ms)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def _calculate_percentile(latencies: list[float], percentile: float) -> float:
        if not latencies:
            return 0.0
        index = int(len(latencies) * percentile)
        if index >= len(latencies):
            index = len(latencies) - 1
        return float(latencies[index])

    @staticmethod
    def _provider_diff(left: Any, right: Any) -> Any:
        return or_(
            left != right,
            and_(left.is_(None), right.is_not(None)),
            and_(left.is_not(None), right.is_(None)),
        )

    @staticmethod
    def _generate_alerts(
        *,
        db: Session,
        window: str,
        since: datetime,
        duration: timedelta,
    ) -> list[LlmOpsAlert]:
        """Génère les alertes structurées pour la fenêtre d'observation."""
        alerts: list[LlmOpsAlert] = []
        alerts.extend(
            LlmOpsMonitoringService._build_repair_hike_alerts(
                db=db,
                since=since,
                duration=duration,
            )
        )
        alerts.extend(LlmOpsMonitoringService._build_nominal_fallback_alerts(db=db, since=since))
        alerts.extend(LlmOpsMonitoringService._build_provider_divergence_alerts(db=db, since=since))
        alerts.extend(LlmOpsMonitoringService._build_impossible_state_alerts(db=db, since=since))
        alerts.extend(LlmOpsMonitoringService._build_unknown_path_alerts(db=db, since=since))
        return alerts

    @staticmethod
    def _build_repair_hike_alerts(
        *,
        db: Session,
        since: datetime,
        duration: timedelta,
    ) -> list[LlmOpsAlert]:
        # Use the exact previous window with same duration anchored on `since`
        # to avoid drift from additional `now()` calls around boundary timestamps.
        baseline_since = since - duration
        # Small guard band to absorb sub-second clock skew between data seeding
        # and request-time window evaluation in integration/runtime contexts.
        baseline_lower_bound = baseline_since - timedelta(seconds=5)

        stmt = (
            select(
                LlmCallLogModel.feature.label("feature"),
                LlmCallLogModel.plan.label("plan"),
                LlmCallLogModel.persona_id.label("persona_id"),
                LlmCallLogOperationalMetadataModel.pipeline_kind.label("pipeline_kind"),
                func.count(LlmCallLogModel.id).label("total"),
                func.sum(case((LlmCallLogModel.repair_attempted.is_(True), 1), else_=0)).label(
                    "repairs"
                ),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(LlmCallLogModel.timestamp >= since)
            .group_by(
                LlmCallLogModel.feature,
                LlmCallLogModel.plan,
                LlmCallLogModel.persona_id,
                LlmCallLogOperationalMetadataModel.pipeline_kind,
            )
        )
        baseline_stmt = (
            select(
                LlmCallLogModel.feature.label("feature"),
                LlmCallLogModel.plan.label("plan"),
                LlmCallLogModel.persona_id.label("persona_id"),
                LlmCallLogOperationalMetadataModel.pipeline_kind.label("pipeline_kind"),
                func.count(LlmCallLogModel.id).label("total"),
                func.sum(case((LlmCallLogModel.repair_attempted.is_(True), 1), else_=0)).label(
                    "repairs"
                ),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(
                and_(
                    LlmCallLogModel.timestamp >= baseline_lower_bound,
                    LlmCallLogModel.timestamp < since,
                )
            )
            .group_by(
                LlmCallLogModel.feature,
                LlmCallLogModel.plan,
                LlmCallLogModel.persona_id,
                LlmCallLogOperationalMetadataModel.pipeline_kind,
            )
        )

        baseline_rates: dict[tuple[Any, Any, Any, Any], float] = {}
        for row in db.execute(baseline_stmt).all():
            total = int(row.total or 0)
            repairs = int(row.repairs or 0)
            if total == 0:
                continue
            baseline_rates[(row.feature, row.plan, row.persona_id, row.pipeline_kind)] = (
                repairs / total
            )

        alerts: list[LlmOpsAlert] = []
        for row in db.execute(stmt).all():
            total = int(row.total or 0)
            repairs = int(row.repairs or 0)
            if total < REPAIR_MIN_OCCURRENCES or total == 0:
                continue

            current_rate = repairs / total
            if current_rate <= REPAIR_RATE_THRESHOLD:
                continue

            key = (row.feature, row.plan, row.persona_id, row.pipeline_kind)
            baseline_rate = baseline_rates.get(key, 0.0)
            if baseline_rate > 0:
                baseline_ratio = current_rate / baseline_rate
            else:
                baseline_ratio = float("inf")

            if baseline_rate > 0 and baseline_ratio < REPAIR_RATE_BASELINE_MULTIPLIER:
                continue
            if (current_rate - baseline_rate) < REPAIR_RATE_MIN_DELTA:
                continue

            persona_label = canonical_persona_label(row.persona_id)
            alerts.append(
                LlmOpsAlert(
                    code="llm_repair_rate_hike",
                    severity="high",
                    status="firing",
                    message=(
                        f"Repair hike detected for {row.feature}/{row.plan}/{persona_label}: "
                        f"{current_rate:.1%} (baseline: {baseline_rate:.1%})"
                    ),
                    labels={
                        "family": str(row.feature or "unknown"),
                        "plan": str(row.plan or "unknown"),
                        "persona": persona_label,
                        "pipeline": str(row.pipeline_kind or "unknown"),
                        "window": "current_vs_previous_window",
                    },
                    annotations={
                        "summary": "Hausse des réparations LLM",
                        "description": (
                            "Le taux de réparation dépasse le seuil et diverge de la fenêtre "
                            "précédente sur le même chemin canonique."
                        ),
                        "runbook_url": "https://ops.example.com/runbooks/llm-repair-rate",
                    },
                    timestamp=datetime_provider.utcnow(),
                )
            )

        return alerts

    @staticmethod
    def _build_nominal_fallback_alerts(*, db: Session, since: datetime) -> list[LlmOpsAlert]:
        stmt = (
            select(
                LlmCallLogModel.feature,
                LlmCallLogOperationalMetadataModel.fallback_kind,
                func.count(LlmCallLogModel.id).label("count"),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(
                and_(
                    LlmCallLogModel.timestamp >= since,
                    LlmCallLogModel.feature.in_(NOMINAL_FAMILIES),
                    LlmCallLogModel.fallback_triggered.is_(True),
                )
            )
            .group_by(
                LlmCallLogModel.feature,
                LlmCallLogOperationalMetadataModel.fallback_kind,
            )
        )

        return [
            LlmOpsAlert(
                code="llm_nominal_fallback_detected",
                severity="high",
                status="firing",
                message=f"Fallback on nominal {row.feature} (kind: {row.fallback_kind})",
                labels={
                    "family": str(row.feature or "unknown"),
                    "fallback_kind": str(row.fallback_kind or "unknown"),
                },
                annotations={
                    "summary": "Fallback sur périmètre nominal",
                    "description": f"Mécanisme de compatibilité activé sur {row.feature}.",
                    "runbook_url": "https://ops.example.com/runbooks/llm-nominal-fallback",
                },
                timestamp=datetime_provider.utcnow(),
            )
            for row in db.execute(stmt).all()
        ]

    @staticmethod
    def _build_provider_divergence_alerts(*, db: Session, since: datetime) -> list[LlmOpsAlert]:
        stmt = (
            select(
                LlmCallLogModel.feature,
                LlmCallLogOperationalMetadataModel.requested_provider,
                LlmCallLogOperationalMetadataModel.resolved_provider,
                LlmCallLogOperationalMetadataModel.executed_provider,
                func.count(LlmCallLogModel.id).label("count"),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(
                and_(
                    LlmCallLogModel.timestamp >= since,
                    or_(
                        LlmOpsMonitoringService._provider_diff(
                            LlmCallLogOperationalMetadataModel.requested_provider,
                            LlmCallLogOperationalMetadataModel.resolved_provider,
                        ),
                        LlmOpsMonitoringService._provider_diff(
                            LlmCallLogOperationalMetadataModel.resolved_provider,
                            LlmCallLogOperationalMetadataModel.executed_provider,
                        ),
                        LlmOpsMonitoringService._provider_diff(
                            LlmCallLogOperationalMetadataModel.requested_provider,
                            LlmCallLogOperationalMetadataModel.executed_provider,
                        ),
                    ),
                )
            )
            .group_by(
                LlmCallLogModel.feature,
                LlmCallLogOperationalMetadataModel.requested_provider,
                LlmCallLogOperationalMetadataModel.resolved_provider,
                LlmCallLogOperationalMetadataModel.executed_provider,
            )
        )

        alerts: list[LlmOpsAlert] = []
        for row in db.execute(stmt).all():
            divergence_types: list[str] = []
            if row.requested_provider != row.resolved_provider:
                divergence_types.append("requested_vs_resolved")
            if row.resolved_provider != row.executed_provider:
                divergence_types.append("resolved_vs_executed")
            if row.requested_provider != row.executed_provider:
                divergence_types.append("requested_vs_executed")

            alerts.append(
                LlmOpsAlert(
                    code="llm_provider_divergence",
                    severity="high",
                    status="firing",
                    message=(
                        f"Provider divergence on {row.feature}: "
                        f"{row.requested_provider}->{row.resolved_provider}->{row.executed_provider}"
                    ),
                    labels={
                        "family": str(row.feature or "unknown"),
                        "requested": str(row.requested_provider or "unknown"),
                        "resolved": str(row.resolved_provider or "unknown"),
                        "executed": str(row.executed_provider or "unknown"),
                        "divergence_types": ",".join(divergence_types),
                    },
                    annotations={
                        "summary": "Divergence de provider LLM",
                        "description": (
                            "Le triplet provider demandé/résolu/exécuté diverge sur la fenêtre "
                            "courante."
                        ),
                        "runbook_url": "https://ops.example.com/runbooks/llm-provider-divergence",
                    },
                    timestamp=datetime_provider.utcnow(),
                )
            )
        return alerts

    @staticmethod
    def _build_impossible_state_alerts(*, db: Session, since: datetime) -> list[LlmOpsAlert]:
        stmt = (
            select(
                LlmCallLogOperationalMetadataModel.pipeline_kind,
                LlmCallLogOperationalMetadataModel.execution_path_kind,
                LlmCallLogOperationalMetadataModel.fallback_kind,
                LlmCallLogOperationalMetadataModel.requested_provider,
                LlmCallLogOperationalMetadataModel.executed_provider,
                func.count(LlmCallLogModel.id).label("count"),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(LlmCallLogModel.timestamp >= since)
            .group_by(
                LlmCallLogOperationalMetadataModel.pipeline_kind,
                LlmCallLogOperationalMetadataModel.execution_path_kind,
                LlmCallLogOperationalMetadataModel.fallback_kind,
                LlmCallLogOperationalMetadataModel.requested_provider,
                LlmCallLogOperationalMetadataModel.executed_provider,
            )
        )

        alerts: list[LlmOpsAlert] = []
        for row in db.execute(stmt).all():
            if not is_impossible_state(
                row.pipeline_kind,
                row.execution_path_kind,
                row.fallback_kind,
                requested_provider=row.requested_provider,
                executed_provider=row.executed_provider,
            ):
                continue
            alerts.append(
                LlmOpsAlert(
                    code="llm_impossible_state_detected",
                    severity="critical",
                    status="firing",
                    message=f"Impossible state: {row.pipeline_kind}/{row.execution_path_kind}",
                    labels={
                        "pipeline": str(row.pipeline_kind or "unknown"),
                        "path": str(row.execution_path_kind or "unknown"),
                        "fallback": str(row.fallback_kind or "none"),
                    },
                    annotations={
                        "summary": "État LLM impossible détecté",
                        "description": "Combinaison interdite de pipeline et chemin observée.",
                        "runbook_url": "https://ops.example.com/runbooks/llm-impossible-state",
                    },
                    timestamp=datetime_provider.utcnow(),
                )
            )
        return alerts

    @staticmethod
    def _build_unknown_path_alerts(*, db: Session, since: datetime) -> list[LlmOpsAlert]:
        stmt = (
            select(
                LlmCallLogOperationalMetadataModel.pipeline_kind,
                LlmCallLogOperationalMetadataModel.execution_path_kind,
                func.count(LlmCallLogModel.id).label("count"),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(
                and_(
                    LlmCallLogModel.timestamp >= since,
                    LlmCallLogOperationalMetadataModel.execution_path_kind == "unknown",
                )
            )
            .group_by(
                LlmCallLogOperationalMetadataModel.pipeline_kind,
                LlmCallLogOperationalMetadataModel.execution_path_kind,
            )
        )

        alerts: list[LlmOpsAlert] = []
        for row in db.execute(stmt).all():
            if is_unknown_allowed(str(row.pipeline_kind), str(row.execution_path_kind)):
                continue
            alerts.append(
                LlmOpsAlert(
                    code="llm_unknown_path_violation",
                    severity="high",
                    status="firing",
                    message=f"Unauthorized unknown path on {row.pipeline_kind}",
                    labels={
                        "pipeline": str(row.pipeline_kind or "unknown"),
                        "path": "unknown",
                    },
                    annotations={
                        "summary": "Violation de contrat 'unknown' LLM",
                        "description": "État 'unknown' non autorisé sur un chemin protégé.",
                        "runbook_url": "https://ops.example.com/runbooks/llm-unknown-violation",
                    },
                    timestamp=datetime_provider.utcnow(),
                )
            )
        return alerts
