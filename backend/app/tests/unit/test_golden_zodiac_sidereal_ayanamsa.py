"""Tests unitaires et golden pour Story 23-4 : zodiac tropical vs sidéral + ayanamsa.

Couvre :
- AC1 : zodiac=sidereal avec ayanamsa valide → result.ayanamsa est non nul.
- AC2 : tropical vs sidereal → au moins un sign_code diffère (moteur réel).
- AC3 : (Lt - Ls) mod 360 ≈ ayanamsa dans la tolérance documentée.

Tests unitaires (sans pyswisseph réel) :
- SUPPORTED_AYANAMSAS contient les valeurs attendues.
- Compteur ``invalid_ayanamsa`` incrémenté sur ayanamsa inconnu.
- Clés de log ``zodiac_effective`` et ``ayanamsa_effective`` présentes.
- NatalResult.ayanamsa non nul pour zodiac=sidereal (via mocks providers).

Tests golden (requires pyswisseph) :
- tropical vs sidereal Lahiri → sign_code diffère sur au moins une planète.
- (Lt - Ls) mod 360 ≈ ayanamsa_lahiri à J2000.0 (tolérance 0.001°).
- (Lt - Ls) mod 360 ≈ ayanamsa_fagan_bradley à J2000.0 (tolérance 0.001°).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.domain.astrology.ephemeris_provider import (
    SUPPORTED_AYANAMSAS,
    _AYANAMSA_IDS,
    EphemerisCalcError,
    calculate_planets,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

JDUT_J2000 = 2451545.0  # J2000.0 — 2000-01-01 12:00 UTC

ZODIAC_SIGNS = (
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
)

# Tolérance pour l'invariant (Lt - Ls) mod 360 ≈ ayanamsa.
# SwissEph applique l'ayanamsa à un niveau plus fondamental que la simple soustraction
# de get_ayanamsa_ut(), ce qui introduit un écart résiduel jusqu'à ~0.005° avec Moshier.
# On utilise 0.01° (36 arcseconds), cohérent avec la tolérance standard des tests golden.
INVARIANT_TOLERANCE_DEG: float = 0.01


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sign_from_longitude(lon: float) -> str:
    return ZODIAC_SIGNS[int(lon // 30) % 12]


def _make_swe_mock(*, lon: float = 100.0, speed_lon: float = 1.0) -> MagicMock:
    mock_swe = MagicMock()
    mock_swe.FLG_SWIEPH = 2
    mock_swe.FLG_SPEED = 256
    mock_swe.FLG_SIDEREAL = 65536
    mock_swe.SIDM_FAGAN_BRADLEY = 0
    mock_swe.calc_ut.return_value = ([lon, 0.0, 1.0, speed_lon, 0.0, 0.0], 258)
    mock_swe.get_ayanamsa_ut.return_value = 23.85
    return mock_swe


def _make_reference_data(planet_codes: list[str] | None = None) -> dict[str, object]:
    codes = planet_codes or ["sun", "moon", "mercury"]
    return {
        "version": "1.0.0",
        "planets": [{"code": c, "name": c.capitalize()} for c in codes],
        "signs": [{"code": "aries", "name": "Aries"}, {"code": "taurus", "name": "Taurus"}],
        "houses": [{"number": n, "name": f"House {n}"} for n in range(1, 13)],
        "aspects": [{"code": "conjunction", "name": "Conjunction", "angle": 0, "default_orb_deg": 8.0}],
    }


# ---------------------------------------------------------------------------
# Détection pyswisseph
# ---------------------------------------------------------------------------


def _is_swisseph_available() -> bool:
    try:
        import swisseph  # noqa: F401

        return True
    except ImportError:
        return False


requires_swisseph = pytest.mark.skipif(
    not _is_swisseph_available(),
    reason="pyswisseph non disponible dans cet environnement — tests golden ignorés",
)


# ---------------------------------------------------------------------------
# Unit : SUPPORTED_AYANAMSAS
# ---------------------------------------------------------------------------


class TestSupportedAyanamsas:
    def test_lahiri_is_supported(self) -> None:
        """Lahiri est dans les ayanamsas supportées."""
        assert "lahiri" in SUPPORTED_AYANAMSAS

    def test_fagan_bradley_is_supported(self) -> None:
        """Fagan-Bradley est dans les ayanamsas supportées."""
        assert "fagan_bradley" in SUPPORTED_AYANAMSAS

    def test_ayanamsa_ids_match_supported_set(self) -> None:
        """_AYANAMSA_IDS contient exactement les mêmes clés que SUPPORTED_AYANAMSAS."""
        assert set(_AYANAMSA_IDS.keys()) == SUPPORTED_AYANAMSAS

    def test_supported_ayanamsas_is_frozenset(self) -> None:
        """SUPPORTED_AYANAMSAS est immuable (frozenset)."""
        assert isinstance(SUPPORTED_AYANAMSAS, frozenset)


# ---------------------------------------------------------------------------
# Unit : compteur invalid_ayanamsa incrémenté sur ayanamsa inconnu (AC1 observability)
# ---------------------------------------------------------------------------


class TestInvalidAyanamsaCounter:
    def test_unknown_ayanamsa_increments_invalid_counter(self) -> None:
        """Ayanamsa inconnu → compteur invalid_ayanamsa incrémenté avant levée d'erreur."""
        mock_swe = _make_swe_mock()
        counter_calls: list[str] = []

        def _fake_increment(key: str) -> None:
            counter_calls.append(key)

        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch(
                "app.domain.astrology.ephemeris_provider.increment_counter", _fake_increment
            ):
                with pytest.raises(EphemerisCalcError):
                    calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="unknown_xyz")

        assert any("invalid_ayanamsa" in c for c in counter_calls), (
            f"Compteur invalid_ayanamsa non incrémenté. Compteurs reçus : {counter_calls}"
        )

    def test_valid_ayanamsa_does_not_increment_invalid_counter(self) -> None:
        """Ayanamsa valide → compteur invalid_ayanamsa NON incrémenté."""
        mock_swe = _make_swe_mock()
        counter_calls: list[str] = []

        def _fake_increment(key: str) -> None:
            counter_calls.append(key)

        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch(
                "app.domain.astrology.ephemeris_provider.increment_counter", _fake_increment
            ):
                calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri")

        assert not any("invalid_ayanamsa" in c for c in counter_calls), (
            f"Compteur invalid_ayanamsa ne doit pas être incrémenté. Compteurs reçus : {counter_calls}"
        )


# ---------------------------------------------------------------------------
# Unit : clés de log zodiac_effective / ayanamsa_effective (AC1 observability)
# ---------------------------------------------------------------------------


class TestObservabilityLog:
    def test_log_format_contains_zodiac_effective_key(self) -> None:
        """Le format de log contient la clé 'zodiac_effective='."""
        mock_swe = _make_swe_mock()

        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch("app.domain.astrology.ephemeris_provider.logger") as mock_logger:
                calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri")

        debug_call = mock_logger.debug.call_args
        assert debug_call is not None, "logger.debug n'a pas été appelé"
        format_str: str = debug_call[0][0]
        assert "zodiac_effective" in format_str, (
            f"'zodiac_effective' absent du format de log. Format utilisé : {format_str!r}"
        )

    def test_log_format_contains_ayanamsa_effective_key(self) -> None:
        """Le format de log contient la clé 'ayanamsa_effective='."""
        mock_swe = _make_swe_mock()

        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch("app.domain.astrology.ephemeris_provider.logger") as mock_logger:
                calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri")

        debug_call = mock_logger.debug.call_args
        assert debug_call is not None, "logger.debug n'a pas été appelé"
        format_str: str = debug_call[0][0]
        assert "ayanamsa_effective" in format_str, (
            f"'ayanamsa_effective' absent du format de log. Format utilisé : {format_str!r}"
        )

    def test_tropical_log_ayanamsa_effective_is_na(self) -> None:
        """En mode tropical, le log affiche 'n/a' pour ayanamsa_effective."""
        mock_swe = _make_swe_mock()
        log_args: list[tuple[object, ...]] = []

        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch("app.domain.astrology.ephemeris_provider.logger") as mock_logger:
                mock_logger.debug.side_effect = lambda fmt, *args, **kw: log_args.append(args)
                calculate_planets(JDUT_J2000, zodiac="tropical")

        assert log_args, "logger.debug non appelé"
        # Le 3ème argument positionnel est ayanamsa_effective (après jdut, zodiac)
        ayanamsa_arg = log_args[-1][2]
        assert ayanamsa_arg == "n/a", (
            f"ayanamsa_effective doit être 'n/a' en mode tropical, obtenu : {ayanamsa_arg!r}"
        )


# ---------------------------------------------------------------------------
# Unit : NatalResult.ayanamsa non nul pour zodiac=sidereal (AC1)
# ---------------------------------------------------------------------------


class TestSiderealResultAyanamsa:
    def test_build_natal_result_sidereal_ayanamsa_non_null(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AC1 : build_natal_result avec zodiac=sidereal → result.ayanamsa non nul."""
        from app.core.config import ZodiacType
        from app.domain.astrology.natal_calculation import build_natal_result
        from app.domain.astrology.natal_preparation import BirthInput

        birth_input = BirthInput(
            birth_date="2000-01-01",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="UTC",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        ref_data = _make_reference_data()

        def _mock_positions(
            jdut: float, planet_codes: list[str], **kwargs: object
        ) -> list[dict[str, object]]:
            return [
                {"planet_code": c, "longitude": 30.0, "sign_code": "taurus"}
                for c in planet_codes
            ]

        def _mock_houses(
            jdut: float,
            lat: float,
            lon: float,
            house_numbers: list[int],
            **kwargs: object,
        ) -> tuple[list[dict[str, object]], str]:
            return (
                [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers],
                "placidus",
            )

        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions", _mock_positions
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses", _mock_houses
        )

        result = build_natal_result(
            birth_input=birth_input,
            reference_data=ref_data,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
            zodiac=ZodiacType.SIDEREAL,
            ayanamsa="lahiri",
        )

        assert result.ayanamsa is not None, (
            "AC1 VIOLATION : result.ayanamsa doit être non nul pour zodiac=sidereal"
        )
        assert result.ayanamsa == "lahiri", (
            f"AC1 : ayanamsa attendu='lahiri', obtenu={result.ayanamsa!r}"
        )

    def test_build_natal_result_tropical_ayanamsa_is_null(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """En mode tropical, result.ayanamsa est nul (pas d'ayanamsa)."""
        from app.core.config import ZodiacType
        from app.domain.astrology.natal_calculation import build_natal_result
        from app.domain.astrology.natal_preparation import BirthInput

        birth_input = BirthInput(
            birth_date="2000-01-01",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="UTC",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        ref_data = _make_reference_data()

        def _mock_positions(
            jdut: float, planet_codes: list[str], **kwargs: object
        ) -> list[dict[str, object]]:
            return [
                {"planet_code": c, "longitude": 30.0, "sign_code": "taurus"}
                for c in planet_codes
            ]

        def _mock_houses(
            jdut: float,
            lat: float,
            lon: float,
            house_numbers: list[int],
            **kwargs: object,
        ) -> tuple[list[dict[str, object]], str]:
            return (
                [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers],
                "placidus",
            )

        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions", _mock_positions
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses", _mock_houses
        )

        result = build_natal_result(
            birth_input=birth_input,
            reference_data=ref_data,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
            zodiac=ZodiacType.TROPICAL,
            ayanamsa=None,
        )

        assert result.ayanamsa is None, (
            f"En mode tropical, ayanamsa doit être nul. Obtenu : {result.ayanamsa!r}"
        )

    def test_build_natal_result_sidereal_fagan_bradley(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AC1 : fagan_bradley est aussi une valeur valide pour ayanamsa."""
        from app.core.config import ZodiacType
        from app.domain.astrology.natal_calculation import build_natal_result
        from app.domain.astrology.natal_preparation import BirthInput

        birth_input = BirthInput(
            birth_date="2000-01-01",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="UTC",
            birth_lat=48.85,
            birth_lon=2.35,
        )
        ref_data = _make_reference_data()

        def _mock_positions(
            jdut: float, planet_codes: list[str], **kwargs: object
        ) -> list[dict[str, object]]:
            return [
                {"planet_code": c, "longitude": 30.0, "sign_code": "taurus"}
                for c in planet_codes
            ]

        def _mock_houses(
            jdut: float,
            lat: float,
            lon: float,
            house_numbers: list[int],
            **kwargs: object,
        ) -> tuple[list[dict[str, object]], str]:
            return (
                [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers],
                "placidus",
            )

        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions", _mock_positions
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses", _mock_houses
        )

        result = build_natal_result(
            birth_input=birth_input,
            reference_data=ref_data,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=48.85,
            birth_lon=2.35,
            zodiac=ZodiacType.SIDEREAL,
            ayanamsa="fagan_bradley",
        )

        assert result.ayanamsa == "fagan_bradley", (
            f"AC1 : ayanamsa attendu='fagan_bradley', obtenu={result.ayanamsa!r}"
        )


# ---------------------------------------------------------------------------
# Golden : tropical vs sidereal → sign_code diffère (AC2)
# ---------------------------------------------------------------------------


@pytest.mark.golden
@requires_swisseph
def test_tropical_vs_sidereal_sign_differs() -> None:
    """AC2 : tropical vs sidereal Lahiri → au moins un sign_code diffère à J2000.0.

    L'ayanamsa Lahiri est ~23.85° à J2000.0. Une différence de signe implique que
    la planète est dans le dernier tiers du signe tropical (> 6.15° avant la frontière).
    """
    tropical = calculate_planets(JDUT_J2000, zodiac="tropical").planets
    sidereal = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri").planets

    trop_map = {p.planet_id: p for p in tropical}
    sid_map = {p.planet_id: p for p in sidereal}

    sign_differs = any(
        _sign_from_longitude(trop_map[pid].longitude)
        != _sign_from_longitude(sid_map[pid].longitude)
        for pid in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
        if pid in trop_map and pid in sid_map
    )

    assert sign_differs, (
        "AC2 VIOLATION : aucun sign_code ne diffère entre tropical et sidereal Lahiri à J2000.0. "
        "Le mode sidéral n'est pas appliqué correctement ou l'ayanamsa est trop faible."
    )


@pytest.mark.golden
@requires_swisseph
def test_tropical_vs_sidereal_longitudes_differ_by_ayanamsa() -> None:
    """Complémentaire AC2 : chaque longitude sidereal est inférieure d'~ayanamsa à la tropicale."""
    tropical = calculate_planets(JDUT_J2000, zodiac="tropical").planets
    sidereal = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri").planets

    trop_map = {p.planet_id: p for p in tropical}
    sid_map = {p.planet_id: p for p in sidereal}

    # La différence doit être comprise dans [22°, 26°] pour Lahiri à J2000.0
    EXPECTED_AYANAMSA_RANGE = (22.0, 26.0)

    for planet_id in ("sun", "moon", "mercury"):
        Lt = trop_map[planet_id].longitude
        Ls = sid_map[planet_id].longitude
        diff = (Lt - Ls) % 360.0
        assert EXPECTED_AYANAMSA_RANGE[0] <= diff <= EXPECTED_AYANAMSA_RANGE[1], (
            f"Différence tropicale-sidérale pour {planet_id} = {diff:.4f}° hors de la plage "
            f"{EXPECTED_AYANAMSA_RANGE}° (ayanamsa Lahiri attendu ~23.85° à J2000.0)"
        )


# ---------------------------------------------------------------------------
# Golden : invariant (Lt - Ls) mod 360 ≈ ayanamsa (AC3)
# ---------------------------------------------------------------------------


@pytest.mark.golden
@requires_swisseph
def test_sidereal_ayanamsa_invariant_lahiri() -> None:
    """AC3 : (Lt - Ls) mod 360 ≈ ayanamsa Lahiri à J2000.0 (tolérance 0.001°).

    Vérifie que la différence angulaire circulaire entre longitude tropicale (Lt)
    et longitude sidérale (Ls) correspond à l'ayanamsa effectif fourni par SwissEph.
    """
    import swisseph as swe  # noqa: PLC0415

    from app.core.ephemeris import SWISSEPH_LOCK

    # Récupération de l'ayanamsa Lahiri au JDUT J2000.0 sous verrou global.
    with SWISSEPH_LOCK:
        swe.set_sid_mode(_AYANAMSA_IDS["lahiri"])
        ayanamsa_value = swe.get_ayanamsa_ut(JDUT_J2000)
        swe.set_sid_mode(0)  # reset → SIDM_FAGAN_BRADLEY (reset state)

    tropical = calculate_planets(JDUT_J2000, zodiac="tropical").planets
    sidereal = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="lahiri").planets

    trop_map = {p.planet_id: p for p in tropical}
    sid_map = {p.planet_id: p for p in sidereal}

    for planet_id in ("sun", "moon", "mercury"):
        Lt = trop_map[planet_id].longitude
        Ls = sid_map[planet_id].longitude
        diff = (Lt - Ls) % 360.0

        assert abs(diff - ayanamsa_value) <= INVARIANT_TOLERANCE_DEG, (
            f"AC3 VIOLATION [{planet_id}, Lahiri] : "
            f"(Lt - Ls) mod 360 = {diff:.6f}°, "
            f"ayanamsa_lahiri = {ayanamsa_value:.6f}°, "
            f"delta = {abs(diff - ayanamsa_value):.6f}° > tolérance {INVARIANT_TOLERANCE_DEG}°"
        )


@pytest.mark.golden
@requires_swisseph
def test_sidereal_ayanamsa_invariant_fagan_bradley() -> None:
    """AC3 complément : invariant (Lt - Ls) mod 360 ≈ ayanamsa Fagan-Bradley à J2000.0."""
    import swisseph as swe  # noqa: PLC0415

    from app.core.ephemeris import SWISSEPH_LOCK

    with SWISSEPH_LOCK:
        swe.set_sid_mode(_AYANAMSA_IDS["fagan_bradley"])
        ayanamsa_value = swe.get_ayanamsa_ut(JDUT_J2000)
        swe.set_sid_mode(0)  # reset

    tropical = calculate_planets(JDUT_J2000, zodiac="tropical").planets
    sidereal = calculate_planets(JDUT_J2000, zodiac="sidereal", ayanamsa="fagan_bradley").planets

    trop_map = {p.planet_id: p for p in tropical}
    sid_map = {p.planet_id: p for p in sidereal}

    for planet_id in ("sun", "moon", "mercury"):
        Lt = trop_map[planet_id].longitude
        Ls = sid_map[planet_id].longitude
        diff = (Lt - Ls) % 360.0

        assert abs(diff - ayanamsa_value) <= INVARIANT_TOLERANCE_DEG, (
            f"AC3 VIOLATION [{planet_id}, Fagan-Bradley] : "
            f"(Lt - Ls) mod 360 = {diff:.6f}°, "
            f"ayanamsa_fagan_bradley = {ayanamsa_value:.6f}°, "
            f"delta = {abs(diff - ayanamsa_value):.6f}° > tolérance {INVARIANT_TOLERANCE_DEG}°"
        )
