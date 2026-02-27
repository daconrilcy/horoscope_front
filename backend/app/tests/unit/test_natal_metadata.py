"""Tests unitaires pour la metadata complète de calcul natal (story 20-5).

Couvre:
- NatalResult defaults backward-compat (engine, zodiac, frame, ayanamsa, ephemeris_path_version)
- build_natal_result() → champs metadata correctement propagés
- metadata sidereal: zodiac=sidereal, ayanamsa=lahiri
- metadata topocentric: frame=topocentric
- UserNatalChartMetadata: timezone_used, ephemeris_path_version
- Rétrocompatibilité: NatalResult.model_validate() accepte anciens payloads
- Champs historiques préservés
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.domain.astrology.natal_calculation import NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_reference_data(planet_codes: list[str] | None = None) -> dict[str, object]:
    codes = planet_codes or ["sun"]
    planets = [{"code": c, "name": c.capitalize()} for c in codes]
    signs = [{"code": "aries", "name": "Aries"}, {"code": "taurus", "name": "Taurus"}]
    houses = [{"number": n, "name": f"House {n}"} for n in range(1, 13)]
    aspects = [{"code": "conjunction", "name": "Conjunction", "angle": 0}]
    return {
        "version": "1.0.0",
        "planets": planets,
        "signs": signs,
        "houses": houses,
        "aspects": aspects,
    }


def _make_birth_input(
    birth_timezone: str = "Europe/Paris",
    birth_lat: float = 48.85,
    birth_lon: float = 2.35,
) -> BirthInput:
    return BirthInput(
        birth_date="1990-06-15",
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone=birth_timezone,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        place_resolved_id=1,
    )


def _make_prepared_data(birth_timezone: str = "Europe/Paris") -> BirthPreparedData:
    return BirthPreparedData(
        birth_datetime_local="1990-06-15T12:00:00+02:00",
        birth_datetime_utc="1990-06-15T10:00:00Z",
        timestamp_utc=645350400,
        julian_day=2448057.0,
        birth_timezone=birth_timezone,
    )


def _swisseph_positions_mock(
    jdut: float, planet_codes: list[str], **kwargs: object
) -> list[dict[str, object]]:
    """Mock positions: sun at 85° (gemini)."""
    return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]


def _swisseph_houses_mock(
    jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
) -> tuple[list[dict[str, object]], str]:
    """Mock houses: equal-spaced at 0, 30, ... 330°."""
    return [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers], "placidus"


# ---------------------------------------------------------------------------
# Task 4.1 — NatalResult defaults backward-compat
# ---------------------------------------------------------------------------

def test_natal_result_defaults() -> None:
    """NatalResult créé avec les seuls champs requis doit avoir les bons defaults."""
    result = NatalResult(
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        house_system="placidus",
        prepared_input=_make_prepared_data(),
        planet_positions=[],
        houses=[],
        aspects=[],
    )

    assert result.engine == "simplified"
    assert result.zodiac == "tropical"
    assert result.frame == "geocentric"
    assert result.ayanamsa is None
    assert result.ephemeris_path_version is None
    assert result.ephemeris_path_hash is None


def test_natal_result_model_validate_legacy_payload() -> None:
    """NatalResult.model_validate() accepte un payload ancien sans les nouveaux champs."""
    # Payload minimal tel que stocké avant story 20-5 (sans engine, zodiac, frame, etc.)
    legacy_payload = {
        "reference_version": "1.0.0",
        "ruleset_version": "1.0.0",
        "house_system": "placidus",
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
        # Pas de engine, zodiac, frame, ayanamsa, ephemeris_path_version
    }
    result = NatalResult.model_validate(legacy_payload)

    assert result.engine == "simplified"
    assert result.zodiac == "tropical"
    assert result.frame == "geocentric"
    assert result.ayanamsa is None
    assert result.ephemeris_path_version is None
    assert result.ephemeris_path_hash is None
    # Champs historiques préservés
    assert result.reference_version == "1.0.0"
    assert result.ruleset_version == "1.0.0"
    assert result.house_system == "placidus"


# ---------------------------------------------------------------------------
# Task 4.2 — build_natal_result avec engine=swisseph: champs metadata propagés
# ---------------------------------------------------------------------------

def test_build_natal_result_swisseph_engine_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """engine=swisseph → NatalResult.engine=swisseph, zodiac/frame/ayanamsa par défaut."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _swisseph_positions_mock,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _swisseph_houses_mock,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
    )

    assert result.engine == "swisseph"
    assert result.zodiac == "tropical"
    assert result.frame == "geocentric"
    assert result.ayanamsa is None
    assert result.ephemeris_path_version is None
    assert result.ephemeris_path_hash is None


def test_build_natal_result_ephemeris_path_version_propagated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ephemeris_path_version passé en paramètre est présent dans NatalResult."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _swisseph_positions_mock,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _swisseph_houses_mock,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        ephemeris_path_version="se2_2.10",
    )

    assert result.ephemeris_path_version == "se2_2.10"
    assert result.ephemeris_path_hash is None


def test_build_natal_result_ephemeris_path_hash_propagated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ephemeris_path_hash passé en paramètre est présent dans NatalResult."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _swisseph_positions_mock,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _swisseph_houses_mock,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        ephemeris_path_hash="abc123",
    )

    assert result.ephemeris_path_hash == "abc123"


def test_build_natal_result_simplified_engine_metadata() -> None:
    """engine=simplified → NatalResult.engine=simplified."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="simplified",
    )

    assert result.engine == "simplified"
    assert result.zodiac == "tropical"
    assert result.frame == "geocentric"
    assert result.ayanamsa is None
    assert result.ephemeris_path_version is None
    assert result.ephemeris_path_hash is None


# ---------------------------------------------------------------------------
# Task 4.3 — metadata sidereal: zodiac=sidereal, ayanamsa=lahiri
# ---------------------------------------------------------------------------

def test_build_natal_result_sidereal_zodiac_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """zodiac=sidereal est propagé dans NatalResult.zodiac, ayanamsa dans NatalResult.ayanamsa."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    captured_kwargs: dict[str, object] = {}

    def _positions_capture(
        jdut: float, planet_codes: list[str], **kwargs: object
    ) -> list[dict[str, object]]:
        captured_kwargs.update(kwargs)
        return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _positions_capture,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _swisseph_houses_mock,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        zodiac="sidereal",
        ayanamsa="lahiri",
    )

    assert result.zodiac == "sidereal"
    assert result.ayanamsa == "lahiri"
    # Vérifier que les kwargs ont été transmis au provider
    assert captured_kwargs.get("zodiac") == "sidereal"
    assert captured_kwargs.get("ayanamsa") == "lahiri"


def test_build_natal_result_sidereal_default_ayanamsa_lahiri(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """zodiac=sidereal sans ayanamsa explicite → ayanamsa=None dans NatalResult."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _swisseph_positions_mock,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _swisseph_houses_mock,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        zodiac="sidereal",
        ayanamsa=None,  # None → le provider utilise lahiri par défaut
    )

    assert result.zodiac == "sidereal"
    assert result.ayanamsa is None


# ---------------------------------------------------------------------------
# Task 4.4 — metadata topocentric: frame=topocentric propagé
# ---------------------------------------------------------------------------

def test_build_natal_result_topocentric_frame_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """frame=topocentric est propagé dans NatalResult.frame et transmis aux houses provider."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    captured_houses_kwargs: dict[str, object] = {}

    def _houses_capture(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict[str, object]], str]:
        captured_houses_kwargs.update(kwargs)
        cusps = [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers]
        return cusps, "placidus"

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _swisseph_positions_mock,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _houses_capture,
    )

    result = build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        frame="topocentric",
        altitude_m=None,
    )

    assert result.frame == "topocentric"
    # Vérifier que les kwargs ont été transmis au provider
    assert captured_houses_kwargs.get("frame") == "topocentric"
    assert captured_houses_kwargs.get("altitude_m") is None


def test_build_natal_result_topocentric_altitude_zero_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """altitude_m=None avec frame=topocentric → None propagé (le provider utilise 0)."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input()

    captured_alt: list[object] = []

    def _houses_capture(
        jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
    ) -> tuple[list[dict[str, object]], str]:
        captured_alt.append(kwargs.get("altitude_m"))
        cusps = [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers]
        return cusps, "placidus"

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _swisseph_positions_mock,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _houses_capture,
    )

    build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        frame="topocentric",
        altitude_m=None,
    )

    assert captured_alt == [None]


def test_build_natal_result_topocentric_propagates_frame_and_coordinates_to_planets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """frame/coords topocentriques sont propagés au provider planétaire SwissEph."""
    ref_data = _make_reference_data()
    birth_input = _make_birth_input(birth_lat=48.85, birth_lon=2.35)

    captured_positions_kwargs: dict[str, object] = {}

    def _positions_capture(
        jdut: float, planet_codes: list[str], **kwargs: object
    ) -> list[dict[str, object]]:
        captured_positions_kwargs.update(kwargs)
        return [{"planet_code": "sun", "longitude": 85.0, "sign_code": "gemini"}]

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions",
        _positions_capture,
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses",
        _swisseph_houses_mock,
    )

    build_natal_result(
        birth_input=birth_input,
        reference_data=ref_data,
        ruleset_version="1.0.0",
        engine="swisseph",
        birth_lat=48.85,
        birth_lon=2.35,
        frame="topocentric",
        altitude_m=120.0,
    )

    assert captured_positions_kwargs.get("frame") == "topocentric"
    assert captured_positions_kwargs.get("lat") == 48.85
    assert captured_positions_kwargs.get("lon") == 2.35
    assert captured_positions_kwargs.get("altitude_m") == 120.0


# ---------------------------------------------------------------------------
# Task 4.5 — UserNatalChartMetadata: timezone_used depuis prepared_input
# ---------------------------------------------------------------------------

def test_user_natal_chart_metadata_timezone_used() -> None:
    """UserNatalChartMetadata.timezone_used est dérivé de prepared_input.birth_timezone."""
    from app.services.user_natal_chart_service import UserNatalChartMetadata

    result = NatalResult(
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        house_system="placidus",
        engine="swisseph",
        zodiac="tropical",
        frame="geocentric",
        ayanamsa=None,
        ephemeris_path_version="se2_2.10",
        ephemeris_path_hash="hash-1",
        prepared_input=_make_prepared_data(birth_timezone="America/New_York"),
        planet_positions=[],
        houses=[],
        aspects=[],
    )

    metadata = UserNatalChartMetadata(
        reference_version=result.reference_version,
        ruleset_version=result.ruleset_version,
        house_system=result.house_system,
        engine=result.engine,
        zodiac=result.zodiac,
        frame=result.frame,
        ayanamsa=result.ayanamsa,
        timezone_used=result.prepared_input.birth_timezone,
        ephemeris_path_version=result.ephemeris_path_version,
        ephemeris_path_hash=result.ephemeris_path_hash,
    )

    assert metadata.timezone_used == "America/New_York"
    assert metadata.engine == "swisseph"
    assert metadata.zodiac == "tropical"
    assert metadata.frame == "geocentric"
    assert metadata.ayanamsa is None
    assert metadata.ephemeris_path_version == "se2_2.10"
    assert metadata.ephemeris_path_hash == "hash-1"


# ---------------------------------------------------------------------------
# Task 4.6 — ephemeris_path_version: None pour simplified, string pour swisseph
# ---------------------------------------------------------------------------

def test_user_natal_chart_metadata_ephemeris_path_version_none_for_simplified() -> None:
    """ephemeris_path_version=None pour le moteur simplified."""
    from app.services.user_natal_chart_service import UserNatalChartMetadata

    result = NatalResult(
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        house_system="placidus",
        engine="simplified",
        ephemeris_path_version=None,
        ephemeris_path_hash=None,
        prepared_input=_make_prepared_data(),
        planet_positions=[],
        houses=[],
        aspects=[],
    )

    metadata = UserNatalChartMetadata(
        reference_version=result.reference_version,
        ruleset_version=result.ruleset_version,
        house_system=result.house_system,
        engine=result.engine,
        zodiac=result.zodiac,
        frame=result.frame,
        ayanamsa=result.ayanamsa,
        timezone_used=result.prepared_input.birth_timezone,
        ephemeris_path_version=result.ephemeris_path_version,
        ephemeris_path_hash=result.ephemeris_path_hash,
    )

    assert metadata.ephemeris_path_version is None
    assert metadata.ephemeris_path_hash is None


# ---------------------------------------------------------------------------
# Task 4.7 — Rétrocompatibilité: champs historiques préservés dans metadata
# ---------------------------------------------------------------------------

def test_user_natal_chart_metadata_historical_fields_preserved() -> None:
    """reference_version, ruleset_version, house_system toujours présents (champs historiques)."""
    from app.services.user_natal_chart_service import UserNatalChartMetadata

    metadata = UserNatalChartMetadata(
        reference_version="v2.0",
        ruleset_version="v1.5",
        house_system="placidus",
    )

    # Champs historiques
    assert metadata.reference_version == "v2.0"
    assert metadata.ruleset_version == "v1.5"
    assert metadata.house_system == "placidus"
    # Nouveaux champs avec defaults
    assert metadata.engine == "simplified"
    assert metadata.zodiac == "tropical"
    assert metadata.frame == "geocentric"
    assert metadata.ayanamsa is None
    assert metadata.timezone_used == ""
    assert metadata.ephemeris_path_version is None
    assert metadata.ephemeris_path_hash is None


# ---------------------------------------------------------------------------
# Task 4.8 — NatalCalculationService extrait ephemeris_path_version du bootstrap
# ---------------------------------------------------------------------------

def test_natal_calculation_service_extracts_ephemeris_path_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NatalCalculationService.calculate() extrait path_version du bootstrap pour swisseph."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)

    mock_bootstrap = MagicMock()
    mock_bootstrap.success = True
    mock_bootstrap.error = None
    mock_bootstrap.path_version = "se2_2.10"
    mock_bootstrap.path_hash = "hash-se2"

    ref_data = _make_reference_data()
    captured_kwargs: dict[str, object] = {}

    def _mock_build_natal_result(**kwargs: object) -> NatalResult:
        captured_kwargs.update(kwargs)
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            engine="swisseph",
            ephemeris_path_version=str(kwargs.get("ephemeris_path_version")),
            ephemeris_path_hash=str(kwargs.get("ephemeris_path_hash")),
            prepared_input=_make_prepared_data(),
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
            natal_calculation_service.NatalCalculationService.calculate(
                db=db, birth_input=birth_input, accurate=True
            )

    assert captured_kwargs.get("ephemeris_path_version") == "se2_2.10"
    assert captured_kwargs.get("ephemeris_path_hash") == "hash-se2"


def test_natal_calculation_service_ephemeris_path_version_none_for_simplified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NatalCalculationService.calculate() passe ephemeris_path_version=None pour simplified."""
    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", False)

    ref_data = _make_reference_data()
    captured_kwargs: dict[str, object] = {}

    def _mock_build_natal_result(**kwargs: object) -> NatalResult:
        captured_kwargs.update(kwargs)
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            engine="simplified",
            ephemeris_path_version=None,
            ephemeris_path_hash=None,
            prepared_input=_make_prepared_data(),
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
            db=db, birth_input=birth_input, accurate=False, house_system="equal"
        )

    assert captured_kwargs.get("ephemeris_path_version") is None
    assert captured_kwargs.get("ephemeris_path_hash") is None
