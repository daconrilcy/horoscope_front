from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.domain.llm.governance.feature_taxonomy import (
    SUPPORTED_FAMILIES,
    is_natal_subfeature_canonical,
    normalize_feature,
    normalize_subfeature,
)
from app.domain.llm.governance.prompt_governance_registry import (
    NATAL_CANONICAL_FEATURE,
    get_prompt_governance_registry,
)
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_canonical_consumption import (
    LlmCanonicalConsumptionAggregateModel,
)
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
    LlmCallLogOperationalMetadataModel,
    LlmValidationStatus,
)
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel

LEGACY_FEATURE_TO_CANONICAL: dict[str, str] = (
    get_prompt_governance_registry().legacy_nominal_feature_aliases_map()
)

Granularity = Literal["day", "month"]
Scope = Literal["nominal", "all"]


class CanonicalConsumptionFilters(BaseModel):
    granularity: Granularity = "day"
    scope: Scope = "nominal"
    from_utc: datetime | None = None
    to_utc: datetime | None = None
    user_id: int | None = None
    feature: str | None = None
    subfeature: str | None = None
    subscription_plan: str | None = None
    locale: str | None = None
    executed_provider: str | None = None
    active_snapshot_version: str | None = None


class CanonicalConsumptionAggregate(BaseModel):
    period_start_utc: datetime
    user_id: int | None
    subscription_plan: str
    feature: str
    subfeature: str | None
    locale: str
    executed_provider: str
    active_snapshot_version: str
    is_legacy_residual: bool
    tokens_in: int
    tokens_out: int
    total_tokens: int
    cost_usd_estimated: float
    call_count: int
    latency_p50: float
    latency_p95: float
    error_rate: float


@dataclass(frozen=True)
class _NormalizedCall:
    call_id: object
    timestamp: datetime
    user_id: int | None
    subscription_plan: str
    feature: str
    subfeature: str | None
    locale: str
    executed_provider: str
    active_snapshot_version: str
    is_legacy_residual: bool
    tokens_in: int
    tokens_out: int
    cost_usd_estimated: float
    latency_ms: int
    is_error: bool


class LlmCanonicalConsumptionService:
    @staticmethod
    def refresh_read_model(
        db: Session,
        *,
        from_utc: datetime | None = None,
        to_utc: datetime | None = None,
    ) -> None:
        if db.bind is not None:
            Base.metadata.create_all(
                bind=db.bind, tables=[LlmCanonicalConsumptionAggregateModel.__table__]
            )

        expanded_from, expanded_to = LlmCanonicalConsumptionService._expanded_refresh_bounds(
            from_utc=from_utc,
            to_utc=to_utc,
        )
        normalized_rows = LlmCanonicalConsumptionService._normalized_calls(
            db=db,
            filters=CanonicalConsumptionFilters(
                scope="all",
                from_utc=expanded_from,
                to_utc=expanded_to,
            ),
        )
        grouped: dict[
            tuple[str, datetime, int | None, str, str, str | None, str, str, str, bool],
            list[_NormalizedCall],
        ] = {}
        for row in normalized_rows:
            for granularity in ("day", "month"):
                period_start = LlmCanonicalConsumptionService._period_start_utc(
                    timestamp=row.timestamp,
                    granularity=granularity,  # type: ignore[arg-type]
                )
                key = (
                    granularity,
                    period_start,
                    row.user_id,
                    row.subscription_plan,
                    row.feature,
                    row.subfeature,
                    row.locale,
                    row.executed_provider,
                    row.active_snapshot_version,
                    row.is_legacy_residual,
                )
                grouped.setdefault(key, []).append(row)

        LlmCanonicalConsumptionService._delete_refresh_scope(
            db=db,
            from_utc=from_utc,
            to_utc=to_utc,
        )
        for key, entries in grouped.items():
            latencies = sorted(float(entry.latency_ms) for entry in entries)
            tokens_in = sum(entry.tokens_in for entry in entries)
            tokens_out = sum(entry.tokens_out for entry in entries)
            call_count = len(entries)
            error_count = sum(1 for entry in entries if entry.is_error)
            (
                granularity,
                period_start,
                user_id,
                subscription_plan,
                feature,
                subfeature,
                locale,
                executed_provider,
                active_snapshot_version,
                is_legacy_residual,
            ) = key
            db.add(
                LlmCanonicalConsumptionAggregateModel(
                    granularity=granularity,
                    period_start_utc=period_start,
                    user_id=user_id,
                    subscription_plan=subscription_plan,
                    feature=feature,
                    subfeature=subfeature,
                    locale=locale,
                    executed_provider=executed_provider,
                    active_snapshot_version=active_snapshot_version,
                    is_legacy_residual=is_legacy_residual,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    total_tokens=tokens_in + tokens_out,
                    cost_usd_estimated_microusd=int(
                        round(sum(entry.cost_usd_estimated for entry in entries) * 1_000_000)
                    ),
                    call_count=call_count,
                    latency_p50_ms=int(
                        round(LlmCanonicalConsumptionService._percentile(latencies, 0.50))
                    ),
                    latency_p95_ms=int(
                        round(LlmCanonicalConsumptionService._percentile(latencies, 0.95))
                    ),
                    error_rate_bps=int(
                        round(((error_count / call_count) if call_count else 0.0) * 10_000)
                    ),
                    refreshed_at=datetime_provider.utcnow(),
                )
            )
        db.commit()

    @staticmethod
    def get_aggregates(
        db: Session,
        *,
        filters: CanonicalConsumptionFilters,
        refresh: bool = False,
    ) -> list[CanonicalConsumptionAggregate]:
        if refresh:
            LlmCanonicalConsumptionService.refresh_read_model(
                db=db,
                from_utc=filters.from_utc,
                to_utc=filters.to_utc,
            )

        stmt = select(LlmCanonicalConsumptionAggregateModel).where(
            LlmCanonicalConsumptionAggregateModel.granularity == filters.granularity
        )
        bucket_from, bucket_to = LlmCanonicalConsumptionService._bucket_query_bounds(
            granularity=filters.granularity,
            from_utc=filters.from_utc,
            to_utc=filters.to_utc,
        )
        if bucket_from:
            stmt = stmt.where(LlmCanonicalConsumptionAggregateModel.period_start_utc >= bucket_from)
        if bucket_to:
            stmt = stmt.where(LlmCanonicalConsumptionAggregateModel.period_start_utc < bucket_to)
        if filters.scope == "nominal":
            stmt = stmt.where(LlmCanonicalConsumptionAggregateModel.is_legacy_residual.is_(False))
        if filters.user_id is not None:
            stmt = stmt.where(LlmCanonicalConsumptionAggregateModel.user_id == filters.user_id)
        if filters.feature is not None:
            stmt = stmt.where(LlmCanonicalConsumptionAggregateModel.feature == filters.feature)
        if filters.subfeature is not None:
            stmt = stmt.where(
                LlmCanonicalConsumptionAggregateModel.subfeature == filters.subfeature
            )
        if filters.subscription_plan is not None:
            stmt = stmt.where(
                LlmCanonicalConsumptionAggregateModel.subscription_plan == filters.subscription_plan
            )
        if filters.locale is not None:
            stmt = stmt.where(LlmCanonicalConsumptionAggregateModel.locale == filters.locale)
        if filters.executed_provider is not None:
            stmt = stmt.where(
                LlmCanonicalConsumptionAggregateModel.executed_provider == filters.executed_provider
            )
        if filters.active_snapshot_version is not None:
            stmt = stmt.where(
                LlmCanonicalConsumptionAggregateModel.active_snapshot_version
                == filters.active_snapshot_version
            )

        rows = db.execute(
            stmt.order_by(
                LlmCanonicalConsumptionAggregateModel.period_start_utc.asc(),
                LlmCanonicalConsumptionAggregateModel.feature.asc(),
            )
        ).scalars()
        return [
            CanonicalConsumptionAggregate(
                period_start_utc=LlmCanonicalConsumptionService._to_utc(row.period_start_utc),
                user_id=row.user_id,
                subscription_plan=row.subscription_plan,
                feature=row.feature,
                subfeature=row.subfeature,
                locale=row.locale,
                executed_provider=row.executed_provider,
                active_snapshot_version=row.active_snapshot_version,
                is_legacy_residual=row.is_legacy_residual,
                tokens_in=row.tokens_in,
                tokens_out=row.tokens_out,
                total_tokens=row.total_tokens,
                cost_usd_estimated=float(row.cost_usd_estimated_microusd) / 1_000_000,
                call_count=row.call_count,
                latency_p50=float(row.latency_p50_ms),
                latency_p95=float(row.latency_p95_ms),
                error_rate=float(row.error_rate_bps) / 10_000,
            )
            for row in rows
        ]

    @staticmethod
    def _normalized_calls(
        *,
        db: Session,
        filters: CanonicalConsumptionFilters,
    ) -> list[_NormalizedCall]:
        stmt = (
            select(
                LlmCallLogModel.id.label("call_id"),
                LlmCallLogModel.timestamp.label("timestamp"),
                func.min(UserTokenUsageLogModel.user_id).label("user_id"),
                func.count(func.distinct(UserTokenUsageLogModel.user_id)).label("user_id_count"),
                LlmCallLogModel.plan.label("subscription_plan"),
                LlmCallLogModel.feature.label("feature"),
                LlmCallLogModel.use_case.label("use_case_compat"),
                LlmCallLogModel.subfeature.label("subfeature"),
                LlmCallLogOperationalMetadataModel.manifest_entry_id.label("manifest_entry_id"),
                LlmCallLogOperationalMetadataModel.executed_provider.label("executed_provider"),
                LlmCallLogOperationalMetadataModel.active_snapshot_version.label(
                    "active_snapshot_version"
                ),
                LlmCallLogModel.tokens_in.label("tokens_in"),
                LlmCallLogModel.tokens_out.label("tokens_out"),
                LlmCallLogModel.cost_usd_estimated.label("cost_usd_estimated"),
                LlmCallLogModel.latency_ms.label("latency_ms"),
                LlmCallLogModel.validation_status.label("validation_status"),
            )
            .select_from(LlmCallLogModel)
            .outerjoin(
                UserTokenUsageLogModel, UserTokenUsageLogModel.llm_call_log_id == LlmCallLogModel.id
            )
            .outerjoin(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .group_by(
                LlmCallLogModel.id,
                LlmCallLogModel.timestamp,
                LlmCallLogModel.plan,
                LlmCallLogModel.feature,
                LlmCallLogModel.use_case,
                LlmCallLogModel.subfeature,
                LlmCallLogOperationalMetadataModel.manifest_entry_id,
                LlmCallLogOperationalMetadataModel.executed_provider,
                LlmCallLogOperationalMetadataModel.active_snapshot_version,
                LlmCallLogModel.tokens_in,
                LlmCallLogModel.tokens_out,
                LlmCallLogModel.cost_usd_estimated,
                LlmCallLogModel.latency_ms,
                LlmCallLogModel.validation_status,
            )
        )
        if filters.from_utc:
            stmt = stmt.where(LlmCallLogModel.timestamp >= filters.from_utc)
        if filters.to_utc:
            stmt = stmt.where(LlmCallLogModel.timestamp < filters.to_utc)

        rows = db.execute(stmt).all()
        normalized: list[_NormalizedCall] = []
        for row in rows:
            manifest_entry_id = str(row.manifest_entry_id or "")
            locale = LlmCanonicalConsumptionService._extract_locale_from_manifest(manifest_entry_id)
            feature, subfeature, is_legacy_residual = (
                LlmCanonicalConsumptionService._normalize_taxonomy(
                    feature=row.feature,
                    subfeature=row.subfeature,
                    use_case_compat=row.use_case_compat,
                )
            )
            if filters.scope == "nominal" and is_legacy_residual:
                continue
            subscription_plan = str(row.subscription_plan or "unknown")
            executed_provider = str(row.executed_provider or "unknown")
            active_snapshot_version = str(row.active_snapshot_version or "unknown")
            resolved_user_id: int | None = row.user_id
            if int(row.user_id_count or 0) > 1:
                # Data-quality guardrail: avoid attributing one call to an arbitrary user.
                # Keeping user_id=None excludes this call from user-scoped breakdowns.
                resolved_user_id = None
            normalized_entry = _NormalizedCall(
                call_id=row.call_id,
                timestamp=LlmCanonicalConsumptionService._to_utc(row.timestamp),
                user_id=resolved_user_id,
                subscription_plan=subscription_plan,
                feature=feature,
                subfeature=subfeature,
                locale=locale,
                executed_provider=executed_provider,
                active_snapshot_version=active_snapshot_version,
                is_legacy_residual=is_legacy_residual,
                tokens_in=int(row.tokens_in or 0),
                tokens_out=int(row.tokens_out or 0),
                cost_usd_estimated=float(row.cost_usd_estimated or 0.0),
                latency_ms=int(row.latency_ms or 0),
                is_error=(row.validation_status == LlmValidationStatus.ERROR),
            )
            if not LlmCanonicalConsumptionService._matches_filters(normalized_entry, filters):
                continue
            normalized.append(normalized_entry)
        return normalized

    @staticmethod
    def _matches_filters(item: _NormalizedCall, filters: CanonicalConsumptionFilters) -> bool:
        if filters.user_id is not None and item.user_id != filters.user_id:
            return False
        if filters.feature is not None and item.feature != filters.feature:
            return False
        if filters.subfeature is not None and item.subfeature != filters.subfeature:
            return False
        if (
            filters.subscription_plan is not None
            and item.subscription_plan != filters.subscription_plan
        ):
            return False
        if filters.locale is not None and item.locale != filters.locale:
            return False
        if (
            filters.executed_provider is not None
            and item.executed_provider != filters.executed_provider
        ):
            return False
        if (
            filters.active_snapshot_version is not None
            and item.active_snapshot_version != filters.active_snapshot_version
        ):
            return False
        return True

    @staticmethod
    def _normalize_taxonomy(
        feature: str | None,
        subfeature: str | None,
        *,
        use_case_compat: str | None = None,
    ) -> tuple[str, str | None, bool]:
        """
        Map legacy / nullable feature columns to canonical nominal taxonomy.

        When `feature` is missing, `use_case_compat` (historical `use_case`) is used so
        older rows that only populated the legacy column still reclassify (Story 66-50).
        """
        raw_source = LlmCanonicalConsumptionService._first_non_empty_str(
            feature,
            use_case_compat,
        )
        if raw_source is None:
            return ("unknown", subfeature, True)
        mapped_feature = LEGACY_FEATURE_TO_CANONICAL.get(raw_source, raw_source)
        normalized_feature = normalize_feature(mapped_feature)
        normalized_subfeature = normalize_subfeature(normalized_feature, subfeature)
        is_legacy_residual = False
        if normalized_feature not in SUPPORTED_FAMILIES:
            is_legacy_residual = True
        raw_sf = str(subfeature).strip() if subfeature is not None else ""
        if raw_sf and normalized_feature == NATAL_CANONICAL_FEATURE:
            if normalized_subfeature is None or not is_natal_subfeature_canonical(
                normalized_subfeature
            ):
                is_legacy_residual = True
        if (
            normalized_subfeature is None
            and subfeature is not None
            and str(subfeature).strip() != ""
        ):
            is_legacy_residual = True
        return (normalized_feature, normalized_subfeature, is_legacy_residual)

    @staticmethod
    def _first_non_empty_str(*candidates: str | None) -> str | None:
        for raw in candidates:
            if raw is None:
                continue
            stripped = str(raw).strip()
            if stripped:
                return stripped
        return None

    @staticmethod
    def _extract_locale_from_manifest(manifest_entry_id: str) -> str:
        parts = manifest_entry_id.split(":")
        if len(parts) == 4 and parts[3].strip():
            return parts[3].strip()
        return "unknown"

    @staticmethod
    def _to_utc(timestamp: datetime) -> datetime:
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            return timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def _period_start_utc(*, timestamp: datetime, granularity: Granularity) -> datetime:
        utc = LlmCanonicalConsumptionService._to_utc(timestamp)
        if granularity == "month":
            return utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return utc.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def _percentile(values: list[float], percentile: float) -> float:
        if not values:
            return 0.0
        index = int((len(values) - 1) * percentile)
        return float(values[index])

    @staticmethod
    def _delete_refresh_scope(
        *,
        db: Session,
        from_utc: datetime | None,
        to_utc: datetime | None,
    ) -> None:
        if from_utc is None and to_utc is None:
            db.query(LlmCanonicalConsumptionAggregateModel).delete()
            return

        for granularity in ("day", "month"):
            stmt = db.query(LlmCanonicalConsumptionAggregateModel).filter(
                LlmCanonicalConsumptionAggregateModel.granularity == granularity
            )
            if from_utc is not None:
                stmt = stmt.filter(
                    LlmCanonicalConsumptionAggregateModel.period_start_utc
                    >= LlmCanonicalConsumptionService._period_start_utc(
                        timestamp=from_utc,
                        granularity=granularity,  # type: ignore[arg-type]
                    )
                )
            if to_utc is not None:
                to_anchor = to_utc - timedelta(microseconds=1)
                stmt = stmt.filter(
                    LlmCanonicalConsumptionAggregateModel.period_start_utc
                    <= LlmCanonicalConsumptionService._period_start_utc(
                        timestamp=to_anchor,
                        granularity=granularity,  # type: ignore[arg-type]
                    )
                )
            stmt.delete()

    @staticmethod
    def _expanded_refresh_bounds(
        *,
        from_utc: datetime | None,
        to_utc: datetime | None,
    ) -> tuple[datetime | None, datetime | None]:
        if from_utc is None and to_utc is None:
            return (None, None)

        expanded_from = from_utc
        expanded_to = to_utc
        if from_utc is not None:
            day_start = LlmCanonicalConsumptionService._period_start_utc(
                timestamp=from_utc,
                granularity="day",
            )
            month_start = LlmCanonicalConsumptionService._period_start_utc(
                timestamp=from_utc,
                granularity="month",
            )
            expanded_from = min(day_start, month_start)
        if to_utc is not None:
            to_anchor = to_utc - timedelta(microseconds=1)
            day_start = LlmCanonicalConsumptionService._period_start_utc(
                timestamp=to_anchor,
                granularity="day",
            )
            month_start = LlmCanonicalConsumptionService._period_start_utc(
                timestamp=to_anchor,
                granularity="month",
            )
            expanded_to = max(
                day_start + timedelta(days=1),
                LlmCanonicalConsumptionService._next_month_start(month_start),
            )
        return (expanded_from, expanded_to)

    @staticmethod
    def _bucket_query_bounds(
        *,
        granularity: Granularity,
        from_utc: datetime | None,
        to_utc: datetime | None,
    ) -> tuple[datetime | None, datetime | None]:
        start = None
        end = None
        if from_utc is not None:
            start = LlmCanonicalConsumptionService._period_start_utc(
                timestamp=from_utc,
                granularity=granularity,
            )
        if to_utc is not None:
            to_anchor = to_utc - timedelta(microseconds=1)
            period_start = LlmCanonicalConsumptionService._period_start_utc(
                timestamp=to_anchor,
                granularity=granularity,
            )
            if granularity == "month":
                end = LlmCanonicalConsumptionService._next_month_start(period_start)
            else:
                end = period_start + timedelta(days=1)
        return (start, end)

    @staticmethod
    def _next_month_start(period_start: datetime) -> datetime:
        if period_start.month == 12:
            return period_start.replace(year=period_start.year + 1, month=1, day=1)
        return period_start.replace(month=period_start.month + 1, day=1)
