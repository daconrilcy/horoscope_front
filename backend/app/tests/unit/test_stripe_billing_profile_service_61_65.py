from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.services.auth_service import AuthService
from app.services.billing.stripe_billing_profile_service import (
    STRIPE_PRICE_ENTITLEMENT_MAP,
    StripeBillingProfileService,
)
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as session:
        yield session
        session.rollback()


@pytest.fixture
def user_id(db: Session):
    auth = AuthService.register(
        db,
        email="stripe-user-61-65@example.com",
        password="strong-pass-123",
        role="user",
    )
    db.commit()
    return auth.user.id


def test_update_from_event_payload_period_fields(db: Session, user_id: int):
    period_start = 1711238400  # 2024-03-24
    period_end = 1713916800  # 2024-04-24

    event_data = {
        "id": "evt_period",
        "type": "customer.subscription.updated",
        "created": 1711238500,
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "active",
                "customer": "cus_123",
                "current_period_start": period_start,
                "current_period_end": period_end,
                "cancel_at_period_end": True,
            }
        },
    }

    with patch.dict(STRIPE_PRICE_ENTITLEMENT_MAP, {"price_basic": "basic"}):
        profile = StripeBillingProfileService.update_from_event_payload(db, user_id, event_data)
        db.commit()
        db.refresh(profile)

        # Helper to compare datetimes without tz for SQLite compatibility
        def assert_dt_equal(dt1, dt2):
            if dt1 is None or dt2 is None:
                assert dt1 == dt2
                return
            assert dt1.replace(tzinfo=None) == dt2.replace(tzinfo=None)

        assert_dt_equal(
            profile.current_period_start, datetime.fromtimestamp(period_start, tz=timezone.utc)
        )
        assert_dt_equal(
            profile.current_period_end, datetime.fromtimestamp(period_end, tz=timezone.utc)
        )
        assert profile.cancel_at_period_end is True
        # AC3: pending_cancellation_effective_at = current_period_end
        assert_dt_equal(profile.pending_cancellation_effective_at, profile.current_period_end)


def test_update_from_event_payload_cancel_at_marks_scheduled_cancellation(
    db: Session, user_id: int
):
    period_end = 1713916800  # 2024-04-24

    event_data = {
        "id": "evt_cancel_at",
        "type": "customer.subscription.updated",
        "created": 1711238500,
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "active",
                "customer": "cus_123",
                "current_period_end": period_end,
                "cancel_at": period_end,
                "cancel_at_period_end": False,
            }
        },
    }

    profile = StripeBillingProfileService.update_from_event_payload(db, user_id, event_data)
    db.commit()
    db.refresh(profile)

    expected_end = datetime.fromtimestamp(period_end, tz=timezone.utc)
    assert profile.cancel_at_period_end is True
    assert profile.current_period_end.replace(tzinfo=None) == expected_end.replace(tzinfo=None)
    assert profile.pending_cancellation_effective_at.replace(tzinfo=None) == expected_end.replace(
        tzinfo=None
    )


def test_update_from_event_payload_cancel_cleanup(db: Session, user_id: int):
    # D'abord on est en "active" avec une annulation programmée
    event_active = {
        "id": "evt_active",
        "type": "customer.subscription.updated",
        "created": 1000,
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "active",
                "cancel_at_period_end": True,
                "current_period_end": 2000,
            }
        },
    }
    StripeBillingProfileService.update_from_event_payload(db, user_id, event_active)
    profile = StripeBillingProfileService.get_or_create_profile(db, user_id)
    assert profile.cancel_at_period_end is True
    assert profile.pending_cancellation_effective_at is not None

    # Maintenant on reçoit le "deleted" (canceled)
    event_deleted = {
        "id": "evt_deleted",
        "type": "customer.subscription.deleted",
        "created": 3000,
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "canceled",
            }
        },
    }
    StripeBillingProfileService.update_from_event_payload(db, user_id, event_deleted)
    db.refresh(profile)

    # AC4: Nettoyage complet
    assert profile.subscription_status == "canceled"
    assert profile.cancel_at_period_end is False
    assert profile.pending_cancellation_effective_at is None
    assert profile.scheduled_plan_code is None
    assert profile.scheduled_change_effective_at is None


@patch("app.services.billing.stripe_billing_profile_service.get_stripe_client")
def test_update_from_event_payload_downgrade_schedule(mock_get_client, db: Session, user_id: int):
    # Mock Stripe Client
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    now_ts = datetime.now(timezone.utc).timestamp()
    future_ts = now_ts + 10000

    # Mock du schedule Stripe
    mock_client.subscription_schedules.retrieve.return_value = {
        "id": "sub_sched_123",
        "phases": [
            {"start_date": now_ts - 1000, "items": [{"price": "price_premium"}]},
            {"start_date": future_ts, "items": [{"price": "price_basic"}]},
        ],
    }

    event_data = {
        "id": "evt_schedule",
        "type": "customer.subscription.updated",
        "created": now_ts,
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "active",
                "schedule": "sub_sched_123",
                "current_period_end": future_ts,
            }
        },
    }

    with patch.dict(
        STRIPE_PRICE_ENTITLEMENT_MAP, {"price_basic": "basic", "price_premium": "premium"}
    ):
        profile = StripeBillingProfileService.update_from_event_payload(db, user_id, event_data)
        db.commit()
        db.refresh(profile)

        # AC2: plan effectif conservé (on suppose qu'il était premium ou qu'on ne l'a pas encore
        # mis à jour dans ce test simplifié)
        # On vérifie surtout le plan programmé
        assert profile.scheduled_plan_code == "basic"

        # Helper for SQLite compatibility
        dt_sched = profile.scheduled_change_effective_at
        dt_expected = datetime.fromtimestamp(future_ts, tz=timezone.utc)
        assert dt_sched.replace(tzinfo=None) == dt_expected.replace(tzinfo=None)


def test_update_from_event_payload_upgrade_clears_schedule(db: Session, user_id: int):
    # D'abord on a un plan programmé
    profile = StripeBillingProfileService.get_or_create_profile(db, user_id)
    profile.scheduled_plan_code = "basic"
    profile.scheduled_change_effective_at = datetime.now(timezone.utc)
    db.commit()

    # On reçoit un upgrade immédiat (pas de schedule dans l'objet Stripe)
    event_upgrade = {
        "id": "evt_upgrade",
        "type": "customer.subscription.updated",
        "created": 1000,
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "active",
                "schedule": None,  # Plus de schedule
                "items": {"data": [{"price": {"id": "price_premium"}}]},
            }
        },
    }

    with patch.dict(STRIPE_PRICE_ENTITLEMENT_MAP, {"price_premium": "premium"}):
        StripeBillingProfileService.update_from_event_payload(db, user_id, event_upgrade)
        db.refresh(profile)

        # AC1: upgrade immédiat + nettoyage schedule
        assert profile.entitlement_plan == "premium"
        assert profile.scheduled_plan_code is None
        assert profile.scheduled_change_effective_at is None


def test_update_from_event_payload_direct_schedule_object(db: Session, user_id: int):
    future_ts = datetime.now(timezone.utc).timestamp() + 20000

    event_schedule = {
        "id": "evt_sched_direct",
        "type": "subscription_schedule.updated",
        "created": 1000,
        "data": {
            "object": {
                "object": "subscription_schedule",
                "id": "sub_sched_123",
                "customer": "cus_123",
                "phases": [
                    {"start_date": 500, "items": [{"price": "price_premium"}]},
                    {"start_date": future_ts, "items": [{"price": "price_basic"}]},
                ],
            }
        },
    }

    # On doit d'abord avoir un profil avec ce customer_id car le resolve_user_id l'utilise
    profile = StripeBillingProfileService.get_or_create_profile(db, user_id)
    profile.stripe_customer_id = "cus_123"
    db.commit()

    with patch.dict(
        STRIPE_PRICE_ENTITLEMENT_MAP, {"price_basic": "basic", "price_premium": "premium"}
    ):
        StripeBillingProfileService.update_from_event_payload(db, user_id, event_schedule)
        db.refresh(profile)

        assert profile.scheduled_plan_code == "basic"
        # Helper for SQLite
        dt_sched = profile.scheduled_change_effective_at
        dt_expected = datetime.fromtimestamp(future_ts, tz=timezone.utc)
        assert dt_sched.replace(tzinfo=None) == dt_expected.replace(tzinfo=None)
