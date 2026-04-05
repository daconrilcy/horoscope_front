import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.infra.db.models.user import UserModel
from app.main import app


@pytest.fixture
def auth_user(db_session: Session) -> AuthenticatedUser:
    user = db_session.query(UserModel).filter(UserModel.email == "test@example.com").first()
    if not user:
        user = UserModel(email="test@example.com", password_hash="...", role="user")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return AuthenticatedUser(
        id=user.id, email=user.email, role=user.role, created_at=user.created_at
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_endpoints_are_404_after_decommission(
    client: TestClient, db_session: Session, auth_user: AuthenticatedUser
):
    # This test is expected to PASS now that endpoints are removed.

    headers = {"Authorization": "Bearer dummy"}

    # We expect these to be 404 (or 405) after my changes
    resp_checkout = client.post("/v1/billing/checkout", json={}, headers=headers)
    assert resp_checkout.status_code in [404, 405]

    resp_retry = client.post("/v1/billing/retry", json={}, headers=headers)
    assert resp_retry.status_code in [404, 405]

    resp_plan = client.post("/v1/billing/plan-change", json={}, headers=headers)
    assert resp_plan.status_code in [404, 405]
