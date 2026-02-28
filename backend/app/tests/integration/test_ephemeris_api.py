"""Tests d'intégration pour l'endpoint GET /v1/ephemeris/status.

Story 20-1: Installation & configuration Swiss Ephemeris

Couvre:
- 200 {"status": "disabled"} quand SWISSEPH_ENABLED=false (AC1)
- 200 {"status": "ok", "path_version": "..."} quand bootstrap réussi (AC1, AC4)
- 503 code=ephemeris_data_missing quand path absent (AC2)
- 503 code=swisseph_init_failed quand init runtime échouée (AC3)

Note: pyswisseph peut ne pas être installé dans l'environnement de test.
      Les tests utilisent patch.dict(sys.modules, ...) pour injecter un mock
      du module swisseph à la place d'un import réel.
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core import ephemeris
from app.infra.observability.metrics import get_counter_sum_in_window, reset_metrics
from app.main import app

client = TestClient(app)


def _make_swe_mock(*, set_ephe_path_side_effect=None) -> MagicMock:
    """Crée un mock du module swisseph."""
    mock_swe = MagicMock()
    if set_ephe_path_side_effect is not None:
        mock_swe.set_ephe_path.side_effect = set_ephe_path_side_effect
    return mock_swe


@pytest.fixture(autouse=True)
def _reset_ephemeris_state() -> None:
    """Réinitialise l'état du module ephemeris avant et après chaque test."""
    ephemeris.reset_bootstrap_state()
    reset_metrics()
    yield
    ephemeris.reset_bootstrap_state()
    reset_metrics()


# ---------------------------------------------------------------------------
# AC1 — Disabled (défaut)
# ---------------------------------------------------------------------------


def test_status_disabled_when_swisseph_not_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """SWISSEPH_ENABLED=false → 200 {"status": "disabled"}."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", False)

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disabled"


# ---------------------------------------------------------------------------
# AC1 — Bootstrap réussi
# ---------------------------------------------------------------------------


def test_status_ok_after_successful_bootstrap(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Bootstrap réussi → 200 {"status": "ok", "path_version": "..."}."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    mock_swe = _make_swe_mock()
    required_file = tmp_path / "sepl_18.se1"
    required_file.write_text("fixture", encoding="utf-8")
    with patch.dict("sys.modules", {"swisseph": mock_swe}):
        ephemeris.bootstrap_swisseph(
            data_path=str(tmp_path),
            path_version="se-test-v1",
            required_files=["sepl_18.se1"],
            validate_required_files=True,
        )

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["path_version"] == "se-test-v1"
    assert isinstance(data["path_hash"], str)
    assert len(data["path_hash"]) == 64


# ---------------------------------------------------------------------------
# AC2 — Erreur 5xx normalisée: path absent
# ---------------------------------------------------------------------------


def test_status_503_when_data_path_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """SWISSEPH_DATA_PATH vide → 503 code=ephemeris_data_missing."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    try:
        ephemeris.bootstrap_swisseph(data_path="", path_version="v1")
    except ephemeris.EphemerisDataMissingError:
        pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "ephemeris_data_missing"
    assert "message" in error

    # Verify metric
    count = get_counter_sum_in_window(ephemeris.METRIC_DATA_MISSING, timedelta(minutes=1))
    assert count == 1.0


def test_status_503_when_data_path_nonexistent(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """SWISSEPH_DATA_PATH inexistant → 503 code=ephemeris_data_missing."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)
    bad_path = str(tmp_path / "no_such_dir")

    try:
        ephemeris.bootstrap_swisseph(data_path=bad_path, path_version="v1")
    except ephemeris.EphemerisDataMissingError:
        pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "ephemeris_data_missing"


def test_status_503_response_does_not_contain_filesystem_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """La réponse 5xx ne doit pas exposer le path brut du filesystem (sans PII)."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)
    bad_path = str(tmp_path / "secret_internal_path")

    try:
        ephemeris.bootstrap_swisseph(data_path=bad_path, path_version="v1")
    except ephemeris.EphemerisDataMissingError:
        pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    body = response.text
    # Le path brut ne doit pas apparaître dans la réponse HTTP
    assert "secret_internal_path" not in body


# ---------------------------------------------------------------------------
# AC3 — Erreur 5xx normalisée: init runtime échouée
# ---------------------------------------------------------------------------


def test_status_503_when_swisseph_init_fails(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Échec d'initialisation pyswisseph → 503 code=swisseph_init_failed."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    mock_swe = _make_swe_mock(set_ephe_path_side_effect=RuntimeError("swe error"))
    with patch.dict("sys.modules", {"swisseph": mock_swe}):
        try:
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
        except ephemeris.SwissEphInitError:
            pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "swisseph_init_failed"
    assert "message" in error

    # Verify metric
    count = get_counter_sum_in_window(ephemeris.METRIC_INIT_ERRORS, timedelta(minutes=1))
    assert count == 1.0


def test_status_503_when_swisseph_module_not_installed(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """pyswisseph non installé → 503 code=swisseph_init_failed."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    with patch.dict("sys.modules", {"swisseph": None}):
        try:
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
        except ephemeris.SwissEphInitError:
            pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "swisseph_init_failed"


# ---------------------------------------------------------------------------
# Enabled mais bootstrap non appelé
# ---------------------------------------------------------------------------


def test_status_503_when_enabled_but_not_initialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SwissEph activé mais bootstrap non appelé → 503 swisseph_not_initialized."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)
    # _reset_ephemeris_state fixture garantit que bootstrap_result est None

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "swisseph_not_initialized"


# ---------------------------------------------------------------------------
# AC4 — Metadata in accurate requests
# ---------------------------------------------------------------------------


def test_natal_calculate_includes_ephemeris_version_in_meta(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """AC4: metadata.ephemeris_path_version est présent dans les réponses engine."""
    monkeypatch.setattr("app.api.v1.routers.astrology_engine.settings.swisseph_enabled", True)
    monkeypatch.setattr("app.api.v1.routers.astrology_engine.settings.swisseph_pro_mode", True)

    # Mock successful bootstrap
    mock_swe = _make_swe_mock()
    required_file = tmp_path / "sepl_18.se1"
    required_file.write_text("fixture", encoding="utf-8")
    with patch.dict("sys.modules", {"swisseph": mock_swe}):
        ephemeris.bootstrap_swisseph(
            data_path=str(tmp_path),
            path_version="se-2024-test",
            required_files=["sepl_18.se1"],
            validate_required_files=True,
        )

    # We use /v1/astrology-engine/natal/prepare as it's easier to call without DB
    payload = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "birth_place": "Paris",
        "birth_timezone": "Europe/Paris",
    }

    response = client.post("/v1/astrology-engine/natal/prepare", json=payload)

    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["ephemeris_path_version"] == "se-2024-test"
    assert isinstance(meta["ephemeris_path_hash"], str)
    assert len(meta["ephemeris_path_hash"]) == 64


def test_natal_calculate_metadata_is_none_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """metadata.ephemeris_path_version est null quand SwissEph est désactivé."""
    monkeypatch.setattr("app.api.v1.routers.astrology_engine.settings.swisseph_enabled", False)

    payload = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "birth_place": "Paris",
        "birth_timezone": "Europe/Paris",
    }

    response = client.post("/v1/astrology-engine/natal/prepare", json=payload)

    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["ephemeris_path_version"] is None
    assert meta["ephemeris_path_hash"] is None


# ---------------------------------------------------------------------------
# Exception handlers (AC2, AC3 via propagation d'exception HTTP)
# ---------------------------------------------------------------------------


def test_exception_handler_ephemeris_data_missing() -> None:
    """EphemerisDataMissingError propagée → 503 normalisé via exception handler."""
    from app.core.ephemeris import EphemerisDataMissingError

    @app.get("/test-ephemeris-data-missing")
    def _raise_data_missing():
        raise EphemerisDataMissingError("test path missing")

    try:
        response = client.get("/test-ephemeris-data-missing")
        assert response.status_code == 503
        error = response.json()["error"]
        assert error["code"] == "ephemeris_data_missing"
        assert "request_id" in error
    finally:
        app.routes[:] = [
            r for r in app.routes if getattr(r, "path", None) != "/test-ephemeris-data-missing"
        ]


def test_exception_handler_swisseph_init_error() -> None:
    """SwissEphInitError propagée → 503 normalisé via exception handler."""
    from app.core.ephemeris import SwissEphInitError

    @app.get("/test-swisseph-init-error")
    def _raise_init_error():
        raise SwissEphInitError("test init error")

    try:
        response = client.get("/test-swisseph-init-error")
        assert response.status_code == 503
        error = response.json()["error"]
        assert error["code"] == "swisseph_init_failed"
        assert "request_id" in error
    finally:
        app.routes[:] = [
            r for r in app.routes if getattr(r, "path", None) != "/test-swisseph-init-error"
        ]


# ---------------------------------------------------------------------------
# Story 21-2 — Payload normalisé: details + request_id
# ---------------------------------------------------------------------------


def test_exception_handler_ephemeris_data_missing_includes_details() -> None:
    """AC1: EphemerisDataMissingError handler inclut details.missing_file."""
    from app.core.ephemeris import EphemerisDataMissingError

    @app.get("/test-ephemeris-data-missing-details")
    def _raise_data_missing_with_file():
        raise EphemerisDataMissingError("required file missing", missing_file="sepl_18.se1")

    try:
        response = client.get("/test-ephemeris-data-missing-details")
        assert response.status_code == 503
        error = response.json()["error"]
        assert error["code"] == "ephemeris_data_missing"
        assert "details" in error
        assert isinstance(error["details"], dict)
        assert error["details"]["missing_file"] == "sepl_18.se1"
        assert "request_id" in error
    finally:
        app.routes[:] = [
            r
            for r in app.routes
            if getattr(r, "path", None) != "/test-ephemeris-data-missing-details"
        ]


def test_exception_handler_ephemeris_data_missing_details_empty_when_no_file() -> None:
    """EphemerisDataMissingError sans missing_file → details vide."""
    from app.core.ephemeris import EphemerisDataMissingError

    @app.get("/test-ephemeris-data-missing-no-file")
    def _raise_data_missing_no_file():
        raise EphemerisDataMissingError("path is empty")

    try:
        response = client.get("/test-ephemeris-data-missing-no-file")
        assert response.status_code == 503
        error = response.json()["error"]
        assert "details" in error
        assert error["details"] == {}
    finally:
        app.routes[:] = [
            r
            for r in app.routes
            if getattr(r, "path", None) != "/test-ephemeris-data-missing-no-file"
        ]


def test_exception_handler_swisseph_init_error_includes_details() -> None:
    """AC2: SwissEphInitError handler inclut details dict vide."""
    from app.core.ephemeris import SwissEphInitError

    @app.get("/test-swisseph-init-error-details")
    def _raise_init_error():
        raise SwissEphInitError("init failed")

    try:
        response = client.get("/test-swisseph-init-error-details")
        assert response.status_code == 503
        error = response.json()["error"]
        assert error["code"] == "swisseph_init_failed"
        assert "details" in error
        assert isinstance(error["details"], dict)
        assert "request_id" in error
    finally:
        app.routes[:] = [
            r for r in app.routes if getattr(r, "path", None) != "/test-swisseph-init-error-details"
        ]


def test_status_503_includes_details_and_request_id_when_data_path_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC1+2: /v1/ephemeris/status 503 inclut details et request_id."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    try:
        ephemeris.bootstrap_swisseph(data_path="", path_version="v1")
    except ephemeris.EphemerisDataMissingError:
        pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "ephemeris_data_missing"
    assert "details" in error
    assert isinstance(error["details"], dict)
    assert "request_id" in error


def test_status_503_includes_missing_file_in_details_when_file_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """AC1: /v1/ephemeris/status inclut details.missing_file quand fichier requis absent."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)
    mock_swe = _make_swe_mock()

    with patch.dict("sys.modules", {"swisseph": mock_swe}):
        try:
            ephemeris.bootstrap_swisseph(
                data_path=str(tmp_path),
                path_version="v1",
                required_files=["sepl_18.se1"],
                validate_required_files=True,
            )
        except ephemeris.EphemerisDataMissingError:
            pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "ephemeris_data_missing"
    assert error["details"].get("missing_file") == "sepl_18.se1"
    assert "request_id" in error


def test_status_503_includes_details_and_request_id_when_init_failed(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """AC2: /v1/ephemeris/status 503 init failure inclut details et request_id."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    mock_swe = _make_swe_mock(set_ephe_path_side_effect=RuntimeError("boom"))
    with patch.dict("sys.modules", {"swisseph": mock_swe}):
        try:
            ephemeris.bootstrap_swisseph(data_path=str(tmp_path), path_version="v1")
        except ephemeris.SwissEphInitError:
            pass

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "swisseph_init_failed"
    assert "details" in error
    assert isinstance(error["details"], dict)
    assert "request_id" in error


def test_status_503_not_initialized_includes_details_and_request_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """swisseph_not_initialized → details et request_id présents."""
    monkeypatch.setattr("app.api.v1.routers.ephemeris.settings.swisseph_enabled", True)

    response = client.get("/v1/ephemeris/status")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "swisseph_not_initialized"
    assert "details" in error
    assert "request_id" in error


def test_natal_endpoint_returns_503_when_swisseph_init_failed() -> None:
    """Integration: endpoint natal retourne 503 conforme quand SwissEphInitError propagée."""
    from app.core.ephemeris import SwissEphInitError

    @app.get("/test-natal-swisseph-init-error")
    def _simulate_natal_swisseph_error():
        raise SwissEphInitError("bootstrap failed")

    try:
        response = client.get("/test-natal-swisseph-init-error")
        assert response.status_code == 503
        error = response.json()["error"]
        assert error["code"] == "swisseph_init_failed"
        assert "details" in error
        assert "request_id" in error
        assert "message" in error
    finally:
        app.routes[:] = [
            r for r in app.routes if getattr(r, "path", None) != "/test-natal-swisseph-init-error"
        ]


def test_natal_endpoint_returns_503_when_ephemeris_data_missing() -> None:
    """Integration: endpoint natal retourne 503 conforme quand
    EphemerisDataMissingError est propagee."""
    from app.core.ephemeris import EphemerisDataMissingError

    @app.get("/test-natal-ephemeris-data-missing")
    def _simulate_natal_data_missing():
        raise EphemerisDataMissingError(
            "required file missing during natal calc", missing_file="seas_18.se1"
        )

    try:
        response = client.get("/test-natal-ephemeris-data-missing")
        assert response.status_code == 503
        error = response.json()["error"]
        assert error["code"] == "ephemeris_data_missing"
        assert error["details"]["missing_file"] == "seas_18.se1"
        assert "request_id" in error
    finally:
        app.routes[:] = [
            r
            for r in app.routes
            if getattr(r, "path", None) != "/test-natal-ephemeris-data-missing"
        ]


def test_natal_calculate_endpoint_returns_503_when_swisseph_init_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le vrai endpoint /natal/calculate renvoie 503 si SwissEphInitError est levée."""
    from app.core.ephemeris import SwissEphInitError

    def _raise_init_error(*args, **kwargs):  # noqa: ANN002, ANN003
        raise SwissEphInitError("bootstrap failed")

    monkeypatch.setattr(
        "app.api.v1.routers.astrology_engine.NatalCalculationService.calculate",
        _raise_init_error,
    )

    payload = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "birth_place": "Paris",
        "birth_timezone": "Europe/Paris",
    }
    response = client.post("/v1/astrology-engine/natal/calculate", json=payload)

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "swisseph_init_failed"
    assert error["details"] == {}
    assert "request_id" in error


def test_natal_calculate_endpoint_returns_503_when_ephemeris_data_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le vrai endpoint /natal/calculate renvoie 503 avec details.missing_file."""
    from app.core.ephemeris import EphemerisDataMissingError

    def _raise_data_missing(*args, **kwargs):  # noqa: ANN002, ANN003
        raise EphemerisDataMissingError(
            "required file missing during natal calc",
            missing_file="seas_18.se1",
        )

    monkeypatch.setattr(
        "app.api.v1.routers.astrology_engine.NatalCalculationService.calculate",
        _raise_data_missing,
    )

    payload = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "birth_place": "Paris",
        "birth_timezone": "Europe/Paris",
    }
    response = client.post("/v1/astrology-engine/natal/calculate", json=payload)

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "ephemeris_data_missing"
    assert error["details"]["missing_file"] == "seas_18.se1"
    assert "request_id" in error
