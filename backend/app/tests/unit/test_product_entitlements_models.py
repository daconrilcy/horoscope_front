from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.infra.db.base import Base
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
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from scripts.seed_product_entitlements import seed


@pytest.fixture(autouse=True)
def run_around_tests():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_seeded_data_presence():
    seed()
    with SessionLocal() as db:
        plans = db.execute(select(PlanCatalogModel)).scalars().all()
        assert len(plans) == 4
        assert {p.plan_code for p in plans} == {"free", "trial", "basic", "premium"}

        features = db.execute(select(FeatureCatalogModel)).scalars().all()
        assert len(features) == 4
        assert {f.feature_code for f in features} == {
            "natal_chart_short",
            "natal_chart_long",
            "astrologer_chat",
            "thematic_consultation",
        }


def test_seed_idempotence():
    seed()
    seed()
    with SessionLocal() as db:
        assert db.execute(select(PlanCatalogModel)).scalars().all()
        assert len(db.execute(select(PlanCatalogModel)).scalars().all()) == 4
        assert len(db.execute(select(FeatureCatalogModel)).scalars().all()) == 4
        assert len(db.execute(select(PlanFeatureBindingModel)).scalars().all()) == 16
        quotas = db.execute(select(PlanFeatureQuotaModel)).scalars().all()
        # trial: 2 quotas, basic: 5 quotas, premium: 5 quotas = 12 quotas
        assert len(quotas) == 12


def test_plan_code_uniqueness():
    with SessionLocal() as db:
        db.add(PlanCatalogModel(plan_code="unique", plan_name="Unique", audience=Audience.B2C))
        db.commit()

        db.add(PlanCatalogModel(plan_code="unique", plan_name="Duplicate", audience=Audience.B2C))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_feature_code_uniqueness():
    with SessionLocal() as db:
        db.add(FeatureCatalogModel(feature_code="feat", feature_name="Feat"))
        db.commit()

        db.add(FeatureCatalogModel(feature_code="feat", feature_name="Feat 2"))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_plan_feature_binding_uniqueness():
    with SessionLocal() as db:
        p = PlanCatalogModel(plan_code="p1", plan_name="P1", audience=Audience.B2C)
        f = FeatureCatalogModel(feature_code="f1", feature_name="F1")
        db.add_all([p, f])
        db.commit()

        db.add(
            PlanFeatureBindingModel(plan_id=p.id, feature_id=f.id, access_mode=AccessMode.UNLIMITED)
        )
        db.commit()

        db.add(PlanFeatureBindingModel(plan_id=p.id, feature_id=f.id, access_mode=AccessMode.QUOTA))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_quota_constraints_and_composite_uniqueness():
    with SessionLocal() as db:
        p = PlanCatalogModel(plan_code="p1", plan_name="P1", audience=Audience.B2C)
        f = FeatureCatalogModel(feature_code="f1", feature_name="F1")
        db.add_all([p, f])
        db.commit()

        b = PlanFeatureBindingModel(plan_id=p.id, feature_id=f.id, access_mode=AccessMode.QUOTA)
        db.add(b)
        db.commit()

        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b.id,
                quota_key="q",
                quota_limit=0,
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b.id,
                quota_key="q",
                quota_limit=10,
                period_unit=PeriodUnit.DAY,
                period_value=0,
                reset_mode=ResetMode.CALENDAR,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        first = PlanFeatureQuotaModel(
            plan_feature_binding_id=b.id,
            quota_key="messages",
            quota_limit=10,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(first)
        db.commit()

        duplicate = PlanFeatureQuotaModel(
            plan_feature_binding_id=b.id,
            quota_key="messages",
            quota_limit=20,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(duplicate)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        different_period = PlanFeatureQuotaModel(
            plan_feature_binding_id=b.id,
            quota_key="messages",
            quota_limit=100,
            period_unit=PeriodUnit.MONTH,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(different_period)
        db.commit()


def test_usage_counter_constraints_and_uniqueness():
    with SessionLocal() as db:
        u = UserModel(email="test2@example.com", password_hash="hash", role="user")
        db.add(u)
        db.commit()

        now = datetime.now(timezone.utc)

        db.add(
            FeatureUsageCounterModel(
                user_id=u.id,
                feature_code="feat",
                quota_key="q",
                period_unit=PeriodUnit.DAY,
                period_value=0,
                reset_mode=ResetMode.CALENDAR,
                window_start=now,
                window_end=now,
                used_count=1,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        db.add(
            FeatureUsageCounterModel(
                user_id=u.id,
                feature_code="feat",
                quota_key="q",
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=now,
                window_end=now,
                used_count=-1,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        db.add(
            FeatureUsageCounterModel(
                user_id=u.id,
                feature_code="feat",
                quota_key="q",
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=now,
                window_end=None,
                used_count=1,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        db.add(
            FeatureUsageCounterModel(
                user_id=u.id,
                feature_code="feat",
                quota_key="q",
                period_unit=PeriodUnit.LIFETIME,
                period_value=1,
                reset_mode=ResetMode.LIFETIME,
                window_start=now,
                window_end=None,
                used_count=1,
            )
        )
        db.commit()

        db.add(
            FeatureUsageCounterModel(
                user_id=u.id,
                feature_code="feat",
                quota_key="q",
                period_unit=PeriodUnit.LIFETIME,
                period_value=1,
                reset_mode=ResetMode.LIFETIME,
                window_start=now,
                window_end=None,
                used_count=2,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_variant_code_seeding():
    seed()
    with SessionLocal() as db:

        def get_variant(plan_code, feature_code):
            return db.execute(
                select(PlanFeatureBindingModel.variant_code)
                .join(PlanCatalogModel, PlanFeatureBindingModel.plan_id == PlanCatalogModel.id)
                .join(
                    FeatureCatalogModel,
                    PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id,
                )
                .where(
                    PlanCatalogModel.plan_code == plan_code,
                    FeatureCatalogModel.feature_code == feature_code,
                )
            ).scalar_one_or_none()

        assert get_variant("trial", "natal_chart_long") == "single_astrologer"
        assert get_variant("basic", "natal_chart_long") == "single_astrologer"
        assert get_variant("premium", "natal_chart_long") == "multi_astrologer"


def test_seeded_quota_shapes():
    seed()
    with SessionLocal() as db:
        rows = db.execute(
            select(
                PlanCatalogModel.plan_code,
                FeatureCatalogModel.feature_code,
                PlanFeatureQuotaModel.quota_key,
                PlanFeatureQuotaModel.quota_limit,
                PlanFeatureQuotaModel.period_unit,
                PlanFeatureQuotaModel.period_value,
                PlanFeatureQuotaModel.reset_mode,
            )
            .join(PlanFeatureBindingModel, PlanFeatureBindingModel.plan_id == PlanCatalogModel.id)
            .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
            .join(
                PlanFeatureQuotaModel,
                PlanFeatureQuotaModel.plan_feature_binding_id == PlanFeatureBindingModel.id,
            )
        ).all()

        assert (
            "trial",
            "thematic_consultation",
            "tokens",
            5000,
            PeriodUnit.WEEK,
            1,
            ResetMode.CALENDAR,
        ) in rows

        assert (
            "basic",
            "astrologer_chat",
            "tokens",
            50000,
            PeriodUnit.MONTH,
            1,
            ResetMode.CALENDAR,
        ) in rows
        assert (
            "premium",
            "astrologer_chat",
            "tokens",
            1500000,
            PeriodUnit.MONTH,
            1,
            ResetMode.CALENDAR,
        ) in rows
        assert (
            "premium",
            "thematic_consultation",
            "tokens",
            200000,
            PeriodUnit.MONTH,
            1,
            ResetMode.CALENDAR,
        ) in rows
