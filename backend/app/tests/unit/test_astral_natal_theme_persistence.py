# Commentaire global: couvre la persistance des thèmes natals Astral par abonnement.
"""Tests de cache applicatif des thèmes natals Astral."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.auth_context import AuthenticatedUser
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_astral_natal_theme import UserAstralNatalThemeModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.services.astral.integration_service import AstralIntegrationService, AstralJobCommand


class FakeAstralClient:
    """Client Astral factice enregistrant les soumissions."""

    mercure_url = "http://mercure.local/.well-known/mercure"

    def __init__(self) -> None:
        """Initialise les réponses déterministes du client."""
        self.submitted_payloads: list[dict[str, Any]] = []
        self.status_calls: list[str] = []
        self.status_payloads: dict[str, dict[str, Any]] = {}

    async def submit_job(
        self,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Simule la création d'un job Astral."""
        self.submitted_payloads.append(payload)
        run_id = f"run-{len(self.submitted_payloads)}"
        self.status_payloads[run_id] = {
            "run_id": run_id,
            "status": "completed",
            "service_code": payload["service_code"],
            "result": {
                "reading": {
                    "status": "success",
                    "reading": {
                        "summary": {"title": f"Lecture {run_id}"},
                        "chapters": [],
                    },
                }
            },
        }
        return {
            "run_id": run_id,
            "status": "queued",
            "service_code": payload["service_code"],
        }

    async def get_job_status(self, run_id: str) -> dict[str, Any]:
        """Retourne la réponse terminale préparée par `submit_job`."""
        self.status_calls.append(run_id)
        return self.status_payloads[run_id]


@pytest.fixture()
def db_session() -> Session:
    """Prépare une base SQLite en mémoire avec un utilisateur et son profil natal."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    session = session_factory()
    user = UserModel(
        id=1,
        email="natal-cache@example.com",
        password_hash="hash",
        role="user",
    )
    profile = UserBirthProfileModel(
        id=10,
        user_id=1,
        birth_date=datetime(1990, 6, 15).date(),
        birth_year=1990,
        birth_month=6,
        birth_day=15,
        birth_date_precision="full",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    session.add_all([user, profile])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _user() -> AuthenticatedUser:
    """Retourne l'identité applicative du compte de test."""
    return AuthenticatedUser(
        id=1,
        role="user",
        email="natal-cache@example.com",
        created_at=datetime(2026, 1, 1),
    )


async def _generate_completed_theme(
    service: AstralIntegrationService,
    db: Session,
    *,
    plan: str,
    client_request_id: str,
) -> dict[str, Any]:
    """Soumet puis poll un thème jusqu'à obtenir une ligne persistée complète."""
    submitted = await service.submit_job(
        db=db,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan=plan,  # type: ignore[arg-type]
            client_request_id=client_request_id,
        ),
    )
    return await service.get_job_status(submitted["run_id"], db=db, user=_user())


@pytest.mark.asyncio
async def test_free_theme_is_reused_after_first_completed_generation(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un plan Free ne régénère pas un thème natal Free déjà produit."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "free"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    completed = await _generate_completed_theme(
        service,
        db_session,
        plan="free",
        client_request_id="free-request-1",
    )
    cached = await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="free",
            client_request_id="free-request-2",
        ),
    )

    assert cached["cached"] is True
    assert cached["run_id"] == completed["run_id"]
    assert len(fake_client.submitted_payloads) == 1

    status_calls_before_cached_poll = len(fake_client.status_calls)
    cached_poll = await service.get_job_status(cached["run_id"], db=db_session, user=_user())
    assert cached_poll["cached"] is True
    assert len(fake_client.status_calls) == status_calls_before_cached_poll


@pytest.mark.asyncio
async def test_limited_theme_reuses_existing_queued_job(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deux demandes rapprochées Free partagent le même job avant sa completion."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "free"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    first = await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="free",
            client_request_id="queued-free-request-1",
        ),
    )
    second = await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="free",
            client_request_id="queued-free-request-2",
        ),
    )

    assert second["cached"] is True
    assert second["run_id"] == first["run_id"]
    assert len(fake_client.submitted_payloads) == 1


@pytest.mark.asyncio
async def test_basic_effective_plan_downgrades_expert_audience(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un utilisateur Basic ne peut pas soumettre un job natal en audience expert."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "basic"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="premium",
            client_request_id="basic-capped-expert-request",
            audience_level="expert",
        ),
    )

    assert fake_client.submitted_payloads[0]["service_code"] == "natal_basic"
    assert fake_client.submitted_payloads[0]["audience_level"] == "beginner"


@pytest.mark.asyncio
async def test_limited_theme_cache_changes_when_birth_profile_changes(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un changement de données natales invalide le cache du même profil."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "basic"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    first = await _generate_completed_theme(
        service,
        db_session,
        plan="basic",
        client_request_id="profile-before-change",
    )
    profile = db_session.scalar(select(UserBirthProfileModel).where(UserBirthProfileModel.id == 10))
    assert profile is not None
    profile.birth_time = "15:45"
    db_session.commit()
    second = await _generate_completed_theme(
        service,
        db_session,
        plan="basic",
        client_request_id="profile-after-change",
    )

    rows = db_session.scalars(select(UserAstralNatalThemeModel)).all()
    assert first["run_id"] != second["run_id"]
    assert len({row.birth_fingerprint for row in rows}) == 2
    assert [row.status for row in rows].count("completed") == 1
    assert [row.status for row in rows].count("superseded") == 1
    assert len(fake_client.submitted_payloads) == 2


@pytest.mark.asyncio
async def test_limited_theme_cache_ignores_current_location_changes(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Une localisation courante ne modifie pas l'empreinte d'un thème natal."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "basic"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    completed = await _generate_completed_theme(
        service,
        db_session,
        plan="basic",
        client_request_id="current-location-before-change",
    )
    profile = db_session.scalar(select(UserBirthProfileModel).where(UserBirthProfileModel.id == 10))
    assert profile is not None
    profile.current_lat = 43.6047
    profile.current_lon = 1.4442
    profile.current_location_display = "Toulouse, France"
    profile.current_timezone = "Europe/Paris"
    db_session.commit()

    cached = await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="basic",
            client_request_id="current-location-after-change",
        ),
    )

    assert cached["cached"] is True
    assert cached["run_id"] == completed["run_id"]
    assert len(fake_client.submitted_payloads) == 1


@pytest.mark.asyncio
async def test_basic_user_keeps_one_free_and_one_basic_theme(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un plan Basic peut conserver un thème Free et un thème Basic distincts."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "basic"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    free_theme = await _generate_completed_theme(
        service,
        db_session,
        plan="free",
        client_request_id="basic-free-request-1",
    )
    basic_theme = await _generate_completed_theme(
        service,
        db_session,
        plan="basic",
        client_request_id="basic-request-1",
    )
    cached_basic = await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="basic",
            client_request_id="basic-request-2",
        ),
    )

    rows = db_session.scalars(select(UserAstralNatalThemeModel)).all()
    assert {row.theme_level for row in rows} == {"free", "basic"}
    assert cached_basic["cached"] is True
    assert cached_basic["run_id"] == basic_theme["run_id"]
    assert free_theme["run_id"] != basic_theme["run_id"]
    assert len(fake_client.submitted_payloads) == 2


@pytest.mark.asyncio
async def test_premium_theme_is_not_reused_by_default(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un plan Premium peut générer plusieurs thèmes Premium."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "premium"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    first = await _generate_completed_theme(
        service,
        db_session,
        plan="premium",
        client_request_id="premium-request-1",
    )
    second = await _generate_completed_theme(
        service,
        db_session,
        plan="premium",
        client_request_id="premium-request-2",
    )

    rows = db_session.scalars(
        select(UserAstralNatalThemeModel).where(UserAstralNatalThemeModel.theme_level == "premium")
    ).all()
    assert first["run_id"] != second["run_id"]
    assert len(rows) == 2
    assert len(fake_client.submitted_payloads) == 2


@pytest.mark.asyncio
async def test_premium_user_can_reuse_included_basic_theme(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un Premium garde aussi le slot Basic inclus dans son abonnement."""
    fake_client = FakeAstralClient()
    monkeypatch.setattr(
        AstralIntegrationService,
        "_resolve_user_plan",
        staticmethod(lambda *_: "premium"),
    )
    service = AstralIntegrationService(client=fake_client)  # type: ignore[arg-type]

    basic_theme = await _generate_completed_theme(
        service,
        db_session,
        plan="basic",
        client_request_id="premium-basic-request-1",
    )
    cached_basic = await service.submit_job(
        db=db_session,
        user=_user(),
        command=AstralJobCommand(
            product="natal_full",
            plan="basic",
            client_request_id="premium-basic-request-2",
        ),
    )

    assert cached_basic["cached"] is True
    assert cached_basic["run_id"] == basic_theme["run_id"]
    assert len(fake_client.submitted_payloads) == 1
