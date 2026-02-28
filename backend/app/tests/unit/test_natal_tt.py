"""Tests unitaires pour les champs Terrestrial Time optionnels (story 22-2).

Couvre:
- _delta_t_seconds(): plages plausibles pour diverses années
- prepare_birth_data() avec tt_enabled=True: delta_t_sec > 0, jd_tt présent, time_scale='TT'
- prepare_birth_data() avec tt_enabled=False: delta_t_sec=None, jd_tt=None, time_scale='UT'
- BirthPreparedData: rétrocompatibilité sans les champs TT
- Métrique time_pipeline_tt_enabled_total incrémentée si tt_enabled=True
- NatalResult.time_scale propagé depuis prepared_input
- build_natal_result() propagation de tt_enabled
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.domain.astrology.natal_preparation import (
    METRIC_TT_ENABLED,
    BirthInput,
    BirthPreparedData,
    _delta_t_seconds,
    prepare_birth_data,
)
from app.infra.observability.metrics import get_counter_sum_in_window, reset_metrics

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_birth_input(birth_date: str = "1990-06-15") -> BirthInput:
    return BirthInput(
        birth_date=birth_date,
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_metrics()
    yield
    reset_metrics()


# ---------------------------------------------------------------------------
# _delta_t_seconds: plages plausibles
# ---------------------------------------------------------------------------


def test_delta_t_modern_year_plausible_range() -> None:
    """ΔT pour 2000–2026 doit être entre 60 et 80 secondes."""
    for year in [2000.0, 2010.0, 2020.0, 2026.0]:
        dt = _delta_t_seconds(year)
        assert 60.0 <= dt <= 80.0, f"ΔT={dt} hors plage plausible pour year={year}"


def test_delta_t_2005_2050_polynomial() -> None:
    """ΔT pour 2005–2050 doit être entre 60 et 120 secondes."""
    for year in [2005.0, 2030.0, 2050.0]:
        dt = _delta_t_seconds(year)
        assert 60.0 <= dt <= 120.0, f"ΔT={dt} hors plage plausible pour year={year}"


def test_delta_t_1980_range() -> None:
    """ΔT pour 1980 (pre-1986 polynomial) doit être entre 40 et 60 secondes."""
    dt = _delta_t_seconds(1980.0)
    assert 40.0 <= dt <= 60.0, f"ΔT={dt} hors plage plausible pour 1980"


def test_delta_t_pre_2005_range() -> None:
    """ΔT pour 1990–2004 doit être entre 55 et 70 secondes."""
    for year in [1990.0, 1995.0, 2000.0, 2004.0]:
        dt = _delta_t_seconds(year)
        assert 55.0 <= dt <= 70.0, f"ΔT={dt} hors plage plausible pour year={year}"


def test_delta_t_deterministic() -> None:
    """_delta_t_seconds() est déterministe: même entrée → même sortie."""
    assert _delta_t_seconds(2024.5) == _delta_t_seconds(2024.5)


def test_delta_t_historical_eras() -> None:
    """ΔT pour les périodes historiques (NASA polynomials).
    Vérifie que les résultats sont dans les ordres de grandeur attendus.
    """
    # Year 1000: NASA roughly ~1570s
    dt_1000 = _delta_t_seconds(1000.0)
    assert 1500.0 <= dt_1000 <= 1700.0

    # Year 1600: NASA roughly ~120s
    dt_1600 = _delta_t_seconds(1600.0)
    assert 100.0 <= dt_1600 <= 140.0

    # Year 1850: NASA roughly ~7s
    dt_1850 = _delta_t_seconds(1850.0)
    assert 5.0 <= dt_1850 <= 10.0


def test_prepare_birth_data_tt_precision_sub_daily() -> None:
    """Vérifie que delta_t_sec change légèrement avec l'heure (continuité)."""
    payload_noon = _make_birth_input("2020-01-01")
    payload_noon.birth_time = "12:00:00"
    result_noon = prepare_birth_data(payload_noon, tt_enabled=True)

    payload_evening = _make_birth_input("2020-01-01")
    payload_evening.birth_time = "23:00:00"
    result_evening = prepare_birth_data(payload_evening, tt_enabled=True)

    # DeltaT augmente d'environ 0.0003s par jour en 2020
    assert result_noon.delta_t_sec != result_evening.delta_t_sec
    assert abs(result_noon.delta_t_sec - result_evening.delta_t_sec) < 0.01


# ---------------------------------------------------------------------------
# prepare_birth_data() — branch tt_enabled=True
# ---------------------------------------------------------------------------


def test_prepare_birth_data_tt_enabled_true() -> None:
    """tt_enabled=True → delta_t_sec > 0, jd_tt présent, time_scale='TT'."""
    payload = _make_birth_input("1990-06-15")
    result = prepare_birth_data(payload, tt_enabled=True)

    assert result.delta_t_sec is not None
    assert result.delta_t_sec > 0.0
    assert result.jd_tt is not None
    assert result.jd_tt > result.jd_ut  # JD TT > JD UT (ΔT > 0)
    assert result.time_scale == "TT"


def test_prepare_birth_data_tt_jd_relation() -> None:
    """jd_tt = jd_ut + delta_t_sec / 86400 à tolérance numérique."""
    payload = _make_birth_input("2000-01-01")
    result = prepare_birth_data(payload, tt_enabled=True)

    expected_jd_tt = result.jd_ut + result.delta_t_sec / 86400.0
    assert abs(result.jd_tt - expected_jd_tt) < 1e-10


def test_prepare_birth_data_tt_delta_t_plausible_modern() -> None:
    """delta_t_sec pour une date moderne est dans la plage [60, 80] secondes."""
    payload = _make_birth_input("2020-07-01")
    result = prepare_birth_data(payload, tt_enabled=True)

    assert 60.0 <= result.delta_t_sec <= 80.0


def test_prepare_birth_data_tt_metric_incremented() -> None:
    """tt_enabled=True → métrique time_pipeline_tt_enabled_total incrémentée."""
    payload = _make_birth_input()
    prepare_birth_data(payload, tt_enabled=True)

    count = get_counter_sum_in_window(METRIC_TT_ENABLED, timedelta(minutes=1))
    assert count == 1.0


# ---------------------------------------------------------------------------
# prepare_birth_data() — branch tt_enabled=False (défaut)
# ---------------------------------------------------------------------------


def test_prepare_birth_data_tt_disabled_by_default() -> None:
    """Sans tt_enabled → delta_t_sec=None, jd_tt=None, time_scale='UT'."""
    payload = _make_birth_input()
    result = prepare_birth_data(payload)

    assert result.delta_t_sec is None
    assert result.jd_tt is None
    assert result.time_scale == "UT"


def test_prepare_birth_data_tt_enabled_false_explicit() -> None:
    """tt_enabled=False explicite → champs TT nuls."""
    payload = _make_birth_input()
    result = prepare_birth_data(payload, tt_enabled=False)

    assert result.delta_t_sec is None
    assert result.jd_tt is None
    assert result.time_scale == "UT"


def test_prepare_birth_data_tt_disabled_no_metric() -> None:
    """tt_enabled=False → métrique non incrémentée."""
    payload = _make_birth_input()
    prepare_birth_data(payload, tt_enabled=False)

    count = get_counter_sum_in_window(METRIC_TT_ENABLED, timedelta(minutes=1))
    assert count == 0.0


# ---------------------------------------------------------------------------
# BirthPreparedData — rétrocompatibilité
# ---------------------------------------------------------------------------


def test_birth_prepared_data_tt_fields_optional() -> None:
    """BirthPreparedData sans champs TT utilise les valeurs par défaut."""
    data = BirthPreparedData(
        birth_datetime_local="1990-06-15T12:00:00+02:00",
        birth_datetime_utc="1990-06-15T10:00:00Z",
        timestamp_utc=645350400,
        julian_day=2448057.0,
        birth_timezone="Europe/Paris",
    )

    assert data.delta_t_sec is None
    assert data.jd_tt is None
    assert data.time_scale == "UT"


def test_birth_prepared_data_model_validate_legacy_without_tt_fields() -> None:
    """model_validate() accepte un payload sans champs TT (rétrocompat)."""
    legacy = {
        "birth_datetime_local": "1990-06-15T12:00:00+02:00",
        "birth_datetime_utc": "1990-06-15T10:00:00Z",
        "timestamp_utc": 645350400,
        "julian_day": 2448057.0,
        "birth_timezone": "Europe/Paris",
    }
    data = BirthPreparedData.model_validate(legacy)

    assert data.delta_t_sec is None
    assert data.jd_tt is None
    assert data.time_scale == "UT"
    # Les champs canoniques 22.1 sont toujours dérivés
    assert data.jd_ut == 2448057.0
    assert data.timezone_used == "Europe/Paris"


# ---------------------------------------------------------------------------
# NatalResult.time_scale propagé via build_natal_result
# ---------------------------------------------------------------------------


def test_build_natal_result_time_scale_tt_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """build_natal_result(tt_enabled=True) → NatalResult.time_scale='TT'."""
    from app.domain.astrology.natal_calculation import build_natal_result

    def _mock_positions(jdut: float, planet_codes: list[str], **kwargs: object) -> list[dict]:
        return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]

    def _mock_houses(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict], str]:
        return [
            {"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers
        ], "placidus"

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions", _mock_positions
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses", _mock_houses
    )

    ref_data = {
        "version": "1.0.0",
        "planets": [{"code": "sun", "name": "Sun"}],
        "signs": [
            {"code": "aries"},
            {"code": "taurus"},
            {"code": "gemini"},
            {"code": "cancer"},
            {"code": "leo"},
            {"code": "virgo"},
            {"code": "libra"},
            {"code": "scorpio"},
            {"code": "sagittarius"},
            {"code": "capricorn"},
            {"code": "aquarius"},
            {"code": "pisces"},
        ],
        "houses": [{"number": n} for n in range(1, 13)],
        "aspects": [{"code": "conjunction", "angle": 0, "default_orb_deg": 8.0}],
    }
    birth_input = BirthInput(
        birth_date="1990-06-15",
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.85,
        birth_lon=2.35,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        tt_enabled=True,
    )

    assert result.time_scale == "TT"
    assert result.prepared_input.delta_t_sec is not None
    assert result.prepared_input.delta_t_sec > 0.0
    assert result.prepared_input.jd_tt is not None


def test_build_natal_result_time_scale_tt_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """build_natal_result(tt_enabled=False) → NatalResult.time_scale='UT', champs TT nuls."""
    from app.domain.astrology.natal_calculation import build_natal_result

    def _mock_positions(jdut: float, planet_codes: list[str], **kwargs: object) -> list[dict]:
        return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]

    def _mock_houses(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict], str]:
        return [
            {"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers
        ], "placidus"

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions", _mock_positions
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses", _mock_houses
    )

    ref_data = {
        "version": "1.0.0",
        "planets": [{"code": "sun", "name": "Sun"}],
        "signs": [
            {"code": "aries"},
            {"code": "taurus"},
            {"code": "gemini"},
            {"code": "cancer"},
            {"code": "leo"},
            {"code": "virgo"},
            {"code": "libra"},
            {"code": "scorpio"},
            {"code": "sagittarius"},
            {"code": "capricorn"},
            {"code": "aquarius"},
            {"code": "pisces"},
        ],
        "houses": [{"number": n} for n in range(1, 13)],
        "aspects": [{"code": "conjunction", "angle": 0, "default_orb_deg": 8.0}],
    }
    birth_input = BirthInput(
        birth_date="1990-06-15",
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.85,
        birth_lon=2.35,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        tt_enabled=False,
    )

    assert result.time_scale == "UT"
    assert result.prepared_input.delta_t_sec is None
    assert result.prepared_input.jd_tt is None


# ---------------------------------------------------------------------------
# NatalResult: rétrocompatibilité time_scale default
# ---------------------------------------------------------------------------


def test_natal_result_time_scale_default_is_ut() -> None: 
    """NatalResult sans time_scale explicite → time_scale='UT' (rétrocompat)."""
    from app.domain.astrology.natal_calculation import NatalResult
    from app.core.config import HouseSystemType

    result = NatalResult(
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        house_system=HouseSystemType.EQUAL,
        prepared_input=BirthPreparedData(
            birth_datetime_local="1990-06-15T12:00:00+02:00",
            birth_datetime_utc="1990-06-15T10:00:00Z",
            timestamp_utc=645350400,
            julian_day=2448057.0,
            birth_timezone="Europe/Paris",
        ),
        planet_positions=[],
        houses=[],
        aspects=[],
    )

    assert result.time_scale == "UT"


def test_natal_result_model_validate_legacy_without_time_scale() -> None:
    """NatalResult.model_validate() accepte payload sans time_scale (rétrocompat)."""
    from app.domain.astrology.natal_calculation import NatalResult
    from app.core.config import HouseSystemType

    legacy = {
        "reference_version": "1.0.0",
        "ruleset_version": "1.0.0",
        "house_system": HouseSystemType.EQUAL.value,
        "prepared_input": {
            "birth_datetime_local": "1990-06-15T12:00:00+02:00",
            "birth_datetime_utc": "1990-06-15T10:00:00Z",
            "timestamp_utc": 645350400,
            "julian_day": 2448057.0,
            "birth_timezone": "Europe/Paris",
        },
        "planet_positions": [],
        "houses": [],
        "aspects": [],
        # Pas de time_scale
    }
    result = NatalResult.model_validate(legacy)

    assert result.time_scale == "UT"
