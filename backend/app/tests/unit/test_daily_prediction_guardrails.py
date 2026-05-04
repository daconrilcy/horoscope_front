"""Garde les invariants runtime et architecture de la prediction quotidienne."""

from __future__ import annotations

import ast
import importlib.util
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
_LEGACY_PREDICTION_ROOT = _APP_ROOT / "prediction"
_PREDICTION_ROOT = _APP_ROOT / "domain" / "prediction"
_PREDICTION_REPOSITORIES_ROOT = _APP_ROOT / "infra" / "db" / "repositories"
_REPO_ROOT = _APP_ROOT.parents[1]
_FORBIDDEN_PREDICTION_IMPORT_MODULES = {
    "app.prediction." + "engine_orchestrator",
    "app.prediction." + "llm_narrator",
}
_FORBIDDEN_PERSISTED_DTO_IMPORT_MODULES = {
    "app.prediction.context",
    "app.prediction.persisted_baseline",
    "app.prediction.persisted_relative_score",
    "app.prediction.persisted_snapshot",
}
_FORBIDDEN_PREDICTION_BOUNDARY_MODULES = {
    "app.api",
    "app.core.config",
    "app.infra",
    "fastapi",
}
_FORBIDDEN_INFRA_BOUNDARY_NAMES = {
    "sqlalchemy",
    "sqlalchemy.orm",
    "app.infra.db.repositories.daily_prediction_repository",
    "app.infra.db.repositories.prediction_reference_repository",
    "app.infra.db.repositories.prediction_ruleset_repository",
}
_FORBIDDEN_PUBLIC_PROJECTION_NAMES = {
    "AIEngineAdapter",
    "LLMRuntime",
    "settings",
    "Session",
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


def test_prediction_legacy_namespace_is_not_importable() -> None:
    """Bloque la recreation importable du package racine legacy `app.prediction`."""
    assert importlib.util.find_spec("app.prediction") is None


def test_prediction_legacy_namespace_has_no_files() -> None:
    """Bloque tout fichier residuel sous l'ancien dossier `backend/app/prediction`."""
    assert not _LEGACY_PREDICTION_ROOT.exists()


def test_prediction_legacy_import_paths_are_removed() -> None:
    """Interdit le retour des imports actifs du namespace legacy."""
    violations: list[str] = []
    for file_path in _python_sources():
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(_APP_ROOT.parent)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and (
                    node.module == "app.prediction"
                    or node.module.startswith("app.prediction.")
                    or node.module in _FORBIDDEN_PREDICTION_IMPORT_MODULES
                )
            ):
                violations.append(f"{relative}: imports {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "app.prediction" or alias.name.startswith("app.prediction."):
                        violations.append(f"{relative}: imports {alias.name}")

    assert not violations, "Forbidden legacy prediction imports detected.\n- " + "\n- ".join(
        violations
    )


def test_prediction_repositories_do_not_import_legacy_persisted_dtos() -> None:
    """Bloque les imports DTO persisted legacy depuis les repositories DB."""
    violations: list[str] = []
    for file_path in sorted(_PREDICTION_REPOSITORIES_ROOT.rglob("*.py")):
        if "__pycache__" in file_path.parts:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(_APP_ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in _FORBIDDEN_PERSISTED_DTO_IMPORT_MODULES:
                    violations.append(f"{relative}: imports {module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _FORBIDDEN_PERSISTED_DTO_IMPORT_MODULES:
                        violations.append(f"{relative}: imports {alias.name}")

    assert not violations, "Forbidden persisted DTO imports detected.\n- " + "\n- ".join(violations)


def test_prediction_pure_namespace_has_no_db_loader_or_persistence_imports() -> None:
    """Bloque le retour de SQLAlchemy/repositories dans le domaine prediction pur."""
    violations: list[str] = []
    for file_path in sorted(_PREDICTION_ROOT.rglob("*.py")):
        if "__pycache__" in file_path.parts:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(_APP_ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in _FORBIDDEN_INFRA_BOUNDARY_NAMES:
                    violations.append(f"{relative}: imports {module}")
                for forbidden in _FORBIDDEN_INFRA_BOUNDARY_NAMES:
                    if module.startswith(f"{forbidden}."):
                        violations.append(f"{relative}: imports {module}")
                        break
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _FORBIDDEN_INFRA_BOUNDARY_NAMES:
                        violations.append(f"{relative}: imports {alias.name}")

    assert not violations, "Forbidden prediction infra imports detected.\n- " + "\n- ".join(
        violations
    )


def test_prediction_namespace_does_not_import_api_settings_or_llm_runtime() -> None:
    """Bloque les dependances API, settings et LLM runtime sous `app.domain.prediction`."""
    violations: list[str] = []
    for file_path in sorted(_PREDICTION_ROOT.rglob("*.py")):
        if "__pycache__" in file_path.parts:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(_APP_ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for forbidden in _FORBIDDEN_PREDICTION_BOUNDARY_MODULES:
                    if module == forbidden or module.startswith(f"{forbidden}."):
                        violations.append(f"{relative}: imports {module}")
                for alias in node.names:
                    if alias.name in _FORBIDDEN_PUBLIC_PROJECTION_NAMES:
                        violations.append(f"{relative}: imports {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in _FORBIDDEN_PREDICTION_BOUNDARY_MODULES:
                        if alias.name == forbidden or alias.name.startswith(f"{forbidden}."):
                            violations.append(f"{relative}: imports {alias.name}")
            elif isinstance(node, ast.Name) and node.id in _FORBIDDEN_PUBLIC_PROJECTION_NAMES:
                violations.append(f"{relative}: references {node.id}")

    assert not violations, "Forbidden prediction boundary imports detected.\n- " + (
        "\n- ".join(violations)
    )


def test_prediction_removed_legacy_compatibility_surfaces_stay_removed() -> None:
    """Bloque le retour des compatibilites prediction supprimees par CS-008."""
    violations: list[str] = []
    schemas_path = _PREDICTION_ROOT / "schemas.py"
    schemas_tree = ast.parse(schemas_path.read_text(encoding="utf-8"), filename=str(schemas_path))
    for node in ast.walk(schemas_tree):
        if isinstance(node, ast.ClassDef) and node.name == "TimeBlock":
            violations.append("app/domain/prediction/schemas.py: class TimeBlock is present")

    for file_path in _python_sources():
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(_APP_ROOT.parent).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            is_save_call = (
                isinstance(function, ast.Attribute)
                and function.attr == "save"
                or isinstance(function, ast.Name)
                and function.id == "save"
            )
            if is_save_call and any(keyword.arg == "engine_output" for keyword in node.keywords):
                violations.append(f"{relative}:{node.lineno} calls save(engine_output=...)")

    assert not violations, "Removed prediction compatibility surfaces detected.\n- " + "\n- ".join(
        violations
    )


def test_public_projection_does_not_own_llm_runtime_or_correlation_ids() -> None:
    """Verrouille la projection publique comme assemblage deterministe sans runtime LLM."""
    projection_path = _PREDICTION_ROOT / "public_projection.py"
    source = projection_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(projection_path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "llm.runtime.adapter" in module or module == "app.core.config":
                violations.append(f"line {node.lineno}: imports {module}")
            for alias in node.names:
                if alias.name in _FORBIDDEN_PUBLIC_PROJECTION_NAMES:
                    violations.append(f"line {node.lineno}: imports {alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "uuid":
                    violations.append(f"line {node.lineno}: imports uuid")
        elif isinstance(node, ast.Name) and node.id in _FORBIDDEN_PUBLIC_PROJECTION_NAMES:
            violations.append(f"line {node.lineno}: references {node.id}")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "uuid4"
        ):
            violations.append(f"line {node.lineno}: calls uuid4")

    assert not violations, "Forbidden public projection runtime dependencies detected.\n- " + (
        "\n- ".join(violations)
    )


def test_public_projection_does_not_generate_local_correlation_ids() -> None:
    """Interdit explicitement toute generation locale d IDs de correlation."""
    projection_path = _PREDICTION_ROOT / "public_projection.py"
    source = projection_path.read_text(encoding="utf-8")
    forbidden_patterns = [
        "uuid.uuid4(",
        "request_id = str(",
        "trace_id = str(",
    ]

    violations = [pattern for pattern in forbidden_patterns if pattern in source]

    assert not violations, "Forbidden local correlation ID generation detected: " + ", ".join(
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
