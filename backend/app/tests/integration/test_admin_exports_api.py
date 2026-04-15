from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.user import UserModel
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-exports.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        test_engine.dispose()


def _login(email: str, password: str) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["data"]["tokens"]["access_token"]


@pytest.fixture
def admin_token() -> str:
    with db_session_module.SessionLocal() as db:
        from app.core.security import hash_password

        admin = UserModel(
            email="admin-export@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard",
        )
        db.add(admin)
        db.commit()

    return _login("admin-export@example.com", "admin123")


@pytest.fixture
def user_token() -> str:
    with db_session_module.SessionLocal() as db:
        from app.core.security import hash_password

        user = UserModel(
            email="user-export@example.com",
            password_hash=hash_password("admin123"),
            role="user",
            astrologer_profile="standard",
        )
        db.add(user)
        db.commit()

    return _login("user-export@example.com", "admin123")


def test_export_users_csv(admin_token: str) -> None:
    response = client.post(
        "/v1/admin/exports/users",
        json={"period": None},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "id,email,role" in response.text

    with db_session_module.SessionLocal() as db:
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "sensitive_data_exported")
        )
        assert audit is not None
        assert audit.details["export_type"] == "users"


def test_export_users_with_period_serializes_datetime_filters(admin_token: str) -> None:
    now = datetime.now(UTC)
    response = client.post(
        "/v1/admin/exports/users",
        json={
            "period": {
                "start": (now - timedelta(days=7)).isoformat(),
                "end": now.isoformat(),
            }
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    with db_session_module.SessionLocal() as db:
        audit = (
            db.query(AuditEventModel)
            .filter(AuditEventModel.action == "sensitive_data_exported")
            .order_by(AuditEventModel.created_at.desc())
            .first()
        )
        assert audit is not None
        assert isinstance(audit.details["filters"]["period"]["start"], str)
        assert audit.details["filters"]["period"]["start"].endswith("Z")


def test_export_generations_json(admin_token: str) -> None:
    response = client.post(
        "/v1/admin/exports/generations",
        json={"period": None, "format": "json"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "Deprecated field: use_case_compat" in response.headers["warning"]
    assert response.headers["sunset"] == "Tue, 30 Sep 2026 23:59:59 GMT"
    assert response.headers["x-deprecated-fields"] == "use_case_compat"
    assert isinstance(response.json(), list)


def test_export_generations_csv(admin_token: str) -> None:
    with db_session_module.SessionLocal() as db:
        db.add(
            LlmCallLogModel(
                use_case="daily_overview",
                model="gpt-test",
                validation_status=LlmValidationStatus.VALID,
                latency_ms=320,
                tokens_in=120,
                tokens_out=240,
                cost_usd_estimated=0.01,
                request_id="req-export-1",
                trace_id="trace-export-1",
                input_hash="hash-export-1",
                environment="test",
                evidence_warnings_count=0,
            )
        )
        db.commit()

    response = client.post(
        "/v1/admin/exports/generations",
        json={"period": None, "format": "csv"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Deprecated field: use_case_compat" in response.headers["warning"]
    assert response.headers["sunset"] == "Tue, 30 Sep 2026 23:59:59 GMT"
    assert response.headers["x-deprecated-fields"] == "use_case_compat"
    assert "id,created_at,feature,subfeature,subscription_plan" in response.text
    assert "use_case_compat" in response.text


def test_export_generations_csv_reclassifies_when_feature_null_but_use_case_compat_set(
    admin_token: str,
) -> None:
    with db_session_module.SessionLocal() as db:
        db.add(
            LlmCallLogModel(
                use_case="natal_interpretation",
                feature=None,
                subfeature="full",
                plan="premium",
                model="gpt-test",
                validation_status=LlmValidationStatus.VALID,
                latency_ms=350,
                tokens_in=90,
                tokens_out=110,
                cost_usd_estimated=0.02,
                request_id="req-export-null-feature",
                trace_id="trace-export-null-feature",
                input_hash="hash-export-null-feature",
                environment="test",
                evidence_warnings_count=0,
            )
        )
        db.commit()

    response = client.post(
        "/v1/admin/exports/generations",
        json={"period": None, "format": "csv"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert "natal,full,premium" in response.text
    assert "nominal" in response.text
    assert "natal_interpretation" in response.text


def test_export_generations_csv_reclassifies_legacy_use_case_to_canonical_feature(
    admin_token: str,
) -> None:
    with db_session_module.SessionLocal() as db:
        db.add(
            LlmCallLogModel(
                use_case="natal_interpretation",
                feature="natal_interpretation",
                subfeature="legacy_unknown",
                plan="free",
                model="gpt-test",
                validation_status=LlmValidationStatus.VALID,
                latency_ms=350,
                tokens_in=90,
                tokens_out=110,
                cost_usd_estimated=0.02,
                request_id="req-export-legacy",
                trace_id="trace-export-legacy",
                input_hash="hash-export-legacy",
                environment="test",
                evidence_warnings_count=0,
            )
        )
        db.commit()

    response = client.post(
        "/v1/admin/exports/generations",
        json={"period": None, "format": "csv"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert "natal,legacy_unknown,free" in response.text
    assert "legacy_residual" in response.text
    assert "natal_interpretation" in response.text


def test_export_billing_csv(admin_token: str) -> None:
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="billing-export@example.com", password_hash="x", role="user")
        db.add(user)
        db.flush()

        plan = BillingPlanModel(
            code="premium",
            display_name="Premium",
            monthly_price_cents=2990,
            currency="EUR",
            daily_message_limit=10,
        )
        db.add(plan)
        db.flush()

        db.add(
            UserSubscriptionModel(
                user_id=user.id,
                plan_id=plan.id,
                status="active",
                failure_reason=None,
                started_at=datetime.now(UTC),
            )
        )
        db.commit()

    response = client.post(
        "/v1/admin/exports/billing",
        json={"period": None},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "user_id,email,plan_code,subscription_status" in response.text
    assert "premium" in response.text

    with db_session_module.SessionLocal() as db:
        audit = (
            db.query(AuditEventModel)
            .filter(AuditEventModel.action == "sensitive_data_exported")
            .order_by(AuditEventModel.created_at.desc())
            .first()
        )
        assert audit is not None
        assert audit.details["export_type"] == "billing"


def test_export_generations_rejects_non_admin(user_token: str) -> None:
    response = client.post(
        "/v1/admin/exports/generations",
        json={"period": None, "format": "json"},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403


def test_export_generations_requires_authentication() -> None:
    response = client.post(
        "/v1/admin/exports/generations",
        json={"period": None, "format": "json"},
    )

    assert response.status_code == 401
