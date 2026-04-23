from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.services.entitlement_types import QuotaDefinition, UsageState
from app.services.feature_scope_registry import (
    FeatureScope,
    require_feature_scope,
)
from app.services.quota_window_resolver import QuotaWindow, QuotaWindowResolver


class QuotaExhaustedError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, feature_code: str) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.feature_code = feature_code
        super().__init__(
            f"Quota '{quota_key}' exhausted for feature '{feature_code}': {used}/{limit}"
        )


class QuotaUsageService:
    _ANNIVERSARY_ANCHORED_FEATURES = frozenset({"astrologer_chat"})

    @staticmethod
    def _resolve_billing_cycle_anchor(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        ref_dt: datetime,
    ) -> tuple[datetime | None, datetime | None]:
        if (
            feature_code not in QuotaUsageService._ANNIVERSARY_ANCHORED_FEATURES
            or quota.quota_key != "tokens"
            or quota.period_unit not in {"day", "week", "month"}
        ):
            return None, None

        profile = db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.user_id == user_id)
            .limit(1)
        )
        if (
            profile is None
            or profile.current_period_start is None
            or profile.current_period_end is None
        ):
            return None, None

        period_start = profile.current_period_start
        period_end = profile.current_period_end
        if period_start.tzinfo is None:
            period_start = period_start.replace(tzinfo=timezone.utc)
        if period_end.tzinfo is None:
            period_end = period_end.replace(tzinfo=timezone.utc)

        ref_dt_utc = ref_dt.astimezone(timezone.utc)
        if not (period_start <= ref_dt_utc < period_end):
            return None, None

        return period_start, period_end

    @staticmethod
    def get_usage(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        ref_dt: datetime | None = None,
    ) -> UsageState:
        require_feature_scope(feature_code, FeatureScope.B2C)

        if ref_dt is None:
            ref_dt = datetime_provider.utcnow()

        anchor_start, anchor_end = QuotaUsageService._resolve_billing_cycle_anchor(
            db,
            user_id=user_id,
            feature_code=feature_code,
            quota=quota,
            ref_dt=ref_dt,
        )
        window = QuotaWindowResolver.compute_window(
            quota.period_unit,
            quota.period_value,
            quota.reset_mode,
            ref_dt,
            anchor_start=anchor_start,
            anchor_end=anchor_end,
        )

        counter = db.scalar(
            select(FeatureUsageCounterModel)
            .where(
                FeatureUsageCounterModel.user_id == user_id,
                FeatureUsageCounterModel.feature_code == feature_code,
                FeatureUsageCounterModel.quota_key == quota.quota_key,
                FeatureUsageCounterModel.period_unit == quota.period_unit,
                FeatureUsageCounterModel.period_value == quota.period_value,
                FeatureUsageCounterModel.reset_mode == quota.reset_mode,
                FeatureUsageCounterModel.window_start == window.window_start,
            )
            .limit(1)
        )

        used = counter.used_count if counter else 0
        remaining = max(0, quota.quota_limit - used)
        exhausted = used >= quota.quota_limit

        return UsageState(
            feature_code=feature_code,
            quota_key=quota.quota_key,
            quota_limit=quota.quota_limit,
            used=used,
            remaining=remaining,
            exhausted=exhausted,
            period_unit=quota.period_unit,
            period_value=quota.period_value,
            reset_mode=quota.reset_mode,
            window_start=window.window_start,
            window_end=window.window_end,
        )

    @staticmethod
    def consume(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        amount: int = 1,
        ref_dt: datetime | None = None,
    ) -> UsageState:
        require_feature_scope(feature_code, FeatureScope.B2C)

        if amount <= 0:
            raise ValueError("amount must be >= 1")

        if ref_dt is None:
            ref_dt = datetime_provider.utcnow()

        anchor_start, anchor_end = QuotaUsageService._resolve_billing_cycle_anchor(
            db,
            user_id=user_id,
            feature_code=feature_code,
            quota=quota,
            ref_dt=ref_dt,
        )
        window = QuotaWindowResolver.compute_window(
            quota.period_unit,
            quota.period_value,
            quota.reset_mode,
            ref_dt,
            anchor_start=anchor_start,
            anchor_end=anchor_end,
        )

        counter = QuotaUsageService._find_or_create_counter(
            db, user_id=user_id, feature_code=feature_code, quota=quota, window=window
        )

        if counter.used_count + amount > quota.quota_limit:
            raise QuotaExhaustedError(
                quota_key=quota.quota_key,
                used=counter.used_count,
                limit=quota.quota_limit,
                feature_code=feature_code,
            )

        counter.used_count += amount
        db.flush()

        used = counter.used_count
        remaining = max(0, quota.quota_limit - used)
        exhausted = used >= quota.quota_limit

        return UsageState(
            feature_code=feature_code,
            quota_key=quota.quota_key,
            quota_limit=quota.quota_limit,
            used=used,
            remaining=remaining,
            exhausted=exhausted,
            period_unit=quota.period_unit,
            period_value=quota.period_value,
            reset_mode=quota.reset_mode,
            window_start=window.window_start,
            window_end=window.window_end,
        )

    @staticmethod
    def consume_up_to_limit(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        amount: int = 1,
        ref_dt: datetime | None = None,
    ) -> UsageState:
        """
        Consume a quota up to its configured limit without raising on overflow.

        This is useful when usage is measured after an LLM call. The full token usage
        can still be logged while the user-facing quota counter saturates at its limit.
        """
        require_feature_scope(feature_code, FeatureScope.B2C)

        if amount <= 0:
            raise ValueError("amount must be >= 1")

        if ref_dt is None:
            ref_dt = datetime_provider.utcnow()

        anchor_start, anchor_end = QuotaUsageService._resolve_billing_cycle_anchor(
            db,
            user_id=user_id,
            feature_code=feature_code,
            quota=quota,
            ref_dt=ref_dt,
        )
        window = QuotaWindowResolver.compute_window(
            quota.period_unit,
            quota.period_value,
            quota.reset_mode,
            ref_dt,
            anchor_start=anchor_start,
            anchor_end=anchor_end,
        )

        counter = QuotaUsageService._find_or_create_counter(
            db, user_id=user_id, feature_code=feature_code, quota=quota, window=window
        )

        remaining_capacity = max(0, quota.quota_limit - counter.used_count)
        applied_amount = min(amount, remaining_capacity)
        counter.used_count += applied_amount
        db.flush()

        used = counter.used_count
        remaining = max(0, quota.quota_limit - used)
        exhausted = used >= quota.quota_limit

        return UsageState(
            feature_code=feature_code,
            quota_key=quota.quota_key,
            quota_limit=quota.quota_limit,
            used=used,
            remaining=remaining,
            exhausted=exhausted,
            period_unit=quota.period_unit,
            period_value=quota.period_value,
            reset_mode=quota.reset_mode,
            window_start=window.window_start,
            window_end=window.window_end,
        )

    @staticmethod
    def _find_or_create_counter(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        window: QuotaWindow,
    ) -> FeatureUsageCounterModel:
        query = (
            select(FeatureUsageCounterModel)
            .where(
                FeatureUsageCounterModel.user_id == user_id,
                FeatureUsageCounterModel.feature_code == feature_code,
                FeatureUsageCounterModel.quota_key == quota.quota_key,
                FeatureUsageCounterModel.period_unit == quota.period_unit,
                FeatureUsageCounterModel.period_value == quota.period_value,
                FeatureUsageCounterModel.reset_mode == quota.reset_mode,
                FeatureUsageCounterModel.window_start == window.window_start,
            )
            .with_for_update()
            .limit(1)
        )
        counter = db.scalar(query)
        if counter is not None:
            return counter

        counter = FeatureUsageCounterModel(
            user_id=user_id,
            feature_code=feature_code,
            quota_key=quota.quota_key,
            period_unit=quota.period_unit,
            period_value=quota.period_value,
            reset_mode=quota.reset_mode,
            window_start=window.window_start,
            window_end=window.window_end,
            used_count=0,
        )
        try:
            with db.begin_nested():
                db.add(counter)
                db.flush()
        except IntegrityError:
            # Another process created it
            counter = db.scalar(query)
            if counter is None:
                raise
        return counter
