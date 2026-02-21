from __future__ import annotations

import json
import os
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService


def _phase_1() -> int:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)
        db.commit()

    client = TestClient(app)
    user_email = f"restart-user-{uuid4().hex}@example.com"
    b2b_admin_email = f"restart-b2b-admin-{uuid4().hex}@example.com"

    register = client.post(
        "/v1/auth/register",
        json={"email": user_email, "password": "strong-pass-123"},
    )
    if register.status_code != 200:
        raise SystemExit(f"phase1 register failed: {register.status_code} {register.text}")
    tokens = register.json()["data"]["tokens"]

    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=b2b_admin_email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Restart Rotation Enterprise",
            status="active",
        )
        db.add(account)
        db.flush()
        credential = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()

    print(
        json.dumps(
            {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "enterprise_credential": credential.api_key,
            }
        )
    )
    return 0


def _phase_2() -> int:
    client = TestClient(app)
    old_access_token = os.environ["ROTATION_OLD_ACCESS_TOKEN"]
    old_refresh_token = os.environ["ROTATION_OLD_REFRESH_TOKEN"]
    old_enterprise_credential = os.environ["ROTATION_OLD_ENTERPRISE_CREDENTIAL"]
    run_id = os.environ["ROTATION_RUN_ID"]

    subscription = client.get(
        "/v1/billing/subscription",
        headers={"Authorization": f"Bearer {old_access_token}"},
    )
    if subscription.status_code != 200:
        raise SystemExit(
            f"phase2 old access token rejected: {subscription.status_code} {subscription.text}"
        )

    checkout = client.post(
        "/v1/billing/checkout",
        headers={"Authorization": f"Bearer {old_access_token}"},
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": f"rotation-restart-checkout-{run_id}",
        },
    )
    if checkout.status_code != 200:
        raise SystemExit(
            f"phase2 billing checkout rejected: {checkout.status_code} {checkout.text}"
        )

    refresh = client.post("/v1/auth/refresh", json={"refresh_token": old_refresh_token})
    if refresh.status_code != 200:
        raise SystemExit(f"phase2 old refresh token rejected: {refresh.status_code} {refresh.text}")

    b2b = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": old_enterprise_credential},
    )
    if b2b.status_code != 200:
        raise SystemExit(f"phase2 old enterprise credential rejected: {b2b.status_code} {b2b.text}")
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: secret_rotation_restart_runner.py <phase1|phase2>")
    phase = sys.argv[1].strip().lower()
    if phase == "phase1":
        return _phase_1()
    if phase == "phase2":
        return _phase_2()
    raise SystemExit(f"Unknown phase: {phase}")


if __name__ == "__main__":
    raise SystemExit(main())
