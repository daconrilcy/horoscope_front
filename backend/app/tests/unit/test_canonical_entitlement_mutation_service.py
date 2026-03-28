from __future__ import annotations

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.infra.db.base import Base
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
from app.services.canonical_entitlement_mutation_service import (
    CanonicalEntitlementMutationService,
    CanonicalMutationValidationError,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def b2c_plan(db):
    plan = PlanCatalogModel(
        plan_code="basic",
        plan_name="Basic",
        audience=Audience.B2C,
        is_active=True,
        source_type="manual",
    )
    db.add(plan)
    db.flush()
    return plan


@pytest.fixture()
def b2b_plan(db):
    plan = PlanCatalogModel(
        plan_code="enterprise",
        plan_name="Enterprise",
        audience=Audience.B2B,
        is_active=True,
        source_type="manual",
    )
    db.add(plan)
    db.flush()
    return plan


@pytest.fixture()
def chat_feature(db):
    feature = FeatureCatalogModel(
        feature_code="astrologer_chat",
        feature_name="Chat",
        is_metered=True,
        is_active=True,
    )
    db.add(feature)
    db.flush()
    return feature


def test_upsert_creates_binding_and_quotas_nominal(db, b2c_plan, chat_feature):
    # GIVEN
    quotas = [
        {
            "quota_key": "messages",
            "quota_limit": 10,
            "period_unit": PeriodUnit.DAY,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        }
    ]

    # WHEN
    binding = CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        quotas=quotas,
        source_origin=SourceOrigin.MANUAL,
    )

    # THEN
    assert binding.id is not None
    assert binding.plan_id == b2c_plan.id
    assert binding.feature_id == chat_feature.id
    assert binding.access_mode == AccessMode.QUOTA

    saved_quotas = db.scalars(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
        )
    ).all()
    assert len(saved_quotas) == 1
    assert saved_quotas[0].quota_key == "messages"
    assert saved_quotas[0].quota_limit == 10


def test_upsert_updates_existing_binding(db, b2c_plan, chat_feature):
    # GIVEN: existing binding
    existing_binding = PlanFeatureBindingModel(
        plan_id=b2c_plan.id,
        feature_id=chat_feature.id,
        is_enabled=True,
        access_mode=AccessMode.UNLIMITED,
        source_origin=SourceOrigin.MANUAL,
    )
    db.add(existing_binding)
    db.flush()

    # WHEN: update to QUOTA
    quotas = [
        {
            "quota_key": "messages",
            "quota_limit": 5,
            "period_unit": PeriodUnit.DAY,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        }
    ]
    binding = CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        quotas=quotas,
        source_origin=SourceOrigin.MIGRATED_FROM_BILLING_PLAN,
    )

    # THEN
    assert binding.id == existing_binding.id
    assert binding.access_mode == AccessMode.QUOTA
    assert binding.source_origin == SourceOrigin.MIGRATED_FROM_BILLING_PLAN


def test_upsert_replaces_stale_quotas(db, b2c_plan, chat_feature):
    # GIVEN: existing binding with 2 quotas
    binding = PlanFeatureBindingModel(
        plan_id=b2c_plan.id,
        feature_id=chat_feature.id,
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        source_origin=SourceOrigin.MANUAL,
    )
    db.add(binding)
    db.flush()
    q1 = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="q1",
        quota_limit=1,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        source_origin=SourceOrigin.MANUAL,
    )
    q2 = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="q2",
        quota_limit=2,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        source_origin=SourceOrigin.MANUAL,
    )
    db.add_all([q1, q2])
    db.flush()

    # WHEN: replace with a single new quota
    new_quotas = [
        {
            "quota_key": "q3",
            "quota_limit": 3,
            "period_unit": PeriodUnit.DAY,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        }
    ]
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        quotas=new_quotas,
        source_origin=SourceOrigin.MANUAL,
    )

    # THEN: only q3 remains
    quotas = db.scalars(
        select(PlanFeatureQuotaModel).where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
        )
    ).all()
    assert len(quotas) == 1
    assert quotas[0].quota_key == "q3"


def test_validation_fails_unknown_feature_code(db, b2c_plan):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="unknown_feature",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "absent de FEATURE_SCOPE_REGISTRY" in str(excinfo.value)


def test_validation_fails_feature_absent_from_catalog(db, b2c_plan):
    # This feature is in registry but not in DB
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="natal_chart_short",  # In registry
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "absent de feature_catalog" in str(excinfo.value)


def test_validation_fails_feature_inactive_in_catalog(db, b2c_plan, chat_feature):
    # GIVEN
    chat_feature.is_active = False
    db.flush()

    # WHEN/THEN
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "is_active=False" in str(excinfo.value)


def test_validation_fails_b2b_feature_on_b2c_plan(db, b2c_plan):
    # Assuming 'b2b_api_access' is a B2B feature in registry
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        # We need the feature to exist in catalog too to reach audience check
        f = FeatureCatalogModel(
            feature_code="b2b_api_access", feature_name="B2B API", is_active=True
        )
        db.add(f)
        db.flush()

        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="b2b_api_access",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "ne peut être bindée qu'à un plan B2B" in str(excinfo.value)


def test_validation_fails_b2c_feature_on_b2b_plan(db, b2b_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2b_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "ne peut être bindée qu'à un plan B2C" in str(excinfo.value)


def test_validation_fails_quota_mode_without_quotas(db, b2c_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.QUOTA,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "requiert au moins un quota" in str(excinfo.value)


def test_validation_fails_quota_mode_with_non_positive_quota_limit(db, b2c_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.QUOTA,
            quotas=[
                {
                    "quota_key": "messages",
                    "quota_limit": 0,
                    "period_unit": PeriodUnit.DAY,
                    "period_value": 1,
                    "reset_mode": ResetMode.CALENDAR,
                }
            ],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "quota_limit > 0" in str(excinfo.value)


def test_validation_fails_unlimited_with_quotas(db, b2c_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[
                {
                    "quota_key": "msg",
                    "quota_limit": 10,
                    "period_unit": PeriodUnit.DAY,
                    "period_value": 1,
                    "reset_mode": ResetMode.CALENDAR,
                }
            ],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "ne doit pas avoir de quotas" in str(excinfo.value)


def test_validation_fails_disabled_with_quotas(db, b2c_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=False,
            access_mode=AccessMode.DISABLED,
            quotas=[
                {
                    "quota_key": "msg",
                    "quota_limit": 10,
                    "period_unit": PeriodUnit.DAY,
                    "period_value": 1,
                    "reset_mode": ResetMode.CALENDAR,
                }
            ],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "ne doit pas avoir de quotas" in str(excinfo.value)


def test_validation_fails_disabled_with_is_enabled_true(db, b2c_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.DISABLED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "requiert is_enabled=False" in str(excinfo.value)


def test_validation_fails_quota_with_is_enabled_false(db, b2c_plan, chat_feature):
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=False,
            access_mode=AccessMode.QUOTA,
            quotas=[
                {
                    "quota_key": "msg",
                    "quota_limit": 10,
                    "period_unit": PeriodUnit.DAY,
                    "period_value": 1,
                    "reset_mode": ResetMode.CALENDAR,
                }
            ],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "requiert is_enabled=True" in str(excinfo.value)


def test_validation_aggregates_multiple_errors(db, b2b_plan):
    # GIVEN: B2C feature on B2B plan + DISABLED with is_enabled=True
    with pytest.raises(CanonicalMutationValidationError) as excinfo:
        # Need feature in catalog
        f = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat", is_active=True)
        db.add(f)
        db.flush()

        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2b_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.DISABLED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )
    assert "ne peut être bindée qu'à un plan B2C" in str(excinfo.value)
    assert "requiert is_enabled=False" in str(excinfo.value)


def test_no_partial_write_on_validation_error(db, b2c_plan, chat_feature):
    # GIVEN
    initial_count = db.scalar(select(func.count(PlanFeatureBindingModel.id))) or 0

    # WHEN: call with multiple errors
    with pytest.raises(CanonicalMutationValidationError):
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.DISABLED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
        )

    # THEN: no binding created
    final_count = db.scalar(select(func.count(PlanFeatureBindingModel.id))) or 0
    assert final_count == initial_count
