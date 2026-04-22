from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies.auth import UserAuthenticationError
from app.core.security import create_access_token, hash_password
from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel


@pytest.fixture
def test_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    database_url = f"sqlite:///{(tmp_path / 'test_llm_qa_router.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    yield test_session_local
    test_engine.dispose()


def _build_test_app(test_db):
    from app.api.v1.routers.internal.llm.qa import router as qa_router
    from app.infra.db.session import get_db_session
    from app.main import handle_user_authentication_error

    test_app = FastAPI()
    test_app.add_exception_handler(UserAuthenticationError, handle_user_authentication_error)

    def override_db():
        with test_db() as db:
            yield db

    test_app.dependency_overrides[get_db_session] = override_db
    test_app.include_router(qa_router)
    return test_app


def _create_user(session_factory, *, email: str, role: str) -> UserModel:
    with session_factory() as db:
        user = UserModel(
            email=email,
            password_hash=hash_password("admin123"),
            role=role,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def test_internal_llm_qa_router_mount_policy(monkeypatch: pytest.MonkeyPatch):
    from app import main as main_module

    disabled_app = FastAPI()
    monkeypatch.setattr(main_module.settings, "llm_qa_routes_enabled", False)
    main_module._include_internal_llm_qa_router(disabled_app)
    assert not any(route.path.startswith("/v1/internal/llm/qa") for route in disabled_app.routes)

    blocked_prod_app = FastAPI()
    monkeypatch.setattr(main_module.settings, "llm_qa_routes_enabled", True)
    monkeypatch.setattr(main_module.settings, "app_env", "production")
    monkeypatch.setattr(main_module.settings, "llm_qa_routes_allow_production", False)
    main_module._include_internal_llm_qa_router(blocked_prod_app)
    assert not any(
        route.path.startswith("/v1/internal/llm/qa") for route in blocked_prod_app.routes
    )

    enabled_app = FastAPI()
    monkeypatch.setattr(main_module.settings, "app_env", "dev")
    main_module._include_internal_llm_qa_router(enabled_app)
    assert any(route.path == "/v1/internal/llm/qa/guidance" for route in enabled_app.routes)


def test_internal_llm_qa_routes_require_ops_role(test_db):
    app = _build_test_app(test_db)
    client = TestClient(app)
    user = _create_user(test_db, email="user@test.com", role="user")
    token = create_access_token(subject=str(user.id), role=user.role)

    response = client.post(
        "/v1/internal/llm/qa/seed-user",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_internal_llm_qa_routes_run_canonical_flows(
    test_db,
    monkeypatch: pytest.MonkeyPatch,
):
    from app.api.v1.routers.internal.llm import qa as qa_module

    app = _build_test_app(test_db)
    client = TestClient(app)

    admin = _create_user(test_db, email="admin@test.com", role="admin")
    target = _create_user(test_db, email="cyril-test@test.com", role="user")
    admin_token = create_access_token(subject=str(admin.id), role=admin.role)

    async def fake_guidance(*args, **kwargs):
        return SimpleNamespace(model_dump=lambda mode="json": {"summary": "guidance-ok"})

    async def fake_chat(*args, **kwargs):
        return SimpleNamespace(
            model_dump=lambda mode="json": {
                "assistant_message": {"content": "chat-ok"},
            }
        )

    async def fake_natal(*args, **kwargs):
        return SimpleNamespace(
            model_dump=lambda mode="json": {
                "data": {"use_case": "natal_interpretation"},
            }
        )

    async def fake_assemble(*args, **kwargs):
        return {"summary": {"overall_summary": "daily-ok"}}

    monkeypatch.setattr(
        qa_module.LlmQaSeedService,
        "ensure_canonical_test_user",
        lambda db: SimpleNamespace(
            user_id=target.id,
            email=target.email,
            birth_place_resolved_id=1,
            birth_timezone="Europe/Paris",
            chart_id="chart-1",
            chart_reused=True,
        ),
    )
    monkeypatch.setattr(qa_module.GuidanceService, "request_guidance_async", fake_guidance)
    monkeypatch.setattr(qa_module.ChatGuidanceService, "send_message_async", fake_chat)
    monkeypatch.setattr(
        qa_module.UserNatalChartService,
        "get_latest_for_user",
        lambda db, user_id: SimpleNamespace(chart_id="chart-1", result={"ok": True}),
    )
    monkeypatch.setattr(
        qa_module.UserBirthProfileService,
        "get_for_user",
        lambda db, user_id: SimpleNamespace(birth_date="1973-04-24", birth_time="11:00"),
    )
    monkeypatch.setattr(qa_module.NatalInterpretationServiceV2, "interpret", fake_natal)
    monkeypatch.setattr(
        qa_module.HoroscopeDailyEntitlementGate,
        "check_and_get_variant",
        lambda db, user_id: SimpleNamespace(variant_code="full"),
    )
    monkeypatch.setattr(
        qa_module.DailyPredictionService,
        "get_or_compute",
        lambda self, **kwargs: SimpleNamespace(
            run=SimpleNamespace(
                run_id=1,
                reference_version_id=1,
                llm_narrative=None,
            ),
            bundle={"provider": "openai"},
            was_reused=True,
        ),
    )
    monkeypatch.setattr(
        qa_module.DailyPredictionRepository,
        "get_full_run",
        lambda self, run_id: SimpleNamespace(
            run_id=run_id,
            reference_version_id=1,
            llm_narrative=None,
        ),
    )
    monkeypatch.setattr(
        qa_module.PredictionReferenceRepository,
        "get_categories",
        lambda self, reference_version_id: [],
    )
    monkeypatch.setattr(
        qa_module.PublicPredictionAssembler,
        "assemble",
        fake_assemble,
    )

    seed_response = client.post(
        "/v1/internal/llm/qa/seed-user",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    guidance_response = client.post(
        "/v1/internal/llm/qa/guidance",
        json={"period": "daily"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    chat_response = client.post(
        "/v1/internal/llm/qa/chat",
        json={"message": "Bonjour"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    natal_response = client.post(
        "/v1/internal/llm/qa/natal",
        json={"use_case_level": "complete"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    daily_response = client.post(
        "/v1/internal/llm/qa/horoscope-daily",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert seed_response.status_code == 200
    assert guidance_response.status_code == 200
    assert chat_response.status_code == 200
    assert natal_response.status_code == 200
    assert daily_response.status_code == 200
    assert guidance_response.json()["data"]["summary"] == "guidance-ok"
    assert chat_response.json()["data"]["assistant_message"]["content"] == "chat-ok"
    assert natal_response.json()["data"]["data"]["use_case"] == "natal_interpretation"
    assert daily_response.json()["data"]["summary"]["overall_summary"] == "daily-ok"
