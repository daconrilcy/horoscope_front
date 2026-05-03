"""Garde les invariants runtime et architecture de la prediction quotidienne."""

from __future__ import annotations

import ast
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.public.predictions import get_daily_prediction_service
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.main import app
from app.services.prediction import (
    DailyPredictionService,
    DailyPredictionServiceError,
)
from app.services.prediction.compute_runner import ComputeResult
from app.services.prediction.run_reuse_policy import ReuseDecision

_APP_ROOT = Path(__file__).resolve().parents[2]
_PREDICTION_ROOT = _APP_ROOT / "prediction"
_APPROVED_PREDICTION_PYTHON_FILES = {
    "__init__.py",
    "aggregator.py",
    "astro_calculator.py",
    "astrologer_prompt_builder.py",
    "block_generator.py",
    "calibrator.py",
    "category_codes.py",
    "context_loader.py",
    "contribution_calculator.py",
    "daily_prediction_evidence_builder.py",
    "decision_window_builder.py",
    "domain_router.py",
    "editorial_builder.py",
    "editorial_service.py",
    "editorial_template_engine.py",
    "enriched_astro_events_builder.py",
    "event_detector.py",
    "exceptions.py",
    "explainability.py",
    "impulse_signal_builder.py",
    "input_hash.py",
    "intraday_activation_builder.py",
    "natal_sensitivity.py",
    "persisted_baseline.py",
    "persisted_relative_score.py",
    "persisted_snapshot.py",
    "persistence_service.py",
    "public_astro_daily_events.py",
    "public_astro_vocabulary.py",
    "public_domain_taxonomy.py",
    "public_label_catalog.py",
    "public_projection.py",
    "public_score_mapper.py",
    "regime_segmenter.py",
    "relative_scoring_calculator.py",
    "schemas.py",
    "temporal_kernel.py",
    "temporal_sampler.py",
    "transit_signal_builder.py",
    "turning_point_detector.py",
}
_FORBIDDEN_PREDICTION_IMPORT_MODULES = {
    "app.prediction." + "engine_orchestrator",
    "app.prediction." + "llm_narrator",
}


def _python_sources() -> list[Path]:
    """Retourne les sources applicatives collectees par la garde AST."""
    roots = [_APP_ROOT, _APP_ROOT.parent / "tests"]
    files: list[Path] = []
    for root in roots:
        files.extend(
            sorted(
                path
                for path in root.rglob("*.py")
                if "__pycache__" not in path.parts and ".venv" not in path.parts
            )
        )
    return files


def test_prediction_namespace_python_inventory_does_not_grow() -> None:
    """Bloque les nouveaux fichiers Python non cartographies sous `app.prediction`."""
    current_files = {
        path.relative_to(_PREDICTION_ROOT).as_posix()
        for path in _PREDICTION_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    }

    assert current_files == _APPROVED_PREDICTION_PYTHON_FILES


def test_prediction_legacy_orchestrator_import_path_is_removed() -> None:
    """Interdit le retour du chemin d'import legacy de l'orchestrateur."""
    violations: list[str] = []
    for file_path in _python_sources():
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(_APP_ROOT.parent)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module in _FORBIDDEN_PREDICTION_IMPORT_MODULES
            ):
                violations.append(f"{relative}: imports {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _FORBIDDEN_PREDICTION_IMPORT_MODULES:
                        violations.append(f"{relative}: imports {alias.name}")

    assert not violations, "Forbidden legacy prediction imports detected.\n- " + "\n- ".join(
        violations
    )


@pytest.fixture(autouse=True)
def allow_daily_prediction_entitlement(monkeypatch: pytest.MonkeyPatch) -> None:
    """Neutralise la gate d entitlement pour les tests focalises sur le routeur."""
    monkeypatch.setattr(
        "app.api.v1.routers.public.predictions.HoroscopeDailyEntitlementGate.check_and_get_variant",
        lambda db, user_id: SimpleNamespace(variant_code="full"),
    )


@pytest.fixture
def mock_deps():
    return {
        "context_loader": MagicMock(),
        "persistence_service": MagicMock(),
        "orchestrator": MagicMock(),
    }


@pytest.fixture
def service(mock_deps):
    return DailyPredictionService(
        mock_deps["context_loader"],
        mock_deps["persistence_service"],
        orchestrator=mock_deps["orchestrator"],
    )


def _make_bundle(*, overall_tone: str | None = None, turning_points: list | None = None):
    bundle = MagicMock()
    bundle.core.turning_points = turning_points or []
    bundle.core.run_metadata = {}
    bundle.editorial = None
    if overall_tone is not None:
        bundle.editorial = MagicMock()
        bundle.editorial.data.overall_tone = overall_tone
    return bundle


def test_fallback_on_engine_error(service, mock_deps, db_session):
    resolved_request = SimpleNamespace(
        user_id=1,
        engine_input=SimpleNamespace(
            reference_version="2.0.0",
            ruleset_version="2.0.0",
        ),
        resolved_date=date(2024, 1, 1),
        reference_version_id=1,
        ruleset_id=1,
        ruleset_version="2.0.0",
        reference_version="2.0.0",
    )
    service.resolver.resolve = MagicMock(return_value=resolved_request)
    service.reuse_policy.decide = MagicMock(return_value=ReuseDecision(should_compute=True))
    service.compute_runner.run_with_timeout = MagicMock(side_effect=Exception("Engine boom"))

    # Mock fallback to return a run
    fallback_run = MagicMock(spec=DailyPredictionRunModel)
    fallback_run.id = 123
    fallback_run.local_date = date(2023, 12, 31)
    service.fallback_policy.try_fallback = MagicMock(
        return_value=SimpleNamespace(success=True, fallback_run=fallback_run)
    )

    result = service.get_or_compute(user_id=1, db=db_session)

    assert result.was_reused is True
    assert result.run.id == 123
    assert result.bundle is None


def test_timeout_raises_on_slow_run(service, mock_deps, db_session):
    resolved_request = SimpleNamespace(
        user_id=1,
        engine_input=SimpleNamespace(
            reference_version="2.0.0",
            ruleset_version="2.0.0",
        ),
        resolved_date=date(2024, 1, 1),
        reference_version_id=1,
        ruleset_id=1,
        ruleset_version="2.0.0",
        reference_version="2.0.0",
    )
    service.resolver.resolve = MagicMock(return_value=resolved_request)
    service.reuse_policy.decide = MagicMock(return_value=ReuseDecision(should_compute=True))
    # Mock _compute_with_timeout directly — avoids patching the stdlib Future class,
    # which is fragile and could affect concurrent code in other tests.
    service.compute_runner.run_with_timeout = MagicMock(
        side_effect=DailyPredictionServiceError(
            "timeout",
            "Calcul trop long - service temporairement degrade",
        )
    )
    # No fallback available so the timeout error propagates
    service.fallback_policy.try_fallback = MagicMock(
        return_value=SimpleNamespace(success=False, fallback_run=None)
    )

    with pytest.raises(DailyPredictionServiceError) as excinfo:
        service.get_or_compute(user_id=1, db=db_session)

    assert excinfo.value.code == "timeout"


def test_latest_run_fallback_found(service, db_session):
    # Integration test of the repository date-filtering query.
    # Uses SQLite in-memory (via conftest db_session) which does NOT enforce FK constraints
    # by default, so reference_version_id=1 and ruleset_id=1 are stored as bare integers
    # without requiring matching rows in the referenced tables.
    # If this test is ever run against a FK-enforcing engine (e.g. PostgreSQL), seed the
    # required ReferenceVersionModel and PredictionRulesetModel rows first.
    from app.infra.db.repositories.daily_prediction_repository import (
        DailyPredictionRepository,
    )

    repo = DailyPredictionRepository(db_session)

    # Seed some runs
    r1 = DailyPredictionRunModel(
        user_id=1,
        local_date=date(2024, 1, 1),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash="h1",
    )
    r2 = DailyPredictionRunModel(
        user_id=1,
        local_date=date(2024, 1, 5),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash="h2",
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    # Search before Jan 10 -> should find r2 (Jan 5)
    fallback = repo.get_latest_run_before(user_id=1, date_local=date(2024, 1, 10))
    assert fallback is not None
    assert fallback.local_date == date(2024, 1, 5)

    # Search before Jan 4 -> should find r1 (Jan 1)
    fallback = repo.get_latest_run_before(user_id=1, date_local=date(2024, 1, 4))
    assert fallback.local_date == date(2024, 1, 1)

    # Search before Jan 1 -> None
    fallback = repo.get_latest_run_before(user_id=1, date_local=date(2024, 1, 1))
    assert fallback is None


def test_log_includes_duration(caplog, service, mock_deps, db_session):
    import logging

    resolved_request = SimpleNamespace(
        user_id=1,
        engine_input=SimpleNamespace(ruleset_version="2.0.0"),
        resolved_date=date(2024, 1, 1),
        reference_version_id=1,
        ruleset_id=1,
        ruleset_version="2.0.0",
    )
    service.resolver.resolve = MagicMock(return_value=resolved_request)
    service.reuse_policy.decide = MagicMock(return_value=ReuseDecision(should_compute=True))
    service.compute_runner.run_with_timeout = MagicMock(
        return_value=ComputeResult(bundle=_make_bundle(overall_tone="neutral"))
    )
    mock_deps["persistence_service"].save.return_value = MagicMock(run=MagicMock())

    with caplog.at_level(logging.INFO):
        service.get_or_compute(user_id=1, db=db_session)

    record = next(r for r in caplog.records if "prediction.run" in r.message)
    assert hasattr(record, "duration_ms")
    assert isinstance(record.duration_ms, int)
    assert record.duration_ms >= 0


def test_503_on_service_timeout():
    client = TestClient(app)

    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError("timeout", "Slow")

    app.dependency_overrides[get_daily_prediction_service] = lambda: mock_service
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=1, role="user")

    try:
        response = client.get("/v1/predictions/daily")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "timeout"
    finally:
        app.dependency_overrides = {}


def test_503_on_compute_failed():
    client = TestClient(app)

    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError(
        "compute_failed", "Calcul indisponible et aucune prédiction en cache."
    )

    app.dependency_overrides[get_daily_prediction_service] = lambda: mock_service
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=1, role="user")

    try:
        response = client.get("/v1/predictions/daily")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "compute_failed"
    finally:
        app.dependency_overrides = {}
