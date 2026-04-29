from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.main import app
from app.services.auth_service import AuthService
from app.services.b2b.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import open_app_test_db_session


def _create_enterprise_api_key(email: str) -> str:
    with open_app_test_db_session() as db:
        from app.infra.db.models.enterprise_billing import (
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingPlanModel,
        )
        from app.infra.db.models.product_entitlements import (
            AccessMode,
            PlanCatalogModel,
            SourceOrigin,
        )

        # Legacy plan
        legacy_plan = db.scalar(
            select(EnterpriseBillingPlanModel).where(
                EnterpriseBillingPlanModel.code == "rotation-ent"
            )
        )
        if not legacy_plan:
            legacy_plan = EnterpriseBillingPlanModel(
                code="rotation-ent",
                display_name="Rotation Ent",
                monthly_fixed_cents=0,
                included_monthly_units=100,
                overage_unit_price_cents=0,
                currency="EUR",
                is_active=True,
            )
            db.add(legacy_plan)
            db.flush()

        # Canonical plan
        canonical_plan = db.scalar(
            select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "rotation-ent")
        )
        if not canonical_plan:
            canonical_plan = PlanCatalogModel(
                plan_code="rotation-ent",
                plan_name="Rotation B2B",
                audience=Audience.B2B,
                is_active=True,
                source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
                source_id=legacy_plan.id,
            )
            db.add(canonical_plan)
            db.flush()
        else:
            canonical_plan.plan_name = "Rotation B2B"
            canonical_plan.audience = Audience.B2B
            canonical_plan.is_active = True
            canonical_plan.source_type = SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value
            canonical_plan.source_id = legacy_plan.id

        # Binding
        from app.infra.db.models.product_entitlements import FeatureCatalogModel
        from app.services.b2b.api_entitlement_gate import B2BApiEntitlementGate

        feat = db.scalar(
            select(FeatureCatalogModel).where(
                FeatureCatalogModel.feature_code == B2BApiEntitlementGate.FEATURE_CODE
            )
        )
        binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == canonical_plan.id,
                PlanFeatureBindingModel.feature_id == feat.id,
            )
        )
        if not binding:
            binding = PlanFeatureBindingModel(
                plan_id=canonical_plan.id,
                feature_id=feat.id,
                access_mode=AccessMode.UNLIMITED,
                is_enabled=True,
                source_origin=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            )
            db.add(binding)
            db.flush()

        binding.access_mode = AccessMode.UNLIMITED
        binding.is_enabled = True
        binding.source_origin = SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value

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

        # Assign plan to account
        db.add(
            EnterpriseAccountBillingPlanModel(
                enterprise_account_id=account.id, plan_id=legacy_plan.id
            )
        )

        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key


def _seed_reference_data() -> None:
    from app.services.billing.service import BillingService

    BillingService.reset_subscription_status_cache()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db)

        # Seed canonical features
        from app.services.entitlement.feature_scope_registry import FEATURE_SCOPE_REGISTRY

        for feature_code in FEATURE_SCOPE_REGISTRY:
            f = db.scalar(
                select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == feature_code)
            )
            if not f:
                f = FeatureCatalogModel(
                    feature_code=feature_code,
                    feature_name=feature_code.replace("_", " ").title(),
                    is_metered=feature_code
                    in {
                        "astrologer_chat",
                        "thematic_consultation",
                        "natal_chart_long",
                        "b2b_api_access",
                    },
                    is_active=True,
                )
                db.add(f)
            else:
                f.is_active = True
        db.flush()

        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "astrologer_chat")
        )

        # Seed basic plan
        p_basic = db.scalar(select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "basic"))
        if not p_basic:
            p_basic = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
            db.add(p_basic)
            db.flush()
        else:
            p_basic.plan_name = "Basic"
            p_basic.audience = Audience.B2C
            p_basic.is_active = True

        b_basic = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == p_basic.id,
                PlanFeatureBindingModel.feature_id == feature.id,
            )
        )
        if not b_basic:
            b_basic = PlanFeatureBindingModel(
                plan_id=p_basic.id,
                feature_id=feature.id,
                access_mode=AccessMode.QUOTA,
                is_enabled=True,
            )
            db.add(b_basic)
            db.flush()
        b_basic.access_mode = AccessMode.QUOTA
        b_basic.is_enabled = True

        q_basic = db.scalar(
            select(PlanFeatureQuotaModel).where(
                PlanFeatureQuotaModel.plan_feature_binding_id == b_basic.id,
                PlanFeatureQuotaModel.quota_key == "daily",
                PlanFeatureQuotaModel.period_unit == PeriodUnit.DAY,
                PlanFeatureQuotaModel.period_value == 1,
                PlanFeatureQuotaModel.reset_mode == ResetMode.CALENDAR,
            )
        )
        if not q_basic:
            q_basic = PlanFeatureQuotaModel(
                plan_feature_binding_id=b_basic.id,
                quota_key="daily",
                quota_limit=5,
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
            db.add(q_basic)

        q_basic.quota_limit = 5

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

    # Inject active subscription directly
    with open_app_test_db_session() as db:
        from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
        from app.infra.db.models.stripe_billing import StripeBillingProfileModel
        from app.infra.db.models.user import UserModel
        from app.services.billing.service import BillingService

        BillingService.ensure_default_plans(db)

        user = db.query(UserModel).filter_by(email=user_email).one()
        # 1. Stripe profile
        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id=f"cus_{user.id}",
                stripe_subscription_id=f"sub_{user.id}",
                subscription_status="active",
                entitlement_plan="basic",
            )
        )
        # 2. Legacy sub record
        p_basic = db.scalar(select(BillingPlanModel).where(BillingPlanModel.code == "basic"))
        db.add(
            UserSubscriptionModel(
                user_id=user.id,
                plan_id=p_basic.id if p_basic else 1,
                status="active",
            )
        )
        db.commit()
        BillingService.reset_subscription_status_cache()

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

    entitlements_after_rotation = client.get("/v1/entitlements/me", headers=user_headers)
    assert entitlements_after_rotation.status_code == 200

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
