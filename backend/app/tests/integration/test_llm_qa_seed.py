from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.security import verify_password
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.services.chart_result_service import ChartResultService
from app.services.llm_qa_seed_service import (
    LLM_QA_TEST_BIRTH_DATE,
    LLM_QA_TEST_BIRTH_PLACE,
    LLM_QA_TEST_BIRTH_TIME,
    LLM_QA_TEST_USER_EMAIL,
    LLM_QA_TEST_USER_PASSWORD,
    LlmQaSeedService,
)


@pytest.fixture
def test_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    database_url = f"sqlite:///{(tmp_path / 'test_llm_qa_seed.db').as_posix()}"
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


def _stub_geocoding_result():
    from app.services.geocoding_service import GeocodingAddress, GeocodingSearchResult

    return GeocodingSearchResult(
        provider="nominatim",
        provider_place_id=987654,
        osm_type="relation",
        osm_id=7444,
        type="administrative",
        class_="boundary",
        display_name="Paris, Ile-de-France, France",
        lat=48.8566,
        lon=2.3522,
        importance=0.9,
        place_rank=12,
        address=GeocodingAddress(
            country_code="fr",
            country="France",
            state="Ile-de-France",
            city="Paris",
            postcode="75000",
        ),
    )


def _stub_generate_for_user(db, user_id: int, *args, **kwargs):
    from app.core.config import settings

    place = db.scalar(select(GeoPlaceResolvedModel))
    assert place is not None
    birth_input = BirthInput(
        birth_date=LLM_QA_TEST_BIRTH_DATE,
        birth_time=LLM_QA_TEST_BIRTH_TIME,
        birth_place=LLM_QA_TEST_BIRTH_PLACE,
        birth_timezone=place.timezone_iana,
        place_resolved_id=place.id,
        birth_lat=float(place.latitude),
        birth_lon=float(place.longitude),
        birth_city=place.city,
        birth_country=place.country,
    )
    input_hash = ChartResultService.compute_input_hash(
        birth_input=birth_input,
        reference_version=settings.active_reference_version,
        ruleset_version=settings.ruleset_version,
    )
    chart_id = str(uuid.uuid4())
    db.add(
        ChartResultModel(
            user_id=user_id,
            chart_id=chart_id,
            reference_version=settings.active_reference_version,
            ruleset_version=settings.ruleset_version,
            input_hash=input_hash,
            result_payload={"chart_id": chart_id, "kind": "qa-seed"},
        )
    )
    db.flush()
    return type("GeneratedChart", (), {"chart_id": chart_id})()


def test_llm_qa_seed_is_idempotent(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.services import llm_qa_seed_service as seed_module

    monkeypatch.setattr(seed_module.settings, "app_env", "dev")
    monkeypatch.setattr(seed_module.settings, "active_reference_version", "ref-test")
    monkeypatch.setattr(seed_module.settings, "ruleset_version", "rules-test")
    monkeypatch.setattr(
        seed_module.GeocodingService,
        "search_with_cache",
        lambda *args, **kwargs: [_stub_geocoding_result()],
    )
    monkeypatch.setattr(
        seed_module.GeocodingService,
        "derive_timezone",
        lambda **kwargs: "Europe/Paris",
    )
    monkeypatch.setattr(
        seed_module.UserNatalChartService,
        "generate_for_user",
        _stub_generate_for_user,
    )

    with test_db() as db:
        first = LlmQaSeedService.ensure_canonical_test_user(db)
        second = LlmQaSeedService.ensure_canonical_test_user(db)

        user = db.scalar(select(UserModel).where(UserModel.email == LLM_QA_TEST_USER_EMAIL))
        assert user is not None
        assert verify_password(LLM_QA_TEST_USER_PASSWORD, user.password_hash)
        assert user.role == "user"
        assert first.user_id == second.user_id
        assert second.chart_reused is True

        birth_profiles = db.scalars(select(UserBirthProfileModel)).all()
        charts = db.scalars(select(ChartResultModel)).all()
        places = db.scalars(select(GeoPlaceResolvedModel)).all()

        assert len(birth_profiles) == 1
        assert len(charts) == 1
        assert len(places) == 1
        assert birth_profiles[0].birth_timezone == "Europe/Paris"
        assert birth_profiles[0].birth_place_resolved_id == places[0].id


def test_llm_qa_seed_is_blocked_in_production(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.services import llm_qa_seed_service as seed_module

    monkeypatch.setattr(seed_module.settings, "app_env", "production")
    monkeypatch.setattr(seed_module.settings, "llm_qa_seed_user_allow_production", False)

    with test_db() as db:
        with pytest.raises(seed_module.LlmQaSeedServiceError) as excinfo:
            LlmQaSeedService.ensure_canonical_test_user(db)

        assert excinfo.value.code == "llm_qa_seed_not_allowed"
        assert db.scalar(select(UserModel).where(UserModel.email == LLM_QA_TEST_USER_EMAIL)) is None


def test_llm_qa_seed_prunes_obsolete_chart_versions(test_db, monkeypatch: pytest.MonkeyPatch):
    from app.services import llm_qa_seed_service as seed_module

    monkeypatch.setattr(seed_module.settings, "app_env", "dev")
    monkeypatch.setattr(seed_module.settings, "active_reference_version", "ref-v1")
    monkeypatch.setattr(seed_module.settings, "ruleset_version", "rules-v1")
    monkeypatch.setattr(
        seed_module.GeocodingService,
        "search_with_cache",
        lambda *args, **kwargs: [_stub_geocoding_result()],
    )
    monkeypatch.setattr(
        seed_module.GeocodingService,
        "derive_timezone",
        lambda **kwargs: "Europe/Paris",
    )
    monkeypatch.setattr(
        seed_module.UserNatalChartService,
        "generate_for_user",
        _stub_generate_for_user,
    )

    with test_db() as db:
        first = LlmQaSeedService.ensure_canonical_test_user(db)

        monkeypatch.setattr(seed_module.settings, "active_reference_version", "ref-v2")
        monkeypatch.setattr(seed_module.settings, "ruleset_version", "rules-v2")

        second = LlmQaSeedService.ensure_canonical_test_user(db)

        charts = db.scalars(select(ChartResultModel)).all()

        assert first.chart_id != second.chart_id
        assert second.chart_reused is False
        assert len(charts) == 1
        assert charts[0].chart_id == second.chart_id
        assert charts[0].reference_version == "ref-v2"
        assert charts[0].ruleset_version == "rules-v2"
