"""Tests golden de référence pour le moteur SwissEph — Story 20-6.

Vérifie la précision et la stabilité temporelle du moteur ephemeris_provider
en comparant les calculs réels aux valeurs de référence gelées.

Ce fichier contient deux catégories de tests :

1. **Tests unitaires de conversion date → JDUT** (sans pyswisseph)
   Testent `prepare_birth_data()` pour les 3 cas principaux + cas historique.
   Ces tests sont TOUJOURS exécutés (pas de dépendance à pyswisseph).

2. **Tests golden d'intégration moteur** (avec pyswisseph réel)
   Appellent directement `calculate_planets()` de `ephemeris_provider.py` et
   comparent les positions à une tolérance absolue de 0.01°.
   Marqués `@pytest.mark.golden`.
   Ignorés automatiquement si pyswisseph n'est pas importable.

Acceptance Criteria couverts :
- AC1 : 3 cas golden Sun/Moon/Mercury respectent ± 0.01° de tolérance.
- AC2 : Cas timezone historique Europe/Paris 1973 (UTC+1, pas UTC+2) — JDUT correct.
- AC3 : Cas rétrograde Mercury (speed_longitude < 0 → is_retrograde=True).
- AC4 : La suite échoue EXPLICITEMENT si une regression dépasse 0.01°.

Paramètres de calcul :
  zodiac=tropical, frame=geocentric, flags=FLG_SWIEPH|FLG_SPEED
  Éphéméride : Moshier intégrée (sans fichiers .se1 obligatoires).
"""

from __future__ import annotations

import pytest

from app.domain.astrology.natal_preparation import BirthInput, prepare_birth_data
from app.tests.golden.fixtures import (
    ALL_GOLDEN_CASES,
    GOLDEN_1973_EUROPE_PARIS,
    GOLDEN_1980,
    GOLDEN_J2000,
    GOLDEN_MERCURY_RETROGRADE,
    GOLDEN_THREE_CASES,
    GoldenCase,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# AC4 : tolérance absolue de précision longitudinale.
# Toute dérive au-delà de cette valeur est une régression EXPLICITE.
LONGITUDE_TOLERANCE_DEG: float = 0.01
SPEED_TOLERANCE_DEG_DAY: float = 0.0001

# Tolérance sur le Jour Julien (~0.08 secondes).
JD_TOLERANCE: float = 0.000001


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
    reason="pyswisseph non disponible dans cet environnement — golden engine tests ignorés",
)


# ---------------------------------------------------------------------------
# Helpers de vérification
# ---------------------------------------------------------------------------


def _make_birth_input(case: GoldenCase) -> BirthInput:
    """Construit un BirthInput depuis un GoldenCase."""
    return BirthInput(
        birth_date=case.birth_date,
        birth_time=case.birth_time,
        birth_place="Golden Test Location",
        birth_timezone=case.birth_timezone,
    )


def _assert_longitude_tolerance(
    planet_id: str,
    actual: float,
    expected: float,
    tolerance: float = LONGITUDE_TOLERANCE_DEG,
) -> None:
    """Vérifie qu'une longitude est dans la tolérance absolue, en gérant le wrap 0°/360°.

    AC4 : Si la différence dépasse `tolerance`, le test échoue avec un message
    explicite identifiant la régression.
    """
    diff = abs(actual - expected)
    # Gestion du wrap-around : e.g. 0.005° vs 359.995° → diff = 0.010°
    if diff > 180.0:
        diff = 360.0 - diff

    assert diff <= tolerance, (
        f"RÉGRESSION DE PRÉCISION [{planet_id}] : "
        f"attendu={expected:.6f}°, obtenu={actual:.6f}°, "
        f"Δ={diff:.6f}° > tolérance={tolerance}° — "
        f"le moteur SwissEph a dérivé de la référence gelée (2026-02-26, Moshier)"
    )


def _assert_speed_tolerance(
    planet_id: str,
    actual: float,
    expected: float,
    tolerance: float = SPEED_TOLERANCE_DEG_DAY,
) -> None:
    """Vérifie qu'une vitesse est dans la tolérance absolue."""
    diff = abs(actual - expected)
    assert diff <= tolerance, (
        f"RÉGRESSION DE VITESSE [{planet_id}] : "
        f"attendu={expected:.8f}°/j, obtenu={actual:.8f}°/j, "
        f"Δ={diff:.8f}°/j > tolérance={tolerance}°/j"
    )


# ---------------------------------------------------------------------------
# Catégorie 1 : Tests unitaires de conversion date locale → JDUT
# (aucune dépendance à pyswisseph)
# ---------------------------------------------------------------------------


class TestDateConversionGolden:
    """Vérifie que prepare_birth_data() produit le JDUT attendu pour chaque cas golden.

    Ces tests n'appellent pas pyswisseph. Ils testent uniquement la conversion
    timezone locale → UTC → JD, indépendamment du moteur de calcul planétaire.
    """

    @pytest.mark.golden
    @pytest.mark.parametrize("case", GOLDEN_THREE_CASES, ids=[c.label for c in GOLDEN_THREE_CASES])
    def test_jd_matches_golden_value(self, case: GoldenCase) -> None:
        """Le JDUT calculé depuis la date/heure/timezone doit correspondre à la valeur golden."""
        prepared = prepare_birth_data(_make_birth_input(case))
        assert abs(prepared.julian_day - case.expected_jd) < JD_TOLERANCE, (
            f"JDUT incorrect pour [{case.label}] : "
            f"attendu={case.expected_jd:.6f}, obtenu={prepared.julian_day:.6f}, "
            f"Δ={abs(prepared.julian_day - case.expected_jd):.6f}"
        )

    @pytest.mark.golden
    def test_j2000_epoch_is_exactly_2451545(self) -> None:
        """J2000.0 doit produire JD = 2451545.0 (définition de l'époque)."""
        prepared = prepare_birth_data(_make_birth_input(GOLDEN_J2000))
        assert abs(prepared.julian_day - 2451545.0) < 0.001, (
            f"J2000.0 doit produire JD=2451545.0, obtenu {prepared.julian_day:.6f}"
        )

    @pytest.mark.golden
    def test_historical_europe_paris_1973_utc_offset(self) -> None:
        """AC2 : Europe/Paris en juillet 1973 était UTC+1 (heure d'été non encore en vigueur).

        La France n'a adopté l'heure d'été qu'en 1976. En juillet 1973,
        Europe/Paris = CET (UTC+1), et non CEST (UTC+2) comme aujourd'hui.
        Ce test vérifie que la base IANA historique (via zoneinfo/tzdata) est
        correctement utilisée pour convertir 09:00 → 08:00 UTC.
        """
        case = GOLDEN_1973_EUROPE_PARIS
        prepared = prepare_birth_data(_make_birth_input(case))

        # Vérification explicite : offset UTC+1 (pas UTC+2)
        assert "+01:00" in prepared.birth_datetime_local, (
            "En juillet 1973, Europe/Paris doit être UTC+1 (CET), pas UTC+2 (CEST). "
            f"Obtenu : {prepared.birth_datetime_local!r}"
        )

        # Vérification de l'heure UTC résultante : 09:00 +01:00 → 08:00 UTC
        assert "T08:00:00" in prepared.birth_datetime_utc, (
            "09:00 Europe/Paris en 1973 (UTC+1) doit donner 08:00 UTC. "
            f"Obtenu : {prepared.birth_datetime_utc!r}"
        )

        # Vérification du JDUT
        assert abs(prepared.julian_day - case.expected_jd) < JD_TOLERANCE, (
            f"JDUT cas historique 1973 incorrect : "
            f"attendu={case.expected_jd:.6f}, obtenu={prepared.julian_day:.6f}"
        )

    @pytest.mark.golden
    def test_historical_europe_paris_1973_jd_matches_golden(self) -> None:
        """AC2 : Le JDUT pour le cas historique 1973 est conforme à la valeur de référence."""
        case = GOLDEN_1973_EUROPE_PARIS
        prepared = prepare_birth_data(_make_birth_input(case))
        assert abs(prepared.julian_day - case.expected_jd) < JD_TOLERANCE, (
            f"JDUT historique 1973 : attendu={case.expected_jd:.6f}, "
            f"obtenu={prepared.julian_day:.6f}"
        )


# ---------------------------------------------------------------------------
# Catégorie 2 : Tests golden d'intégration moteur (pyswisseph réel)
# ---------------------------------------------------------------------------


class TestGoldenPlanetPositions:
    """Tests d'intégration golden via appels réels à ephemeris_provider.calculate_planets().

    Utilise l'éphéméride Moshier intégrée de pyswisseph (aucun fichier .se1 requis).
    Ces tests échouent EXPLICITEMENT (AC4) si une longitude dépasse 0.01° de la
    valeur de référence gelée (générée le 2026-02-26).
    """

    @pytest.mark.golden
    @requires_swisseph
    @pytest.mark.parametrize("case", GOLDEN_THREE_CASES, ids=[c.label for c in GOLDEN_THREE_CASES])
    def test_sun_moon_mercury_within_tolerance(self, case: GoldenCase) -> None:
        """AC1 : Sun, Moon et Mercury respectent une tolérance absolue de 0.01°."""
        from app.domain.astrology.ephemeris_provider import calculate_planets

        results = calculate_planets(case.expected_jd).planets
        result_map = {p.planet_id: p for p in results}
        golden_map = {pg.planet_id: pg for pg in case.planets}

        for planet_id in ("sun", "moon", "mercury"):
            if planet_id not in golden_map:
                continue
            actual = result_map[planet_id]
            expected = golden_map[planet_id]
            _assert_longitude_tolerance(planet_id, actual.longitude, expected.longitude)
            _assert_speed_tolerance(planet_id, actual.speed_longitude, expected.speed_longitude)

    @pytest.mark.golden
    @requires_swisseph
    def test_historical_timezone_1973_positions(self) -> None:
        """AC2 : Positions planétaires du cas historique 1973 conformes aux valeurs de référence."""
        from app.domain.astrology.ephemeris_provider import calculate_planets

        case = GOLDEN_1973_EUROPE_PARIS
        results = calculate_planets(case.expected_jd).planets
        result_map = {p.planet_id: p for p in results}
        golden_map = {pg.planet_id: pg for pg in case.planets}

        for planet_id in ("sun", "moon", "mercury"):
            if planet_id not in golden_map:
                continue
            actual = result_map[planet_id]
            expected = golden_map[planet_id]
            _assert_longitude_tolerance(planet_id, actual.longitude, expected.longitude)
            _assert_speed_tolerance(planet_id, actual.speed_longitude, expected.speed_longitude)

    @pytest.mark.golden
    @requires_swisseph
    def test_mercury_retrograde_speed_and_flag(self) -> None:
        """AC3 : Mercure en rétrograde → speed_longitude < 0 et is_retrograde=True."""
        from app.domain.astrology.ephemeris_provider import calculate_planets

        case = GOLDEN_MERCURY_RETROGRADE
        results = calculate_planets(case.expected_jd).planets
        result_map = {p.planet_id: p for p in results}

        mercury = result_map["mercury"]
        expected = next(pg for pg in case.planets if pg.planet_id == "mercury")

        assert mercury.speed_longitude < 0.0, (
            f"AC3 : Mercure doit être rétrograde (speed < 0) le {case.birth_date}. "
            f"Obtenu speed_longitude={mercury.speed_longitude:.6f}°/j"
        )
        assert mercury.is_retrograde is True, (
            "AC3 : is_retrograde doit être True lorsque speed_longitude < 0"
        )
        _assert_longitude_tolerance("mercury", mercury.longitude, expected.longitude)
        _assert_speed_tolerance("mercury", mercury.speed_longitude, expected.speed_longitude)

    @pytest.mark.golden
    @requires_swisseph
    def test_j2000_saturn_retrograde(self) -> None:
        """AC3 complément : Saturne en rétrograde dans le cas J2000.0."""
        from app.domain.astrology.ephemeris_provider import calculate_planets

        case = GOLDEN_J2000
        results = calculate_planets(case.expected_jd).planets
        result_map = {p.planet_id: p for p in results}

        saturn = result_map["saturn"]
        expected = next(pg for pg in case.planets if pg.planet_id == "saturn")

        assert saturn.speed_longitude < 0.0, (
            f"Saturne doit être rétrograde (speed < 0) le {case.birth_date}. "
            f"Obtenu speed_longitude={saturn.speed_longitude:.6f}°/j"
        )
        assert saturn.is_retrograde is True
        _assert_longitude_tolerance("saturn", saturn.longitude, expected.longitude)
        _assert_speed_tolerance("saturn", saturn.speed_longitude, expected.speed_longitude)

    @pytest.mark.golden
    @requires_swisseph
    def test_1980_mars_retrograde(self) -> None:
        """AC3 complément : Mars en rétrograde dans le cas 1980-03-21."""
        from app.domain.astrology.ephemeris_provider import calculate_planets

        case = GOLDEN_1980
        results = calculate_planets(case.expected_jd).planets
        result_map = {p.planet_id: p for p in results}

        mars = result_map["mars"]
        expected = next(pg for pg in case.planets if pg.planet_id == "mars")

        assert mars.speed_longitude < 0.0, (
            f"Mars doit être rétrograde (speed < 0) le {case.birth_date}. "
            f"Obtenu speed_longitude={mars.speed_longitude:.6f}°/j"
        )
        assert mars.is_retrograde is True
        _assert_longitude_tolerance("mars", mars.longitude, expected.longitude)
        _assert_speed_tolerance("mars", mars.speed_longitude, expected.speed_longitude)

    @pytest.mark.golden
    @requires_swisseph
    @pytest.mark.parametrize("case", ALL_GOLDEN_CASES, ids=[c.label for c in ALL_GOLDEN_CASES])
    def test_all_golden_cases_sun_in_tolerance(self, case: GoldenCase) -> None:
        """AC4 : Pour chaque cas golden contenant sun, la longitude est dans ± 0.01°.

        Ce test paramétré garantit qu'une régression au-delà de 0.01° sur n'importe
        quel cas golden échoue EXPLICITEMENT en CI (pas de skip silencieux).
        """
        from app.domain.astrology.ephemeris_provider import calculate_planets

        golden_map = {pg.planet_id: pg for pg in case.planets}
        if "sun" not in golden_map:
            pytest.skip(f"Cas {case.label!r} n'inclut pas de valeur golden pour 'sun'")

        results = calculate_planets(case.expected_jd).planets
        result_map = {p.planet_id: p for p in results}

        _assert_longitude_tolerance("sun", result_map["sun"].longitude, golden_map["sun"].longitude)
