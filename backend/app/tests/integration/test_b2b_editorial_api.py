from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.main import app
from app.services.auth_service import AuthService
from app.services.b2b.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        for model in (
            AuditEventModel,
            EnterpriseEditorialConfigModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingPlanModel,
            EnterpriseAccountModel,
            PlanFeatureQuotaModel,
            PlanFeatureBindingModel,
            FeatureCatalogModel,
            PlanCatalogModel,
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
    with open_app_test_db_session() as db:
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


def _create_enterprise_api_key_with_canonical_plan(
    email: str,
    access_mode: AccessMode = AccessMode.UNLIMITED,
    quota_limit: int = 100,
) -> str:
    with open_app_test_db_session() as db:
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

        # Plan enterprise fictif
        ent_plan = EnterpriseBillingPlanModel(
            code=f"plan-{auth.user.id}",
            display_name="Test Plan",
            monthly_fixed_cents=1000,
            included_monthly_units=0,
        )
        db.add(ent_plan)
        db.flush()
        db.add(
            EnterpriseAccountBillingPlanModel(
                enterprise_account_id=account.id,
                plan_id=ent_plan.id,
            )
        )

        # Plan canonique
        plan = PlanCatalogModel(
            plan_code=f"b2b-{auth.user.id}",
            plan_name="B2B Test",
            audience=Audience.B2B,
            source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            source_id=ent_plan.id,
            is_active=True,
        )
        db.add(plan)
        db.flush()

        # Feature catalog
        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "b2b_api_access")
        )
        if not feature:
            feature = FeatureCatalogModel(
                feature_code="b2b_api_access", feature_name="B2B API", is_metered=True
            )
            db.add(feature)
            db.flush()

        # Binding classifié manuellement
        binding = PlanFeatureBindingModel(
            plan_id=plan.id,
            feature_id=feature.id,
            access_mode=access_mode,
            is_enabled=True,
            source_origin="manual",
        )
        db.add(binding)
        db.flush()

        if access_mode == AccessMode.QUOTA:
            quota = PlanFeatureQuotaModel(
                plan_feature_binding_id=binding.id,
                quota_key="calls",
                quota_limit=quota_limit,
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                source_origin="manual",
            )
            db.add(quota)

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

    with open_app_test_db_session() as db:
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

    with open_app_test_db_session() as db:
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
    api_key = _create_enterprise_api_key_with_canonical_plan("b2b-editorial-weekly@example.com")
    with open_app_test_db_session() as db:
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
