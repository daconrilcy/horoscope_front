import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import (
    PlanCatalogModel,
    FeatureCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    FeatureUsageCounterModel,
    Audience,
    AccessMode,
    PeriodUnit,
    ResetMode,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from scripts.seed_product_entitlements import seed

@pytest.fixture(autouse=True)
def run_around_tests():
    # Ensure tables are fresh
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_seeded_data_presence():
    seed()
    with SessionLocal() as db:
        plans = db.execute(select(PlanCatalogModel)).scalars().all()
        assert len(plans) == 4
        plan_codes = {p.plan_code for p in plans}
        assert plan_codes == {"free", "trial", "basic", "premium"}

        features = db.execute(select(FeatureCatalogModel)).scalars().all()
        assert len(features) == 4
        feature_codes = {f.feature_code for f in features}
        assert feature_codes == {"natal_chart_short", "natal_chart_long", "astrologer_chat", "thematic_consultation"}

def test_plan_code_uniqueness():
    with SessionLocal() as db:
        db.add(PlanCatalogModel(plan_code="unique", plan_name="Unique", audience=Audience.B2C))
        db.commit()
        
        db.add(PlanCatalogModel(plan_code="unique", plan_name="Duplicate", audience=Audience.B2C))
        with pytest.raises(IntegrityError):
            db.commit()

def test_feature_code_uniqueness():
    with SessionLocal() as db:
        db.add(FeatureCatalogModel(feature_code="feat", feature_name="Feat"))
        db.commit()
        
        db.add(FeatureCatalogModel(feature_code="feat", feature_name="Feat 2"))
        with pytest.raises(IntegrityError):
            db.commit()

def test_plan_feature_binding_uniqueness():
    with SessionLocal() as db:
        p = PlanCatalogModel(plan_code="p1", plan_name="P1", audience=Audience.B2C)
        f = FeatureCatalogModel(feature_code="f1", feature_name="F1")
        db.add_all([p, f])
        db.commit()
        
        db.add(PlanFeatureBindingModel(plan_id=p.id, feature_id=f.id, access_mode=AccessMode.UNLIMITED))
        db.commit()
        
        db.add(PlanFeatureBindingModel(plan_id=p.id, feature_id=f.id, access_mode=AccessMode.QUOTA))
        with pytest.raises(IntegrityError):
            db.commit()

def test_quota_constraints():
    with SessionLocal() as db:
        p = PlanCatalogModel(plan_code="p1", plan_name="P1", audience=Audience.B2C)
        f = FeatureCatalogModel(feature_code="f1", feature_name="F1")
        db.add_all([p, f])
        db.commit()
        
        b = PlanFeatureBindingModel(plan_id=p.id, feature_id=f.id, access_mode=AccessMode.QUOTA)
        db.add(b)
        db.commit()
        
        # quota_limit > 0
        db.add(PlanFeatureQuotaModel(
            plan_feature_binding_id=b.id,
            quota_key="q",
            quota_limit=0,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # period_value >= 1
        db.add(PlanFeatureQuotaModel(
            plan_feature_binding_id=b.id,
            quota_key="q",
            quota_limit=10,
            period_unit=PeriodUnit.DAY,
            period_value=0,
            reset_mode=ResetMode.CALENDAR
        ))
        with pytest.raises(IntegrityError):
            db.commit()

def test_usage_counter_uniqueness():
    from app.infra.db.models.user import UserModel
    with SessionLocal() as db:
        u = UserModel(email="test@example.com", password_hash="hash", role="user")
        db.add(u)
        db.commit()
        
        now = datetime.now(timezone.utc)
        counter1 = FeatureUsageCounterModel(
            user_id=u.id,
            feature_code="feat",
            quota_key="q",
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
            window_start=now,
            used_count=1
        )
        db.add(counter1)
        db.commit()
        
        counter2 = FeatureUsageCounterModel(
            user_id=u.id,
            feature_code="feat",
            quota_key="q",
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
            window_start=now,
            used_count=2
        )
        db.add(counter2)
        with pytest.raises(IntegrityError):
            db.commit()

def test_variant_code_seeding():
    seed()
    with SessionLocal() as db:
        def get_variant(plan_code, feature_code):
            return db.execute(
                select(PlanFeatureBindingModel.variant_code)
                .join(PlanCatalogModel, PlanFeatureBindingModel.plan_id == PlanCatalogModel.id)
                .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
                .where(PlanCatalogModel.plan_code == plan_code, FeatureCatalogModel.feature_code == feature_code)
            ).scalar_one_or_none()

        assert get_variant("trial", "natal_chart_long") == "single_astrologer"
        assert get_variant("basic", "natal_chart_long") == "single_astrologer"
        assert get_variant("premium", "natal_chart_long") == "multi_astrologer"
