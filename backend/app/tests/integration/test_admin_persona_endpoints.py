from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmUseCaseConfigModel
from app.infra.db.models.user import UserModel
from app.main import app
from app.services.auth_service import AuthService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        db.execute(delete(LlmPersonaModel))
        db.execute(delete(LlmUseCaseConfigModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_admin_and_token() -> str:
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db, email="admin@test.com", password="admin-pass-123", role="admin"
        )
        db.commit()
        return auth.tokens.access_token


def test_admin_persona_crud_lifecycle() -> None:
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create
    create_resp = client.post(
        "/v1/admin/llm/personas",
        headers=headers,
        json={
            "name": "Luna",
            "description": "Bienveillante",
            "tone": "warm",
            "verbosity": "medium",
            "style_markers": ["tutoiement"],
            "boundaries": ["pas de fatalisme"],
            "formatting": {"sections": True, "bullets": False, "emojis": False},
        },
    )
    assert create_resp.status_code == 200
    persona_id = create_resp.json()["data"]["id"]
    assert create_resp.json()["data"]["name"] == "Luna"

    # 2. List
    list_resp = client.get("/v1/admin/llm/personas", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 1

    # 3. Update
    update_resp = client.patch(
        f"/v1/admin/llm/personas/{persona_id}",
        headers=headers,
        json={"tone": "mystical", "name": "Luna Mystica"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["tone"] == "mystical"
    assert update_resp.json()["data"]["name"] == "Luna Mystica"

    # 4. Legacy association endpoint is frozen
    # Create use case first to verify canonical governance refusal on an existing key.
    with open_app_test_db_session() as db:
        uc = LlmUseCaseConfigModel(
            key="guidance_daily",
            display_name="Guidance",
            description="Daily guidance",
        )
        db.add(uc)
        db.commit()

    assoc_resp = client.patch(
        "/v1/admin/llm/use-cases/guidance_daily/persona",
        headers=headers,
        json={"persona_id": persona_id},
    )
    assert assoc_resp.status_code == 409
    assert assoc_resp.json()["error"]["code"] == "forbidden_feature"

    # 5. Disable (Delete)
    del_resp = client.delete(f"/v1/admin/llm/personas/{persona_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["enabled"] is False


def test_admin_persona_rbac() -> None:
    _cleanup_tables()
    # Register regular user
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db, email="user@test.com", password="user-pass-123", role="user"
        )
        db.commit()
        user_token = auth.tokens.access_token

    response = client.get(
        "/v1/admin/llm/personas", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_admin_persona_detail_and_deactivation_audit() -> None:
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}", "X-Request-Id": "rid-persona-detail-1"}

    create_resp = client.post(
        "/v1/admin/llm/personas",
        headers=headers,
        json={
            "name": "Luna",
            "description": "Bienveillante",
            "tone": "warm",
            "verbosity": "medium",
            "style_markers": ["tutoiement"],
            "boundaries": ["pas de fatalisme"],
            "formatting": {"sections": True, "bullets": False, "emojis": False},
        },
    )
    persona_id = create_resp.json()["data"]["id"]

    with open_app_test_db_session() as db:
        db.add(
            BillingPlanModel(
                code="premium",
                display_name="Premium",
                monthly_price_cents=1990,
                currency="EUR",
                daily_message_limit=50,
            )
        )
        db.flush()
        user = UserModel(
            email="persona-user@example.com",
            password_hash="x",
            role="user",
            default_astrologer_id=persona_id,
        )
        db.add(user)
        db.flush()
        plan = db.scalar(
            select(BillingPlanModel).where(BillingPlanModel.code == "premium").limit(1)
        )
        assert plan is not None
        db.add(UserSubscriptionModel(user_id=user.id, plan_id=plan.id, status="active"))
        db.commit()

    detail_resp = client.get(f"/v1/admin/llm/personas/{persona_id}", headers=headers)
    assert detail_resp.status_code == 200
    payload = detail_resp.json()["data"]
    assert payload["persona"]["name"] == "Luna"
    assert payload["use_cases"] == []
    assert payload["affected_users_count"] == 1

    deactivate_resp = client.patch(
        f"/v1/admin/llm/personas/{persona_id}",
        headers=headers,
        json={"enabled": False},
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["data"]["enabled"] is False

    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-persona-detail-1")
            .where(AuditEventModel.action == "persona_deactivated")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert event is not None
        assert event.details["persona_name"] == "Luna"
