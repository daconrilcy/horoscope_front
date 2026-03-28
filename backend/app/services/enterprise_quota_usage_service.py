from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.services.entitlement_types import QuotaDefinition, UsageState
from app.services.feature_scope_registry import (
    FeatureScope,
    InvalidQuotaScopeError,
    get_feature_scope,
)
from app.services.quota_usage_service import QuotaExhaustedError
from app.services.quota_window_resolver import QuotaWindow, QuotaWindowResolver


class EnterpriseQuotaUsageService:
    @staticmethod
    def get_usage(
        db: Session,
        *,
        account_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        ref_dt: datetime | None = None,
    ) -> UsageState:
        scope = get_feature_scope(feature_code)
        if scope == FeatureScope.B2C:
            raise InvalidQuotaScopeError(
                feature_code=feature_code,
                actual_scope=FeatureScope.B2C,
                expected_scope=FeatureScope.B2B,
                correct_service="QuotaUsageService",
                wrong_service="EnterpriseQuotaUsageService",
            )

        if ref_dt is None:
            ref_dt = datetime.now(timezone.utc)

        window = QuotaWindowResolver.compute_window(
            quota.period_unit, quota.period_value, quota.reset_mode, ref_dt
        )

        counter = db.scalar(
            select(EnterpriseFeatureUsageCounterModel)
            .where(
                EnterpriseFeatureUsageCounterModel.enterprise_account_id == account_id,
                EnterpriseFeatureUsageCounterModel.feature_code == feature_code,
                EnterpriseFeatureUsageCounterModel.quota_key == quota.quota_key,
                EnterpriseFeatureUsageCounterModel.period_unit == quota.period_unit,
                EnterpriseFeatureUsageCounterModel.period_value == quota.period_value,
                EnterpriseFeatureUsageCounterModel.reset_mode == quota.reset_mode,
                EnterpriseFeatureUsageCounterModel.window_start == window.window_start,
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
        account_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        amount: int = 1,
        ref_dt: datetime | None = None,
    ) -> UsageState:
        scope = get_feature_scope(feature_code)
        if scope == FeatureScope.B2C:
            raise InvalidQuotaScopeError(
                feature_code=feature_code,
                actual_scope=FeatureScope.B2C,
                expected_scope=FeatureScope.B2B,
                correct_service="QuotaUsageService",
                wrong_service="EnterpriseQuotaUsageService",
            )

        if amount <= 0:
            raise ValueError("amount must be >= 1")

        if ref_dt is None:
            ref_dt = datetime.now(timezone.utc)

        window = QuotaWindowResolver.compute_window(
            quota.period_unit, quota.period_value, quota.reset_mode, ref_dt
        )

        counter = EnterpriseQuotaUsageService._find_or_create_counter(
            db, account_id=account_id, feature_code=feature_code, quota=quota, window=window
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
    def _find_or_create_counter(
        db: Session,
        *,
        account_id: int,
        feature_code: str,
        quota: QuotaDefinition,
        window: QuotaWindow,
    ) -> EnterpriseFeatureUsageCounterModel:
        query = (
            select(EnterpriseFeatureUsageCounterModel)
            .where(
                EnterpriseFeatureUsageCounterModel.enterprise_account_id == account_id,
                EnterpriseFeatureUsageCounterModel.feature_code == feature_code,
                EnterpriseFeatureUsageCounterModel.quota_key == quota.quota_key,
                EnterpriseFeatureUsageCounterModel.period_unit == quota.period_unit,
                EnterpriseFeatureUsageCounterModel.period_value == quota.period_value,
                EnterpriseFeatureUsageCounterModel.reset_mode == quota.reset_mode,
                EnterpriseFeatureUsageCounterModel.window_start == window.window_start,
            )
            .with_for_update()
            .limit(1)
        )
        counter = db.scalar(query)
        if counter is not None:
            return counter

        counter = EnterpriseFeatureUsageCounterModel(
            enterprise_account_id=account_id,
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
