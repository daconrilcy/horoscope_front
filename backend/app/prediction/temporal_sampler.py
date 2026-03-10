from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_tz
from typing import Optional
from zoneinfo import ZoneInfo

import swisseph as swe

from app.prediction.schemas import SamplePoint


@dataclass(frozen=True)
class DayGrid:
    """A grid of sample points for a specific local day."""

    samples: list[SamplePoint]
    ut_start: float
    ut_end: float
    sunrise_ut: Optional[float]
    sunset_ut: Optional[float]
    local_date: date
    timezone: str


class TemporalSampler:
    """Service to generate temporal grids for astrological calculations."""

    STEP_MINUTES = 15

    def build_day_grid(
        self,
        local_date: date,
        tz_name: str,
        latitude: float,
        longitude: float,
    ) -> DayGrid:
        """Build a 15-minute grid covering the requested local day."""
        tz = ZoneInfo(tz_name)
        local_start = datetime.combine(local_date, time.min, tzinfo=tz)
        next_local_start = datetime.combine(
            local_date + timedelta(days=1),
            time.min,
            tzinfo=tz,
        )
        local_end = next_local_start - timedelta(seconds=1)

        utc_start = local_start.astimezone(dt_tz.utc)
        utc_end_exclusive = next_local_start.astimezone(dt_tz.utc)

        ut_start = self._datetime_to_jd(local_start)
        ut_end = self._datetime_to_jd(local_end)

        samples: list[SamplePoint] = []
        current_utc = utc_start
        while current_utc < utc_end_exclusive:
            local_time = current_utc.astimezone(tz)
            samples.append(
                SamplePoint(
                    ut_time=self._datetime_to_jd(current_utc),
                    local_time=local_time,
                )
            )
            current_utc += timedelta(minutes=self.STEP_MINUTES)

        sunrise_ut = self._get_sun_event(ut_start, latitude, longitude, swe.CALC_RISE)
        sunset_ut = self._get_sun_event(ut_start, latitude, longitude, swe.CALC_SET)

        return DayGrid(
            samples=samples,
            ut_start=ut_start,
            ut_end=ut_end,
            sunrise_ut=sunrise_ut,
            sunset_ut=sunset_ut,
            local_date=local_date,
            timezone=tz_name,
        )

    def refine_around(
        self,
        ut_jd: float,
        radius_minutes: int = 5,
        tz_name: str = "UTC",
    ) -> list[SamplePoint]:
        """Generate 1-minute samples symmetrically around a Julian Day.
        
        Args:
            ut_jd: The Julian Day center point.
            radius_minutes: How many minutes to sample on each side.
            tz_name: The IANA timezone name for local_time representation.
        """
        one_minute = timedelta(minutes=1)
        center_utc = self._jd_to_local_datetime(ut_jd, "UTC")
        start_utc = center_utc - ((radius_minutes - 0.5) * one_minute)

        points: list[SamplePoint] = []
        for offset in range(2 * radius_minutes):
            sample_utc = start_utc + (offset * one_minute)
            points.append(
                SamplePoint(
                    ut_time=self._datetime_to_jd(sample_utc),
                    local_time=sample_utc.astimezone(ZoneInfo(tz_name)),
                )
            )

        return points

    def _get_sun_event(
        self,
        ut_start: float,
        lat: float,
        lon: float,
        event_type: int,
    ) -> Optional[float]:
        """Calculate sunrise or sunset using Swiss Ephemeris."""
        try:
            result_code, event_times = swe.rise_trans(
                ut_start,
                swe.SUN,
                event_type,
                (lon, lat, 0.0),
                0.0,
                0.0,
                swe.FLG_SWIEPH,
            )
        except Exception:
            return None

        if result_code == 0:
            return event_times[0]
        return None

    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert a timezone-aware datetime to Julian Day UT."""
        utc = dt.astimezone(dt_tz.utc)
        hour_fraction = (
            utc.hour
            + (utc.minute / 60.0)
            + (utc.second / 3600.0)
            + (utc.microsecond / 3_600_000_000.0)
        )
        return swe.julday(utc.year, utc.month, utc.day, hour_fraction)

    def _jd_to_local_datetime(self, jd: float, tz_name: str) -> datetime:
        """Convert Julian Day UT to a timezone-aware datetime."""
        year, month, day, hour_fraction = swe.revjul(jd)
        hours = int(hour_fraction)
        minutes_fraction = (hour_fraction - hours) * 60
        minutes = int(minutes_fraction)
        seconds_fraction = (minutes_fraction - minutes) * 60
        seconds = int(seconds_fraction)
        microseconds = int(round((seconds_fraction - seconds) * 1_000_000))

        base_utc = datetime(year, month, day, hours, minutes, tzinfo=dt_tz.utc)
        utc_datetime = base_utc + timedelta(seconds=seconds, microseconds=microseconds)
        return utc_datetime.astimezone(ZoneInfo(tz_name))
