from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.stripe_billing_profile_service import (
    STRIPE_PRICE_ENTITLEMENT_MAP,
    StripeBillingProfileService,
    derive_entitlement_plan,
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        yield session
        session.rollback()


@pytest.fixture
def user_id(db: Session):
    auth = AuthService.register(
        db,
        email="stripe-user@example.com",
        password="strong-pass-123",
        role="user",
    )
    db.commit()
    return auth.user.id


def test_derive_entitlement_plan_basic_cases():
    # Mock du mapping pour le test
    mapping = {"price_basic": "basic", "price_premium": "premium"}
    with patch.dict(STRIPE_PRICE_ENTITLEMENT_MAP, mapping):
        # Cas nominaux
        assert derive_entitlement_plan("active", "price_basic") == "basic"
        assert derive_entitlement_plan("trialing", "price_premium") == "premium"

        # Price ID inconnu -> free + warning (fail-closed)
        assert derive_entitlement_plan("active", "unknown_price") == "free"

        # past_due -> conserve le plan actuel
        assert derive_entitlement_plan(
            "past_due", "price_basic", current_entitlement="premium"
        ) == "premium"
        assert derive_entitlement_plan(
            "past_due", None, current_entitlement="basic"
        ) == "basic"

        # Cas de révocation
        assert derive_entitlement_plan("canceled", "price_basic") == "free"
        assert derive_entitlement_plan("unpaid", "price_basic") == "free"
        assert derive_entitlement_plan("incomplete_expired", "price_basic") == "free"

        # Cas d'attente / suspension
        assert derive_entitlement_plan("incomplete", "price_basic") == "free"
        assert derive_entitlement_plan("paused", "price_basic") == "free"

        # Aucun statut
        assert derive_entitlement_plan(None, "price_basic") == "free"

        # active + stripe_price_id None → fail-closed → free
        assert derive_entitlement_plan("active", None) == "free"
        # active + price_id absent du map → fail-closed → free
        assert derive_entitlement_plan("active", "price_unknown_xyz") == "free"


def test_update_from_event_payload_idempotence_stricte(db: Session, user_id: int):
    event_id = "evt_123"
    event_data = {
        "id": event_id,
        "type": "customer.subscription.updated",
        "created": 1711238400,  # 2024-03-24 00:00:00 UTC
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_123",
                "status": "active",
                "customer": "cus_123",
                "items": {"data": [{"price": {"id": "price_basic"}}]}
            }
        }
    }

    with patch.dict(STRIPE_PRICE_ENTITLEMENT_MAP, {"price_basic": "basic"}):
        # Premier traitement
        profile1 = StripeBillingProfileService.update_from_event_payload(db, user_id, event_data)
        db.commit()
        synced_at1 = profile1.synced_at

        # Deuxième traitement du même event_id
        profile2 = StripeBillingProfileService.update_from_event_payload(db, user_id, event_data)
        db.commit()

        # Ne doit pas avoir été modifié (même synced_at)
        assert profile1.id == profile2.id
        assert profile1.last_stripe_event_id == event_id
        assert profile2.synced_at == synced_at1


def test_update_from_event_payload_hors_ordre(db: Session, user_id: int):
    # Event récent
    event_recent = {
        "id": "evt_recent",
        "created": 1711324800,  # Plus récent
        "data": {"object": {"object": "subscription", "status": "active", "id": "sub_123"}}
    }
    # Event ancien
    event_ancien = {
        "id": "evt_ancien",
        "created": 1711238400,  # Plus ancien
        "data": {"object": {"object": "subscription", "status": "canceled", "id": "sub_123"}}
    }

    # On traite le récent d'abord
    StripeBillingProfileService.update_from_event_payload(db, user_id, event_recent)
    db.commit()
    
    profile = StripeBillingProfileService.get_or_create_profile(db, user_id)
    assert profile.subscription_status == "active"
    last_event_id = profile.last_stripe_event_id

    # On traite l'ancien ensuite -> doit être ignoré
    StripeBillingProfileService.update_from_event_payload(db, user_id, event_ancien)
    db.commit()

    db.refresh(profile)
    assert profile.subscription_status == "active"  # Toujours active !
    assert profile.last_stripe_event_id == last_event_id


def test_transition_entitlement_plan(db: Session, user_id: int):
    with patch.dict(STRIPE_PRICE_ENTITLEMENT_MAP, {"price_premium": "premium"}):
        # 1. Passage en Premium
        event_premium = {
            "id": "evt_1",
            "created": 1000,
            "data": {
                "object": {
                    "object": "subscription",
                    "status": "active",
                    "items": {"data": [{"price": {"id": "price_premium"}}]}
                }
            }
        }
        StripeBillingProfileService.update_from_event_payload(db, user_id, event_premium)
        assert StripeBillingProfileService.get_entitlement_plan(db, user_id) == "premium"

        # 2. Passage en past_due -> conserve premium
        event_past_due = {
            "id": "evt_2",
            "created": 2000,
            "data": {"object": {"object": "subscription", "status": "past_due"}}
        }
        StripeBillingProfileService.update_from_event_payload(db, user_id, event_past_due)
        assert StripeBillingProfileService.get_entitlement_plan(db, user_id) == "premium"

        # 3. Passage en canceled -> free
        event_canceled = {
            "id": "evt_3",
            "created": 3000,
            "data": {"object": {"object": "subscription", "status": "canceled"}}
        }
        StripeBillingProfileService.update_from_event_payload(db, user_id, event_canceled)
        assert StripeBillingProfileService.get_entitlement_plan(db, user_id) == "free"
