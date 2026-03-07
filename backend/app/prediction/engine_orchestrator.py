import hashlib
import json
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from numbers import Real
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app.infra.db.repositories.prediction_schemas import RulesetContext

from .astro_calculator import AstroCalculator
from .context_loader import LoadedPredictionContext
from .event_detector import EventDetector
from .exceptions import PredictionContextError
from .natal_sensitivity import NatalSensitivityCalculator
from .schemas import (
    EffectiveContext,
    EngineInput,
    EngineOutput,
    NatalChart,
)
from .temporal_sampler import TemporalSampler

_ZODIAC_SIGNS = (
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

_PLANET_NAME_MAP = {
    "sun": "Sun",
    "moon": "Moon",
    "mercury": "Mercury",
    "venus": "Venus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto",
}


class EngineOrchestrator:
    """Orchestrates the prediction engine run."""

    def __init__(
        self,
        ruleset_context_loader: Callable[[str], RulesetContext | None] | None = None,
        prediction_context_loader: (
            Callable[[str, str, date], LoadedPredictionContext | None] | None
        ) = None,
        temporal_sampler: TemporalSampler | None = None,
        astro_calculator_factory: (
            Callable[[list[float], float, float], AstroCalculator] | None
        ) = None,
        event_detector_factory: (
            Callable[[LoadedPredictionContext, dict[str, float]], EventDetector] | None
        ) = None,
        natal_sensitivity_calculator: NatalSensitivityCalculator | None = None,
    ) -> None:
        self._ruleset_context_loader = ruleset_context_loader
        self._prediction_context_loader = prediction_context_loader
        self._temporal_sampler = temporal_sampler or TemporalSampler()
        self._astro_calculator_factory = astro_calculator_factory or AstroCalculator
        self._event_detector_factory = event_detector_factory or EventDetector
        self._natal_sensitivity_calculator = (
            natal_sensitivity_calculator or NatalSensitivityCalculator()
        )

    def run(self, engine_input: EngineInput) -> EngineOutput:
        """
        Executes the prediction engine for a given input.

        Args:
            engine_input: The canonical input for the engine.

        Returns:
            EngineOutput: The structured output of the engine.
        """
        # AC3 - Compute hash
        input_hash = self._compute_hash(engine_input)

        # AC4 - Convert local date to UT interval (JD)
        jd_start, jd_end = self._local_date_to_ut_interval(
            engine_input.local_date, engine_input.timezone
        )

        loaded_context = self._load_prediction_context(engine_input)
        house_system_requested = self._resolve_house_system(
            engine_input.ruleset_version,
            loaded_context,
        )

        natal_cusps = self._extract_house_cusps(engine_input.natal_chart)
        natal_positions = self._extract_natal_positions(engine_input.natal_chart)
        natal_chart = self._build_natal_chart(engine_input.natal_chart, natal_cusps)

        day_grid = self._temporal_sampler.build_day_grid(
            engine_input.local_date,
            engine_input.timezone,
            engine_input.latitude,
            engine_input.longitude,
        )
        astro_calculator = self._astro_calculator_factory(
            natal_cusps,
            engine_input.latitude,
            engine_input.longitude,
        )
        astro_states = [
            astro_calculator.compute_step(sample.ut_time, sample.local_time)
            for sample in day_grid.samples
        ]
        event_detector = self._event_detector_factory(loaded_context, natal_positions)
        detected_events = event_detector.detect(astro_states, day_grid)
        natal_sensitivity = self._natal_sensitivity_calculator.compute(
            natal_chart,
            loaded_context,
        )
        house_system_effective = self._resolve_effective_house_system(
            house_system_requested,
            astro_states,
        )

        effective_context = EffectiveContext(
            house_system_requested=house_system_requested,
            house_system_effective=house_system_effective,
            timezone=engine_input.timezone,
            input_hash=input_hash,
        )

        run_metadata = {
            "run_id": None,  # Will be handled by persistence in later stories
            "computed_at": self._local_date_start_utc(
                engine_input.local_date, engine_input.timezone
            ).isoformat(),
            "debug_mode": engine_input.debug_mode,
            "jd_interval": [jd_start, jd_end],
            "is_provisional_calibration": loaded_context.is_provisional_calibration,
        }

        return EngineOutput(
            run_metadata=run_metadata,
            effective_context=effective_context,
            sampling_timeline=list(day_grid.samples),
            detected_events=detected_events,
            category_scores=natal_sensitivity,
            time_blocks=[],
            turning_points=[],
        )

    def _compute_hash(self, engine_input: EngineInput) -> str:
        """Computes a stable SHA-256 hash for the engine input."""
        canonical = {
            "natal": engine_input.natal_chart,
            "local_date": engine_input.local_date.isoformat(),
            "timezone": engine_input.timezone,
            "latitude": engine_input.latitude,
            "longitude": engine_input.longitude,
            "reference_version": engine_input.reference_version,
            "ruleset_version": engine_input.ruleset_version,
        }
        serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def _local_date_to_ut_interval(self, local_date: date, tz_name: str) -> tuple[float, float]:
        """Converts a local date + timezone into a UT interval (Julian Day start/end)."""
        dt_start_utc = self._local_date_start_utc(local_date, tz_name)
        dt_end_utc = self._local_date_end_utc(local_date, tz_name)
        return self._datetime_to_julian_day(dt_start_utc), self._datetime_to_julian_day(dt_end_utc)

    def _local_date_start_utc(self, local_date: date, tz_name: str) -> datetime:
        return self._local_datetime_to_utc(datetime.combine(local_date, time.min), tz_name)

    def _local_date_end_utc(self, local_date: date, tz_name: str) -> datetime:
        next_day = local_date + timedelta(days=1)
        return self._local_datetime_to_utc(datetime.combine(next_day, time.min), tz_name)

    def _local_datetime_to_utc(self, local_dt: datetime, tz_name: str) -> datetime:
        try:
            tz = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError as exc:
            raise PredictionContextError(f"Unknown IANA timezone: {tz_name!r}") from exc

        return local_dt.replace(tzinfo=tz).astimezone(UTC)

    def _datetime_to_julian_day(self, dt_utc: datetime) -> float:
        return swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        )

    def _load_prediction_context(self, engine_input: EngineInput) -> LoadedPredictionContext:
        if self._prediction_context_loader is None:
            raise PredictionContextError(
                "Prediction context loader not configured for EngineOrchestrator"
            )

        loaded_context = self._prediction_context_loader(
            engine_input.reference_version,
            engine_input.ruleset_version,
            engine_input.local_date,
        )
        if loaded_context is None:
            raise PredictionContextError(
                "Prediction context not found for "
                f"reference={engine_input.reference_version!r} "
                f"ruleset={engine_input.ruleset_version!r}"
            )
        return loaded_context

    def _resolve_house_system(
        self,
        ruleset_version: str,
        loaded_context: LoadedPredictionContext | None = None,
    ) -> str:
        if loaded_context is not None:
            house_system = loaded_context.ruleset_context.ruleset.house_system.strip()
            if not house_system:
                raise PredictionContextError(
                    f"Ruleset {ruleset_version!r} does not define a house_system"
                )
            return house_system

        if self._ruleset_context_loader is None:
            return "placidus"

        ruleset_context = self._ruleset_context_loader(ruleset_version)
        if ruleset_context is None:
            raise PredictionContextError(
                f"Ruleset context not found for version {ruleset_version!r}"
            )

        house_system = ruleset_context.ruleset.house_system.strip()
        if not house_system:
            raise PredictionContextError(
                f"Ruleset {ruleset_version!r} does not define a house_system"
            )

        return house_system

    def _resolve_effective_house_system(
        self,
        house_system_requested: str,
        astro_states: list,
    ) -> str:
        if not astro_states:
            return house_system_requested

        effective_systems = {state.house_system_effective for state in astro_states}
        if len(effective_systems) == 1:
            return effective_systems.pop()
        if "porphyre" in effective_systems:
            return "porphyre"
        return astro_states[0].house_system_effective

    def _extract_house_cusps(self, natal_chart: dict) -> list[float]:
        raw_cusps = natal_chart.get("house_cusps")
        if raw_cusps is None:
            raw_houses = natal_chart.get("houses")
            if isinstance(raw_houses, list):
                raw_cusps = [
                    house.get("cusp_longitude")
                    for house in sorted(
                        raw_houses,
                        key=lambda item: int(item.get("number", 0)),
                    )
                ]

        if not isinstance(raw_cusps, list) or len(raw_cusps) != 12:
            raise PredictionContextError(
                "EngineInput.natal_chart must provide 12 house cusps via "
                "'house_cusps' or chart_json-style 'houses'"
            )

        try:
            return [self._coerce_longitude(value) for value in raw_cusps]
        except (TypeError, ValueError) as exc:
            raise PredictionContextError("Natal house cusps must be numeric") from exc

    def _extract_natal_positions(self, natal_chart: dict) -> dict[str, float]:
        positions = self._extract_named_longitudes(natal_chart.get("planets"), code_key="code")
        normalized_positions: dict[str, float] = {}
        for code, longitude in positions.items():
            canonical = self._canonical_planet_name(code)
            if canonical is not None:
                normalized_positions[canonical] = longitude

        for angle_code, longitude in self._extract_angle_longitudes(natal_chart).items():
            normalized_positions[angle_code] = longitude

        return normalized_positions

    def _build_natal_chart(self, natal_chart: dict, natal_cusps: list[float]) -> NatalChart:
        planet_positions = self._extract_named_longitudes(
            natal_chart.get("planets"),
            code_key="code",
        )
        planet_houses = self._extract_planet_houses(natal_chart, planet_positions, natal_cusps)
        house_sign_rulers = self._extract_house_sign_rulers(natal_chart, natal_cusps)
        return NatalChart(
            planet_positions=planet_positions,
            planet_houses=planet_houses,
            house_sign_rulers=house_sign_rulers,
        )

    def _extract_named_longitudes(
        self,
        raw_value: object,
        *,
        code_key: str,
    ) -> dict[str, float]:
        if isinstance(raw_value, dict):
            return {
                str(code): self._coerce_longitude(longitude)
                for code, longitude in raw_value.items()
            }
        if isinstance(raw_value, list):
            positions: dict[str, float] = {}
            for item in raw_value:
                if not isinstance(item, dict) or code_key not in item or "longitude" not in item:
                    raise PredictionContextError(
                        "Natal chart planet entries must expose 'code' and 'longitude'"
                    )
                positions[str(item[code_key])] = self._coerce_longitude(item["longitude"])
            return positions
        raise PredictionContextError("EngineInput.natal_chart must provide planet positions")

    def _extract_angle_longitudes(self, natal_chart: dict) -> dict[str, float]:
        raw_angles = natal_chart.get("angles")
        if not isinstance(raw_angles, dict):
            return {}

        angle_positions: dict[str, float] = {}
        for raw_code, value in raw_angles.items():
            if value is None:
                continue
            normalized_code = str(raw_code).strip().upper()
            if normalized_code not in {"ASC", "MC"}:
                continue
            longitude_value = value.get("longitude") if isinstance(value, dict) else value
            angle_positions["Asc" if normalized_code == "ASC" else "MC"] = self._coerce_longitude(
                longitude_value
            )
        return angle_positions

    def _extract_planet_houses(
        self,
        natal_chart: dict,
        planet_positions: dict[str, float],
        natal_cusps: list[float],
    ) -> dict[str, int]:
        raw_planets = natal_chart.get("planets")
        if isinstance(raw_planets, dict):
            return {
                code: self._house_for_longitude(longitude, natal_cusps)
                for code, longitude in planet_positions.items()
            }

        if isinstance(raw_planets, list):
            planet_houses: dict[str, int] = {}
            for item in raw_planets:
                code = str(item["code"])
                house_number = item.get("house")
                if house_number is None:
                    house_number = self._house_for_longitude(planet_positions[code], natal_cusps)
                planet_houses[code] = int(house_number)
            return planet_houses

        raise PredictionContextError("EngineInput.natal_chart must provide planet positions")

    def _extract_house_sign_rulers(
        self,
        natal_chart: dict,
        natal_cusps: list[float],
    ) -> dict[int, str]:
        raw_house_sign_rulers = natal_chart.get("house_sign_rulers")
        if isinstance(raw_house_sign_rulers, dict):
            return {int(house_num): str(sign) for house_num, sign in raw_house_sign_rulers.items()}

        return {
            index + 1: _ZODIAC_SIGNS[int(cusp // 30) % len(_ZODIAC_SIGNS)]
            for index, cusp in enumerate(natal_cusps)
        }

    def _house_for_longitude(self, longitude: float, cusps: list[float]) -> int:
        normalized = longitude % 360.0
        for index, cusp_start in enumerate(cusps):
            cusp_end = cusps[(index + 1) % len(cusps)]
            if cusp_start < cusp_end:
                if cusp_start <= normalized < cusp_end:
                    return index + 1
            elif normalized >= cusp_start or normalized < cusp_end:
                return index + 1
        return 1

    def _canonical_planet_name(self, raw_code: str) -> str | None:
        return _PLANET_NAME_MAP.get(str(raw_code).strip().lower())

    def _coerce_longitude(self, value: object) -> float:
        if not isinstance(value, Real):
            raise TypeError(f"Longitude value must be numeric, got {type(value).__name__}")
        return float(value) % 360.0
