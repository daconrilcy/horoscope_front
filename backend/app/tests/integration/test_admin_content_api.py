from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel, RulesetParameterModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(AuditEventModel))
        db.execute(delete(EditorialTemplateVersionModel))
        db.execute(delete(ConfigTextModel))
        db.execute(delete(FeatureFlagModel))
        db.execute(delete(RulesetParameterModel))
        db.execute(delete(PredictionRulesetModel))
        db.execute(delete(BillingPlanModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_admin_and_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db, email="content-admin@test.com", password="admin-pass-123", role="admin"
        )
        db.commit()
        return auth.tokens.access_token


def test_admin_content_texts_and_feature_flags() -> None:
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}", "X-Request-Id": "rid-admin-content-1"}

    list_resp = client.get("/v1/admin/content/texts?category=paywall", headers=headers)
    assert list_resp.status_code == 200
    assert any(item["key"] == "paywall.daily.locked_section" for item in list_resp.json()["data"])

    update_resp = client.patch(
        "/v1/admin/content/texts/paywall.daily.locked_section",
        headers=headers,
        json={"value": "Nouveau texte premium."},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["value"] == "Nouveau texte premium."

    flags_resp = client.get("/v1/admin/content/feature-flags", headers=headers)
    assert flags_resp.status_code == 200
    keys = {item["key"] for item in flags_resp.json()["data"]}
    assert "paywall_experiment_copy" in keys

    toggle_resp = client.patch(
        "/v1/admin/content/feature-flags/paywall_experiment_copy",
        headers=headers,
        json={"enabled": True, "target_roles": [], "target_user_ids": []},
    )
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["data"]["enabled"] is True

    with SessionLocal() as db:
        content_event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.action == "content_text_updated")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert content_event is not None
        assert content_event.details["content_key"] == "paywall.daily.locked_section"

        flag_event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.action == "feature_flag_toggled")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert flag_event is not None
        assert flag_event.details["flag_code"] == "paywall_experiment_copy"


def test_admin_content_editorial_templates_and_calibration_rules() -> None:
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}", "X-Request-Id": "rid-admin-content-2"}

    with SessionLocal() as db:
        reference_version = ReferenceVersionModel(
            version="2026.04-ref",
            description="Reference version de test",
            is_locked=False,
        )
        db.add(reference_version)
        db.flush()
        ruleset = PredictionRulesetModel(
            version="2026.04",
            reference_version_id=reference_version.id,
        )
        db.add(ruleset)
        db.flush()
        db.add(
            RulesetParameterModel(
                ruleset_id=ruleset.id,
                param_key="scores.flat_day_threshold",
                param_value="0.45",
                data_type="float",
            )
        )
        db.commit()

    templates_resp = client.get("/v1/admin/content/editorial-templates", headers=headers)
    assert templates_resp.status_code == 200
    template_code = templates_resp.json()["data"][0]["template_code"]

    detail_resp = client.get(
        f"/v1/admin/content/editorial-templates/{template_code}",
        headers=headers,
    )
    assert detail_resp.status_code == 200
    active_version_id = detail_resp.json()["data"]["active_version_id"]

    create_resp = client.post(
        f"/v1/admin/content/editorial-templates/{template_code}/versions",
        headers=headers,
        json={
            "title": "Daily overview updated",
            "content": "<intro>\n<advice>\n<cta>",
            "expected_tags": ["intro", "advice", "cta"],
            "example_render": "Nouvelle structure",
        },
    )
    assert create_resp.status_code == 200
    created_payload = create_resp.json()["data"]
    assert created_payload["active_version_id"] != active_version_id
    rollback_target_id = next(
        version["id"]
        for version in created_payload["versions"]
        if version["version_number"] == 1
    )

    rollback_resp = client.post(
        f"/v1/admin/content/editorial-templates/{template_code}/rollback",
        headers=headers,
        json={"version_id": rollback_target_id},
    )
    assert rollback_resp.status_code == 200
    assert rollback_resp.json()["data"]["active_version_id"] == rollback_target_id

    rules_resp = client.get("/v1/admin/content/calibration-rules", headers=headers)
    assert rules_resp.status_code == 200
    assert rules_resp.json()["data"][0]["rule_code"] == "scores.flat_day_threshold"

    update_rule_resp = client.patch(
        "/v1/admin/content/calibration-rules/scores.flat_day_threshold",
        headers=headers,
        json={"value": "0.55"},
    )
    assert update_rule_resp.status_code == 200
    assert update_rule_resp.json()["data"]["value"] == "0.55"

    with SessionLocal() as db:
        template_event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.action == "editorial_template_updated")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert template_event is not None
        assert template_event.details["template_code"] == template_code

        calibration_event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.action == "calibration_rule_updated")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert calibration_event is not None
        assert calibration_event.details["rule_code"] == "scores.flat_day_threshold"


def test_admin_content_rejects_invalid_calibration_value_and_noop_rollback() -> None:
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}", "X-Request-Id": "rid-admin-content-3"}

    with SessionLocal() as db:
        reference_version = ReferenceVersionModel(
            version="2026.04-ref",
            description="Reference version de test",
            is_locked=False,
        )
        db.add(reference_version)
        db.flush()
        ruleset = PredictionRulesetModel(
            version="2026.04",
            reference_version_id=reference_version.id,
        )
        db.add(ruleset)
        db.flush()
        db.add(
            RulesetParameterModel(
                ruleset_id=ruleset.id,
                param_key="scores.flat_day_threshold",
                param_value="0.45",
                data_type="float",
            )
        )
        db.commit()

    templates_resp = client.get("/v1/admin/content/editorial-templates", headers=headers)
    template_code = templates_resp.json()["data"][0]["template_code"]
    detail_resp = client.get(
        f"/v1/admin/content/editorial-templates/{template_code}",
        headers=headers,
    )
    create_resp = client.post(
        f"/v1/admin/content/editorial-templates/{template_code}/versions",
        headers=headers,
        json={
            "title": "Daily overview updated",
            "content": "<intro>\n<advice>\n<cta>",
            "expected_tags": ["intro", "advice", "cta"],
            "example_render": "Nouvelle structure",
        },
    )
    assert create_resp.status_code == 200
    active_version_id = create_resp.json()["data"]["active_version_id"]

    rollback_resp = client.post(
        f"/v1/admin/content/editorial-templates/{template_code}/rollback",
        headers=headers,
        json={"version_id": active_version_id},
    )
    assert rollback_resp.status_code == 200
    assert rollback_resp.json()["data"]["active_version_id"] == active_version_id

    invalid_rule_resp = client.patch(
        "/v1/admin/content/calibration-rules/scores.flat_day_threshold",
        headers=headers,
        json={"value": {"not": "a-float"}},
    )
    assert invalid_rule_resp.status_code == 422
    assert invalid_rule_resp.json()["error"]["code"] == "invalid_calibration_rule_value"
