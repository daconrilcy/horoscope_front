import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.dependencies.auth import require_admin_user
from app.infra.db.models.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.session import SessionLocal, get_db_session
from app.main import app


async def mock_admin_user():
    return MagicMock(id=123, role="admin")


def _build_payload(**overrides):
    base = {
        "name": "natal-default",
        "feature": "natal",
        "locale": "fr-FR",
        "payload_json": {
            "chart_json": {"sun": "aries", "moon": "leo"},
            "runtime_placeholders": {"timezone": "Europe/Paris"},
        },
        "description": "Payload natal synthétique",
        "is_default": True,
        "is_active": True,
    }
    base.update(overrides)
    return base


def test_admin_llm_sample_payload_crud_list_and_recommended_default():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_ids: list[uuid.UUID] = []
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        response_1 = client.post("/v1/admin/llm/sample-payloads", json=_build_payload())
        assert response_1.status_code == 200
        item_1 = response_1.json()["data"]
        created_ids.append(uuid.UUID(item_1["id"]))
        assert item_1["feature"] == "natal"
        assert item_1["payload_json"]["chart_json"] == {"sun": "aries", "moon": "leo"}

        response_2 = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="natal-alt", is_default=False),
        )
        assert response_2.status_code == 200
        item_2 = response_2.json()["data"]
        created_ids.append(uuid.UUID(item_2["id"]))

        list_response = client.get("/v1/admin/llm/sample-payloads?feature=natal&locale=fr-FR")
        assert list_response.status_code == 200
        list_payload = list_response.json()["data"]
        assert len(list_payload["items"]) == 2
        assert "payload_json" not in list_payload["items"][0]
        assert list_payload["recommended_default_id"] == item_1["id"]

        patch_response = client.patch(
            f"/v1/admin/llm/sample-payloads/{item_2['id']}",
            json={"is_default": True},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["data"]["is_default"] is True

        reloaded_list_response = client.get(
            "/v1/admin/llm/sample-payloads?feature=natal&locale=fr-FR"
        )
        assert reloaded_list_response.status_code == 200
        reloaded_payload = reloaded_list_response.json()["data"]
        assert reloaded_payload["recommended_default_id"] == item_2["id"]

        delete_response = client.delete(f"/v1/admin/llm/sample-payloads/{item_2['id']}")
        assert delete_response.status_code == 200
        delete_payload = delete_response.json()
        assert delete_payload["data"]["id"] == item_2["id"]
        assert delete_payload["meta"]["request_id"]
    finally:
        app.dependency_overrides.clear()
        if created_ids:
            db.execute(
                delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id.in_(created_ids))
            )
            db.commit()
        db.close()


def test_admin_llm_sample_payload_post_default_switches_previous_default():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_ids: list[uuid.UUID] = []
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        response_1 = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="default-1", is_default=True),
        )
        assert response_1.status_code == 200
        item_1 = response_1.json()["data"]
        created_ids.append(uuid.UUID(item_1["id"]))

        response_2 = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="default-2", is_default=True),
        )
        assert response_2.status_code == 200
        item_2 = response_2.json()["data"]
        created_ids.append(uuid.UUID(item_2["id"]))

        detail_1 = client.get(f"/v1/admin/llm/sample-payloads/{item_1['id']}")
        assert detail_1.status_code == 200
        assert detail_1.json()["data"]["is_default"] is False

        detail_2 = client.get(f"/v1/admin/llm/sample-payloads/{item_2['id']}")
        assert detail_2.status_code == 200
        assert detail_2.json()["data"]["is_default"] is True
    finally:
        app.dependency_overrides.clear()
        if created_ids:
            db.execute(
                delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id.in_(created_ids))
            )
            db.commit()
        db.close()


def test_admin_llm_sample_payload_rejects_whitespace_only_name():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        response = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="   "),
        )
        assert response.status_code == 422
        payload = response.json()["error"]
        assert payload["code"] == "invalid_sample_payload"
        assert "whitespace-only" in payload["message"]
    finally:
        app.dependency_overrides.clear()
        db.close()


def test_admin_llm_sample_payload_patch_can_clear_description():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_id: uuid.UUID | None = None
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        create_response = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="with-description", description="A enlever"),
        )
        assert create_response.status_code == 200
        created_id = uuid.UUID(create_response.json()["data"]["id"])

        patch_response = client.patch(
            f"/v1/admin/llm/sample-payloads/{created_id}",
            json={"description": None},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["data"]["description"] is None
    finally:
        app.dependency_overrides.clear()
        if created_id is not None:
            db.execute(delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == created_id))
            db.commit()
        db.close()


def test_admin_llm_sample_payload_post_duplicate_name_returns_conflict():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_ids: list[uuid.UUID] = []
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        first = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="duplicate-name", is_default=False),
        )
        assert first.status_code == 200
        created_ids.append(uuid.UUID(first.json()["data"]["id"]))

        second = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="duplicate-name", is_default=False),
        )
        assert second.status_code == 409
        error = second.json()["error"]
        assert error["code"] == "sample_payload_name_conflict"
    finally:
        app.dependency_overrides.clear()
        if created_ids:
            db.execute(
                delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id.in_(created_ids))
            )
            db.commit()
        db.close()


def test_admin_llm_sample_payload_patch_duplicate_name_returns_conflict():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_ids: list[uuid.UUID] = []
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        first = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="first-name", is_default=False),
        )
        assert first.status_code == 200
        first_id = first.json()["data"]["id"]
        created_ids.append(uuid.UUID(first_id))

        second = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="second-name", is_default=False),
        )
        assert second.status_code == 200
        second_id = second.json()["data"]["id"]
        created_ids.append(uuid.UUID(second_id))

        patch_response = client.patch(
            f"/v1/admin/llm/sample-payloads/{second_id}",
            json={"name": "first-name"},
        )
        assert patch_response.status_code == 409
        error = patch_response.json()["error"]
        assert error["code"] == "sample_payload_name_conflict"
    finally:
        app.dependency_overrides.clear()
        if created_ids:
            db.execute(
                delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id.in_(created_ids))
            )
            db.commit()
        db.close()


def test_admin_llm_sample_payload_patch_default_locale_conflict_returns_409():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_ids: list[uuid.UUID] = []
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        fr_payload = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="fr-default", locale="fr-FR", is_default=True),
        )
        assert fr_payload.status_code == 200
        fr_id = fr_payload.json()["data"]["id"]
        created_ids.append(uuid.UUID(fr_id))

        en_payload = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="en-default", locale="en-US", is_default=True),
        )
        assert en_payload.status_code == 200
        en_id = en_payload.json()["data"]["id"]
        created_ids.append(uuid.UUID(en_id))

        patch_response = client.patch(
            f"/v1/admin/llm/sample-payloads/{en_id}",
            json={"locale": "fr-FR"},
        )
        assert patch_response.status_code == 409
        error = patch_response.json()["error"]
        assert error["code"] == "sample_payload_default_conflict"
    finally:
        app.dependency_overrides.clear()
        if created_ids:
            db.execute(
                delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id.in_(created_ids))
            )
            db.commit()
        db.close()


def test_admin_llm_sample_payload_rejects_sensitive_fields():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        response = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(
                payload_json={"chart_json": {"sun": "aries"}, "email": "john@doe.com"}
            ),
        )
        assert response.status_code == 422
        payload = response.json()["error"]
        assert payload["code"] == "invalid_sample_payload"
        assert "forbidden sensitive keys" in payload["message"]
    finally:
        app.dependency_overrides.clear()
        db.close()


def test_admin_llm_sample_payload_requires_natal_chart_json():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        response = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(
                payload_json={"runtime_placeholders": {"timezone": "Europe/Paris"}}
            ),
        )
        assert response.status_code == 422
        payload = response.json()["error"]
        assert payload["code"] == "invalid_sample_payload"
        assert "must include chart_json" in payload["message"]
    finally:
        app.dependency_overrides.clear()
        db.close()


def test_admin_llm_sample_payload_list_include_inactive():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    created_id: uuid.UUID | None = None
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        create = client.post(
            "/v1/admin/llm/sample-payloads",
            json=_build_payload(name="inactive-list-test", is_default=False),
        )
        assert create.status_code == 200
        created_id = uuid.UUID(create.json()["data"]["id"])

        patch = client.patch(
            f"/v1/admin/llm/sample-payloads/{created_id}",
            json={"is_active": False},
        )
        assert patch.status_code == 200

        active_only = client.get("/v1/admin/llm/sample-payloads?feature=natal&locale=fr-FR")
        assert active_only.status_code == 200
        assert active_only.json()["data"]["items"] == []

        with_inactive = client.get(
            "/v1/admin/llm/sample-payloads?feature=natal&locale=fr-FR&include_inactive=true"
        )
        assert with_inactive.status_code == 200
        items = with_inactive.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["id"] == str(created_id)
        assert items[0]["is_active"] is False
    finally:
        app.dependency_overrides.clear()
        if created_id is not None:
            db.execute(delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == created_id))
            db.commit()
        db.close()


def test_admin_llm_sample_payload_get_returns_unsanitized_payload_json_for_round_trip():
    """P1: GET/POST/PATCH expose payload_json brut (pas de redaction ADMIN_API au round-trip)."""
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    created_ids: list[uuid.UUID] = []
    try:
        db.execute(delete(LlmSamplePayloadModel))
        db.commit()

        body = {
            "name": "chat-round-trip",
            "feature": "chat",
            "locale": "fr-FR",
            "payload_json": {
                "sample": True,
                "last_user_msg": "Question utilisateur à préserver",
            },
            "description": None,
            "is_default": False,
            "is_active": True,
        }
        create = client.post("/v1/admin/llm/sample-payloads", json=body)
        assert create.status_code == 200
        row = create.json()["data"]
        created_ids.append(uuid.UUID(row["id"]))
        assert row["payload_json"]["last_user_msg"] == "Question utilisateur à préserver"

        get_resp = client.get(f"/v1/admin/llm/sample-payloads/{row['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["payload_json"]["last_user_msg"] == "Question utilisateur à préserver"

        patch = client.patch(
            f"/v1/admin/llm/sample-payloads/{row['id']}",
            json={"description": "mise à jour sans toucher au JSON"},
        )
        assert patch.status_code == 200
        assert patch.json()["data"]["payload_json"]["last_user_msg"] == "Question utilisateur à préserver"
    finally:
        app.dependency_overrides.clear()
        if created_ids:
            db.execute(
                delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id.in_(created_ids))
            )
            db.commit()
        db.close()
