"""Tests unitaires pour le provider SwissEph de positions planétaires.

Story 20-2: Provider ephemeris_provider SwissEph pour positions planétaires

Couvre:
- Tests paramétrés par planète (10 corps) — chaque planète retourne les 4 champs (AC1)
- Test tropical par défaut — set_sid_mode NON appelé (AC2)
- Test sidéral Lahiri par défaut — set_sid_mode(1) appelé, reset effectué (AC3)
- Test rétrograde — speed_longitude < 0 → is_retrograde=True (AC4)
- Test erreur calc_ut → EphemerisCalcError normalisée (AC5)

Note: pyswisseph peut ne pas être installé dans l'environnement de test.
      Les tests utilisent patch.dict(sys.modules, ...) pour injecter un mock
      du module swisseph à la place d'un import réel.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from app.domain.astrology.ephemeris_provider import (
    EphemerisCalcError,
    PlanetData,
    _AYANAMSA_IDS,
    _PLANET_IDS,
    calculate_planets,
)

# ---------------------------------------------------------------------------
# Constantes de référence
# ---------------------------------------------------------------------------

JDUT_J2000 = 2451545.0  # J2000.0 — 1 janvier 2000, 12h TT

ALL_PLANETS = list(_PLANET_IDS.keys())

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_swe_mock(
    *,
    lon: float = 123.45,
    lat: float = -1.23,
    speed_lon: float = 0.98,
    retflag: int = 258,  # FLG_SWIEPH | FLG_SPEED
    calc_ut_side_effect=None,
    set_sid_mode_side_effect=None,
) -> MagicMock:
    """Crée un mock du module swisseph avec calc_ut configuré."""
    mock_swe = MagicMock()
    # Ensure constants are present in mock
    mock_swe.FLG_SWIEPH = 2
    mock_swe.FLG_SPEED = 256
    mock_swe.FLG_SIDEREAL = 65536
    mock_swe.SIDM_FAGAN_BRADLEY = 0

    if calc_ut_side_effect is not None:
        mock_swe.calc_ut.side_effect = calc_ut_side_effect
    else:
        # xx = [lon, lat, dist, speed_lon, speed_lat, speed_dist]
        mock_swe.calc_ut.return_value = (
            [lon, lat, 1.0, speed_lon, 0.01, 0.001],
            retflag,
        )
    if set_sid_mode_side_effect is not None:
        mock_swe.set_sid_mode.side_effect = set_sid_mode_side_effect
    return mock_swe


# ---------------------------------------------------------------------------
# Tests paramétrés par planète (AC1)
# ---------------------------------------------------------------------------


class TestPlanetDataFields:
    @pytest.mark.parametrize("planet_id", ALL_PLANETS)
    def test_planet_returns_all_required_fields(self, planet_id: str) -> None:
        """Chaque planète doit être retournée avec les 4 champs requis."""
        mock_swe = _make_swe_mock(lon=180.0, lat=0.5, speed_lon=1.2)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)

        planet_map = {p.planet_id: p for p in results}
        assert planet_id in planet_map, f"Planète {planet_id} absente du résultat"
        p = planet_map[planet_id]
        assert isinstance(p, PlanetData)
        assert isinstance(p.longitude, float)
        assert isinstance(p.latitude, float)
        assert isinstance(p.speed_longitude, float)
        assert isinstance(p.is_retrograde, bool)

    def test_returns_exactly_10_planets(self) -> None:
        """Le résultat doit contenir exactement 10 corps."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)
        assert len(results) == 10

    def test_planets_order_matches_definition(self) -> None:
        """L'ordre des planètes dans le résultat doit correspondre à _PLANET_IDS."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)
        assert [p.planet_id for p in results] == ALL_PLANETS

    @pytest.mark.parametrize("planet_id", ALL_PLANETS)
    def test_longitude_normalized_in_0_360(self, planet_id: str) -> None:
        """La longitude doit être dans [0, 360)."""
        # On teste différentes valeurs brutes incluant hors-range
        for raw_lon in [-10.0, 0.0, 90.0, 359.99, 370.0, 720.5]:
            mock_swe = _make_swe_mock(lon=raw_lon)
            with patch.dict("sys.modules", {"swisseph": mock_swe}):
                results = calculate_planets(JDUT_J2000)
            planet_map = {p.planet_id: p for p in results}
            lon = planet_map[planet_id].longitude
            assert 0.0 <= lon < 360.0, (
                f"Longitude {lon} hors [0, 360) pour planète {planet_id} "
                f"(valeur brute: {raw_lon})"
            )


# ---------------------------------------------------------------------------
# Test tropical par défaut (AC2)
# ---------------------------------------------------------------------------


class TestTropicalDefault:
    def test_no_zodiac_param_uses_tropical(self) -> None:
        """Sans paramètre zodiacal, le mode tropical est utilisé."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000)
        # set_sid_mode ne doit PAS être appelé en mode tropical
        mock_swe.set_sid_mode.assert_not_called()

    def test_zodiac_tropical_explicit(self) -> None:
        """zodiac='tropical' explicite — set_sid_mode non appelé."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000, zodiac="tropical")
        mock_swe.set_sid_mode.assert_not_called()

    def test_tropical_calc_ut_called_for_each_planet(self) -> None:
        """calc_ut est appelé une fois par planète en mode tropical."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000)
        assert mock_swe.calc_ut.call_count == 10


# ---------------------------------------------------------------------------
# Test sidéral — Lahiri par défaut (AC3)
# ---------------------------------------------------------------------------


class TestSiderealMode:
    def test_sidereal_calls_set_sid_mode_lahiri_by_default(self) -> None:
        """zodiac='sidereal' sans ayanamsa → set_sid_mode(1) = Lahiri."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000, zodiac="sidereal")
        # Premier appel doit être set_sid_mode(1) pour Lahiri
        assert mock_swe.set_sid_mode.call_count >= 2  # set + reset
        first_call_arg = mock_swe.set_sid_mode.call_args_list[0][0][0]
        assert first_call_arg == _AYANAMSA_IDS["lahiri"]

    def test_sidereal_resets_sid_mode_after_calc(self) -> None:
        """set_sid_mode(0) est appelé après le calcul pour reset global."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000, zodiac="sidereal")
        # Dernier appel à set_sid_mode doit être 0 (reset)
        last_call_arg = mock_swe.set_sid_mode.call_args_list[-1][0][0]
        assert last_call_arg == 0

    def test_sidereal_explicit_lahiri(self) -> None:
        """zodiac='sidereal' avec ayanamsa='lahiri' → set_sid_mode(1)."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri")
        first_call_arg = mock_swe.set_sid_mode.call_args_list[0][0][0]
        assert first_call_arg == 1

    def test_sidereal_calc_ut_called_for_each_planet(self) -> None:
        """calc_ut est appelé une fois par planète en mode sidéral."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_planets(JDUT_J2000, zodiac="sidereal")
        assert mock_swe.calc_ut.call_count == 10

    def test_sidereal_reset_called_even_on_calc_error(self) -> None:
        """Le reset set_sid_mode(0) est appelé même en cas d'erreur calc_ut."""
        mock_swe = _make_swe_mock(
            calc_ut_side_effect=RuntimeError("swe error")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError):
                calculate_planets(JDUT_J2000, zodiac="sidereal")
        # Le reset doit quand même avoir été appelé (via finally)
        last_call_arg = mock_swe.set_sid_mode.call_args_list[-1][0][0]
        assert last_call_arg == 0


# ---------------------------------------------------------------------------
# Test rétrograde (AC4)
# ---------------------------------------------------------------------------


class TestRetrograde:
    def test_negative_speed_means_retrograde(self) -> None:
        """speed_longitude < 0 → is_retrograde=True."""
        mock_swe = _make_swe_mock(speed_lon=-0.5)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)
        for p in results:
            assert p.is_retrograde is True
            assert p.speed_longitude == -0.5

    def test_positive_speed_means_direct(self) -> None:
        """speed_longitude > 0 → is_retrograde=False."""
        mock_swe = _make_swe_mock(speed_lon=1.5)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)
        for p in results:
            assert p.is_retrograde is False

    def test_zero_speed_is_not_retrograde(self) -> None:
        """speed_longitude = 0 → is_retrograde=False (stationnaire)."""
        mock_swe = _make_swe_mock(speed_lon=0.0)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)
        for p in results:
            assert p.is_retrograde is False

    def test_speed_longitude_matches_calc_ut_output(self) -> None:
        """speed_longitude doit correspondre exactement à xx[3] de calc_ut."""
        expected_speed = -1.234
        mock_swe = _make_swe_mock(speed_lon=expected_speed)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            results = calculate_planets(JDUT_J2000)
        for p in results:
            assert p.speed_longitude == expected_speed


# ---------------------------------------------------------------------------
# Test erreur SwissEph → EphemerisCalcError normalisée (AC5)
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_import_error_raises_ephemeris_calc_error(self) -> None:
        """Si pyswisseph n'est pas installé → EphemerisCalcError."""
        with patch("app.domain.astrology.ephemeris_provider._get_swe_module", side_effect=EphemerisCalcError("pyswisseph module is not installed")):
            with pytest.raises(EphemerisCalcError) as exc_info:
                calculate_planets(JDUT_J2000)
        assert exc_info.value.code == "ephemeris_calc_failed"
        assert "not installed" in exc_info.value.message

    def test_calc_ut_exception_raises_ephemeris_calc_error(self) -> None:
        """Exception dans calc_ut → EphemerisCalcError (pas de stack brute)."""
        mock_swe = _make_swe_mock(
            calc_ut_side_effect=RuntimeError("internal swe error")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError) as exc_info:
                calculate_planets(JDUT_J2000)
        assert exc_info.value.code == "ephemeris_calc_failed"
        assert "internal swe error" not in exc_info.value.message

    def test_calc_ut_negative_retflag_raises_ephemeris_calc_error(self) -> None:
        """retflag < 0 de calc_ut → EphemerisCalcError."""
        mock_swe = _make_swe_mock(retflag=-1)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError) as exc_info:
                calculate_planets(JDUT_J2000)
        assert exc_info.value.code == "ephemeris_calc_failed"

    def test_set_sid_mode_exception_raises_ephemeris_calc_error(self) -> None:
        """Exception dans set_sid_mode → EphemerisCalcError."""
        mock_swe = _make_swe_mock(
            set_sid_mode_side_effect=RuntimeError("sid error")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError) as exc_info:
                calculate_planets(JDUT_J2000, zodiac="sidereal")
        assert exc_info.value.code == "ephemeris_calc_failed"

    def test_unknown_ayanamsa_raises_ephemeris_calc_error(self) -> None:
        """Ayanamsa inconnu → EphemerisCalcError."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError) as exc_info:
                calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="unknown_system")
        assert exc_info.value.code == "ephemeris_calc_failed"

    def test_error_does_not_expose_raw_stack(self) -> None:
        """Le message d'erreur ne contient pas de stack trace brute."""
        mock_swe = _make_swe_mock(
            calc_ut_side_effect=RuntimeError("super secret internal path /srv/data")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(EphemerisCalcError) as exc_info:
                calculate_planets(JDUT_J2000)
        assert "/srv/data" not in exc_info.value.message
        assert "super secret" not in exc_info.value.message


# ---------------------------------------------------------------------------
# Smoke Test (Real library interaction)
# ---------------------------------------------------------------------------

@pytest.mark.skipif("swisseph" not in sys.modules and not patch.dict("sys.modules", {}), reason="swisseph not installed")
def test_swisseph_smoke_test() -> None:
    """Basic smoke test to ensure we can at least call the real library if present."""
    try:
        import swisseph as swe
        # Just a simple call to verify it doesn't crash
        results = calculate_planets(JDUT_J2000)
        assert len(results) == 10
    except (ImportError, EphemerisCalcError):
        pytest.skip("swisseph not fully configured or data files missing")
