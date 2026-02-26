"""Tests unitaires pour le module de bootstrap Swiss Ephemeris.

Story 20-1: Installation & configuration Swiss Ephemeris

Couvre:
- Valeurs par défaut des settings SwissEph (AC1)
- Overrides env pour SWISSEPH_ENABLED, SWISSEPH_DATA_PATH, SWISSEPH_PATH_VERSION
- bootstrap_swisseph: path vide, path inexistant, import failure, succès (AC2, AC3)
- Métriques swisseph_data_missing_total et swisseph_init_errors_total (AC3)
- Logs structurés sans PII

Note: pyswisseph peut ne pas être installé dans l'environnement de test.
      Les tests utilisent patch.dict(sys.modules, ...) pour injecter un mock
      du module swisseph à la place d'un import réel.
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

import app.infra.observability.metrics as metrics_module
from app.core import ephemeris
from app.core.config import Settings
from app.infra.observability.metrics import get_counter_sum_in_window

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_env(monkeypatch: pytest.MonkeyPatch, **overrides: str) -> None:
    """Configure un environnement minimal pour instancier Settings."""
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-creds-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-key")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    for k, v in overrides.items():
        monkeypatch.setenv(k, v)


def _make_swe_mock(*, set_ephe_path_side_effect=None) -> MagicMock:
    """Crée un mock du module swisseph."""
    mock_swe = MagicMock()
    if set_ephe_path_side_effect is not None:
        mock_swe.set_ephe_path.side_effect = set_ephe_path_side_effect
    return mock_swe


# ---------------------------------------------------------------------------
# Settings SwissEph
# ---------------------------------------------------------------------------


class TestSwissEphSettings:
    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.delenv("SWISSEPH_ENABLED", raising=False)
        monkeypatch.delenv("SWISSEPH_DATA_PATH", raising=False)
        monkeypatch.delenv("SWISSEPH_PATH_VERSION", raising=False)

        s = Settings()
        assert s.swisseph_enabled is False
        assert s.swisseph_data_path == ""
        assert s.swisseph_path_version == ""

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_ENABLED", "true")
        monkeypatch.setenv("SWISSEPH_DATA_PATH", str(tmp_path))
        monkeypatch.setenv("SWISSEPH_PATH_VERSION", "se-2024-v1")

        s = Settings()
        assert s.swisseph_enabled is True
        assert s.swisseph_data_path == str(tmp_path)
        assert s.swisseph_path_version == "se-2024-v1"

    def test_enabled_false_when_env_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_ENABLED", "0")
        assert Settings().swisseph_enabled is False

    def test_enabled_false_when_env_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_ENABLED", "false")
        assert Settings().swisseph_enabled is False

    def test_enabled_true_when_env_yes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_ENABLED", "yes")
        assert Settings().swisseph_enabled is True

    def test_enabled_true_when_env_one(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_ENABLED", "1")
        assert Settings().swisseph_enabled is True

    def test_data_path_stripped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_DATA_PATH", "  /some/path  ")
        assert Settings().swisseph_data_path == "/some/path"

    def test_path_version_stripped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _base_env(monkeypatch)
        monkeypatch.setenv("SWISSEPH_PATH_VERSION", "  se-2024-v1  ")
        assert Settings().swisseph_path_version == "se-2024-v1"


# ---------------------------------------------------------------------------
# Bootstrap tests
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    """Réinitialise l'état du module ephemeris et les métriques avant chaque test."""
    ephemeris.reset_bootstrap_state()
    metrics_module.reset_metrics()
    yield
    ephemeris.reset_bootstrap_state()
    metrics_module.reset_metrics()


class TestBootstrapSwisseph:
    def test_raises_when_path_version_empty(self, tmp_path) -> None:
        with pytest.raises(ephemeris.SwissEphInitError) as exc_info:
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="")
        assert "path_version is empty" in str(exc_info.value)
        assert exc_info.value.code == "swisseph_init_failed"

    def test_raises_when_data_path_empty(self) -> None:
        with pytest.raises(ephemeris.EphemerisDataMissingError) as exc_info:
            ephemeris.bootstrap_swisseph(data_path="", path_version="v1")
        assert exc_info.value.code == "ephemeris_data_missing"

    def test_raises_when_data_path_blank(self) -> None:
        """Un path composé uniquement d'espaces équivaut à un path vide."""
        with pytest.raises(ephemeris.EphemerisDataMissingError) as exc_info:
            ephemeris.bootstrap_swisseph(data_path="   ", path_version="v1")
        assert exc_info.value.code == "ephemeris_data_missing"

    def test_raises_when_data_path_not_a_directory(self, tmp_path) -> None:
        fake = str(tmp_path / "nonexistent_dir")
        with pytest.raises(ephemeris.EphemerisDataMissingError) as exc_info:
            ephemeris.bootstrap_swisseph(data_path=fake, path_version="v1")
        assert exc_info.value.code == "ephemeris_data_missing"

    def test_raises_when_data_path_is_a_file(self, tmp_path) -> None:
        f = tmp_path / "not_a_dir.txt"
        f.write_text("data")
        with pytest.raises(ephemeris.EphemerisDataMissingError) as exc_info:
            ephemeris.bootstrap_swisseph(data_path=str(f), path_version="v1")
        assert exc_info.value.code == "ephemeris_data_missing"

    def test_raises_swisseph_init_error_on_import_failure(self, tmp_path) -> None:
        with patch.dict("sys.modules", {"swisseph": None}):
            with pytest.raises(ephemeris.SwissEphInitError) as exc_info:
                ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
        assert exc_info.value.code == "swisseph_init_failed"

    def test_raises_swisseph_init_error_on_set_ephe_path_failure(self, tmp_path) -> None:
        mock_swe = _make_swe_mock(set_ephe_path_side_effect=RuntimeError("swe error"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(ephemeris.SwissEphInitError) as exc_info:
                ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
        assert exc_info.value.code == "swisseph_init_failed"

    def test_success_stores_result(self, tmp_path) -> None:
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="se-2024")

        result = ephemeris.get_bootstrap_result()
        assert result is not None
        assert result.success is True
        assert result.path_version == "se-2024"
        assert result.error is None

    def test_success_calls_set_ephe_path(self, tmp_path) -> None:
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")

        mock_swe.set_ephe_path.assert_called_once_with(str(tmp_path))

    def test_failure_stores_error_in_result(self) -> None:
        try:
            ephemeris.bootstrap_swisseph(data_path="", path_version="v1")
        except ephemeris.EphemerisDataMissingError:
            pass

        result = ephemeris.get_bootstrap_result()
        assert result is not None
        assert result.success is False
        assert isinstance(result.error, ephemeris.EphemerisDataMissingError)

    def test_init_failure_stores_error_in_result(self, tmp_path) -> None:
        mock_swe = _make_swe_mock(set_ephe_path_side_effect=RuntimeError("boom"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            try:
                ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
            except ephemeris.SwissEphInitError:
                pass

        result = ephemeris.get_bootstrap_result()
        assert result is not None
        assert result.success is False
        assert isinstance(result.error, ephemeris.SwissEphInitError)

    def test_get_bootstrap_result_returns_none_before_bootstrap(self) -> None:
        assert ephemeris.get_bootstrap_result() is None

    def test_reset_bootstrap_state_clears_result(self, tmp_path) -> None:
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
        assert ephemeris.get_bootstrap_result() is not None

        ephemeris.reset_bootstrap_state()
        assert ephemeris.get_bootstrap_result() is None


# ---------------------------------------------------------------------------
# Métriques
# ---------------------------------------------------------------------------


class TestEphemerisMetrics:
    def test_data_missing_metric_incremented_on_empty_path(self) -> None:
        try:
            ephemeris.bootstrap_swisseph(data_path="", path_version="v1")
        except ephemeris.EphemerisDataMissingError:
            pass

        count = get_counter_sum_in_window(
            ephemeris.METRIC_DATA_MISSING, timedelta(minutes=1)
        )
        assert count == 1.0

    def test_data_missing_metric_incremented_on_missing_dir(self, tmp_path) -> None:
        bad_path = str(tmp_path / "no_such_dir")
        try:
            ephemeris.bootstrap_swisseph(data_path=bad_path, path_version="v1")
        except ephemeris.EphemerisDataMissingError:
            pass

        count = get_counter_sum_in_window(
            ephemeris.METRIC_DATA_MISSING, timedelta(minutes=1)
        )
        assert count == 1.0

    def test_init_errors_metric_incremented_on_swe_failure(self, tmp_path) -> None:
        mock_swe = _make_swe_mock(set_ephe_path_side_effect=RuntimeError("boom"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            try:
                ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
            except ephemeris.SwissEphInitError:
                pass

        count = get_counter_sum_in_window(
            ephemeris.METRIC_INIT_ERRORS, timedelta(minutes=1)
        )
        assert count == 1.0

    def test_no_metrics_on_success(self, tmp_path) -> None:
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")

        missing_count = get_counter_sum_in_window(
            ephemeris.METRIC_DATA_MISSING, timedelta(minutes=1)
        )
        init_error_count = get_counter_sum_in_window(
            ephemeris.METRIC_INIT_ERRORS, timedelta(minutes=1)
        )
        assert missing_count == 0.0
        assert init_error_count == 0.0
