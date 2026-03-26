import pytest
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.stripe_billing_profile_service import StripeBillingProfileService


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
        email="stripe-integration@example.com",
        password="strong-pass-123",
        role="user",
    )
    db.commit()
    return auth.user.id


def test_get_or_create_profile_is_idempotent(db: Session, user_id: int):
    # Premier appel
    profile1 = StripeBillingProfileService.get_or_create_profile(db, user_id)
    db.commit()
    assert profile1.user_id == user_id
    assert profile1.entitlement_plan == "free"

    # Deuxième appel
    profile2 = StripeBillingProfileService.get_or_create_profile(db, user_id)
    assert profile1.id == profile2.id


def test_resolution_by_stripe_ids(db: Session, user_id: int):
    # Création manuelle d'un profil avec IDs Stripe
    profile = StripeBillingProfileService.get_or_create_profile(db, user_id)
    profile.stripe_customer_id = "cus_integration_123"
    profile.stripe_subscription_id = "sub_integration_456"
    db.commit()

    # Résolution par Customer ID
    resolved_cus = StripeBillingProfileService.get_by_stripe_customer_id(db, "cus_integration_123")
    assert resolved_cus is not None
    assert resolved_cus.user_id == user_id

    # Résolution par Subscription ID
    resolved_sub = StripeBillingProfileService.get_by_stripe_subscription_id(
        db, "sub_integration_456"
    )
    assert resolved_sub is not None
    assert resolved_sub.user_id == user_id

    # Non trouvé
    assert StripeBillingProfileService.get_by_stripe_customer_id(db, "unknown") is None


def test_update_from_event_payload_hors_ordre_ignored(db: Session, user_id: int):
    # Event récent traité en premier
    event_recent = {
        "id": "evt_recent_integ",
        "created": 1711324800,
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_integ_123",
                "status": "active",
                "customer": "cus_integ_123",
            }
        },
    }
    StripeBillingProfileService.update_from_event_payload(db, user_id, event_recent)
    db.commit()

    profile = StripeBillingProfileService.get_or_create_profile(db, user_id)
    assert profile.subscription_status == "active"
    event_id_after_recent = profile.last_stripe_event_id

    # Event plus ancien arrivant après — doit être ignoré sans modification
    event_ancien = {
        "id": "evt_ancien_integ",
        "created": 1711238400,  # antérieur
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_integ_123",
                "status": "canceled",
                "customer": "cus_integ_123",
            }
        },
    }
    StripeBillingProfileService.update_from_event_payload(db, user_id, event_ancien)
    db.commit()

    db.refresh(profile)
    assert profile.subscription_status == "active"  # inchangé
    assert profile.last_stripe_event_id == event_id_after_recent  # inchangé


def test_update_from_event_payload_updates_synced_at(db: Session, user_id: int):
    event_data = {
        "id": "evt_sync_test",
        "created": 1711238400,
        "type": "customer.updated",
        "data": {"object": {"object": "customer", "id": "cus_123", "email": "billing@example.com"}},
    }

    # Appel au service
    profile = StripeBillingProfileService.update_from_event_payload(db, user_id, event_data)
    db.commit()

    assert profile.stripe_customer_id == "cus_123"
    assert profile.billing_email == "billing@example.com"
    assert profile.synced_at is not None
    assert profile.last_stripe_event_id == "evt_sync_test"
    assert profile.last_stripe_event_type == "customer.updated"
