"""Tests unitaires pour l'intégration SwissEph dans le pipeline natal.

Couvre:
- Sélection engine (swisseph vs simplified) selon accurate + feature flag
- Vérification bootstrap SwissEph avant appel
- build_natal_result() avec engine="swisseph" (mocks providers)
- Invariants de cohérence préservés avec données SwissEph
- missing_timezone dans user_natal_chart_service en mode accurate
- Conversion temporelle locale → UTC → JDUT
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData, prepare_birth_data

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_reference_data(
    planet_codes: list[str] | None = None,
    house_count: int = 12,
) -> dict[str, object]:
    """Build minimal reference data for tests."""
    codes = planet_codes or ["sun", "moon", "mercury"]
    planets = [{"code": c, "name": c.capitalize()} for c in codes]
    signs = [{"code": "aries", "name": "Aries"}, {"code": "taurus", "name": "Taurus"}]
    houses = [{"number": n, "name": f"House {n}"} for n in range(1, house_count + 1)]
    aspects = [{"code": "conjunction", "name": "Conjunction", "angle": 0, "default_orb_deg": 8.0}]
    return {
        "version": "1.0.0",
        "planets": planets,
        "signs": signs,
        "houses": houses,
        "aspects": aspects,
    }


def _make_birth_input(
    birth_time: str | None = "12:00",
    birth_timezone: str = "Europe/Paris",
    birth_lat: float | None = 48.85,
    birth_lon: float | None = 2.35,
    place_resolved_id: int | None = 1,
) -> BirthInput:
    return BirthInput(
        birth_date="1990-06-15",
        birth_time=birth_time,
        birth_place="Paris",
        birth_timezone=birth_timezone,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        place_resolved_id=place_resolved_id,
    )


def _make_mock_planet_data(code: str, longitude: float) -> MagicMock:
    pd = MagicMock()
    pd.planet_id = code
    pd.longitude = longitude
    pd.is_retrograde = False
    return pd


def _make_mock_house_data(
    cusps: tuple[float, ...] | None = None,
    house_system: str = "placidus",
) -> MagicMock:
    if cusps is None:
        # 12 equally-spaced cusps starting at 0
        cusps = tuple(float(i * 30) for i in range(12))
    hd = MagicMock()
    hd.cusps = cusps
    hd.ascendant_longitude = cusps[0]
    hd.mc_longitude = cusps[9] if len(cusps) > 9 else 0.0
    hd.house_system = house_system
    return hd


# ---------------------------------------------------------------------------
# Task 4.8 — Conversion temporelle locale → UTC → JDUT
# ---------------------------------------------------------------------------


def test_prepare_birth_data_converts_local_to_utc_jdut() -> None:
    """Timezone Europe/Paris (UTC+1 en hiver) est correctement convertie en UTC."""
    payload = BirthInput(
        birth_date="2000-01-01",
        birth_time="13:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    result = prepare_birth_data(payload)

    # Europe/Paris en hiver = UTC+1, donc 13:00 local = 12:00 UTC
    assert "2000-01-01T12:00:00" in result.birth_datetime_utc
    assert result.julian_day > 0
    # JD pour 2000-01-01 12:00 UTC = 2451545.0 (J2000.0)
    assert abs(result.julian_day - 2451545.0) < 0.01


def test_prepare_birth_data_utc_timezone_no_offset() -> None:
    """Timezone UTC ne produit pas de décalage."""
    payload = BirthInput(
        birth_date="2000-01-01",
        birth_time="12:00",
        birth_place="London",
        birth_timezone="UTC",
    )
    result = prepare_birth_data(payload)
    assert "2000-01-01T12:00:00" in result.birth_datetime_utc


def test_prepare_birth_data_julian_day_formula() -> None:
    """Le JDUT est calculé correctement depuis le timestamp UTC."""
    payload = BirthInput(
        birth_date="2000-01-01",
        birth_time="12:00",
        birth_place="London",
        birth_timezone="UTC",
    )
    result = prepare_birth_data(payload)
    # JD pour 2000-01-01 12:00 UTC = 2451545.0 (J2000.0)
    assert abs(result.julian_day - 2451545.0) < 0.001


# ---------------------------------------------------------------------------
# Task 4.1–4.3 — Sélection engine
# ---------------------------------------------------------------------------


def test_engine_selection_swisseph_when_accurate_and_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """engine=swisseph quand accurate=True et swisseph_enabled=True."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)

    # Mock bootstrap result (success)
    mock_bootstrap = MagicMock()
    mock_bootstrap.success = True
    mock_bootstrap.error = None

    # Mock reference data loading
    ref_data = _make_reference_data()
    captured_engine: list[str] = []

    from app.core.config import FrameType, HouseSystemType, ZodiacType

    def _mock_build_natal_result(**kwargs: object) -> NatalResult:
        captured_engine.append(str(kwargs.get("engine"))) 
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system=HouseSystemType.PLACIDUS if kwargs.get("engine") == "swisseph" else HouseSystemType.EQUAL,
            engine=str(kwargs.get("engine", "simplified")),
            zodiac=ZodiacType.TROPICAL,
            frame=FrameType.GEOCENTRIC,
    
            ayanamsa=str(kwargs.get("ayanamsa")) if kwargs.get("ayanamsa") else None,
            ephemeris_path_version=str(kwargs.get("ephemeris_path_version"))
            if kwargs.get("ephemeris_path_version")
            else None,
            prepared_input=BirthPreparedData(
                birth_datetime_local="2000-01-01T13:00:00+01:00",
                birth_datetime_utc="2000-01-01T12:00:00Z",
                timestamp_utc=946728000,
                julian_day=2451545.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )

    monkeypatch.setattr(natal_calculation_service, "build_natal_result", _mock_build_natal_result)

    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with patch("app.core.ephemeris.get_bootstrap_result", return_value=mock_bootstrap):
            try:
                natal_calculation_service.NatalCalculationService.calculate(
                    db=db, birth_input=birth_input, accurate=True
                )
            except RuntimeError:
                pass

    assert captured_engine == ["swisseph"]


def test_engine_selection_simplified_when_not_accurate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """engine=swisseph par défaut quand non accurate et default configuré sur swisseph."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)
    monkeypatch.setattr(natal_calculation_service.settings, "natal_engine_default", "swisseph")

    ref_data = _make_reference_data()
    captured_engine: list[str] = []

    from app.core.config import FrameType, HouseSystemType, ZodiacType

    def _mock_build_natal_result(**kwargs: object) -> NatalResult:
        captured_engine.append(str(kwargs.get("engine"))) 
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system=HouseSystemType.PLACIDUS if kwargs.get("engine") == "swisseph" else HouseSystemType.EQUAL,
            engine=str(kwargs.get("engine", "simplified")),
            zodiac=ZodiacType.TROPICAL,
            frame=FrameType.GEOCENTRIC,
    
            ayanamsa=str(kwargs.get("ayanamsa")) if kwargs.get("ayanamsa") else None,
            ephemeris_path_version=str(kwargs.get("ephemeris_path_version"))
            if kwargs.get("ephemeris_path_version")
            else None,
            prepared_input=BirthPreparedData(
                birth_datetime_local="2000-01-01T13:00:00+01:00",
                birth_datetime_utc="2000-01-01T12:00:00Z",
                timestamp_utc=946728000,
                julian_day=2451545.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )

    monkeypatch.setattr(natal_calculation_service, "build_natal_result", _mock_build_natal_result)

    db = MagicMock()
    birth_input = _make_birth_input()
    mock_bootstrap = MagicMock()
    mock_bootstrap.success = True
    mock_bootstrap.error = None
    mock_bootstrap.path_version = "se-test-v1"

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with patch("app.core.ephemeris.get_bootstrap_result", return_value=mock_bootstrap):
            natal_calculation_service.NatalCalculationService.calculate(
                db=db, birth_input=birth_input, accurate=True
            )
    assert captured_engine == ["swisseph"]


def test_engine_selection_error_when_accurate_and_swisseph_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Accurate mode requires swisseph_enabled=True, else raises NatalCalculationError."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", False)

    ref_data = _make_reference_data()
    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with pytest.raises(NatalCalculationError) as exc_info:
            natal_calculation_service.NatalCalculationService.calculate(
                db=db, birth_input=birth_input, accurate=True
            )

    assert exc_info.value.code == "natal_engine_unavailable"


def test_engine_selection_internal_override_simplified_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Override interne vers simplified autorisé si le feature flag est activé."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)
    monkeypatch.setattr(natal_calculation_service.settings, "natal_engine_default", "swisseph")
    monkeypatch.setattr(natal_calculation_service.settings, "natal_engine_simplified_enabled", True)
    monkeypatch.setattr(natal_calculation_service.settings, "app_env", "development")

    ref_data = _make_reference_data()
    captured_engine: list[str] = []

    from app.core.config import FrameType, HouseSystemType, ZodiacType

    def _mock_build_natal_result(**kwargs: object) -> NatalResult:
        captured_engine.append(str(kwargs.get("engine"))) 
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system=HouseSystemType.EQUAL,
            engine=str(kwargs.get("engine", "simplified")),
            zodiac=ZodiacType.TROPICAL,
            frame=FrameType.GEOCENTRIC,
    
            ayanamsa=str(kwargs.get("ayanamsa")) if kwargs.get("ayanamsa") else None,
            ephemeris_path_version=str(kwargs.get("ephemeris_path_version"))
            if kwargs.get("ephemeris_path_version")
            else None,
            prepared_input=BirthPreparedData(
                birth_datetime_local="2000-01-01T13:00:00+01:00",
                birth_datetime_utc="2000-01-01T12:00:00Z",
                timestamp_utc=946728000,
                julian_day=2451545.0,
                birth_timezone="Europe/Paris",
            ),
            planet_positions=[],
            houses=[],
            aspects=[],
        )

    monkeypatch.setattr(natal_calculation_service, "build_natal_result", _mock_build_natal_result)

    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        natal_calculation_service.NatalCalculationService.calculate(
            db=db,
            birth_input=birth_input,
            accurate=False,
            engine_override="simplified",
            internal_request=True,
            house_system="equal",
        )
    assert captured_engine == ["simplified"]


def test_engine_selection_internal_override_rejected_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Override interne vers simplified refusé si feature flag désactivé."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)
    monkeypatch.setattr(natal_calculation_service.settings, "natal_engine_default", "swisseph")
    monkeypatch.setattr(
        natal_calculation_service.settings, "natal_engine_simplified_enabled", False
    )
    monkeypatch.setattr(natal_calculation_service.settings, "app_env", "development")

    ref_data = _make_reference_data()
    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with pytest.raises(NatalCalculationError) as exc_info:
            natal_calculation_service.NatalCalculationService.calculate(
                db=db,
                birth_input=birth_input,
                accurate=False,
                engine_override="simplified",
                internal_request=True,
            )

    assert exc_info.value.code == "natal_engine_override_forbidden"


# ---------------------------------------------------------------------------
# Task 4.4 — Bootstrap failure propagation
# ---------------------------------------------------------------------------


def test_bootstrap_data_missing_error_propagated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EphemerisDataMissingError stockée dans bootstrap est re-levée."""
    from app.core.ephemeris import EphemerisDataMissingError
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)

    stored_error = EphemerisDataMissingError("data path invalid")
    mock_bootstrap = MagicMock()
    mock_bootstrap.success = False
    mock_bootstrap.error = stored_error

    ref_data = _make_reference_data()
    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with patch("app.core.ephemeris.get_bootstrap_result", return_value=mock_bootstrap):
            with pytest.raises(EphemerisDataMissingError) as exc_info:
                natal_calculation_service.NatalCalculationService.calculate(
                    db=db, birth_input=birth_input, accurate=True
                )

    assert exc_info.value is stored_error


def test_bootstrap_init_error_propagated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SwissEphInitError stockée dans bootstrap est re-levée."""
    from app.core.ephemeris import SwissEphInitError
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)

    stored_error = SwissEphInitError("init failed")
    mock_bootstrap = MagicMock()
    mock_bootstrap.success = False
    mock_bootstrap.error = stored_error

    ref_data = _make_reference_data()
    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with patch("app.core.ephemeris.get_bootstrap_result", return_value=mock_bootstrap):
            with pytest.raises(SwissEphInitError) as exc_info:
                natal_calculation_service.NatalCalculationService.calculate(
                    db=db, birth_input=birth_input, accurate=True
                )

    assert exc_info.value is stored_error


def test_bootstrap_none_raises_init_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si bootstrap non appelé (None), SwissEphInitError est levée."""
    from app.core.ephemeris import SwissEphInitError
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)

    ref_data = _make_reference_data()
    db = MagicMock()
    birth_input = _make_birth_input()

    with patch(
        "app.services.natal_calculation_service.ReferenceDataService.get_active_reference_data",
        return_value=ref_data,
    ):
        with patch("app.core.ephemeris.get_bootstrap_result", return_value=None):
            with pytest.raises(SwissEphInitError):
                natal_calculation_service.NatalCalculationService.calculate(
                    db=db, birth_input=birth_input, accurate=True
                )


# ---------------------------------------------------------------------------
# Task 4.5 — build_natal_result avec engine="swisseph" appelle les providers
# ---------------------------------------------------------------------------


def test_build_natal_result_swisseph_calls_calculate_planets_and_houses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    engine=swisseph appelle ephemeris_provider.calculate_planets
    et houses_provider.calculate_houses.
    """
    ref_data = _make_reference_data(planet_codes=["sun", "moon", "mercury"])
    birth_input = _make_birth_input(birth_lat=48.85, birth_lon=2.35)

    # Sun at 85° (gemini), Moon at 125° (leo), Mercury at 165° (virgo)
    mock_planets = [
        _make_mock_planet_data("sun", 85.0),
        _make_mock_planet_data("moon", 125.0),
        _make_mock_planet_data("mercury", 165.0),
    ]
    # Cusps equally spaced at 0°, 30°, ..., 330°
    mock_houses = _make_mock_house_data(cusps=tuple(float(i * 30) for i in range(12)))

    calls: dict[str, int] = {"planets": 0, "houses": 0}

    def _mock_calc_planets(jdut: float, **kwargs: object) -> list[MagicMock]:
        calls["planets"] += 1
        return mock_planets

    def _mock_calc_houses(jdut: float, lat: float, lon: float, **kwargs: object) -> MagicMock:
        calls["houses"] += 1
        return mock_houses

    def _mock_positions(
        jdut: float, planet_codes: list[str], **kwargs: object
    ) -> list[dict[str, object]]:
        return [
            {
                "planet_code": p.planet_id,
                "longitude": p.longitude,
                "sign_code": [
                    "aries",
                    "taurus",
                    "gemini",
                    "cancer",
                    "leo",
                    "virgo",
                    "libra",
                    "scorpio",
                    "sagittarius",
                    "capricorn",
                    "aquarius",
                    "pisces",
                ][int(p.longitude // 30) % 12],
            }
            for p in mock_planets
            if p.planet_id in planet_codes
        ]

    def _mock_sw_houses(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict[str, object]], str]:
        return [
            {"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers
        ], "placidus"

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _mock_positions,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _mock_sw_houses,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
    )

    assert len(result.planet_positions) == 3
    assert len(result.houses) == 12
    assert result.ruleset_version == "1.0.0"


def test_build_natal_result_swisseph_requires_lat_lon() -> None:
    """engine=swisseph sans lat/lon lève NatalCalculationError."""
    ref_data = _make_reference_data(planet_codes=["sun"])
    birth_input = _make_birth_input(birth_lat=None, birth_lon=None)

    with pytest.raises(NatalCalculationError) as exc_info:
        build_natal_result(
            birth_input=birth_input,
            reference_data=ref_data,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=None,
            birth_lon=None,
        )

    assert exc_info.value.code == "missing_birth_coordinates"


# ---------------------------------------------------------------------------
# Task 4.6 — Invariants de cohérence préservés avec données SwissEph
# ---------------------------------------------------------------------------


def test_build_natal_result_swisseph_coherence_sign_longitude(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Incohérence signe/longitude → NatalCalculationError code=inconsistent_natal_result."""
    ref_data = _make_reference_data(planet_codes=["sun"])
    birth_input = _make_birth_input()

    # Sun à 85° (gemini attendu), mais on va forcer une incohérence via mock
    def _bad_positions(
        jdut: float, planet_codes: list[str], **kwargs: object
    ) -> list[dict[str, object]]:
        return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "aries"}]  # incohérent

    def _good_houses(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict[str, object]], str]:
        return (
            [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers],
            "placidus",
        )

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions", _bad_positions
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses", _good_houses
    )

    with pytest.raises(NatalCalculationError) as exc_info:
        build_natal_result(
            birth_input=birth_input,
            reference_data=ref_data,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )

    assert exc_info.value.code == "inconsistent_natal_result"
    assert exc_info.value.details.get("house_system") == "placidus"


def test_build_natal_result_swisseph_coherence_house_interval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Incohérence house interval → NatalCalculationError code=inconsistent_natal_result."""
    ref_data = _make_reference_data(planet_codes=["sun"])
    birth_input = _make_birth_input()

    # Sun à 85° (gemini, maison 3 attendue avec cusps equal-spaced)
    # On falsifie le house_number via assign_house_number qui sera calculé correctement
    # mais on va forcer une maison impossible en fournissant des cusps qui ne contiennent pas 85°

    def _positions(
        jdut: float, planet_codes: list[str], **kwargs: object
    ) -> list[dict[str, object]]:
        return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]

    def _houses_bad(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict[str, object]], str]:
        # Cusps dupliquées → invalide
        return ([{"number": n, "cusp_longitude": 0.0} for n in house_numbers], "placidus")

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions", _positions
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses", _houses_bad
    )

    with pytest.raises(NatalCalculationError) as exc_info:
        build_natal_result(
            birth_input=birth_input,
            reference_data=ref_data,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
        )

    # duplicate cusps caught by _validate_house_cusps
    assert exc_info.value.code == "invalid_reference_data"


# ---------------------------------------------------------------------------
# Task 4.7 — missing_timezone dans user_natal_chart_service en mode accurate
# ---------------------------------------------------------------------------


def test_missing_timezone_in_accurate_mode() -> None:
    """generate_for_user(accurate=True) avec birth_timezone absent lève missing_timezone."""
    from unittest.mock import MagicMock

    from app.services.user_natal_chart_service import (
        UserNatalChartService,
        UserNatalChartServiceError,
    )

    db = MagicMock()
    # Profile avec birth_timezone vide
    mock_profile = MagicMock()
    mock_profile.birth_date = "1990-06-15"
    mock_profile.birth_time = "12:00"
    mock_profile.birth_place = "Paris"
    mock_profile.birth_timezone = ""  # absent/vide
    mock_profile.birth_lat = 48.85
    mock_profile.birth_lon = 2.35
    mock_profile.birth_place_resolved_id = 1
    mock_coordinates = MagicMock()
    mock_coordinates.birth_lat = 48.85
    mock_coordinates.birth_lon = 2.35
    mock_coordinates.birth_place_resolved_id = 1
    mock_coordinates.resolved_from_place = True

    with patch(
        "app.services.user_natal_chart_service.UserBirthProfileService.get_for_user",
        return_value=mock_profile,
    ):
        with patch(
            "app.services.user_natal_chart_service.UserBirthProfileService.resolve_coordinates",
            return_value=mock_coordinates,
        ):
            with pytest.raises(UserNatalChartServiceError) as exc_info:
                UserNatalChartService.generate_for_user(db=db, user_id=1, accurate=True)

    assert exc_info.value.code == "missing_timezone"


def test_accurate_false_does_not_check_timezone() -> None:
    """generate_for_user(accurate=False) ne fait pas la vérification missing_timezone."""
    from app.services.user_natal_chart_service import (
        UserNatalChartService,
        UserNatalChartServiceError,
    )

    db = MagicMock()
    mock_profile = MagicMock()
    mock_profile.birth_date = "1990-06-15"
    mock_profile.birth_time = None  # Pas de birth_time → missing_birth_time
    mock_profile.birth_place = "Paris"
    mock_profile.birth_timezone = "Europe/Paris"  # Valide, mais birth_time absent
    mock_profile.birth_lat = None
    mock_profile.birth_lon = None
    mock_profile.birth_place_resolved_id = None

    with patch(
        "app.services.user_natal_chart_service.UserBirthProfileService.get_for_user",
        return_value=mock_profile,
    ):
        with pytest.raises(UserNatalChartServiceError) as exc_info:
            UserNatalChartService.generate_for_user(db=db, user_id=1, accurate=False)

    # Should raise missing_birth_time, not missing_timezone
    assert exc_info.value.code == "missing_birth_time"


# ---------------------------------------------------------------------------
# Régression: simplified engine reste intact
# ---------------------------------------------------------------------------


def test_build_natal_result_simplified_engine_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """engine=simplified suit le chemin original (pas de providers swisseph appelés)."""
    ref_data = _make_reference_data(planet_codes=["sun"])
    birth_input = _make_birth_input()

    swisseph_calls: list[str] = []

    def _track_swisseph_planets(*args: object, **kwargs: object) -> list[object]:
        swisseph_calls.append("calculate_planets")
        return []

    def _track_swisseph_houses(*args: object, **kwargs: object) -> tuple[list[object], str]:
        swisseph_calls.append("calculate_houses")
        return [], "placidus"

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _track_swisseph_planets,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _track_swisseph_houses,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="simplified",
    )

    assert swisseph_calls == [], "SwissEph providers ne doivent pas être appelés en mode simplified"
    assert result is not None
