# Commentaire global: vérifie le script de purge du thème natal et du quota associé.
"""Teste le script local qui purge le thème natal d'un utilisateur ciblé."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import scripts.reset_user_natal_theme as reset_script
from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel, PeriodUnit, ResetMode
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_astral_natal_theme import UserAstralNatalThemeModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel


@pytest.fixture()
def sqlite_session(monkeypatch: pytest.MonkeyPatch) -> Session:
    """Construit une base SQLite mémoire et redirige le script vers cette session."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    monkeypatch.setattr(reset_script, "SessionLocal", session_factory)

    session = session_factory()
    user = UserModel(
        id=14,
        email="daconrilcy@hotmail.com",
        password_hash="hash",
        role="user",
    )
    birth_profile = UserBirthProfileModel(
        id=1,
        user_id=14,
        birth_date=datetime(1990, 1, 1).date(),
        birth_year=1990,
        birth_month=1,
        birth_day=1,
        birth_date_precision="full",
        birth_time="12:00",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_city="Paris",
        birth_country="France",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    theme = UserAstralNatalThemeModel(
        id=1,
        user_id=14,
        birth_profile_id=1,
        birth_fingerprint="fingerprint-1",
        theme_level="basic",
        requested_product="natal_full",
        requested_plan="basic",
        service_code="natal_basic",
        status="completed",
        run_id="run-1",
        client_request_id="request-1",
        response_payload={"status": "completed"},
    )
    superseded_theme = UserAstralNatalThemeModel(
        id=2,
        user_id=14,
        birth_profile_id=1,
        birth_fingerprint="fingerprint-2",
        theme_level="basic",
        requested_product="natal_full",
        requested_plan="basic",
        service_code="natal_basic",
        status="superseded",
        run_id="run-2",
        client_request_id="request-2",
        response_payload={"status": "superseded"},
    )
    counter = FeatureUsageCounterModel(
        id=1,
        user_id=14,
        feature_code="natal_chart_long",
        quota_key="interpretations",
        period_unit=PeriodUnit.LIFETIME,
        period_value=1,
        reset_mode=ResetMode.LIFETIME,
        window_start=datetime(1970, 1, 1, tzinfo=timezone.utc),
        window_end=None,
        used_count=3,
    )
    session.add_all([user, birth_profile, theme, superseded_theme, counter])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_reset_user_natal_theme_deletes_saved_theme_and_zeroes_counter(
    sqlite_session: Session, capsys: pytest.CaptureFixture[str]
) -> None:
    """Le script doit supprimer le thème natal et remettre le compteur natal long à zéro."""
    reset_script.reset_user_natal_theme("daconrilcy@hotmail.com")
    sqlite_session.expire_all()

    remaining_themes = sqlite_session.scalars(select(UserAstralNatalThemeModel)).all()
    counter = sqlite_session.scalar(
        select(FeatureUsageCounterModel).where(
            FeatureUsageCounterModel.user_id == 14,
            FeatureUsageCounterModel.feature_code == "natal_chart_long",
            FeatureUsageCounterModel.quota_key == "interpretations",
            FeatureUsageCounterModel.period_unit == PeriodUnit.LIFETIME,
            FeatureUsageCounterModel.period_value == 1,
            FeatureUsageCounterModel.reset_mode == ResetMode.LIFETIME,
        )
    )
    output = capsys.readouterr().out

    assert len(remaining_themes) == 1
    assert remaining_themes[0].status == "superseded"
    assert counter is not None
    assert counter.used_count == 0
    assert "deleted_themes=1" in output
    assert "natal_long_used_count=0" in output


def test_reset_user_natal_theme_ps1_wraps_the_python_script() -> None:
    """Le wrapper PowerShell doit activer le venv puis lancer le script Python local."""
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "reset_user_natal_theme.ps1"
    content = script_path.read_text(encoding="utf-8")

    assert "Split-Path -Parent (Split-Path -Parent $PSScriptRoot)" in content
    assert ".venv\\Scripts\\Activate.ps1" in content
    assert "Set-Location -LiteralPath $backendPath" in content
    assert "reset_user_natal_theme.py" in content
    assert "python -B $pythonScriptPath --email $Email" in content
