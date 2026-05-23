"""Fabriques partagées pour les résultats natals utilisés en tests."""

from __future__ import annotations

from app.domain.astrology.natal_calculation import (
    AspectResult,
    HouseResult,
    NatalResult,
    PlanetPosition,
)
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.domain.astrology.runtime.aspect_runtime_data import AspectInterpretiveHintsRuntimeData


def _aspect_hints(
    aspect_code: str,
    *,
    default_valence: str = "contextual",
    interpretive_valence: str = "amplifying",
    energy_type: str = "fusion_intensification",
) -> AspectInterpretiveHintsRuntimeData:
    """Construit les hints interpretatifs explicites requis par la projection publique."""
    return AspectInterpretiveHintsRuntimeData(
        aspect_code=aspect_code,
        default_valence=default_valence,
        interpretive_valence=interpretive_valence,
        energy_type=energy_type,
        source_codes=(f"aspect:{aspect_code}", f"aspect_profile:{aspect_code}"),
    )


def make_natal_result() -> NatalResult:
    """Crée un résultat natal stable pour les tests de services."""
    aspect_meta = {"family": "major", "is_major": True, "is_minor": False}
    return NatalResult(
        reference_version="v1.0",
        ruleset_version="r1.0",
        house_system="placidus",
        prepared_input=BirthPreparedData(
            birth_datetime_local="1990-06-15T14:30:00+02:00",
            birth_datetime_utc="1990-06-15T12:30:00+00:00",
            timestamp_utc=645364200,
            julian_day=2448073.02,
            birth_timezone="Europe/Paris",
        ),
        planet_positions=[
            PlanetPosition(planet_code="sun", longitude=84.5, sign_code="gemini", house_number=10),
            PlanetPosition(
                planet_code="moon", longitude=112.3, sign_code="cancer", house_number=11
            ),
            PlanetPosition(
                planet_code="mercury", longitude=92.1, sign_code="cancer", house_number=10
            ),
            PlanetPosition(planet_code="venus", longitude=72.8, sign_code="gemini", house_number=9),
            PlanetPosition(planet_code="mars", longitude=25.5, sign_code="aries", house_number=7),
        ],
        houses=[
            HouseResult(number=1, cusp_longitude=195.5),
            HouseResult(number=4, cusp_longitude=285.2),
            HouseResult(number=7, cusp_longitude=15.5),
            HouseResult(number=10, cusp_longitude=105.3),
        ],
        aspects=[
            AspectResult(
                aspect_code="conjunction",
                planet_a="sun",
                planet_b="mercury",
                angle=0.0,
                orb=7.6,
                orb_used=7.6,
                orb_max=8.0,
                aspect_interpretive_hints=_aspect_hints("conjunction"),
                **aspect_meta,
            ),
            AspectResult(
                aspect_code="square",
                planet_a="sun",
                planet_b="mars",
                angle=90.0,
                orb=4.0,
                orb_used=4.0,
                orb_max=6.0,
                aspect_interpretive_hints=_aspect_hints(
                    "square",
                    interpretive_valence="dynamic_challenging",
                ),
                **aspect_meta,
            ),
            AspectResult(
                aspect_code="trine",
                planet_a="moon",
                planet_b="venus",
                angle=120.0,
                orb=0.5,
                orb_used=0.5,
                orb_max=6.0,
                aspect_interpretive_hints=_aspect_hints(
                    "trine",
                    default_valence="positive",
                    interpretive_valence="harmonious",
                ),
                **aspect_meta,
            ),
            AspectResult(
                aspect_code="opposition",
                planet_a="mars",
                planet_b="venus",
                angle=180.0,
                orb=2.7,
                orb_used=2.7,
                orb_max=8.0,
                aspect_interpretive_hints=_aspect_hints(
                    "opposition",
                    interpretive_valence="polarizing",
                ),
                **aspect_meta,
            ),
            AspectResult(
                aspect_code="sextile",
                planet_a="mercury",
                planet_b="venus",
                angle=60.0,
                orb=1.3,
                orb_used=1.3,
                orb_max=4.0,
                aspect_interpretive_hints=_aspect_hints(
                    "sextile",
                    default_valence="positive",
                    interpretive_valence="supportive",
                ),
                **aspect_meta,
            ),
        ],
    )
