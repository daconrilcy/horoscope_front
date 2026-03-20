from __future__ import annotations

import logging
from datetime import date, datetime

import swisseph as swe

from app.prediction.public_astro_vocabulary import FIXED_STARS
from app.prediction.schemas import AstroEvent, NatalChart, StepAstroState

logger = logging.getLogger(__name__)

_FLG_SWIEPH_SPEED = swe.FLG_SWIEPH | swe.FLG_SPEED

SWE_BODY_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

ASPECTS = {
    0: "conjunction",
    60: "sextile",
    90: "square",
    120: "trine",
    180: "opposition",
}


class EnrichedAstroEventsBuilder:
    """
    Builds enriched astrological events (Story 60.15).
    Includes aspects, nodes, returns, progressions and fixed stars.
    """

    def build(
        self,
        astro_states: list[StepAstroState],
        natal_chart: NatalChart,
        local_date: date,
        birth_date: datetime,
        timezone_name: str,
    ) -> list[AstroEvent]:
        events: list[AstroEvent] = []

        if not astro_states:
            return events

        # 1. Sky-to-sky aspects
        events.extend(self._compute_sky_aspects(astro_states))

        # 2. Lunar Nodes
        events.extend(self._compute_node_events(astro_states, natal_chart, timezone_name))

        # 3. Returns (Solar/Lunar)
        events.extend(self._compute_returns(astro_states, natal_chart))

        # 4. Secondary Progressions
        # Use first step local_time as reference to preserve timezone-awareness
        ref_dt = astro_states[0].local_time
        events.extend(self._compute_progressions(natal_chart, local_date, birth_date, ref_dt))

        # 5. Fixed Stars
        events.extend(self._compute_fixed_star_conjunctions(astro_states))

        return events

    def _compute_sky_aspects(self, steps: list[StepAstroState]) -> list[AstroEvent]:
        detected: list[AstroEvent] = []
        # Track best orbs for deduplication across the day
        best_orbs: dict[tuple[str, str, str], tuple[float, StepAstroState]] = {}

        planets_to_check = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]

        for step in steps:
            for i, p1_name in enumerate(planets_to_check):
                p1 = step.planets.get(p1_name)
                if not p1:
                    continue

                for j in range(i + 1, len(planets_to_check)):
                    p2_name = planets_to_check[j]
                    p2 = step.planets.get(p2_name)
                    if not p2:
                        continue

                    # Skip Moon/Moon (same step)
                    if p1_name == p2_name:
                        continue

                    dist = self._angular_distance(p1.longitude, p2.longitude)

                    for asp_deg, asp_code in ASPECTS.items():
                        orb = abs(dist - asp_deg)
                        if orb <= 1.5:
                            key = tuple(sorted([p1_name.lower(), p2_name.lower()])) + (asp_code,)
                            if key not in best_orbs or orb < best_orbs[key][0]:
                                best_orbs[key] = (orb, step)

        # Convert best orbs to events
        for (body, target, asp_code), (orb, step) in best_orbs.items():
            # AC1 prioritization: slower planets first
            priority = 50
            slow_planets = {"jupiter", "saturn", "uranus", "neptune", "pluto"}
            if body in slow_planets or target in slow_planets:
                priority = 70
            if body == "moon" or target == "moon":
                priority -= 5  # Moon aspects are very common

            detected.append(
                AstroEvent(
                    event_type="sky_aspect",
                    ut_time=step.ut_jd,
                    local_time=step.local_time,
                    body=body,
                    target=target,
                    aspect=asp_code,
                    orb_deg=orb,
                    priority=priority,
                    base_weight=0.0,
                    metadata={},
                )
            )

        # Sort and limit to 4
        detected.sort(key=lambda e: e.priority, reverse=True)
        return detected[:4]

    def _compute_node_events(
        self, steps: list[StepAstroState], natal_chart: NatalChart, _tz_name: str = ""
    ) -> list[AstroEvent]:
        events: list[AstroEvent] = []
        if not steps:
            return events

        # Positions are stable enough for transits detection on the grid
        # Calculate mean node for the middle of the day
        mid_jd = steps[len(steps) // 2].ut_jd
        xx, _ = swe.calc_ut(mid_jd, swe.MEAN_NODE, _FLG_SWIEPH_SPEED)
        north_node_lon = xx[0] % 360.0
        south_node_lon = (north_node_lon + 180.0) % 360.0

        # Transit to Nodes
        best_orbs: dict[tuple[str, str], tuple[float, StepAstroState]] = {}
        for step in steps:
            for p_name, p_state in step.planets.items():
                # Conjunction/Opposition to Nodes
                for node_name, node_lon in [
                    ("north_node", north_node_lon),
                    ("south_node", south_node_lon),
                ]:
                    dist = self._angular_distance(p_state.longitude, node_lon)
                    if dist <= 2.0:  # AC2 orb 2.0 for transits
                        key = (p_name.lower(), node_name)
                        if key not in best_orbs or dist < best_orbs[key][0]:
                            best_orbs[key] = (dist, step)

        for (p_code, node_name), (orb, step) in best_orbs.items():
            events.append(
                AstroEvent(
                    event_type="node_conjunction",
                    ut_time=step.ut_jd,
                    local_time=step.local_time,
                    body=p_code,
                    target=node_name,
                    aspect="conjunction",
                    orb_deg=orb,
                    priority=60,
                    base_weight=0.0,  # display-only, no signal contribution
                    metadata={},
                )
            )

        # Nodes to Natal (Stable on the day)
        for natal_p, natal_lon in natal_chart.planet_positions.items():
            for node_name, node_lon in [
                ("north_node", north_node_lon),
                ("south_node", south_node_lon),
            ]:
                dist = self._angular_distance(node_lon, natal_lon)
                if dist <= 1.5:  # AC2 orb 1.5 for natal
                    events.append(
                        AstroEvent(
                            event_type="node_conjunction",
                            ut_time=mid_jd,
                            local_time=steps[len(steps) // 2].local_time,
                            body=node_name,
                            target=natal_p.lower(),
                            aspect="conjunction",
                            orb_deg=dist,
                            priority=55,
                            base_weight=0.0,  # display-only, no signal contribution
                            metadata={"is_natal": True},
                        )
                    )

        return events

    def _compute_returns(
        self, steps: list[StepAstroState], natal_chart: NatalChart
    ) -> list[AstroEvent]:
        events: list[AstroEvent] = []
        natal_moon = natal_chart.planet_positions.get("Moon")
        natal_sun = natal_chart.planet_positions.get("Sun")

        if natal_moon is not None:
            # Look for moon return
            best_orb = 1.0
            best_step = None
            for step in steps:
                moon = step.planets.get("Moon")
                if moon:
                    orb = self._angular_distance(moon.longitude, natal_moon)
                    if orb <= best_orb:
                        best_orb = orb
                        best_step = step
            if best_step:
                events.append(
                    AstroEvent(
                        event_type="lunar_return",
                        ut_time=best_step.ut_jd,
                        local_time=best_step.local_time,
                        body="moon",
                        target=None,
                        aspect=None,
                        orb_deg=best_orb,
                        priority=80,
                        base_weight=0.0,  # display-only, no signal contribution
                        metadata={},
                    )
                )

        if natal_sun is not None:
            # Look for sun return
            best_orb = 0.5
            best_step = None
            for step in steps:
                sun = step.planets.get("Sun")
                if sun:
                    orb = self._angular_distance(sun.longitude, natal_sun)
                    if orb <= best_orb:
                        best_orb = orb
                        best_step = step
            if best_step:
                events.append(
                    AstroEvent(
                        event_type="solar_return",
                        ut_time=best_step.ut_jd,
                        local_time=best_step.local_time,
                        body="sun",
                        target=None,
                        aspect=None,
                        orb_deg=best_orb,
                        priority=95,
                        base_weight=0.0,  # display-only, no signal contribution
                        metadata={},
                    )
                )

        return events

    def _compute_progressions(
        self,
        natal_chart: NatalChart,
        local_date: date,
        birth_date: datetime,
        ref_local_time: datetime,
    ) -> list[AstroEvent]:
        events: list[AstroEvent] = []
        # Calculate progressed date: birth_jd + (age_in_days / 365.25)
        age_days = (local_date - birth_date.date()).days
        if age_days < 0:
            return events

        progressed_offset = age_days / 365.25
        birth_jd = swe.julday(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            birth_date.hour + birth_date.minute / 60.0 + birth_date.second / 3600.0,
        )
        progressed_jd = birth_jd + progressed_offset

        progressed_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
        prog_positions = {}

        for p in progressed_planets:
            swe_id = SWE_BODY_IDS[p]
            xx, _ = swe.calc_ut(progressed_jd, swe_id, _FLG_SWIEPH_SPEED)
            prog_positions[p.lower()] = xx[0] % 360.0

        for p_code, prog_lon in prog_positions.items():
            for natal_p, natal_lon in natal_chart.planet_positions.items():
                dist = self._angular_distance(prog_lon, natal_lon)
                # Check for major aspects (AC4: orbe <= 1°)
                for asp_deg, asp_code in ASPECTS.items():
                    orb = abs(dist - asp_deg)
                    if orb <= 1.0:
                        events.append(
                            AstroEvent(
                                event_type="progression_aspect",
                                ut_time=progressed_jd,
                                local_time=ref_local_time,
                                body=f"prog_{p_code}",
                                target=natal_p.lower(),
                                aspect=asp_code,
                                orb_deg=orb,
                                priority=65,
                                base_weight=0.0,  # display-only, no signal contribution
                                metadata={},
                            )
                        )
                        break  # Only one aspect per pair

        return events

    def _compute_fixed_star_conjunctions(self, steps: list[StepAstroState]) -> list[AstroEvent]:
        events: list[AstroEvent] = []
        best_orbs: dict[tuple[str, str], tuple[float, StepAstroState]] = {}

        for step in steps:
            for p_name, p_state in step.planets.items():
                for star_key, star_data in FIXED_STARS.items():
                    dist = self._angular_distance(p_state.longitude, star_data["lon"])
                    if dist <= 1.0:  # AC5 orb 1.0
                        key = (p_name.lower(), star_key)
                        if key not in best_orbs or dist < best_orbs[key][0]:
                            best_orbs[key] = (dist, step)

        for (p_code, star_key), (orb, step) in best_orbs.items():
            events.append(
                AstroEvent(
                    event_type="fixed_star_conjunction",
                    ut_time=step.ut_jd,
                    local_time=step.local_time,
                    body=p_code,
                    target=star_key,
                    aspect="conjunction",
                    orb_deg=orb,
                    priority=45,
                    base_weight=0.0,  # display-only, no signal contribution
                    metadata={"star_name_fr": FIXED_STARS[star_key]["name_fr"]},
                )
            )

        return events

    def _angular_distance(self, lon_a: float, lon_b: float) -> float:
        diff = abs(lon_a - lon_b) % 360.0
        return min(diff, 360.0 - diff)
