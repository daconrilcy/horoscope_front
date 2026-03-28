from __future__ import annotations

import pytest
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    ResetMode,
    SourceOrigin,
)
from app.services.canonical_entitlement_mutation_service import (
    CanonicalEntitlementMutationService,
    CanonicalMutationContext,
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


_TEST_CONTEXT = CanonicalMutationContext(
    actor_type="script",
    actor_identifier="test_script.py",
    request_id="req-123",
)


def test_audit_row_created_on_binding_create(db, b2c_plan, chat_feature):
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
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        quotas=quotas,
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )

    # THEN
    audits = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits) == 1
    audit = audits[0]
    assert audit.operation == "upsert_plan_feature_configuration"
    assert audit.plan_id == b2c_plan.id
    assert audit.feature_code == "astrologer_chat"


def test_audit_row_created_on_binding_update(db, b2c_plan, chat_feature):
    # GIVEN: existing binding
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.UNLIMITED,
        quotas=[],
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )
    db.flush()
    # Clear first audit
    db.execute(delete(CanonicalEntitlementMutationAuditModel))
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
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        quotas=quotas,
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )

    # THEN
    audits = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits) == 1
    audit = audits[0]
    assert audit.before_payload["access_mode"] == "unlimited"
    assert audit.after_payload["access_mode"] == "quota"


def test_audit_row_contains_before_and_after_payload(db, b2c_plan, chat_feature):
    # WHEN
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.UNLIMITED,
        quotas=[],
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )

    # THEN
    audit = db.scalars(select(CanonicalEntitlementMutationAuditModel)).one()
    assert audit.before_payload == {}
    assert audit.after_payload["is_enabled"] is True
    assert audit.after_payload["access_mode"] == "unlimited"
    assert audit.after_payload["quotas"] == []


def test_audit_row_contains_actor_context(db, b2c_plan, chat_feature):
    # WHEN
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.UNLIMITED,
        quotas=[],
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )

    # THEN
    audit = db.scalars(select(CanonicalEntitlementMutationAuditModel)).one()
    assert audit.actor_type == "script"
    assert audit.actor_identifier == "test_script.py"
    assert audit.request_id == "req-123"


def test_no_audit_row_on_validation_error(db, b2c_plan, chat_feature):
    # WHEN: call with error
    with pytest.raises(CanonicalMutationValidationError):
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.DISABLED,  # Error: is_enabled=True with DISABLED
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
            mutation_context=_TEST_CONTEXT,
        )

    # THEN
    audits = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits) == 0


def test_no_audit_row_on_dry_run(db, b2c_plan, chat_feature):
    # WHEN: simulate dry_run via savepoint rollback (as done in b2b_entitlement_repair_service)
    with db.begin_nested() as sp:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
            mutation_context=_TEST_CONTEXT,
        )
        # Inside savepoint, audit exists
        assert len(db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()) == 1
        sp.rollback()

    # THEN: outside savepoint, audit is gone
    audits = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits) == 0


def test_no_audit_row_when_no_effective_change(db, b2c_plan, chat_feature):
    # GIVEN: existing state
    quotas = [
        {
            "quota_key": "messages",
            "quota_limit": 10,
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
        quotas=quotas,
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )
    db.flush()
    audits_before = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits_before) == 1

    # WHEN: call with same state
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db,
        plan=b2c_plan,
        feature_code="astrologer_chat",
        is_enabled=True,
        access_mode=AccessMode.QUOTA,
        quotas=quotas,
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )

    # THEN: no new audit row
    audits_after = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits_after) == 1


def test_audit_row_is_rolled_back_with_transaction(db, b2c_plan, chat_feature):
    # WHEN: start transaction, upsert, then rollback
    with db.begin_nested() as sp:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=b2c_plan,
            feature_code="astrologer_chat",
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            quotas=[],
            source_origin=SourceOrigin.MANUAL,
            mutation_context=_TEST_CONTEXT,
        )
        # In-transaction audit exists
        assert len(db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()) == 1
        sp.rollback()

    # THEN: audit row is gone
    assert len(db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()) == 0
