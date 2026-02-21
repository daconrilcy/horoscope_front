from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            EnterpriseEditorialConfigModel,
            EnterpriseDailyUsageModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


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
            company_name="Acme Media",
            status="active",
        )
        db.add(account)
        db.flush()
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key


def test_b2b_editorial_get_returns_default_config() -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-editorial-default@example.com")

    response = client.get(
        "/v1/b2b/editorial/config",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-editorial-default"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-b2b-editorial-default"
    assert payload["data"]["version_number"] == 0
    assert payload["data"]["output_format"] == "paragraph"


def test_b2b_editorial_update_persists_config_and_audit() -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-editorial-update@example.com")

    response = client.put(
        "/v1/b2b/editorial/config",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-editorial-update"},
        json={
            "tone": "friendly",
            "length_style": "short",
            "output_format": "bullet",
            "preferred_terms": ["focus", "clarte"],
            "avoided_terms": ["drama"],
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["version_number"] == 1
    assert payload["output_format"] == "bullet"

    with SessionLocal() as db:
        audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-editorial-update")
            .where(AuditEventModel.action == "b2b_editorial_config_update")
            .limit(1)
        )
        assert audit is not None
        assert audit.status == "success"


def test_b2b_editorial_invalid_payload_returns_422_and_audit_failed() -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-editorial-invalid@example.com")

    response = client.put(
        "/v1/b2b/editorial/config",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-editorial-invalid"},
        json={
            "tone": "unknown-tone",
            "length_style": "short",
            "output_format": "paragraph",
            "preferred_terms": [],
            "avoided_terms": [],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_editorial_config"

    with SessionLocal() as db:
        audit = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-editorial-invalid")
            .where(AuditEventModel.action == "b2b_editorial_config_update")
            .limit(1)
        )
        assert audit is not None
        assert audit.status == "failed"


def test_b2b_editorial_config_influences_weekly_by_sign_output() -> None:
    _cleanup_tables()
    api_key = _create_enterprise_api_key("b2b-editorial-weekly@example.com")
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)

    update = client.put(
        "/v1/b2b/editorial/config",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-editorial-weekly-update"},
        json={
            "tone": "friendly",
            "length_style": "short",
            "output_format": "bullet",
            "preferred_terms": ["focus"],
            "avoided_terms": ["drama"],
        },
    )
    assert update.status_code == 200

    weekly = client.get(
        "/v1/b2b/astrology/weekly-by-sign",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-editorial-weekly-call"},
    )
    assert weekly.status_code == 200
    first_summary = weekly.json()["data"]["items"][0]["weekly_summary"]
    assert first_summary.startswith("- Conseil ")
    assert "focus" in first_summary
