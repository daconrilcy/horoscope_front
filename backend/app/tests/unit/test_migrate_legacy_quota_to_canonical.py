from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.billing import UserDailyQuotaUsageModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.services.billing.service import BillingPlanData, SubscriptionStatusData
from scripts.migrate_legacy_quota_to_canonical import migrate


def _subscription(plan_code: str) -> SubscriptionStatusData:
    return SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code=plan_code,
            display_name=plan_code.title(),
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=datetime.now(UTC),
    )


def _patch_script_session(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> None:
    @contextmanager
    def _session_local() -> Session:
        yield db_session

    monkeypatch.setattr(
        "scripts.migrate_legacy_quota_to_canonical.SessionLocal",
        _session_local,
    )


def _seed_chat_feature(db_session: Session) -> FeatureCatalogModel:
    feature = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Astrologer Chat")
    db_session.add(feature)
    db_session.flush()
    return feature


def _seed_plan(
    db_session: Session,
    *,
    plan_code: str,
    access_mode: AccessMode | None,
    period_unit: PeriodUnit | None = None,
    quota_limit: int | None = None,
) -> PlanCatalogModel:
    plan = PlanCatalogModel(
        plan_code=plan_code,
        plan_name=plan_code.title(),
        audience=Audience.B2C,
    )
    db_session.add(plan)
    db_session.flush()

    feature = db_session.scalar(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "astrologer_chat")
    )
    if access_mode is None or feature is None:
        return plan

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feature.id,
        access_mode=access_mode,
        is_enabled=True,
    )
    db_session.add(binding)
    db_session.flush()

    if access_mode == AccessMode.QUOTA:
        assert period_unit is not None
        assert quota_limit is not None
        db_session.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=binding.id,
                quota_key="messages",
                quota_limit=quota_limit,
                period_unit=period_unit,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )

    return plan


def test_migrate_counts_no_binding_as_anomaly(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _patch_script_session(monkeypatch, db_session)
    _seed_chat_feature(db_session)
    _seed_plan(db_session, plan_code="basic", access_mode=None)
    db_session.add(
        UserDailyQuotaUsageModel(
            user_id=42,
            quota_date=date.today(),
            used_count=3,
        )
    )
    db_session.commit()

    monkeypatch.setattr(
        "scripts.migrate_legacy_quota_to_canonical.BillingService.get_subscription_status",
        lambda db, user_id: _subscription("basic"),
    )

    with caplog.at_level("WARNING", logger="scripts.migrate_legacy_quota_to_canonical"):
        stats = migrate(dry_run=True)

    assert stats["anomalies"] == 1
    assert stats["skipped_disabled"] == 0
    assert "no canonical binding" in caplog.text


def test_migrate_skips_disabled_bindings_without_anomaly(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_script_session(monkeypatch, db_session)
    _seed_chat_feature(db_session)
    _seed_plan(db_session, plan_code="free", access_mode=AccessMode.DISABLED)
    db_session.add(
        UserDailyQuotaUsageModel(
            user_id=7,
            quota_date=date.today(),
            used_count=2,
        )
    )
    db_session.commit()

    monkeypatch.setattr(
        "scripts.migrate_legacy_quota_to_canonical.BillingService.get_subscription_status",
        lambda db, user_id: _subscription("free"),
    )

    stats = migrate(dry_run=True)

    assert stats["skipped_disabled"] == 1
    assert stats["anomalies"] == 0


def test_migrate_monthly_uses_current_window_by_default(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_script_session(monkeypatch, db_session)
    _seed_chat_feature(db_session)
    _seed_plan(
        db_session,
        plan_code="premium",
        access_mode=AccessMode.QUOTA,
        period_unit=PeriodUnit.MONTH,
        quota_limit=2000,
    )

    now = datetime.now(UTC)
    current_month_day = max(1, now.day - 1)
    current_row_date = date(now.year, now.month, current_month_day)
    previous_month_date = (datetime(now.year, now.month, 1, tzinfo=UTC) - timedelta(days=1)).date()

    db_session.add_all(
        [
            UserDailyQuotaUsageModel(user_id=99, quota_date=current_row_date, used_count=4),
            UserDailyQuotaUsageModel(user_id=99, quota_date=previous_month_date, used_count=6),
        ]
    )
    db_session.commit()

    monkeypatch.setattr(
        "scripts.migrate_legacy_quota_to_canonical.BillingService.get_subscription_status",
        lambda db, user_id: _subscription("premium"),
    )

    stats = migrate()
    counter = db_session.scalar(
        select(FeatureUsageCounterModel).where(
            FeatureUsageCounterModel.user_id == 99,
            FeatureUsageCounterModel.feature_code == "astrologer_chat",
            FeatureUsageCounterModel.period_unit == PeriodUnit.MONTH,
        )
    )

    assert stats["created_or_updated"] == 1
    assert counter is not None
    assert counter.used_count == 4
