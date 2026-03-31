from contextlib import nullcontext
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.models.user import UserModel
from app.services.entitlement_types import QuotaDefinition
from app.services.feature_scope_registry import (
    InvalidQuotaScopeError,
    UnknownFeatureCodeError,
)
from app.services.quota_usage_service import QuotaExhaustedError, QuotaUsageService
from app.services.quota_window_resolver import QuotaWindow

UTC = timezone.utc


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    # Insérer un user pour satisfaire la FK user_id
    user = UserModel(id=1, email="test@test.com", password_hash="x", role="user")
    session.add(user)
    session.commit()
    yield session
    session.close()


def test_quota_usage_service_rejects_b2b_feature_on_get_usage(db_session):
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    with pytest.raises(InvalidQuotaScopeError) as exc_info:
        QuotaUsageService.get_usage(
            db_session,
            user_id=1,
            feature_code="b2b_api_access",
            quota=quota,
        )
    assert "EnterpriseQuotaUsageService" in str(exc_info.value)
    assert exc_info.value.actual_scope.value == "b2b"
    assert exc_info.value.expected_scope.value == "b2c"


def test_quota_usage_service_rejects_b2b_feature_on_consume(db_session):
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    with pytest.raises(InvalidQuotaScopeError) as exc_info:
        QuotaUsageService.consume(
            db_session,
            user_id=1,
            feature_code="b2b_api_access",
            quota=quota,
        )
    assert "EnterpriseQuotaUsageService" in str(exc_info.value)


def test_quota_usage_service_rejects_b2b_feature_before_db_access():
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    fake_db = Mock()

    with pytest.raises(InvalidQuotaScopeError):
        QuotaUsageService.get_usage(
            fake_db,
            user_id=1,
            feature_code="b2b_api_access",
            quota=quota,
        )

    fake_db.scalar.assert_not_called()
    fake_db.flush.assert_not_called()


def test_quota_usage_service_rejects_unknown_feature_before_db_access():
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    fake_db = Mock()

    with pytest.raises(UnknownFeatureCodeError):
        QuotaUsageService.consume(
            fake_db,
            user_id=1,
            feature_code="unregistered_feature",
            quota=quota,
        )

    fake_db.scalar.assert_not_called()
    fake_db.flush.assert_not_called()


def test_quota_usage_service_rejects_unknown_feature_code(db_session):
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    with pytest.raises(UnknownFeatureCodeError):
        QuotaUsageService.get_usage(
            db_session,
            user_id=1,
            feature_code="unregistered_feature",
            quota=quota,
        )


def test_get_usage_counter_absent(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    usage = QuotaUsageService.get_usage(
        db_session,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota,
        ref_dt=datetime(2026, 3, 15, 10, 0, tzinfo=UTC),
    )
    assert usage.used == 0
    assert usage.remaining == 5
    assert usage.exhausted is False


def test_get_usage_counter_present(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    window_start = datetime(2026, 3, 15, 0, 0, tzinfo=UTC)
    counter = FeatureUsageCounterModel(
        user_id=1,
        feature_code="astrologer_chat",
        quota_key="daily",
        period_unit="day",
        period_value=1,
        reset_mode="calendar",
        window_start=window_start,
        window_end=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
        used_count=3,
    )
    db_session.add(counter)
    db_session.commit()

    usage = QuotaUsageService.get_usage(
        db_session,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota,
        ref_dt=datetime(2026, 3, 15, 10, 0, tzinfo=UTC),
    )
    assert usage.used == 3
    assert usage.remaining == 2
    assert usage.exhausted is False


def test_get_usage_exhausted(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    window_start = datetime(2026, 3, 15, 0, 0, tzinfo=UTC)
    counter = FeatureUsageCounterModel(
        user_id=1,
        feature_code="astrologer_chat",
        quota_key="daily",
        period_unit="day",
        period_value=1,
        reset_mode="calendar",
        window_start=window_start,
        window_end=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
        used_count=5,
    )
    db_session.add(counter)
    db_session.commit()

    usage = QuotaUsageService.get_usage(
        db_session,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota,
        ref_dt=datetime(2026, 3, 15, 10, 0, tzinfo=UTC),
    )
    assert usage.used == 5
    assert usage.remaining == 0
    assert usage.exhausted is True


def test_consume_first_creates_counter(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    usage = QuotaUsageService.consume(
        db_session,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota,
        amount=1,
        ref_dt=datetime(2026, 3, 15, 10, 0, tzinfo=UTC),
    )
    assert usage.used == 1
    assert usage.remaining == 4

    # Verify DB
    counter = db_session.query(FeatureUsageCounterModel).first()
    assert counter is not None
    assert counter.used_count == 1
    # SQLite returns naive datetimes
    actual_start = counter.window_start
    if actual_start.tzinfo is None:
        actual_start = actual_start.replace(tzinfo=UTC)
    assert actual_start == datetime(2026, 3, 15, 0, 0, tzinfo=UTC)


def test_consume_increments(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=2, ref_dt=ref_dt
    )
    usage = QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=1, ref_dt=ref_dt
    )

    assert usage.used == 3
    assert usage.remaining == 2

    counter = db_session.query(FeatureUsageCounterModel).first()
    assert counter.used_count == 3


def test_consume_amount_3(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=2, ref_dt=ref_dt
    )
    usage = QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=3, ref_dt=ref_dt
    )

    assert usage.used == 5
    assert usage.remaining == 0
    assert usage.exhausted is True


def test_consume_exceeded_raises(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=5, ref_dt=ref_dt
    )

    with pytest.raises(QuotaExhaustedError) as excinfo:
        QuotaUsageService.consume(
            db_session,
            user_id=1,
            feature_code="astrologer_chat",
            quota=quota,
            amount=1,
            ref_dt=ref_dt,
        )

    assert excinfo.value.used == 5
    assert excinfo.value.limit == 5


def test_consume_amount_zero_raises(db_session):
    quota = QuotaDefinition(
        quota_key="d", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    with pytest.raises(ValueError, match="amount must be >= 1"):
        QuotaUsageService.consume(
            db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=0
        )


def test_consume_amount_negative_raises(db_session):
    quota = QuotaDefinition(
        quota_key="d", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    with pytest.raises(ValueError, match="amount must be >= 1"):
        QuotaUsageService.consume(
            db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=-1
        )


def test_usage_state_contains_all_fields(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    usage = QuotaUsageService.get_usage(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, ref_dt=ref_dt
    )

    assert usage.feature_code == "astrologer_chat"
    assert usage.quota_key == "daily"
    assert usage.quota_limit == 5
    assert usage.period_unit == "day"
    assert usage.period_value == 1
    assert usage.reset_mode == "calendar"
    assert usage.window_start == datetime(2026, 3, 15, 0, 0, tzinfo=UTC)
    assert usage.window_end == datetime(2026, 3, 16, 0, 0, tzinfo=UTC)


def test_get_usage_still_available(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    window_start = datetime(2026, 3, 15, 0, 0, tzinfo=UTC)
    counter = FeatureUsageCounterModel(
        user_id=1,
        feature_code="astrologer_chat",
        quota_key="daily",
        period_unit="day",
        period_value=1,
        reset_mode="calendar",
        window_start=window_start,
        window_end=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
        used_count=4,
    )
    db_session.add(counter)
    db_session.commit()

    usage = QuotaUsageService.get_usage(
        db_session,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota,
        ref_dt=datetime(2026, 3, 15, 10, 0, tzinfo=UTC),
    )
    assert usage.used == 4
    assert usage.remaining == 1
    assert usage.exhausted is False


def test_get_usage_multiple_quotas_same_feature(db_session):
    quota_daily = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    quota_monthly = QuotaDefinition(
        quota_key="monthly",
        quota_limit=50,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)

    usage_daily = QuotaUsageService.get_usage(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota_daily, ref_dt=ref_dt
    )
    usage_monthly = QuotaUsageService.get_usage(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota_monthly, ref_dt=ref_dt
    )

    assert usage_daily.quota_key == "daily"
    assert usage_daily.quota_limit == 5
    assert usage_monthly.quota_key == "monthly"
    assert usage_monthly.quota_limit == 50
    assert usage_daily.used == 0
    assert usage_monthly.used == 0


def test_get_usage_no_side_effect(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)

    usage1 = QuotaUsageService.get_usage(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, ref_dt=ref_dt
    )
    usage2 = QuotaUsageService.get_usage(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, ref_dt=ref_dt
    )

    assert usage1.used == usage2.used == 0
    count = db_session.query(FeatureUsageCounterModel).count()
    assert count == 0


def test_consume_exactly_limit(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=4, ref_dt=ref_dt
    )

    usage = QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=1, ref_dt=ref_dt
    )
    assert usage.used == 5
    assert usage.remaining == 0
    assert usage.exhausted is True


def test_consume_amount_exceeds_raises(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)
    QuotaUsageService.consume(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=3, ref_dt=ref_dt
    )

    with pytest.raises(QuotaExhaustedError):
        QuotaUsageService.consume(
            db_session,
            user_id=1,
            feature_code="astrologer_chat",
            quota=quota,
            amount=3,
            ref_dt=ref_dt,
        )

    counter = db_session.query(FeatureUsageCounterModel).first()
    assert counter.used_count == 3  # inchangé après l'échec


def test_consume_atomicity_with_for_update(db_session):
    # Vérifier le vrai query builder de production, compilé avec le dialecte PostgreSQL.
    from sqlalchemy.dialects import postgresql

    quota = QuotaDefinition(
        quota_key="daily",
        quota_limit=5,
        period_unit="day",
        period_value=1,
        reset_mode="calendar",
    )
    window = QuotaWindow(
        window_start=datetime(2026, 3, 15, 0, 0, tzinfo=UTC),
        window_end=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
    )
    fake_db = Mock()
    fake_db.scalar.return_value = None
    fake_db.begin_nested.return_value = nullcontext()

    QuotaUsageService._find_or_create_counter(
        fake_db,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota,
        window=window,
    )

    query = fake_db.scalar.call_args.args[0]
    compiled = str(query.compile(dialect=postgresql.dialect()))
    assert "FOR UPDATE" in compiled


def test_upgrade_behavior(db_session):
    # Setup initial quota (basic: 50/month)
    quota_basic = QuotaDefinition(
        quota_key="messages",
        quota_limit=50,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    ref_dt = datetime(2026, 3, 15, 10, 0, tzinfo=UTC)

    # Consume 10 messages under basic
    QuotaUsageService.consume(
        db_session,
        user_id=1,
        feature_code="astrologer_chat",
        quota=quota_basic,
        amount=10,
        ref_dt=ref_dt,
    )

    # Simulate upgrade to premium (1000/month)
    # The key composite is the same (messages, month, 1, calendar, 2026-03-01)
    quota_premium = QuotaDefinition(
        quota_key="messages",
        quota_limit=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )

    # Check usage under premium
    usage = QuotaUsageService.get_usage(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota_premium, ref_dt=ref_dt
    )

    assert usage.used == 10
    assert usage.quota_limit == 1000
    assert usage.remaining == 990
