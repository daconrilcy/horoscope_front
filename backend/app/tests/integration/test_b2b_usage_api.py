from datetime import datetime, timezone

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
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.models.user import UserModel
from app.main import app
from app.services.auth_service import AuthService
from app.services.b2b.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.ops.audit_service import AuditServiceError
from app.services.quota.window_resolver import QuotaWindowResolver
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        for model in (
            AuditEventModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            UserModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingPlanModel,
            PlanCatalogModel,
            PlanFeatureBindingModel,
            PlanFeatureQuotaModel,
            EnterpriseFeatureUsageCounterModel,
            FeatureUsageCounterModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_b2b_account_with_canonical_plan(
    email: str,
    access_mode: AccessMode = AccessMode.UNLIMITED,
    quota_limit: int = 100,
) -> tuple[str, int, int]:
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db, email=email, password="strong-pass-123", role="enterprise_admin"
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id, company_name="Acme Media", status="active"
        )
        db.add(account)
        db.flush()

        ent_plan = EnterpriseBillingPlanModel(
            code=f"plan-{auth.user.id}",
            display_name="Test Plan",
            monthly_fixed_cents=1000,
            included_monthly_units=0,
        )
        db.add(ent_plan)
        db.flush()
        db.add(
            EnterpriseAccountBillingPlanModel(enterprise_account_id=account.id, plan_id=ent_plan.id)
        )

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

        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "b2b_api_access")
        )
        if not feature:
            feature = FeatureCatalogModel(
                feature_code="b2b_api_access", feature_name="B2B API", is_metered=True
            )
            db.add(feature)
            db.flush()

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
        return created.api_key, account.id, created.credential_id


def test_b2b_usage_summary_requires_api_key() -> None:
    _cleanup_tables()
    response = client.get("/v1/b2b/usage/summary")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_b2b_usage_summary_returns_data_for_valid_api_key() -> None:
    _cleanup_tables()
    api_key, account_id, _ = _create_b2b_account_with_canonical_plan(
        "b2b-usage-summary@example.com", access_mode=AccessMode.UNLIMITED
    )

    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-summary"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-b2b-usage-summary"
    assert payload["data"]["source"] == "canonical"
    assert payload["data"]["access_mode"] == "unlimited"
    assert "limit" not in payload["data"]
    assert "used" not in payload["data"]


def test_b2b_usage_summary_quota_mode() -> None:
    _cleanup_tables()
    api_key, account_id, credential_id = _create_b2b_account_with_canonical_plan(
        "b2b-usage-quota@example.com", access_mode=AccessMode.QUOTA, quota_limit=100
    )

    with open_app_test_db_session() as db:
        ref_dt = datetime.now(timezone.utc)
        window = QuotaWindowResolver.compute_window(PeriodUnit.MONTH, 1, ResetMode.CALENDAR, ref_dt)
        db.add(
            EnterpriseFeatureUsageCounterModel(
                enterprise_account_id=account_id,
                feature_code="b2b_api_access",
                quota_key="calls",
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=window.window_start,
                window_end=window.window_end,
                used_count=42,
            )
        )
        db.commit()

    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-quota"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["access_mode"] == "quota"
    assert payload["data"]["quota_key"] == "calls"
    assert payload["data"]["limit"] == 100
    assert payload["data"]["used"] == 42
    assert payload["data"]["remaining"] == 58
    assert "window_end" in payload["data"]


def test_b2b_usage_summary_returns_403_when_no_canonical_plan() -> None:
    _cleanup_tables()
    # On crée juste un compte et une clé sans plan canonique
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db, email="no-plan@example.com", password="strong-pass-123", role="enterprise_admin"
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id, company_name="No Plan Inc", status="active"
        )
        db.add(account)
        db.flush()
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        api_key = created.api_key
        db.commit()

    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "b2b_no_canonical_plan"


def test_b2b_usage_summary_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key, _, _ = _create_b2b_account_with_canonical_plan("b2b-usage-429@example.com")

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "4"},
            status_code=429,
        )

    monkeypatch.setattr("app.services.b2b.api_usage.check_rate_limit", _always_rate_limited)
    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-429"},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"


def test_b2b_usage_summary_writes_success_audit_event() -> None:
    _cleanup_tables()
    api_key, account_id, credential_id = _create_b2b_account_with_canonical_plan(
        "b2b-usage-audit@example.com"
    )
    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-audit"},
    )
    assert response.status_code == 200

    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-b2b-usage-audit")
            .where(AuditEventModel.action == "b2b_usage_summary_read")
            .where(AuditEventModel.status == "success")
            .limit(1)
        )
        assert event is not None
        assert event.target_type == "enterprise_usage"
        assert event.target_id == str(credential_id)
        assert int(event.details["account_id"]) == account_id


def test_b2b_usage_summary_returns_503_when_audit_unavailable(monkeypatch: object) -> None:
    _cleanup_tables()
    api_key, _, _ = _create_b2b_account_with_canonical_plan("b2b-usage-audit-down@example.com")

    def _raise_audit_error(*args: object, **kwargs: object) -> None:
        raise AuditServiceError(
            code="audit_unavailable",
            message="audit unavailable",
            details={},
        )

    monkeypatch.setattr(
        "app.services.b2b.api_usage.AuditService.record_event",
        _raise_audit_error,
    )
    response = client.get(
        "/v1/b2b/usage/summary",
        headers={"X-API-Key": api_key, "X-Request-Id": "rid-b2b-usage-audit-down"},
    )
    assert response.status_code == 503
    payload = response.json()["error"]
    assert payload["code"] == "audit_unavailable"
