"""Configuration pytest partagee pour isoler les tests et classer les suites lentes."""

from __future__ import annotations

import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest

_TMP_ROOT = Path(__file__).resolve().parent / ".tmp-pytest" / "fixture-tmp"
_TMP_ROOT.mkdir(parents=True, exist_ok=True)

_BACKEND_ROOT = Path(__file__).resolve().parent
_SLOW_TEST_FILES = {
    "app/tests/test_full_reconciliation_chain.py",
    "app/tests/integration/test_backup_restore_scripts.py",
    "app/tests/integration/test_db_bootstrap.py",
    "app/tests/integration/test_db_bootstrap_partial_upgrade.py",
    "app/tests/integration/test_migration_0037_add_contributors_json.py",
    "app/tests/integration/test_migration_0039_add_is_provisional_calibration.py",
    "app/tests/integration/test_migration_20260422_0073_cleanup_llm_legacy.py",
    "app/tests/integration/test_migration_20260424_0082_drop_remaining_llm_legacy_columns.py",
    "app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py",
    "app/tests/integration/test_migration_8b2d52442493_add_input_schema_to_assembly.py",
    "app/tests/integration/test_migration_a_prediction_tables.py",
    "app/tests/integration/test_migration_b_ruleset_tables.py",
    "app/tests/integration/test_migration_c_daily_prediction.py",
    "app/tests/integration/test_reference_data_migrations.py",
    "app/tests/integration/test_secret_rotation_process_restart.py",
    "app/tests/integration/test_seed_31_prediction_v2.py",
    "app/tests/integration/test_user_prediction_baseline.py",
    "app/tests/unit/test_backend_pytest_collection.py",
}
_REGRESSION_TEST_DIRS = ("app/tests/regression/",)
_INTEGRATION_TEST_DIRS = (
    "app/tests/integration/",
    "tests/integration/",
)
_FAST_EXCLUDED_MARKERS = ("integration", "slow", "regression")


@dataclass
class WorkspaceTmpPathFactory:
    base_temp: Path

    def getbasetemp(self) -> Path:
        return self.base_temp

    def mktemp(self, basename: str, numbered: bool = True) -> Path:
        suffix = f"-{uuid.uuid4().hex}" if numbered else ""
        path = self.base_temp / f"{basename}{suffix}"
        path.mkdir(parents=True, exist_ok=False)
        return path


def pytest_addoption(parser: pytest.Parser) -> None:
    """Ajoute l'option qui active la suite complete locale."""
    parser.addoption(
        "--long",
        action="store_true",
        default=False,
        help="Lance aussi les tests d'integration, lents et de regression.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Ajoute les markers de selection rapide et deselectionne sans --long."""
    deselected: list[pytest.Item] = []
    selected: list[pytest.Item] = []
    long_run = bool(config.getoption("--long"))

    for item in items:
        relative_path = _relative_test_path(item)
        if relative_path.startswith(_INTEGRATION_TEST_DIRS):
            item.add_marker(pytest.mark.integration)
        if relative_path in _SLOW_TEST_FILES:
            item.add_marker(pytest.mark.slow)
        if relative_path.startswith(_REGRESSION_TEST_DIRS):
            item.add_marker(pytest.mark.regression)

        if not long_run and _is_fast_excluded(item):
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


def _is_fast_excluded(item: pytest.Item) -> bool:
    """Indique si un test doit sortir de la suite rapide par defaut."""
    return any(item.get_closest_marker(marker) for marker in _FAST_EXCLUDED_MARKERS)


def _relative_test_path(item: pytest.Item) -> str:
    """Retourne le chemin de test relatif au dossier backend avec des separateurs POSIX."""
    path = Path(str(item.fspath)).resolve()
    try:
        return path.relative_to(_BACKEND_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


@pytest.fixture(scope="session")
def tmp_path_factory() -> WorkspaceTmpPathFactory:
    try:
        yield WorkspaceTmpPathFactory(base_temp=_TMP_ROOT)
    finally:
        shutil.rmtree(_TMP_ROOT, ignore_errors=True)


@pytest.fixture
def tmp_path(tmp_path_factory: WorkspaceTmpPathFactory) -> Path:
    path = tmp_path_factory.mktemp("test")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
