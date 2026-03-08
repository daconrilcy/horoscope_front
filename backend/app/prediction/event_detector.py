import dataclasses
import logging
from datetime import datetime, timedelta
from datetime import timezone as dt_tz
from zoneinfo import ZoneInfo

import swisseph as swe

from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.schemas import AstroEvent, NatalChart, StepAstroState
from app.prediction.temporal_sampler import DayGrid

logger = logging.getLogger(__name__)


class EventDetector:
    """
    Service to detect astrological events from a sequence of astronomical states.
    Transforms StepAstroState sequence into a list of enriched AstroEvents.
    """

    ASPECTS_V1: dict[int, str] = {
        0: "conjunction",
        60: "sextile",
        90: "square",
        120: "trine",
        180: "opposition",
    }

    CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

    V1_NATAL_TARGETS = {
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
        "Asc",
        "MC",
    }

    def __init__(self, ctx: LoadedPredictionContext, natal_chart: NatalChart):
        self.ctx = ctx
        self.natal_chart = natal_chart
        # Filter natal positions for V1 targets
        self.natal_positions = {
            k: v for k, v in natal_chart.planet_positions.items() if k in self.V1_NATAL_TARGETS
        }
        # Add angles if present in natal_chart (might be in angles dict in some versions,
        # but orchestrator normalizes them into planet_positions)
        # We also need their houses.
        # If Asc/MC are not in planet_houses, we can assume 1 and 10 or calculate if we had cusps.
        # But EngineOrchestrator should have put them in planet_houses if it normalized them.

    def detect(self, steps: list[StepAstroState], day_grid: DayGrid) -> list[AstroEvent]:
        """
        Main detection loop for all event types.
        Returns a list of AstroEvent sorted by ut_time.
        """
        events: list[AstroEvent] = []

        # 1. Aspects (enter_orb, exact, exit_orb)
        if steps:
            events.extend(self._detect_aspects(steps))

        # 2. Moon Sign Ingress
        if steps:
            events.extend(self._detect_moon_ingress(steps))

        # 3. Ascendant Sign Change
        if steps:
            events.extend(self._detect_asc_sign_change(steps))

        # 4. Planetary Hours
        events.extend(self._detect_planetary_hours(day_grid))

        # Sort all events chronologically
        events.sort(key=lambda e: e.ut_time)
        return events

    def refine_exact_event(
        self,
        coarse_event: AstroEvent,
        refined_steps: list[StepAstroState],
    ) -> AstroEvent:
        """Refine an exact event using denser astro states around the coarse timestamp."""
        if coarse_event.event_type != "exact":
            return coarse_event
        if coarse_event.body is None or coarse_event.target is None or coarse_event.aspect is None:
            return coarse_event

        natal_lon = self.natal_positions.get(coarse_event.target)
        if natal_lon is None:
            return coarse_event

        aspect_deg = next(
            (
                aspect_value
                for aspect_value, aspect_code in self.ASPECTS_V1.items()
                if aspect_code == coarse_event.aspect
            ),
            None,
        )
        if aspect_deg is None:
            return coarse_event

        best_step: StepAstroState | None = None
        best_orb: float | None = None
        for step in refined_steps:
            planet_state = step.planets.get(coarse_event.body)
            if planet_state is None:
                continue
            orb = self._orb(planet_state.longitude, natal_lon, aspect_deg)
            if best_orb is None or orb < best_orb:
                best_orb = orb
                best_step = step

        if best_step is None or best_orb is None:
            return coarse_event

        refined_metadata = {
            **coarse_event.metadata,
            "refined": True,
            "coarse_ut_time": coarse_event.ut_time,
        }
        return dataclasses.replace(
            coarse_event,
            ut_time=best_step.ut_jd,
            local_time=best_step.local_time,
            orb_deg=best_orb,
            metadata=refined_metadata,
        )

    def _detect_aspects(self, steps: list[StepAstroState]) -> list[AstroEvent]:
        detected: list[AstroEvent] = []

        # Track history for each (transit, target, aspect)
        # key -> list of orbs
        history: dict[tuple[str, str, int], list[float]] = {}

        for i, step in enumerate(steps):
            for body_code, planet_state in step.planets.items():
                transit_lon = planet_state.longitude
                transit_house = planet_state.natal_house_transited

                for target_code, natal_lon in self.natal_positions.items():
                    target_house = self.natal_chart.planet_houses.get(target_code)

                    for aspect_deg, aspect_code in self.ASPECTS_V1.items():
                        key = (body_code, target_code, aspect_deg)
                        orb = self._orb(transit_lon, natal_lon, aspect_deg)
                        orb_max = self._orb_max(body_code, aspect_code)

                        if key not in history:
                            history[key] = []

                        h = history[key]
                        h.append(orb)

                        # Metadata for enriched routing
                        meta = {
                            "natal_house_target": target_house,
                            "natal_house_transited": transit_house,
                            "orb_max": orb_max,
                        }

                        if len(h) >= 2:
                            prev_orb = h[-2]
                            phase = "applying" if orb < prev_orb else "separating"
                            meta["phase"] = phase

                            # enter_orb
                            if prev_orb > orb_max and orb <= orb_max:
                                detected.append(
                                    self._create_event(
                                        "enter_orb",
                                        step.ut_jd,
                                        step.local_time,
                                        body_code,
                                        target_code,
                                        aspect_code,
                                        orb,
                                        meta.copy(),
                                    )
                                )

                            # exit_orb
                            elif prev_orb <= orb_max and orb > orb_max:
                                detected.append(
                                    self._create_event(
                                        "exit_orb",
                                        step.ut_jd,
                                        step.local_time,
                                        body_code,
                                        target_code,
                                        aspect_code,
                                        orb,
                                        meta.copy(),
                                    )
                                )

                        # exact detection (local minimum)
                        if len(h) >= 3:
                            p1, p2, p3 = h[-3], h[-2], h[-1]
                            if p2 < p1 and p2 < p3 and p2 <= orb_max:
                                # p2 is a local minimum — orb was decreasing into it (applying)
                                prev_step = steps[i - 1]
                                # natal_house_transited must come from prev_step,
                                # not from the current step i.
                                prev_planet = prev_step.planets.get(body_code)
                                meta_exact = {
                                    "natal_house_target": target_house,
                                    "natal_house_transited": (
                                        prev_planet.natal_house_transited
                                        if prev_planet
                                        else transit_house
                                    ),
                                    "orb_max": orb_max,
                                    "phase": "applying",
                                }
                                detected.append(
                                    self._create_event(
                                        "exact",
                                        prev_step.ut_jd,
                                        prev_step.local_time,
                                        body_code,
                                        target_code,
                                        aspect_code,
                                        p2,
                                        meta_exact,
                                    )
                                )

        return detected

    def _detect_moon_ingress(self, steps: list[StepAstroState]) -> list[AstroEvent]:
        detected: list[AstroEvent] = []
        prev_sign = None

        for step in steps:
            moon = step.planets.get("Moon")
            if not moon:
                continue

            if prev_sign is not None and moon.sign_code != prev_sign:
                detected.append(
                    self._create_event(
                        "moon_sign_ingress",
                        step.ut_jd,
                        step.local_time,
                        "Moon",
                        None,
                        None,
                        0.0,
                        {"from_sign": prev_sign, "to_sign": moon.sign_code},
                    )
                )

            prev_sign = moon.sign_code

        return detected

    def _detect_asc_sign_change(self, steps: list[StepAstroState]) -> list[AstroEvent]:
        detected: list[AstroEvent] = []
        prev_sign = None

        for step in steps:
            # Ascendant sign code (0-11)
            sign_code = int(step.ascendant_deg // 30)

            if prev_sign is not None and sign_code != prev_sign:
                detected.append(
                    self._create_event(
                        "asc_sign_change",
                        step.ut_jd,
                        step.local_time,
                        "Asc",
                        None,
                        None,
                        0.0,
                        {"from_sign": prev_sign, "to_sign": sign_code},
                    )
                )

            prev_sign = sign_code

        return detected

    def _detect_planetary_hours(self, day_grid: DayGrid) -> list[AstroEvent]:
        detected: list[AstroEvent] = []
        if day_grid.sunrise_ut is None or day_grid.sunset_ut is None:
            return detected

        # Day hours
        day_duration = day_grid.sunset_ut - day_grid.sunrise_ut
        hour_len_day = day_duration / 12

        # Night hours: 1.0 JD ≈ one solar day, so night ≈ 1.0 - day_duration.
        # V1 approximation: assumes next sunrise = current sunrise + 1.0 JD (accurate to ~seconds).
        hour_len_night = (1.0 - day_duration) / 12

        dow_sun_start = (day_grid.local_date.weekday() + 1) % 7

        tz_name = day_grid.timezone

        # 12 day hours
        for i in range(12):
            ut_time = day_grid.sunrise_ut + i * hour_len_day
            ruler = self._planetary_hour_ruler(dow_sun_start, i)
            detected.append(self._create_planetary_hour_event(ut_time, ruler, i + 1, tz_name))

        # 12 night hours
        for i in range(12):
            ut_time = day_grid.sunset_ut + i * hour_len_night
            ruler = self._planetary_hour_ruler(dow_sun_start, i + 12)
            detected.append(self._create_planetary_hour_event(ut_time, ruler, i + 13, tz_name))

        return detected

    def _planetary_hour_ruler(self, day_of_week: int, hour_index: int) -> str:
        DAY_RULERS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        first_ruler_idx = self.CHALDEAN_ORDER.index(DAY_RULERS[day_of_week])
        return self.CHALDEAN_ORDER[(first_ruler_idx + hour_index) % 7]

    def _create_planetary_hour_event(
        self, ut_time: float, ruler: str, hour_num: int, tz_name: str
    ) -> AstroEvent:
        local_time = self._jd_to_local_datetime(ut_time, tz_name)
        return self._create_event(
            "planetary_hour_change",
            ut_time,
            local_time,
            ruler,
            None,
            None,
            0.0,
            {"hour_number": hour_num},
        )

    def _jd_to_local_datetime(self, jd: float, tz_name: str) -> datetime:
        """Convert a Julian Day UT to a timezone-aware local datetime."""
        year, month, day, hour_fraction = swe.revjul(jd)
        hours = int(hour_fraction)
        minutes_fraction = (hour_fraction - hours) * 60
        minutes = int(minutes_fraction)
        seconds_fraction = (minutes_fraction - minutes) * 60
        seconds = int(seconds_fraction)
        microseconds = int(round((seconds_fraction - seconds) * 1_000_000))
        base_utc = datetime(year, month, day, hours, minutes, tzinfo=dt_tz.utc)
        utc_dt = base_utc + timedelta(seconds=seconds, microseconds=microseconds)
        return utc_dt.astimezone(ZoneInfo(tz_name))

    def _orb(self, transit_lon: float, natal_lon: float, aspect_deg: int) -> float:
        """Orb in degrees (always positive)."""
        diff = abs(transit_lon - natal_lon) % 360
        if diff > 180:
            diff = 360 - diff
        return abs(diff - aspect_deg)

    def _orb_max(self, planet_code: str, aspect_code: str) -> float:
        planet_profile = self._lookup_mapping_value(
            self.ctx.prediction_context.planet_profiles,
            planet_code,
        )
        orb_active_raw = getattr(planet_profile, "orb_active_deg", None) if planet_profile else None
        if orb_active_raw is None:
            logger.warning(
                "orb_max_fallback planet=%s aspect=%s default=2.0", planet_code, aspect_code
            )
        orb_active = float(orb_active_raw) if orb_active_raw is not None else 2.0
        aspect_profile = self._lookup_mapping_value(
            self.ctx.prediction_context.aspect_profiles,
            aspect_code,
        )
        multiplier_raw = getattr(aspect_profile, "orb_multiplier", None) if aspect_profile else None
        multiplier = float(multiplier_raw) if multiplier_raw is not None else 1.0
        return orb_active * multiplier

    def _lookup_mapping_value(self, mapping: dict, key: str) -> object | None:
        candidates = (key, key.lower(), key.upper(), key.title())
        for candidate in candidates:
            if candidate in mapping:
                return mapping[candidate]
        return None

    def _create_event(
        self,
        event_type: str,
        ut_time: float,
        local_time: datetime,
        body: str | None,
        target: str | None,
        aspect: str | None,
        orb_deg: float,
        metadata: dict,
    ) -> AstroEvent:
        et_data = self.ctx.ruleset_context.event_types.get(event_type)
        priority = et_data.priority if et_data else 50
        base_weight = et_data.base_weight if et_data else 1.0

        return AstroEvent(
            event_type=event_type,
            ut_time=ut_time,
            local_time=local_time,
            body=body,
            target=target,
            aspect=aspect,
            orb_deg=orb_deg,
            priority=priority,
            base_weight=base_weight,
            metadata=metadata,
        )
