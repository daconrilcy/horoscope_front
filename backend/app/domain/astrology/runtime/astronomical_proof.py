# Contrat interne de preuve astronomique avant toute ouverture temporelle publique.
"""Centralise la preuve SwissEph, les cas golden sensibles et le gate CS-253."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from app.core.ephemeris import get_bootstrap_result
from app.domain.astrology.ephemeris_provider import calculate_planets
from app.domain.astrology.houses_provider import calculate_houses
from app.domain.astrology.swisseph_runtime import load_swisseph

PRODUCTION_ASTRONOMY_MODE = "swisseph"
CS253_GATE_MARKER = "cs253-blocked-by-cs250-astronomical-proof"
CS253_PUBLIC_GATE_STATE = "blocked"


@dataclass(frozen=True)
class AstronomicalTolerancePolicy:
    """Décrit les tolérances réutilisées par la preuve astronomique."""

    name: str
    longitude_degrees: float
    house_angle_degrees: float
    ayanamsa_degrees: float
    julian_day_days: float
    reason: str


PRODUCTION_TOLERANCE = AstronomicalTolerancePolicy(
    name="swisseph-sensitive-v1",
    longitude_degrees=0.01,
    house_angle_degrees=0.02,
    ayanamsa_degrees=0.01,
    julian_day_days=0.000001,
    reason=(
        "Tolérance serrée pour pyswisseph>=2.10.0 avec Moshier intégré; "
        "les maisons gardent une marge légèrement supérieure pour les angles."
    ),
)


@dataclass(frozen=True)
class GoldenInputProfile:
    """Paramètres d'entrée minimaux d'un cas astronomique sensible."""

    birth_date: str
    birth_time: str
    birth_timezone: str
    jd_ut: float
    latitude: float
    longitude: float
    house_system: str
    zodiac: str
    frame: str
    ayanamsa: str | None = None
    altitude_m: float | None = None


@dataclass(frozen=True)
class GoldenExpectedReference:
    """Valeurs SwissEph gelées vérifiées par les tests golden."""

    sun_longitude: float
    moon_longitude: float
    mercury_longitude: float
    ascendant_longitude: float
    mc_longitude: float
    cusp_1_longitude: float
    cusp_10_longitude: float
    ayanamsa_value: float | None = None


@dataclass(frozen=True)
class SensitiveGoldenCase:
    """Cas golden sensible avec objectif, tolérance et référence attendue."""

    golden_case_id: str
    objective: str
    input_profile: GoldenInputProfile
    expected_reference: GoldenExpectedReference
    tolerance: AstronomicalTolerancePolicy = PRODUCTION_TOLERANCE


@dataclass(frozen=True)
class EphemerisTrace:
    """Trace reproductible de l'environnement éphéméride chargé."""

    mode: str
    swisseph_version: str
    path_version: str | None
    path_hash: str | None
    reproducibility_note: str


@dataclass(frozen=True)
class PublicTemporalGate:
    """État du gate qui empêche CS-253 d'ouvrir une surface publique."""

    marker: str
    cs253_gate_state: Literal["blocked", "proof-closed", "risk-accepted-non-public"]
    authorized_public_temporal: bool
    reason: str


@dataclass(frozen=True)
class AstronomicalProofManifest:
    """Manifest de preuve conservé dans les artefacts de story."""

    mode: str
    authorized_public_temporal: bool
    tolerance_policy: AstronomicalTolerancePolicy
    ephemeris_trace: EphemerisTrace
    cs253_gate: PublicTemporalGate
    golden_cases: tuple[SensitiveGoldenCase, ...]


SENSITIVE_GOLDEN_CASES: tuple[SensitiveGoldenCase, ...] = (
    SensitiveGoldenCase(
        golden_case_id="paris-normal-placidus",
        objective="Cas Paris standard tropical Placidus.",
        input_profile=GoldenInputProfile(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_timezone="Europe/Paris",
            jd_ut=2448057.8541666665,
            latitude=48.8566,
            longitude=2.3522,
            house_system="placidus",
            zodiac="tropical",
            frame="geocentric",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=83.990280,
            moon_longitude=343.413125,
            mercury_longitude=65.440952,
            ascendant_longitude=138.870068,
            mc_longitude=35.519045,
            cusp_1_longitude=138.870068,
            cusp_10_longitude=35.519045,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="paris-dst-ambiguous",
        objective="Heure locale ambigue de fin DST Europe/Paris.",
        input_profile=GoldenInputProfile(
            birth_date="2024-10-27",
            birth_time="02:30",
            birth_timezone="Europe/Paris",
            jd_ut=2460610.5208333335,
            latitude=48.8566,
            longitude=2.3522,
            house_system="placidus",
            zodiac="tropical",
            frame="geocentric",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=214.080240,
            moon_longitude=154.351320,
            mercury_longitude=230.283789,
            ascendant_longitude=147.879810,
            mc_longitude=48.179520,
            cusp_1_longitude=147.879810,
            cusp_10_longitude=48.179520,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="paris-dst-nonexistent",
        objective="Heure locale apres saut DST Europe/Paris.",
        input_profile=GoldenInputProfile(
            birth_date="2024-03-31",
            birth_time="03:30",
            birth_timezone="Europe/Paris",
            jd_ut=2460400.5625,
            latitude=48.8566,
            longitude=2.3522,
            house_system="placidus",
            zodiac="tropical",
            frame="geocentric",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=10.826916,
            moon_longitude=255.613553,
            mercury_longitude=27.009673,
            ascendant_longitude=273.769477,
            mc_longitude=216.088823,
            cusp_1_longitude=273.769477,
            cusp_10_longitude=216.088823,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="high-latitude-placidus",
        objective="Latitude elevee avec maisons Placidus stables.",
        input_profile=GoldenInputProfile(
            birth_date="1985-01-10",
            birth_time="12:00",
            birth_timezone="Atlantic/Reykjavik",
            jd_ut=2446076.0,
            latitude=64.1466,
            longitude=-21.9426,
            house_system="placidus",
            zodiac="tropical",
            frame="geocentric",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=290.197152,
            moon_longitude=154.350058,
            mercury_longitude=268.369213,
            ascendant_longitude=340.090263,
            mc_longitude=268.173542,
            cusp_1_longitude=340.090263,
            cusp_10_longitude=268.173542,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="lahiri-sidereal",
        objective="Mode sideral Lahiri et trace d'ayanamsa.",
        input_profile=GoldenInputProfile(
            birth_date="2000-01-01",
            birth_time="12:00",
            birth_timezone="UTC",
            jd_ut=2451545.0,
            latitude=28.6139,
            longitude=77.2090,
            house_system="placidus",
            zodiac="sidereal",
            frame="geocentric",
            ayanamsa="lahiri",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=256.515697,
            moon_longitude=199.470553,
            mercury_longitude=248.036053,
            ascendant_longitude=100.191313,
            mc_longitude=357.456455,
            cusp_1_longitude=100.191313,
            cusp_10_longitude=357.456455,
            ayanamsa_value=23.857092,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="topocentric-altitude",
        objective="Calcul topocentrique avec altitude explicite.",
        input_profile=GoldenInputProfile(
            birth_date="2000-07-17",
            birth_time="12:00",
            birth_timezone="UTC",
            jd_ut=2451743.0,
            latitude=46.8523,
            longitude=-121.7603,
            house_system="placidus",
            zodiac="tropical",
            frame="topocentric",
            altitude_m=4392.0,
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=115.202661,
            moon_longitude=304.591124,
            mercury_longitude=100.389013,
            ascendant_longitude=108.160128,
            mc_longitude=353.306935,
            cusp_1_longitude=108.160128,
            cusp_10_longitude=353.306935,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="whole-sign-paris",
        objective="Maisons whole sign sans derive de cuspides Placidus.",
        input_profile=GoldenInputProfile(
            birth_date="1973-07-04",
            birth_time="09:00",
            birth_timezone="Europe/Paris",
            jd_ut=2441867.8333333335,
            latitude=48.8566,
            longitude=2.3522,
            house_system="whole_sign",
            zodiac="tropical",
            frame="geocentric",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=102.200902,
            moon_longitude=154.960685,
            mercury_longitude=123.125606,
            ascendant_longitude=147.033682,
            mc_longitude=47.009905,
            cusp_1_longitude=120.0,
            cusp_10_longitude=30.0,
        ),
    ),
    SensitiveGoldenCase(
        golden_case_id="placidus-edge-helsinki",
        objective="Cas Placidus limite a latitude nord sans bascule silencieuse.",
        input_profile=GoldenInputProfile(
            birth_date="1966-12-21",
            birth_time="23:45",
            birth_timezone="Europe/Helsinki",
            jd_ut=2439481.40625,
            latitude=60.1699,
            longitude=24.9384,
            house_system="placidus",
            zodiac="tropical",
            frame="geocentric",
        ),
        expected_reference=GoldenExpectedReference(
            sun_longitude=269.587628,
            moon_longitude=21.306723,
            mercury_longitude=254.637502,
            ascendant_longitude=174.537887,
            mc_longitude=81.913408,
            cusp_1_longitude=174.537887,
            cusp_10_longitude=81.913408,
        ),
    ),
)


def build_ephemeris_trace() -> EphemerisTrace:
    """Construit la trace d'éphémérides active sans exposer de chemin brut."""
    swe = load_swisseph()
    bootstrap = get_bootstrap_result()
    path_version = None
    path_hash = None
    if bootstrap is not None and bootstrap.success:
        path_version = bootstrap.path_version
        path_hash = bootstrap.path_hash or None
    note = (
        "external-path-bootstrap"
        if path_version
        else "pyswisseph-moshier-integrated-no-external-path"
    )
    return EphemerisTrace(
        mode=PRODUCTION_ASTRONOMY_MODE,
        swisseph_version=str(getattr(swe, "version", "unknown")),
        path_version=path_version,
        path_hash=path_hash,
        reproducibility_note=note,
    )


def build_public_temporal_gate(*, cs250_status: str) -> PublicTemporalGate:
    """Retourne le gate public CS-253 selon le statut de la preuve CS-250."""
    normalized_status = cs250_status.strip().lower()
    if normalized_status == "done":
        return PublicTemporalGate(
            marker=CS253_GATE_MARKER,
            cs253_gate_state="proof-closed",
            authorized_public_temporal=True,
            reason="CS-250 est done; une story temporelle publique peut revalider son scope.",
        )
    return PublicTemporalGate(
        marker=CS253_GATE_MARKER,
        cs253_gate_state=CS253_PUBLIC_GATE_STATE,
        authorized_public_temporal=False,
        reason="CS-250 n'est pas done; CS-253 reste bloque pour toute surface publique.",
    )


def build_astronomical_proof_manifest(*, cs250_status: str) -> AstronomicalProofManifest:
    """Assemble le manifest canonique utilise par les preuves et les tests."""
    gate = build_public_temporal_gate(cs250_status=cs250_status)
    return AstronomicalProofManifest(
        mode=PRODUCTION_ASTRONOMY_MODE,
        authorized_public_temporal=gate.authorized_public_temporal,
        tolerance_policy=PRODUCTION_TOLERANCE,
        ephemeris_trace=build_ephemeris_trace(),
        cs253_gate=gate,
        golden_cases=SENSITIVE_GOLDEN_CASES,
    )


def calculate_sensitive_case(case: SensitiveGoldenCase) -> GoldenExpectedReference:
    """Calcule les valeurs courantes SwissEph pour un cas golden sensible."""
    profile = case.input_profile
    planets = calculate_planets(
        profile.jd_ut,
        lat=profile.latitude,
        lon=profile.longitude,
        zodiac=profile.zodiac,
        ayanamsa=profile.ayanamsa,
        frame=profile.frame,
        altitude_m=profile.altitude_m,
    )
    houses = calculate_houses(
        profile.jd_ut,
        profile.latitude,
        profile.longitude,
        house_system=profile.house_system,
        frame=profile.frame,
        altitude_m=profile.altitude_m,
    )
    planets_by_id = {planet.planet_id: planet for planet in planets.planets}
    return GoldenExpectedReference(
        sun_longitude=planets_by_id["sun"].longitude,
        moon_longitude=planets_by_id["moon"].longitude,
        mercury_longitude=planets_by_id["mercury"].longitude,
        ascendant_longitude=houses.ascendant_longitude,
        mc_longitude=houses.mc_longitude,
        cusp_1_longitude=houses.cusps[0],
        cusp_10_longitude=houses.cusps[9],
        ayanamsa_value=planets.ayanamsa_value,
    )


def manifest_to_dict(manifest: AstronomicalProofManifest) -> dict[str, object]:
    """Serialise le manifest en dictionnaire JSON snake_case stable."""
    return asdict(manifest)
