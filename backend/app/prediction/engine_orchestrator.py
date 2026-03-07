import hashlib
import json
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app.infra.db.repositories.prediction_schemas import RulesetContext

from .exceptions import PredictionContextError
from .schemas import (
    EffectiveContext,
    EngineInput,
    EngineOutput,
)


class EngineOrchestrator:
    """Orchestrates the prediction engine run."""

    def __init__(
        self,
        ruleset_context_loader: Callable[[str], RulesetContext | None] | None = None,
    ) -> None:
        self._ruleset_context_loader = ruleset_context_loader

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

        # AC5 - House system handling
        house_system_requested = self._resolve_house_system(engine_input.ruleset_version)
        house_system_effective = house_system_requested

        effective_context = EffectiveContext(
            house_system_requested=house_system_requested,
            house_system_effective=house_system_effective,
            timezone=engine_input.timezone,
            input_hash=input_hash,
        )

        # AC2/AC6 - Build output (stubs for now)
        run_metadata = {
            "run_id": None,  # Will be handled by persistence in later stories
            "computed_at": self._local_date_start_utc(
                engine_input.local_date, engine_input.timezone
            ).isoformat(),
            "debug_mode": engine_input.debug_mode,
            "jd_interval": [jd_start, jd_end],
        }

        # TODO: story 33-2 (Context Loader)
        # TODO: story 33-3 (Temporal Sampler)
        # TODO: story 33-4 (Astro Calculator)
        # TODO: story 33-5 (Event Detector)
        # TODO: story 33-6 (Natal Sensitivity)

        return EngineOutput(
            run_metadata=run_metadata,
            effective_context=effective_context,
            sampling_timeline=[],
            detected_events=[],
            category_scores={},
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

    def _resolve_house_system(self, ruleset_version: str) -> str:
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
