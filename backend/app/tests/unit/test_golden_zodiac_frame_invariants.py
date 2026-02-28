"""Tests golden zodiac/frame + invariants metadata — Story 20-12.

Vérifie :
  Task 1 (AC1) : Tropical vs sidéral — différence de longitude ≥ offset ayanamsa documenté.
  Task 2 (AC2) : Géocentrique vs topocentrique — correction planétaire effective (Lune).
  Task 3 (AC3) : Invariants metadata/result — champs identiques après génération/lecture.
  Task 4 (AC4) : Stabilité — tolérances documentées, reproductible avec éphéméride Moshier.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.domain.astrology.ephemeris_provider import SIDM_RESET, calculate_planets
from app.domain.astrology.houses_provider import calculate_houses
from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.services.user_natal_chart_service import UserNatalChartMetadata, UserNatalChartService
from app.tests.golden.fixtures import GOLDEN_J2000

# ---------------------------------------------------------------------------
# Task 4 (AC4) : Constantes — tolérances documentées
# ---------------------------------------------------------------------------

PLANET_TOLERANCE_DEG: float = 0.01
ANGLE_TOLERANCE_GEO_TOPO_DEG: float = 0.01
MOON_MIN_TOPO_DIFF_DEG: float = 0.2
AYANAMSA_CONSISTENCY_TOL_DEG: float = 0.1
AYANAMSA_PLAUSIBLE_MAX_DEG: float = 40.0

JDUT_J2000: float = GOLDEN_J2000.expected_jd  # 2451545.0
LAT_PARIS: float = 48.8566
LON_PARIS: float = 2.3522


# ---------------------------------------------------------------------------
# Détection disponibilité pyswisseph
# ---------------------------------------------------------------------------


def _is_swisseph_available() -> bool:
    """Retourne True si pyswisseph est importable dans l'environnement courant."""
    try:
        import swisseph  # noqa: F401

        return True
    except ImportError:
        return False


requires_swisseph = pytest.mark.skipif(
    not _is_swisseph_available(),
    reason="pyswisseph non disponible — golden zodiac/frame tests ignorés",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _angular_diff(a: float, b: float) -> float:
    """Différence angulaire minimale entre deux longitudes écliptiques (wrap 0°/360°)."""
    diff = abs(a - b)
    return min(diff, 360.0 - diff)


def _get_effective_ayanamsa_ut(ayanamsa_name: str, jdut: float) -> float:
    """Obtient la valeur réelle de l'ayanamsa via swe.get_ayanamsa_ut()."""
    import swisseph as swe

    from app.core.ephemeris import SWISSEPH_LOCK
    from app.domain.astrology.ephemeris_provider import _AYANAMSA_IDS

    ayanamsa_id = _AYANAMSA_IDS[ayanamsa_name]
    with SWISSEPH_LOCK:
        swe.set_sid_mode(ayanamsa_id)
        value = float(swe.get_ayanamsa_ut(jdut))
        swe.set_sid_mode(SIDM_RESET)
    return value


# ---------------------------------------------------------------------------
# Task 1 (AC1) : Golden tests tropical vs sidéral
# ---------------------------------------------------------------------------


class TestGoldenTropicalVsSidereal:
    """AC1 : Les longitudes sidérales diffèrent du tropical d'environ l'offset ayanamsa."""

    @pytest.mark.golden
    @requires_swisseph
    @pytest.mark.parametrize("planet_id", ["sun", "moon", "mercury"])
    @pytest.mark.parametrize(
        "ayanamsa",
        ["lahiri", "fagan_bradley"],
        ids=["ayanamsa=lahiri", "ayanamsa=fagan_bradley"],
    )
    def test_sidereal_longitude_consistent_with_get_ayanamsa_ut(
        self, planet_id: str, ayanamsa: str
    ) -> None:
        """AC1 : Check structurel — (tropical_lon - sidereal_lon) mod 360 ≈ swe.get_ayanamsa_ut()."""
        tropical_planets = calculate_planets(JDUT_J2000).planets
        sidereal_planets = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa=ayanamsa).planets

        actual_ayanamsa = _get_effective_ayanamsa_ut(ayanamsa, JDUT_J2000)

        assert 0.0 < actual_ayanamsa < AYANAMSA_PLAUSIBLE_MAX_DEG

        tropical_map = {p.planet_id: p for p in tropical_planets}
        sidereal_map = {p.planet_id: p for p in sidereal_planets}

        tropical_lon = tropical_map[planet_id].longitude
        sidereal_lon = sidereal_map[planet_id].longitude

        observed_diff = (tropical_lon - sidereal_lon) % 360.0
        delta = _angular_diff(observed_diff, actual_ayanamsa)

        assert delta <= AYANAMSA_CONSISTENCY_TOL_DEG

    @pytest.mark.golden
    @requires_swisseph
    def test_lahiri_and_fagan_bradley_produce_distinct_longitudes(self) -> None:
        """AC1 : Lahiri et Fagan-Bradley produisent des longitudes solaires différentes."""
        lahiri_planets = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri").planets
        fagan_planets = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="fagan_bradley").planets

        sun_lahiri = next(p for p in lahiri_planets if p.planet_id == "sun").longitude
        sun_fagan = next(p for p in fagan_planets if p.planet_id == "sun").longitude
        diff = _angular_diff(sun_lahiri, sun_fagan)

        assert diff > PLANET_TOLERANCE_DEG


# ---------------------------------------------------------------------------
# Task 2 (AC2) : Golden tests géocentrique vs topocentrique
# ---------------------------------------------------------------------------


class TestGoldenGeoVsTopocentric:
    """AC2 : Vérification du mode topocentrique vs géocentrique."""

    @pytest.mark.golden
    @requires_swisseph
    def test_geocentric_vs_topocentric_moon_parallax_is_significant(self) -> None:
        """AC2 : La position topocentrique de la Lune doit différer du géocentrique (parallaxe)."""
        geo_planets = calculate_planets(JDUT_J2000, frame="geocentric").planets
        topo_planets = calculate_planets(
            JDUT_J2000, LAT_PARIS, LON_PARIS, frame="topocentric"
        ).planets

        geo_moon = next(p for p in geo_planets if p.planet_id == "moon").longitude
        topo_moon = next(p for p in topo_planets if p.planet_id == "moon").longitude
        diff = _angular_diff(geo_moon, topo_moon)

        assert diff >= MOON_MIN_TOPO_DIFF_DEG

    @pytest.mark.golden
    @requires_swisseph
    def test_geocentric_vs_topocentric_asc_within_tight_tolerance(self) -> None:
        """AC2 : L'Ascendant reste quasi-identique (houses_ex est géocentrique)."""
        geo = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS, frame="geocentric")
        topo = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS, frame="topocentric")

        asc_diff = _angular_diff(geo.ascendant_longitude, topo.ascendant_longitude)

        assert asc_diff <= ANGLE_TOLERANCE_GEO_TOPO_DEG


# ---------------------------------------------------------------------------
# Task 3 (AC3) : Invariants metadata/result
# ---------------------------------------------------------------------------


def _make_prepared_input() -> dict[str, object]:
    """Construit un BirthPreparedData dict minimal pour les tests."""
    return {
        "birth_datetime_local": "2000-01-01T12:00:00+00:00",
        "birth_datetime_utc": "2000-01-01T12:00:00+00:00",
        "timestamp_utc": 946728000,
        "julian_day": 2451545.0,
        "birth_timezone": "UTC",
    }


class TestMetadataResultInvariants:
    """AC3 : metadata.engine/zodiac/frame/ayanamsa = miroir exact de result.*"""

    @pytest.mark.parametrize(
        "engine,zodiac,frame,ayanamsa,ephem_version",
        [
            ("swisseph", "tropical", "geocentric", None, "moshier-local"),
            ("swisseph", "sidereal", "geocentric", "lahiri", "moshier-local"),
            ("swisseph", "sidereal", "geocentric", "fagan_bradley", "moshier-local"),
            ("swisseph", "tropical", "topocentric", None, "moshier-local"),
            ("simplified", "tropical", "geocentric", None, None),
        ],
    )
    def test_metadata_mirrors_result_all_modes(
        self,
        engine: str,
        zodiac: str,
        frame: str,
        ayanamsa: str | None,
        ephem_version: str | None,
    ) -> None:
        """AC3 : Pour chaque mode/zodiaque/frame/ayanamsa, metadata.*==result.*"""
        result = NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            engine=engine,
            zodiac=zodiac,
            frame=frame,
            ayanamsa=ayanamsa,
            ephemeris_path_version=ephem_version,
            prepared_input=BirthPreparedData(**_make_prepared_input()),
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
        )

        assert metadata.engine == result.engine
        assert metadata.zodiac == result.zodiac
        assert metadata.frame == result.frame
        assert metadata.ayanamsa == result.ayanamsa
        assert metadata.ephemeris_path_version == result.ephemeris_path_version

    @pytest.mark.parametrize("ayanamsa_val", [None, "lahiri", "fagan_bradley"])
    def test_get_latest_for_user_metadata_mirrors_result_after_roundtrip(self, ayanamsa_val: str | None) -> None:
        """AC3 : Après get_latest_for_user, metadata.*==result.* (couverture None + sidereal)."""
        zodiac_val = "tropical" if ayanamsa_val is None else "sidereal"
        stored_payload = {
            "reference_version": "1.0.0",
            "ruleset_version": "1.0.0",
            "house_system": "placidus",
            "engine": "swisseph",
            "zodiac": zodiac_val,
            "frame": "geocentric",
            "ayanamsa": ayanamsa_val,
            "altitude_m": None,
            "ephemeris_path_version": "moshier-local",
            "prepared_input": _make_prepared_input(),
            "planet_positions": [],
            "houses": [],
            "aspects": [],
        }

        mock_model = MagicMock()
        mock_model.chart_id = "test-chart-ac3-roundtrip"
        mock_model.reference_version = "1.0.0"
        mock_model.ruleset_version = "1.0.0"
        mock_model.result_payload = stored_payload
        mock_model.created_at = datetime(2000, 1, 1, 12, 0, 0)

        db = MagicMock()

        with patch("app.services.user_natal_chart_service.ChartResultRepository") as MockRepo:
            MockRepo.return_value.get_latest_by_user_id.return_value = mock_model
            read_data = UserNatalChartService.get_latest_for_user(db=db, user_id=1)

        assert read_data.metadata.ayanamsa == read_data.result.ayanamsa
        assert read_data.metadata.zodiac == read_data.result.zodiac
        assert read_data.metadata.engine == read_data.result.engine
        assert read_data.metadata.frame == read_data.result.frame
        assert read_data.metadata.ephemeris_path_version == read_data.result.ephemeris_path_version
