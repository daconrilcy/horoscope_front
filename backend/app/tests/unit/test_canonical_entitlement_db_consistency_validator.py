import pytest
from sqlalchemy import create_engine
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
)
from app.services.canonical_entitlement.shared.db_consistency_validator import (
    CanonicalEntitlementDbConsistencyError,
    CanonicalEntitlementDbConsistencyValidator,
)
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def _seed_consistent_db(db: Session) -> None:
    mandatory_metered_features = {
        "astrologer_chat",
        "thematic_consultation",
        "natal_chart_long",
        "b2b_api_access",
    }
    features = []
    for feature_code in FEATURE_SCOPE_REGISTRY:
        features.append(
            FeatureCatalogModel(
                feature_code=feature_code,
                feature_name=feature_code.replace("_", " ").title(),
                is_metered=feature_code in mandatory_metered_features,
                is_active=True,
            )
        )
    db.add_all(features)
    db.flush()

    b2c_plan = PlanCatalogModel(
        plan_code="premium",
        plan_name="Premium",
        audience=Audience.B2C,
        is_active=True,
    )
    b2b_plan = PlanCatalogModel(
        plan_code="enterprise",
        plan_name="Enterprise",
        audience=Audience.B2B,
        is_active=True,
    )
    db.add_all([b2c_plan, b2b_plan])
    db.flush()

    # B2C feature bound to B2C plan (QUOTA with quota)
    chat_feature = next(f for f in features if f.feature_code == "astrologer_chat")
    binding_b2c = PlanFeatureBindingModel(
        plan_id=b2c_plan.id,
        feature_id=chat_feature.id,
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
    )
    db.add(binding_b2c)
    db.flush()
    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding_b2c.id,
            quota_key="daily",
            quota_limit=5,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
    )

    # B2B feature bound to B2B plan (UNLIMITED, no quota)
    b2b_feature = next(f for f in features if f.feature_code == "b2b_api_access")
    db.add(
        PlanFeatureBindingModel(
            plan_id=b2b_plan.id,
            feature_id=b2b_feature.id,
            access_mode=AccessMode.UNLIMITED,
            is_enabled=True,
        )
    )
    db.commit()


def test_validator_ok_nominal(db):
    _seed_consistent_db(db)
    CanonicalEntitlementDbConsistencyValidator.validate(db)


def test_validator_fails_feature_missing_from_catalog(db):
    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "absent de feature_catalog" in str(excinfo.value)


def test_validator_fails_feature_inactive_in_catalog(db):
    _seed_consistent_db(db)
    feature = db.query(FeatureCatalogModel).filter_by(feature_code="astrologer_chat").one()
    feature.is_active = False
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "is_active=False" in str(excinfo.value)


def test_validator_fails_b2b_feature_bound_to_b2c_plan(db):
    _seed_consistent_db(db)
    b2b_feature = db.query(FeatureCatalogModel).filter_by(feature_code="b2b_api_access").one()
    b2c_plan = db.query(PlanCatalogModel).filter_by(audience=Audience.B2C).first()

    db.add(
        PlanFeatureBindingModel(
            plan_id=b2c_plan.id,
            feature_id=b2b_feature.id,
            access_mode=AccessMode.UNLIMITED,
            is_enabled=True,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "attendu audience=b2b" in str(excinfo.value)


def test_validator_fails_b2c_feature_bound_to_b2b_plan(db):
    _seed_consistent_db(db)
    b2c_feature = db.query(FeatureCatalogModel).filter_by(feature_code="astrologer_chat").one()
    b2b_plan = db.query(PlanCatalogModel).filter_by(audience=Audience.B2B).first()

    db.add(
        PlanFeatureBindingModel(
            plan_id=b2b_plan.id,
            feature_id=b2c_feature.id,
            access_mode=AccessMode.UNLIMITED,
            is_enabled=True,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "attendu audience=b2c" in str(excinfo.value)


def test_validator_fails_quota_binding_without_quota(db):
    _seed_consistent_db(db)
    feature = db.query(FeatureCatalogModel).filter_by(feature_code="thematic_consultation").one()
    b2c_plan = db.query(PlanCatalogModel).filter_by(audience=Audience.B2C).first()

    db.add(
        PlanFeatureBindingModel(
            plan_id=b2c_plan.id,
            feature_id=feature.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "n'a aucun quota dans plan_feature_quotas" in str(excinfo.value)


def test_validator_fails_unlimited_binding_with_quota(db):
    _seed_consistent_db(db)
    binding = db.query(PlanFeatureBindingModel).filter_by(access_mode=AccessMode.UNLIMITED).first()
    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="parasite",
            quota_limit=10,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "a 1 quota(s) parasite(s)" in str(excinfo.value)


def test_validator_fails_disabled_binding_with_quota(db):
    _seed_consistent_db(db)
    feature = db.query(FeatureCatalogModel).filter_by(feature_code="thematic_consultation").one()
    b2c_plan = db.query(PlanCatalogModel).filter_by(audience=Audience.B2C).first()

    binding = PlanFeatureBindingModel(
        plan_id=b2c_plan.id,
        feature_id=feature.id,
        access_mode=AccessMode.DISABLED,
        is_enabled=True,
    )
    db.add(binding)
    db.flush()
    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="parasite",
            quota_limit=10,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "a 1 quota(s) parasite(s)" in str(excinfo.value)


def test_validator_fails_bound_feature_not_registered(db):
    _seed_consistent_db(db)
    unregistered_feature = FeatureCatalogModel(
        feature_code="not_in_registry",
        feature_name="Not Registered",
        is_metered=False,
        is_active=True,
    )
    db.add(unregistered_feature)
    b2c_plan = db.query(PlanCatalogModel).filter_by(audience=Audience.B2C).first()
    db.flush()

    db.add(
        PlanFeatureBindingModel(
            plan_id=b2c_plan.id,
            feature_id=unregistered_feature.id,
            access_mode=AccessMode.UNLIMITED,
            is_enabled=True,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "not_in_registry" in str(excinfo.value)
    assert "absent de FEATURE_SCOPE_REGISTRY" in str(excinfo.value)


def test_validator_fails_metered_feature_not_registered(db):
    _seed_consistent_db(db)
    unregistered_metered = FeatureCatalogModel(
        feature_code="unregistered_metered",
        feature_name="Unregistered Metered",
        is_metered=True,
        is_active=True,
    )
    db.add(unregistered_metered)
    b2c_plan = db.query(PlanCatalogModel).filter_by(audience=Audience.B2C).first()
    db.flush()
    db.add(
        PlanFeatureBindingModel(
            plan_id=b2c_plan.id,
            feature_id=unregistered_metered.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
    )
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "unregistered_metered" in str(excinfo.value)
    assert "absent de FEATURE_SCOPE_REGISTRY" in str(excinfo.value)


def test_validator_ignores_unregistered_metered_feature_without_quota_entitlement(db):
    _seed_consistent_db(db)
    db.add(
        FeatureCatalogModel(
            feature_code="unregistered_metered",
            feature_name="Unregistered Metered",
            is_metered=True,
            is_active=True,
        )
    )
    db.commit()

    CanonicalEntitlementDbConsistencyValidator.validate(db)


def test_validator_aggregates_multiple_errors(db):
    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)

    error_msg = str(excinfo.value)
    assert error_msg.count("absent de feature_catalog") == len(FEATURE_SCOPE_REGISTRY)
