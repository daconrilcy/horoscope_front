"""Logique d'observabilité admin LLM partagée par les routeurs API v1."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.core.datetime_provider import datetime_provider
from app.domain.llm.runtime.observability import purge_expired_logs
from app.infra.db.models.llm.llm_observability import LlmCallLogModel
from app.ops.llm.services import replay
from app.services.api_contracts.admin.llm.error_codes import AdminLlmErrorCode
from app.services.api_contracts.admin.llm.prompts import (
    LlmCallLog,
    LlmDashboardMetrics,
    ReplayPayload,
)
from app.services.llm_generation.admin_manual_execution import _record_audit_event
from app.services.llm_generation.admin_prompts import (
    _call_log_scope_filter,
    _legacy_removed_call_log_filter,
    _raise_error,
)


def list_call_logs(
    request_id: str,
    use_case: Optional[str] = None,
    status: Optional[str] = None,
    prompt_version_id: Optional[uuid.UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: AuthenticatedUser | None = None,
    db: Session | None = None,
) -> Any:
    """Retourne les journaux d'appels LLM filtrés pour l'administration."""
    del current_user
    if db is None:
        raise ValueError("db session is required")

    stmt = select(LlmCallLogModel)
    if use_case:
        stmt = stmt.where(_call_log_scope_filter(use_case))
    if status:
        stmt = stmt.where(LlmCallLogModel.validation_status == status)
    if prompt_version_id:
        stmt = stmt.where(LlmCallLogModel.prompt_version_id == prompt_version_id)
    if from_date:
        stmt = stmt.where(LlmCallLogModel.timestamp >= from_date)
    if to_date:
        stmt = stmt.where(LlmCallLogModel.timestamp <= to_date)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    stmt = (
        stmt.order_by(desc(LlmCallLogModel.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    logs = db.execute(stmt).scalars().all()

    return {
        "data": [LlmCallLog.model_validate(log, from_attributes=True) for log in logs],
        "meta": {
            "request_id": request_id,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


def get_dashboard(
    request_id: str,
    period_hours: int = 24,
    current_user: AuthenticatedUser | None = None,
    db: Session | None = None,
) -> Any:
    """Calcule les métriques d'observabilité LLM pour le tableau de bord admin."""
    del current_user
    if db is None:
        raise ValueError("db session is required")

    since = datetime_provider.utcnow() - timedelta(hours=period_hours)
    feature_stmt = (
        select(LlmCallLogModel.feature)
        .where(and_(LlmCallLogModel.timestamp >= since, LlmCallLogModel.feature.is_not(None)))
        .distinct()
    )
    use_cases = [value for value in db.execute(feature_stmt).scalars().all() if value]
    legacy_removed_count = (
        db.execute(
            select(func.count(LlmCallLogModel.id)).where(
                and_(LlmCallLogModel.timestamp >= since, _legacy_removed_call_log_filter())
            )
        ).scalar()
        or 0
    )
    if legacy_removed_count:
        use_cases.append("legacy_removed")

    metrics_list = []
    for uc in use_cases:
        base_stmt = select(
            func.count(LlmCallLogModel.id).label("count"),
            func.avg(LlmCallLogModel.latency_ms).label("avg_lat"),
            func.sum(LlmCallLogModel.tokens_in + LlmCallLogModel.tokens_out).label("total_tokens"),
            func.sum(LlmCallLogModel.cost_usd_estimated).label("total_cost"),
            func.sum(sa.case((LlmCallLogModel.repair_attempted, 1), else_=0)).label("repair_count"),
            func.sum(sa.case((LlmCallLogModel.fallback_triggered, 1), else_=0)).label(
                "fallback_count"
            ),
            func.sum(sa.case((LlmCallLogModel.evidence_warnings_count > 0, 1), else_=0)).label(
                "warning_count"
            ),
        ).where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))

        stats = db.execute(base_stmt).first()
        count = stats.count or 0
        if count == 0:
            continue

        dist_stmt = (
            select(LlmCallLogModel.validation_status, func.count(LlmCallLogModel.id))
            .where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))
            .group_by(LlmCallLogModel.validation_status)
        )
        dist_res = db.execute(dist_stmt).all()
        distribution = {status: (c / count) * 100 for status, c in dist_res}

        is_sqlite = db.bind.dialect.name == "sqlite"
        if not is_sqlite:
            p95_stmt = select(
                func.percentile_cont(0.95).within_group(LlmCallLogModel.latency_ms)
            ).where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))
            p95 = db.execute(p95_stmt).scalar() or 0
        else:
            latencies_stmt = (
                select(LlmCallLogModel.latency_ms)
                .where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))
                .order_by(LlmCallLogModel.latency_ms)
            )
            latencies = db.execute(latencies_stmt).scalars().all()
            p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0

        metrics_list.append(
            LlmDashboardMetrics(
                use_case=uc,
                request_count=count,
                avg_latency_ms=float(stats.avg_lat or 0),
                p95_latency_ms=float(p95),
                total_tokens=int(stats.total_tokens or 0),
                total_cost_usd=float(stats.total_cost or 0),
                validation_status_distribution=distribution,
                repair_rate=(stats.repair_count / count) * 100 if stats.repair_count else 0,
                fallback_rate=(stats.fallback_count / count) * 100 if stats.fallback_count else 0,
                avg_tokens_per_request=(stats.total_tokens / count) if stats.total_tokens else 0,
                evidence_warning_rate=(stats.warning_count / count) * 100
                if stats.warning_count
                else 0,
            )
        )

    return {"data": metrics_list, "meta": {"request_id": request_id}}


async def replay_request(
    request_id: str,
    payload: ReplayPayload,
    current_user: AuthenticatedUser,
    db: Session,
) -> Any:
    """Relance une requête LLM observée pour diagnostic admin."""
    try:
        result = await replay(
            db=db, request_id=payload.request_id, prompt_version_id=payload.prompt_version_id
        )

        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="llm_call_replayed",
            target_type="llm_call_log",
            target_id=payload.request_id,
            status="success",
            details={"new_prompt_version_id": payload.prompt_version_id},
        )
        db.commit()

        return {"data": result, "meta": {"request_id": request_id}}
    except Exception as exc:
        return _raise_error(
            request_id=request_id,
            code=AdminLlmErrorCode.REPLAY_FAILED.value,
            message=str(exc),
            details={},
        )


async def purge_logs(
    request_id: str,
    current_user: AuthenticatedUser,
    db: Session,
) -> Any:
    """Purge les journaux LLM expirés et trace l'opération admin."""
    deleted_count = await purge_expired_logs(db)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_logs_purge",
        target_type="llm_call_log",
        target_id=None,
        status="success",
        details={"deleted_count": deleted_count},
    )
    db.commit()

    return {"data": {"deleted_count": deleted_count}, "meta": {"request_id": request_id}}
