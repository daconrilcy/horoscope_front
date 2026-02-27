"""Tests unitaires pour l'observabilité du moteur SwissEph.

Story 21-3: Observabilité perf engine SwissEph

Couvre :
- Métrique swisseph_calc_latency_ms émise sur calculate_planets() success/error (AC1)
- Métrique swisseph_houses_latency_ms émise sur calculate_houses() success/error (AC1)
- Compteur swisseph_errors_total{code} incrémenté sur erreurs calc (AC2)
- Logs structurés avec request_id, engine, ephe_version, ephe_hash sur erreur swisseph (AC2)
"""

from __future__ import annotations

import importlib
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

import app.infra.observability.metrics as metrics_module
from app.domain.astrology.ephemeris_provider import (
    METRIC_CALC_LATENCY,
    EphemerisCalcError,
    calculate_planets,
)
from app.domain.astrology.ephemeris_provider import (
    METRIC_ERRORS as EPHE_METRIC_ERRORS,
)
from app.domain.astrology.houses_provider import (
    METRIC_ERRORS as HOUSES_METRIC_ERRORS,
)
from app.domain.astrology.houses_provider import (
    METRIC_HOUSES_LATENCY,
    HousesCalcError,
    calculate_houses,
)
from app.infra.observability.metrics import (
    get_counter_sum_in_window,
    get_duration_values_in_window,
)

# ---------------------------------------------------------------------------
# Constantes de référence
# ---------------------------------------------------------------------------

JDUT_J2000 = 2451545.0
LAT_PARIS = 48.8566
LON_PARIS = 2.3522


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ephe_mock(
    *,
    lon: float = 123.45,
    lat: float = -1.23,
    speed_lon: float = 0.98,
    retflag: int = 258,
    calc_ut_side_effect=None,
) -> MagicMock:
    mock_swe = MagicMock()
    mock_swe.FLG_SWIEPH = 2
    mock_swe.FLG_SPEED = 256
    mock_swe.FLG_SIDEREAL = 65536
    mock_swe.SIDM_FAGAN_BRADLEY = 0
    if calc_ut_side_effect is not None:
        mock_swe.calc_ut.side_effect = calc_ut_side_effect
    else:
        mock_swe.calc_ut.return_value = ([lon, lat, 1.0, speed_lon, 0.01, 0.001], retflag)
    return mock_swe


_MOCK_CUSPS_RAW = (
    0.0,
    10.0,
    40.0,
    70.0,
    100.0,
    130.0,
    160.0,
    190.0,
    220.0,
    250.0,
    280.0,
    310.0,
    340.0,
)
_MOCK_ASCMC_RAW = (10.0, 280.0) + (0.0,) * 8


def _make_houses_mock(*, houses_ex_side_effect=None) -> MagicMock:
    mock_swe = MagicMock()
    if houses_ex_side_effect is not None:
        mock_swe.houses_ex.side_effect = houses_ex_side_effect
    else:
        mock_swe.houses_ex.return_value = (_MOCK_CUSPS_RAW, _MOCK_ASCMC_RAW)
    return mock_swe


# ---------------------------------------------------------------------------
# Fixture : réinitialiser métriques avant chaque test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_metrics() -> None:
    metrics_module.reset_metrics()
    yield
    metrics_module.reset_metrics()


# ---------------------------------------------------------------------------
# Tests métriques calculate_planets (AC1)
# ---------------------------------------------------------------------------


class TestEphemerisCalcLatency:
    def test_calc_latency_emitted_on_success(self) -> None:
        """swisseph_calc_latency_ms est enregistré après un calcul réussi."""
        mock_swe = _make_ephe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000)

        values = get_duration_values_in_window(METRIC_CALC_LATENCY, timedelta(minutes=1))
        assert len(values) == 1, "Une seule observation de latence attendue"
        assert values[0] >= 0.0, "Latence doit être positive ou nulle"

    def test_calc_latency_is_float(self) -> None:
        """La valeur de latence est un float en ms."""
        mock_swe = _make_ephe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000)

        values = get_duration_values_in_window(METRIC_CALC_LATENCY, timedelta(minutes=1))
        assert isinstance(values[0], float)

    def test_calc_latency_not_emitted_on_import_error(self) -> None:
        """swisseph_calc_latency_ms n'est PAS enregistré si le module est absent."""
        with patch.dict("sys.modules", {"swisseph": None}):
            with pytest.raises(EphemerisCalcError):
                calculate_planets(JDUT_J2000)

        values = get_duration_values_in_window(METRIC_CALC_LATENCY, timedelta(minutes=1))
        assert len(values) == 0, "Aucune latence ne doit être enregistrée en cas d'erreur"

    def test_calc_latency_not_emitted_on_calc_ut_error(self) -> None:
        """swisseph_calc_latency_ms n'est PAS enregistré si calc_ut échoue."""
        mock_swe = _make_ephe_mock(calc_ut_side_effect=RuntimeError("swe error"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError):
                calculate_planets(JDUT_J2000)

        values = get_duration_values_in_window(METRIC_CALC_LATENCY, timedelta(minutes=1))
        assert len(values) == 0


class TestEphemerisCalcErrors:
    def test_error_counter_incremented_on_calc_ut_exception(self) -> None:
        """swisseph_errors_total|code=ephemeris_calc_failed incrémenté sur erreur calc."""
        mock_swe = _make_ephe_mock(calc_ut_side_effect=RuntimeError("swe error"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError):
                calculate_planets(JDUT_J2000)

        count = get_counter_sum_in_window(
            f"{EPHE_METRIC_ERRORS}|code=ephemeris_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 1.0

    def test_error_counter_incremented_on_import_error(self) -> None:
        """swisseph_errors_total|code=ephemeris_calc_failed incrémenté si module absent."""
        with patch.dict("sys.modules", {"swisseph": None}):
            with pytest.raises(EphemerisCalcError):
                calculate_planets(JDUT_J2000)

        count = get_counter_sum_in_window(
            f"{EPHE_METRIC_ERRORS}|code=ephemeris_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 1.0

    def test_error_counter_incremented_on_negative_retflag(self) -> None:
        """swisseph_errors_total|code=ephemeris_calc_failed incrémenté sur retflag < 0."""
        mock_swe = _make_ephe_mock(retflag=-1)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError):
                calculate_planets(JDUT_J2000)

        count = get_counter_sum_in_window(
            f"{EPHE_METRIC_ERRORS}|code=ephemeris_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 1.0

    def test_error_counter_not_incremented_on_success(self) -> None:
        """swisseph_errors_total n'est PAS incrémenté en cas de succès."""
        mock_swe = _make_ephe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000)

        count = get_counter_sum_in_window(
            f"{EPHE_METRIC_ERRORS}|code=ephemeris_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 0.0


# ---------------------------------------------------------------------------
# Tests métriques calculate_houses (AC1)
# ---------------------------------------------------------------------------


class TestHousesCalcLatency:
    def test_houses_latency_emitted_on_success(self) -> None:
        """swisseph_houses_latency_ms est enregistré après un calcul réussi."""
        mock_swe = _make_houses_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)

        values = get_duration_values_in_window(METRIC_HOUSES_LATENCY, timedelta(minutes=1))
        assert len(values) == 1, "Une seule observation de latence attendue"
        assert values[0] >= 0.0

    def test_houses_latency_not_emitted_on_error(self) -> None:
        """swisseph_houses_latency_ms n'est PAS enregistré si houses_ex échoue."""
        mock_swe = _make_houses_mock(houses_ex_side_effect=RuntimeError("swe error"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(HousesCalcError):
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)

        values = get_duration_values_in_window(METRIC_HOUSES_LATENCY, timedelta(minutes=1))
        assert len(values) == 0


class TestHousesCalcErrors:
    def test_error_counter_incremented_on_houses_ex_exception(self) -> None:
        """swisseph_errors_total|code=houses_calc_failed incrémenté sur erreur houses_ex."""
        mock_swe = _make_houses_mock(houses_ex_side_effect=RuntimeError("swe error"))
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(HousesCalcError):
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)

        count = get_counter_sum_in_window(
            f"{HOUSES_METRIC_ERRORS}|code=houses_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 1.0

    def test_error_counter_incremented_on_import_error(self) -> None:
        """swisseph_errors_total|code=houses_calc_failed incrémenté si module absent."""
        with patch(
            "app.domain.astrology.houses_provider._get_swe_module",
            side_effect=HousesCalcError("pyswisseph module is not installed"),
        ):
            with pytest.raises(HousesCalcError):
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)

        count = get_counter_sum_in_window(
            f"{HOUSES_METRIC_ERRORS}|code=houses_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 1.0

    def test_error_counter_not_incremented_on_success(self) -> None:
        """swisseph_errors_total n'est PAS incrémenté sur succès."""
        mock_swe = _make_houses_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)

        count = get_counter_sum_in_window(
            f"{HOUSES_METRIC_ERRORS}|code=houses_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 0.0

    def test_error_counter_not_incremented_for_unsupported_system(self) -> None:
        """swisseph_errors_total n'est PAS incrémenté pour UnsupportedHouseSystemError."""
        from app.domain.astrology.houses_provider import UnsupportedHouseSystemError

        mock_swe = _make_houses_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(UnsupportedHouseSystemError):
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS, house_system="regiomontanus")

        count = get_counter_sum_in_window(
            f"{HOUSES_METRIC_ERRORS}|code=houses_calc_failed",
            timedelta(minutes=1),
        )
        assert count == 0.0


# ---------------------------------------------------------------------------
# Tests logs structurés — service level (AC2)
# ---------------------------------------------------------------------------


def _run_failing_natal_calc(
    caplog: pytest.LogCaptureFixture, request_id: str = "test-req-001"
) -> list:
    """Lance un calcul natal qui déclenche EphemerisCalcError et capture les logs ERROR."""
    from app.domain.astrology.natal_preparation import BirthInput
    from app.services.natal_calculation_service import NatalCalculationService

    service_module = importlib.import_module(NatalCalculationService.__module__)

    reference_data = {
        "version": "test-v1",
        "planets": [{"code": "sun"}],
        "signs": [{"code": "aries"}],
        "houses": [{"number": 1, "cusp_longitude": 0.0}],
        "aspects": [{"code": "conjunction", "angle": 0.0}],
    }
    birth_input = BirthInput(
        birth_date="1990-01-01",
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    mock_db = MagicMock()
    mock_bootstrap = MagicMock()
    mock_bootstrap.success = True
    mock_bootstrap.path_version = "se-test-v1"
    mock_bootstrap.path_hash = "abc123"

    with (
        patch.object(
            service_module.ReferenceDataService,
            "get_active_reference_data",
            return_value=reference_data,
        ),
        patch.object(service_module, "settings") as mock_settings,
        patch.object(
            service_module,
            "build_natal_result",
            side_effect=EphemerisCalcError("calc_ut failed"),
        ),
        patch.object(service_module.logger, "error") as mock_logger_error,
        patch(
            "app.core.ephemeris.get_bootstrap_result",
            return_value=mock_bootstrap,
        ),
    ):
        mock_settings.active_reference_version = "test-v1"
        mock_settings.ruleset_version = "rules-v1"
        mock_settings.swisseph_enabled = True
        mock_settings.natal_engine_default = "swisseph"
        mock_settings.natal_engine_simplified_enabled = False
        mock_settings.natal_engine_compare_enabled = False
        mock_settings.app_env = "development"
        mock_settings.natal_ruleset_default_zodiac = "tropical"
        mock_settings.natal_ruleset_default_ayanamsa = None
        mock_settings.natal_ruleset_default_frame = "geocentric"
        mock_settings.natal_ruleset_default_house_system = "placidus"

        with pytest.raises(Exception):
            NatalCalculationService.calculate(
                db=mock_db,
                birth_input=birth_input,
                accurate=True,
                request_id=request_id,
            )

    messages: list[str] = []
    for call in mock_logger_error.call_args_list:
        if not call.args:
            continue
        template = str(call.args[0])
        values = call.args[1:]
        try:
            rendered = template % values if values else template
        except (TypeError, ValueError):
            rendered = template
        messages.append(rendered)
    return [msg for msg in messages if "swisseph_calc_error" in msg]


class TestSwissephStructuredLogs:
    """Vérifie que les logs d'erreur contiennent les champs structurés requis (AC2)."""

    def test_error_log_emitted_on_ephemeris_calc_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Un log ERROR est émis quand EphemerisCalcError est capturée."""
        error_records = _run_failing_natal_calc(caplog, request_id="req-001")
        assert len(error_records) >= 1, "Au moins un log ERROR attendu lors d'une erreur swisseph"

    def test_error_log_contains_engine_field(self, caplog: pytest.LogCaptureFixture) -> None:
        """Le log d'erreur contient le champ engine."""
        error_records = _run_failing_natal_calc(caplog, request_id="req-002")
        assert len(error_records) >= 1
        log_msg = error_records[-1]
        assert "engine=swisseph" in log_msg, (
            f"'engine=swisseph' manquant dans le log. Message: {log_msg}"
        )

    def test_error_log_contains_ephe_version_field(self, caplog: pytest.LogCaptureFixture) -> None:
        """Le log d'erreur contient le champ ephe_version."""
        error_records = _run_failing_natal_calc(caplog, request_id="req-003")
        assert len(error_records) >= 1
        log_msg = error_records[-1]
        assert "ephe_version=se-test-v1" in log_msg, (
            f"'ephe_version=se-test-v1' manquant dans le log. Message: {log_msg}"
        )

    def test_error_log_contains_request_id_field(self, caplog: pytest.LogCaptureFixture) -> None:
        """Le log d'erreur contient le champ request_id."""
        error_records = _run_failing_natal_calc(caplog, request_id="req-004")
        assert len(error_records) >= 1
        log_msg = error_records[-1]
        assert "request_id=req-004" in log_msg, (
            f"'request_id=req-004' manquant dans le log. Message: {log_msg}"
        )

    def test_error_log_contains_ephe_hash_field(self, caplog: pytest.LogCaptureFixture) -> None:
        """Le log d'erreur contient explicitement le champ ephe_hash."""
        error_records = _run_failing_natal_calc(caplog, request_id="req-006")
        assert len(error_records) >= 1
        log_msg = error_records[-1]
        assert "ephe_hash=abc123" in log_msg, (
            f"'ephe_hash=abc123' manquant dans le log. Message: {log_msg}"
        )

    def test_error_log_contains_no_pii(self, caplog: pytest.LogCaptureFixture) -> None:
        """Le log d'erreur ne contient pas les coordonnées GPS brutes (pas de PII)."""
        error_records = _run_failing_natal_calc(caplog, request_id="req-005")
        assert len(error_records) >= 1
        log_msg = error_records[-1]
        assert "48.8566" not in log_msg, "Latitude GPS ne doit pas être dans le log"
        assert "2.3522" not in log_msg, "Longitude GPS ne doit pas être dans le log"
