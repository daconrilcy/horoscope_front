"""Fixtures golden de référence pour le moteur SwissEph.

Origine des valeurs : pyswisseph>=2.10.0 avec l'éphéméride Moshier intégrée
(sans fichiers .se1 externes). Les valeurs sont deterministes et reproductibles
sans données SwissEph additionnelles.

Date de génération : 2026-02-26
Paramètres de calcul gelés :
  - zodiac      : tropical (zodiaque des signes tropicaux)
  - frame       : geocentric
  - flags       : FLG_SWIEPH | FLG_SPEED (= 2 | 256 = 258, stables entre versions)
  - ayanamsa    : n/a (mode tropical uniquement)
  - house_system: placidus (pour les maisons, non inclus ici)

Utilisation :
    from app.tests.golden.fixtures import GOLDEN_THREE_CASES, ALL_GOLDEN_CASES

Tolérance de précision : 0.01° (36 arcseconds). Toute dérive au-delà de cette
valeur indique une régression du moteur de calcul.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanetGolden:
    """Valeurs de référence gelées pour une planète donnée.

    Attributes:
        planet_id:       Identifiant interne (e.g. "sun", "mercury").
        longitude:       Longitude écliptique tropicale gelée, [0, 360), degrés.
        speed_longitude: Vitesse longitudinale, degrés/jour (< 0 si rétrograde).
        is_retrograde:   True quand speed_longitude < 0.
    """

    planet_id: str
    longitude: float
    speed_longitude: float
    is_retrograde: bool


@dataclass(frozen=True)
class GoldenCase:
    """Un cas de test golden : paramètres d'entrée + valeurs attendues gelées.

    Attributes:
        label:          Identifiant lisible (affiché dans les rapports pytest).
        birth_date:     Date de naissance ISO (YYYY-MM-DD).
        birth_time:     Heure locale (HH:MM).
        birth_timezone: Timezone IANA (e.g. "UTC", "Europe/Paris").
        expected_jd:    Jour Julien UT attendu (tolérance vérification : < 0.001).
        planets:        Tuple de PlanetGolden avec valeurs de longitude gelées.
    """

    label: str
    birth_date: str
    birth_time: str
    birth_timezone: str
    expected_jd: float
    planets: tuple[PlanetGolden, ...]


# ---------------------------------------------------------------------------
# Cas 1 : J2000.0 — 2000-01-01 12:00 UTC
# ---------------------------------------------------------------------------
# Contexte : Époque de référence astronomique standard (J2000.0).
# JD = 2451545.0 exactement (définition de l'époque).
# Saturne est en rétrograde ce jour-là (speed = -0.019945°/j).
#
# Valeurs générées le 2026-02-26 avec pyswisseph Moshier (sans set_ephe_path).
GOLDEN_J2000 = GoldenCase(
    label="J2000.0 — 2000-01-01 12:00 UTC",
    birth_date="2000-01-01",
    birth_time="12:00",
    birth_timezone="UTC",
    expected_jd=2451545.0,
    planets=(
        PlanetGolden("sun", longitude=280.368920, speed_longitude=1.019432, is_retrograde=False),
        PlanetGolden("moon", longitude=223.323775, speed_longitude=12.021183, is_retrograde=False),
        PlanetGolden("mercury", longitude=271.889275, speed_longitude=1.556254,
                     is_retrograde=False),
        PlanetGolden("saturn", longitude=40.395639, speed_longitude=-0.019945, is_retrograde=True),
    ),
)

# ---------------------------------------------------------------------------
# Cas 2 : 1990-06-15 12:00 UTC (solstice d'été approchant)
# ---------------------------------------------------------------------------
# JD = 2448058.0. Saturne en rétrograde (speed = -0.058637°/j).
#
# Valeurs générées le 2026-02-26 avec pyswisseph Moshier.
GOLDEN_1990 = GoldenCase(
    label="1990-06-15 12:00 UTC",
    birth_date="1990-06-15",
    birth_time="12:00",
    birth_timezone="UTC",
    expected_jd=2448058.0,
    planets=(
        PlanetGolden("sun", longitude=84.129567, speed_longitude=0.955101, is_retrograde=False),
        PlanetGolden("moon", longitude=345.357940, speed_longitude=13.361713, is_retrograde=False),
        PlanetGolden("mercury", longitude=65.690706, speed_longitude=1.715937, is_retrograde=False),
    ),
)

# ---------------------------------------------------------------------------
# Cas 3 : 1980-03-21 12:00 UTC (équinoxe de printemps)
# ---------------------------------------------------------------------------
# JD = 2444320.0. Mars ET Jupiter ET Saturne sont en rétrograde ce jour.
#
# Valeurs générées le 2026-02-26 avec pyswisseph Moshier.
GOLDEN_1980 = GoldenCase(
    label="1980-03-21 12:00 UTC (équinoxe de printemps)",
    birth_date="1980-03-21",
    birth_time="12:00",
    birth_timezone="UTC",
    expected_jd=2444320.0,
    planets=(
        PlanetGolden("sun", longitude=1.027914, speed_longitude=0.992876, is_retrograde=False),
        PlanetGolden("moon", longitude=65.944288, speed_longitude=13.866655, is_retrograde=False),
        PlanetGolden("mercury", longitude=337.585422, speed_longitude=0.182641,
                     is_retrograde=False),
        PlanetGolden("mars", longitude=147.471070, speed_longitude=-0.203976, is_retrograde=True),
    ),
)

# ---------------------------------------------------------------------------
# Cas 4 : Timezone historique Europe/Paris en 1973
# ---------------------------------------------------------------------------
# Contexte : La France n'avait pas encore adopté l'heure d'été en juillet 1973.
# Le passage à l'heure d'été (CEST, UTC+2) est intervenu en 1976 suite au choc
# pétrolier. En juillet 1973, Europe/Paris = UTC+1 (CET toute l'année).
# Ce cas vérifie que la base IANA historique est correctement appliquée :
#   09:00 Europe/Paris → UTC+1 → 08:00 UTC → JD ≈ 2441867.833333
#
# Valeurs générées le 2026-02-26 avec pyswisseph Moshier.
GOLDEN_1973_EUROPE_PARIS = GoldenCase(
    label="1973-07-04 09:00 Europe/Paris (UTC+1 historique — heure d'été non en vigueur)",
    birth_date="1973-07-04",
    birth_time="09:00",
    birth_timezone="Europe/Paris",
    # 1973-07-04 08:00:00 UTC → ts=110620800 → JD=2441867.833...
    expected_jd=2441867.833333,
    planets=(
        PlanetGolden("sun", longitude=102.200902, speed_longitude=0.953584, is_retrograde=False),
        PlanetGolden("moon", longitude=154.960685, speed_longitude=13.948549, is_retrograde=False),
        PlanetGolden("mercury", longitude=123.125606, speed_longitude=0.185201,
                     is_retrograde=False),
    ),
)

# ---------------------------------------------------------------------------
# Cas 5 : Mercure rétrograde connu — 2000-07-17 12:00 UTC
# ---------------------------------------------------------------------------
# Mercure était en rétrograde du 17 juillet 2000 au 11 août 2000.
# speed_longitude = -0.005020°/j → is_retrograde = True.
#
# Valeurs générées le 2026-02-26 avec pyswisseph Moshier.
GOLDEN_MERCURY_RETROGRADE = GoldenCase(
    label="2000-07-17 12:00 UTC (Mercure en rétrograde)",
    birth_date="2000-07-17",
    birth_time="12:00",
    birth_timezone="UTC",
    expected_jd=2451743.0,
    planets=(
        PlanetGolden("mercury", longitude=100.386439, speed_longitude=-0.005020,
                     is_retrograde=True),
    ),
)

# ---------------------------------------------------------------------------
# Référentiels exportés
# ---------------------------------------------------------------------------

# Les 3 cas principaux (Sun/Moon/Mercury ± 0.01°) — AC1
GOLDEN_THREE_CASES: tuple[GoldenCase, ...] = (
    GOLDEN_J2000,
    GOLDEN_1990,
    GOLDEN_1980,
)

# Tous les cas golden (incluant TZ historique et rétrograde) — AC1 + AC2 + AC3
ALL_GOLDEN_CASES: tuple[GoldenCase, ...] = (
    GOLDEN_J2000,
    GOLDEN_1990,
    GOLDEN_1980,
    GOLDEN_1973_EUROPE_PARIS,
    GOLDEN_MERCURY_RETROGRADE,
)
