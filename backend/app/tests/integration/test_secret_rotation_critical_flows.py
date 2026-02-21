from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.session import SessionLocal
from app.main import app
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService


def _create_enterprise_api_key(email: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Rotation Test Enterprise",
            status="active",
        )
        db.add(account)
        db.flush()
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key


def _seed_reference_data() -> None:
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)
        db.commit()


def _run_pre_rotation_journey(client: TestClient, run_id: str) -> tuple[dict[str, str], str]:
    user_email = f"rotation-user-{run_id}@example.com"
    b2b_admin_email = f"rotation-b2b-admin-{run_id}@example.com"

    register = client.post(
        "/v1/auth/register",
        json={"email": user_email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    tokens_before = register.json()["data"]["tokens"]
    access_before = tokens_before["access_token"]
    user_headers = {"Authorization": f"Bearer {access_before}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=user_headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": f"rotation-checkout-{run_id}",
        },
    )
    assert checkout.status_code == 200

    chat_first = client.post(
        "/v1/chat/messages",
        headers=user_headers,
        json={"message": "Test continuite avant rotation."},
    )
    assert chat_first.status_code == 200

    b2b_api_key = _create_enterprise_api_key(b2b_admin_email)
    b2b_before = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": b2b_api_key},
    )
    assert b2b_before.status_code == 200

    return tokens_before, b2b_api_key


def _assert_post_rotation_journey(
    client: TestClient,
    access_before: str,
    refresh_before: str,
    b2b_api_key: str,
) -> None:
    user_headers = {"Authorization": f"Bearer {access_before}"}

    billing_after_rotation = client.get("/v1/billing/quota", headers=user_headers)
    assert billing_after_rotation.status_code == 200

    chat_history_after_rotation = client.get(
        "/v1/chat/conversations?limit=20&offset=0",
        headers=user_headers,
    )
    assert chat_history_after_rotation.status_code == 200

    refresh_after_rotation = client.post(
        "/v1/auth/refresh",
        json={"refresh_token": refresh_before},
    )
    assert refresh_after_rotation.status_code == 200
    access_after = refresh_after_rotation.json()["data"]["access_token"]

    subscription_after_rotation = client.get(
        "/v1/billing/subscription",
        headers={"Authorization": f"Bearer {access_after}"},
    )
    assert subscription_after_rotation.status_code == 200

    b2b_after = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": b2b_api_key},
    )
    assert b2b_after.status_code == 200


def _rotate_runtime_secrets(monkeypatch: object) -> None:
    old_jwt_secret = settings.jwt_secret_key
    old_api_secret = settings.api_credentials_secret_key

    monkeypatch.setattr(settings, "jwt_secret_key", "rotated-jwt-secret-key-1234567890")
    monkeypatch.setattr(settings, "jwt_previous_secret_keys", [old_jwt_secret])
    monkeypatch.setattr(settings, "api_credentials_secret_key", "rotated-api-secret-key-1234567890")
    monkeypatch.setattr(settings, "api_credentials_previous_secret_keys", [old_api_secret])


def test_secret_rotation_keeps_auth_billing_chat_and_b2b_alive(monkeypatch: object) -> None:
    _seed_reference_data()
    run_id = uuid4().hex
    with TestClient(app) as client:
        tokens_before, b2b_api_key = _run_pre_rotation_journey(client, run_id)
        _rotate_runtime_secrets(monkeypatch)
        _assert_post_rotation_journey(
            client=client,
            access_before=tokens_before["access_token"],
            refresh_before=tokens_before["refresh_token"],
            b2b_api_key=b2b_api_key,
        )


def test_secret_rotation_survives_client_restart(monkeypatch: object) -> None:
    _seed_reference_data()
    run_id = uuid4().hex

    with TestClient(app) as before_restart_client:
        tokens_before, b2b_api_key = _run_pre_rotation_journey(before_restart_client, run_id)

    _rotate_runtime_secrets(monkeypatch)

    with TestClient(app) as after_restart_client:
        _assert_post_rotation_journey(
            client=after_restart_client,
            access_before=tokens_before["access_token"],
            refresh_before=tokens_before["refresh_token"],
            b2b_api_key=b2b_api_key,
        )
