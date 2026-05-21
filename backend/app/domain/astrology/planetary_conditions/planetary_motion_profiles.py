"""Catalogue pur des profils de mouvement planetaire."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from app.domain.astrology.planetary_conditions.contracts import PlanetaryMotionProfile


def _profile(planet_key: str, mean_speed_deg_per_day: float) -> PlanetaryMotionProfile:
    return PlanetaryMotionProfile(
        planet_key=planet_key,
        mean_speed_deg_per_day=mean_speed_deg_per_day,
        stationary_threshold_abs=mean_speed_deg_per_day * 0.05,
    )


DEFAULT_PLANETARY_MOTION_PROFILES: Mapping[str, PlanetaryMotionProfile] = MappingProxyType(
    {
        "moon": _profile("moon", 13.176),
        "mercury": _profile("mercury", 1.2),
        "venus": _profile("venus", 1.18),
        "sun": _profile("sun", 0.9856),
        "mars": _profile("mars", 0.524),
        "jupiter": _profile("jupiter", 0.083),
        "saturn": _profile("saturn", 0.033),
        "uranus": _profile("uranus", 0.0117),
        "neptune": _profile("neptune", 0.006),
        "pluto": _profile("pluto", 0.004),
    }
)
