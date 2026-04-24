import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    engine.dispose()

    yield db_url

    # Disposal is important on Windows
    if os.path.exists(path):
        try:
            os.unlink(path)
        except PermissionError:
            pass  # fallback if still locked


@pytest.fixture
def db_session_temp(temp_db):
    engine = create_engine(temp_db)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def seed_audits(db_session_temp: Session):
    now = datetime.now(timezone.utc)

    # Item 1: High risk, 5h ago -> Overdue (SLA 4h)
    a1 = CanonicalEntitlementMutationAuditModel(
        operation="update",
        plan_id=1,
        plan_code_snapshot="p1",
        feature_code="f1",
        actor_type="user",
        actor_identifier="u1",
        source_origin="test_script",
        before_payload={"is_enabled": True},
        after_payload={"is_enabled": False},  # High risk
        occurred_at=now - timedelta(hours=5),
        request_id="req1",
    )

    # Item 2: Medium risk, 1h ago -> Within SLA (SLA 24h)
    a2 = CanonicalEntitlementMutationAuditModel(
        operation="update",
        plan_id=1,
        plan_code_snapshot="p1",
        feature_code="f1",
        actor_type="user",
        actor_identifier="u1",
        source_origin="test_script",
        before_payload={"variant_code": "v1"},
        after_payload={"variant_code": "v2"},  # Medium risk
        occurred_at=now - timedelta(hours=1),
        request_id="req2",
    )

    db_session_temp.add_all([a1, a2])
    db_session_temp.commit()
    return [a1, a2]


def test_script_dry_run_no_persisted_rows(temp_db, db_session_temp: Session, seed_audits):
    env = os.environ.copy()
    env["OPS_REVIEW_QUEUE_ALERTS_ENABLED"] = "True"
    env["DATABASE_URL"] = temp_db

    script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_ops_review_queue_alerts.py"
    res = subprocess.run(
        [sys.executable, str(script_path), "--dry-run"], capture_output=True, text=True, env=env
    )

    assert res.returncode == 0
    assert "emitted=1" in res.stdout
    assert "candidates=1" in res.stdout

    count = db_session_temp.query(CanonicalEntitlementMutationAlertEventModel).count()
    assert count == 0


def test_script_persists_alert_event_on_overdue(temp_db, db_session_temp: Session, seed_audits):
    env = os.environ.copy()
    env["OPS_REVIEW_QUEUE_ALERTS_ENABLED"] = "True"
    env["DATABASE_URL"] = temp_db

    script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_ops_review_queue_alerts.py"
    res = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True, env=env
    )

    assert res.returncode == 0
    assert "emitted=1" in res.stdout

    event = db_session_temp.query(CanonicalEntitlementMutationAlertEventModel).first()
    assert event.audit_id == seed_audits[0].id
    assert event.alert_kind == "sla_overdue"


def test_script_no_duplicate_alert_on_second_run(temp_db, db_session_temp: Session, seed_audits):
    env = os.environ.copy()
    env["OPS_REVIEW_QUEUE_ALERTS_ENABLED"] = "True"
    env["DATABASE_URL"] = temp_db

    script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_ops_review_queue_alerts.py"

    # First run
    subprocess.run([sys.executable, str(script_path)], env=env)

    # Second run
    res = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True, env=env
    )

    assert "emitted=0" in res.stdout
    assert "skipped_duplicate=1" in res.stdout


def test_script_exit_code_1_on_delivery_failure(temp_db, db_session_temp: Session, seed_audits):
    env = os.environ.copy()
    env["OPS_REVIEW_QUEUE_ALERTS_ENABLED"] = "True"
    env["DATABASE_URL"] = temp_db
    env["OPS_REVIEW_QUEUE_ALERT_WEBHOOK_URL"] = "http://localhost:1"  # Should fail fast

    script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_ops_review_queue_alerts.py"
    res = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True, env=env
    )

    assert res.returncode == 1
    assert "failed=1" in res.stdout

    event = db_session_temp.query(CanonicalEntitlementMutationAlertEventModel).first()
    assert event.delivery_status == "failed"


def test_script_limit_prefers_oldest_pending_item(temp_db, db_session_temp: Session):
    now = datetime.now(timezone.utc)
    older_overdue = CanonicalEntitlementMutationAuditModel(
        operation="update",
        plan_id=1,
        plan_code_snapshot="p1",
        feature_code="f1",
        actor_type="user",
        actor_identifier="u1",
        source_origin="test_script",
        before_payload={"is_enabled": True},
        after_payload={"is_enabled": False},
        occurred_at=now - timedelta(hours=5),
        request_id="req-older",
    )
    newer_due_soon = CanonicalEntitlementMutationAuditModel(
        operation="update",
        plan_id=1,
        plan_code_snapshot="p1",
        feature_code="f1",
        actor_type="user",
        actor_identifier="u1",
        source_origin="test_script",
        before_payload={"is_enabled": True},
        after_payload={"is_enabled": False},
        occurred_at=now - timedelta(hours=3, minutes=30),
        request_id="req-newer",
    )
    db_session_temp.add_all([older_overdue, newer_due_soon])
    db_session_temp.commit()

    env = os.environ.copy()
    env["OPS_REVIEW_QUEUE_ALERTS_ENABLED"] = "True"
    env["DATABASE_URL"] = temp_db

    script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_ops_review_queue_alerts.py"
    res = subprocess.run(
        [sys.executable, str(script_path), "--limit", "1"],
        capture_output=True,
        text=True,
        env=env,
    )

    assert res.returncode == 0
    event = db_session_temp.query(CanonicalEntitlementMutationAlertEventModel).one()
    assert event.audit_id == older_overdue.id

