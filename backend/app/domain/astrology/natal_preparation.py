from __future__ import annotations

import logging
from datetime import date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

METRIC_TIMEZONE_ERRORS = "natal_preparation_timezone_errors_total"
METRIC_TT_ENABLED = "time_pipeline_tt_enabled_total"
# Story 26.1 — source metrics: timezone_source_{source}_total
METRIC_TIMEZONE_SOURCE_USER_PROVIDED = "timezone_source_user_provided_total"
METRIC_TIMEZONE_SOURCE_DERIVED = "timezone_source_derived_total"
METRIC_TIMEZONE_DERIVATION_ERRORS = "timezone_derivation_errors_total"

# ---------------------------------------------------------------------------
# Offline timezone derivation from lat/lon (Story 26.1)
# Uses timezonefinder for deterministic, offline resolution.
# ---------------------------------------------------------------------------

_timezone_finder_instance = None


def warmup_timezone_finder() -> None:
    """Ensure timezonefinder is installed and warmed up (pre-loads polygon data).

    Called at application startup to avoid latency spikes on first request
    and to fail fast if the library is missing.
    """
    global _timezone_finder_instance
    try:
        from timezonefinder import TimezoneFinder

        if _timezone_finder_instance is None:
            logger.info("natal_preparation_timezone_finder_warmup_start")
            _timezone_finder_instance = TimezoneFinder()
            # Accessing any property or calling a method can trigger data load,
            # but usually instantiation is enough for most data files in newer versions.
            logger.info("natal_preparation_timezone_finder_warmup_complete")
    except ImportError as e:
        logger.error("natal_preparation_timezonefinder_library_missing")
        raise RuntimeError("timezonefinder library is required but not installed") from e
    except Exception:
        logger.exception("natal_preparation_timezone_finder_warmup_failed")
        raise


def _get_timezone_finder():  # type: ignore[return]
    """Return a cached TimezoneFinder instance (lazy initialisation)."""
    global _timezone_finder_instance
    if _timezone_finder_instance is None:
        warmup_timezone_finder()
    return _timezone_finder_instance


def _derive_timezone_from_coords(lat: float, lon: float) -> str | None:
    """Derive IANA timezone from coordinates using offline polygon lookup.

    Returns None if derivation fails (e.g. coordinates in international waters).
    Never raises: errors are logged and return None.
    """
    try:
        tf = _get_timezone_finder()
        return tf.timezone_at(lng=lon, lat=lat)
    except Exception:
        logger.exception(
            "natal_preparation_timezone_derivation_failed lat=%s lon=%s", lat, lon
        )
        return None

# ---------------------------------------------------------------------------
# DeltaT polynomial approximation (Espenak & Meeus)
# Source: https://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html
# Deterministic — depends only on the decimal year.
# Plausible range for modern dates (1900–2100): roughly 0–200 seconds.
# ---------------------------------------------------------------------------


def _delta_t_seconds(year: float) -> float:
    """Return ΔT = TT − UT1 in seconds for the given decimal year.

    Uses NASA polynomial approximations (Espenak & Meeus).
    Ranges cover -500 to 2150+.
    """
    if year < -500:
        return -20.0 + 32.0 * ((year - 1820.0) / 100.0) ** 2
    if year < 500:
        u = year / 100.0
        return (
            10583.6
            - 1014.41 * u
            + 33.7831 * u**2
            - 5.952053 * u**3
            - 0.1798452 * u**4
            + 0.022174192 * u**5
            + 0.0090316521 * u**6
        )
    if year < 1600:
        u = (year - 1000.0) / 100.0
        return (
            1574.2
            - 556.01 * u
            + 71.23472 * u**2
            + 0.319781 * u**3
            - 0.8503463 * u**4
            + 0.4715099 * u**5
            - 0.0524673 * u**6
        )
    if year < 1700:
        t = year - 1600.0
        return 120.0 - 0.9808 * t - 0.01532 * t**2 + t**3 / 7129.0
    if year < 1800:
        t = year - 1700.0
        return 8.83 + 0.1603 * t - 0.0059285 * t**2 + 0.00013336 * t**3 - t**4 / 1174000.0
    if year < 1860:
        t = year - 1800.0
        return (
            13.72
            - 0.332447 * t
            + 0.0068612 * t**2
            + 0.0041116 * t**3
            - 0.00037436 * t**4
            + 0.0000121272 * t**5
            - 0.0000001699 * t**6
            + 0.000000000875 * t**7
        )
    if year < 1900:
        t = year - 1860.0
        return (
            7.62
            + 0.5737 * t
            - 0.251754 * t**2
            + 0.01680668 * t**3
            - 0.0004473624 * t**4
            + t**5 / 233174.0
        )
    if year < 1920:
        t = year - 1900.0
        return -2.73 + 0.121814 * t - 0.0202206 * t**2 - 0.00110474 * t**3 + t**4 / 24334.4
    if year < 1941:
        t = year - 1920.0
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if year < 1961:
        t = year - 1950.0
        return 29.07 + 0.407 * t - t**2 / 233.0 + t**3 / 2547.0
    if year < 1986:
        t = year - 1975.0
        return 45.45 + 1.067 * t - t**2 / 260.0 - t**3 / 718.0
    if year < 2005:
        t = year - 2000.0
        return 63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3 + 0.000651814 * t**4
    if year <= 2050:
        t = year - 2000.0
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    if year <= 2150:
        return -20.0 + 32.0 * ((year - 1820.0) / 100.0) ** 2 - 0.5628 * (2150.0 - year)

    # 2150+
    return -20.0 + 32.0 * ((year - 1820.0) / 100.0) ** 2


class BirthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: date
    birth_time: str | None = Field(default=None, min_length=4, max_length=15)
    birth_place: str = Field(min_length=1, max_length=255)
    # Story 26.1: birth_timezone is optional — can be None when offline derivation
    # from lat/lon is enabled via TIMEZONE_DERIVED_ENABLED feature flag.
    birth_timezone: str | None = Field(default=None, min_length=1, max_length=64)
    place_resolved_id: int | None = Field(default=None, gt=0)
    # Optional geo/context fields accepted from frontend payloads.
    # They are currently not required by the natal engine pipeline.
    birth_city: str | None = Field(default=None, max_length=255)
    birth_country: str | None = Field(default=None, max_length=100)
    birth_lat: float | None = None
    birth_lon: float | None = None

    @field_validator("birth_place")
    @classmethod
    def validate_non_blank(cls, value: str, info: ValidationInfo) -> str:
        if not value.strip():
            raise ValueError(f"{info.field_name} must not be blank")
        return value.strip()

    @field_validator("birth_timezone")
    @classmethod
    def validate_birth_timezone_non_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.strip():
            raise ValueError("birth_timezone must not be blank")
        return value.strip()

    @field_validator("birth_city", "birth_country")
    @classmethod
    def validate_optional_non_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.strip():
            raise ValueError("optional location field must not be blank")
        return value.strip()

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time_non_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("birth_time must not be blank")
        return value.strip() if value is not None else None


class BirthPreparedData(BaseModel):
    birth_datetime_local: str
    birth_datetime_utc: str
    timestamp_utc: int
    julian_day: float
    birth_timezone: str
    # Canonical fields for the standardized temporal pipeline (story 22.1).
    # jd_ut: Julian Day in Universal Time (UT1 approximation via POSIX timestamp).
    # timezone_used: IANA timezone identifier actually applied for local→UTC conversion.
    # When deserializing legacy payloads that lack these fields, the model validator
    # derives them from julian_day and birth_timezone respectively.
    jd_ut: float | None = None
    timezone_used: str | None = None
    # Terrestrial Time fields (story 22.2) — present only when tt_enabled=True.
    # delta_t_sec: ΔT = TT − UT1 in seconds (deterministic polynomial approximation).
    # jd_tt: Julian Day in Terrestrial Time = jd_ut + delta_t_sec / 86400.
    # time_scale: "TT" when TT fields are computed, "UT" otherwise.
    delta_t_sec: float | None = None
    jd_tt: float | None = None
    time_scale: str = "UT"
    # Story 26.1 — Timezone IANA derivée + source de tracabilité.
    # timezone_iana: IANA identifier of the timezone effectively applied (user-provided or derived).
    # timezone_source: provenance — "user_provided" when supplied by caller, "derived" when
    #   resolved offline from lat/lon coordinates (requires TIMEZONE_DERIVED_ENABLED flag).
    timezone_iana: str | None = None
    timezone_source: str | None = None  # "user_provided" | "derived"

    @model_validator(mode="after")
    def _fill_canonical_temporal_fields(self) -> BirthPreparedData:
        if self.jd_ut is None:
            self.jd_ut = self.julian_day
        if self.timezone_used is None:
            self.timezone_used = self.birth_timezone
        # Story 26.1: fill timezone_iana from timezone_used for legacy payloads.
        if self.timezone_iana is None and self.timezone_used is not None:
            self.timezone_iana = self.timezone_used
        return self


class BirthPreparationError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def _parse_birth_time(raw_value: str) -> time:
    formats = ["%H:%M", "%H:%M:%S", "%H:%M:%S.%f"]
    for fmt in formats:
        try:
            return datetime.strptime(raw_value, fmt).time()
        except ValueError:
            continue

    raise BirthPreparationError(
        code="invalid_birth_time",
        message="birth_time must use HH:MM or HH:MM:SS format",
        details={"field": "birth_time", "value": raw_value},
    )


def _julian_day_from_timestamp(timestamp_utc: float) -> float:
    return (timestamp_utc / 86400.0) + 2440587.5


def prepare_birth_data(
    payload: BirthInput,
    *,
    tt_enabled: bool = False,
    derive_enabled: bool = False,
) -> BirthPreparedData:
    # ---------------------------------------------------------------------------
    # Story 26.1 — Resolve effective timezone with source precedence:
    #   1. user_provided: birth_timezone is explicitly set by the caller.
    #   2. derived: offline derivation from lat/lon (requires derive_enabled=True).
    # ---------------------------------------------------------------------------
    if payload.birth_timezone is not None:
        effective_timezone_iana = payload.birth_timezone
        timezone_source = "user_provided"
    elif derive_enabled:
        if payload.birth_lat is None or payload.birth_lon is None:
            raise BirthPreparationError(
                code="missing_coordinates",
                message="birth_lat and birth_lon are required for timezone derivation",
                details={"field": "birth_lat/birth_lon"},
            )
        derived = _derive_timezone_from_coords(payload.birth_lat, payload.birth_lon)
        if derived is None:
            increment_counter(METRIC_TIMEZONE_DERIVATION_ERRORS)
            raise BirthPreparationError(
                code="timezone_derivation_failed",
                message="Could not derive timezone from coordinates",
                details={
                    "lat": str(payload.birth_lat),
                    "lon": str(payload.birth_lon),
                },
            )
        logger.debug(
            "natal_preparation_timezone_derived lat=%s lon=%s timezone=%s",
            payload.birth_lat,
            payload.birth_lon,
            derived,
        )
        effective_timezone_iana = derived
        timezone_source = "derived"
    else:
        raise BirthPreparationError(
            code="missing_timezone",
            message="birth_timezone is required when timezone derivation is not enabled",
            details={"field": "birth_timezone"},
        )

    try:
        timezone = ZoneInfo(effective_timezone_iana)
    except ZoneInfoNotFoundError as error:
        increment_counter(METRIC_TIMEZONE_ERRORS)
        logger.warning(
            "natal_preparation_invalid_timezone timezone=%s",
            effective_timezone_iana,
        )
        raise BirthPreparationError(
            code="invalid_timezone",
            message="birth_timezone is invalid",
            details={"field": "birth_timezone", "value": effective_timezone_iana},
        ) from error

    # Track timezone source metric (Story 26.1 observability).
    if timezone_source == "user_provided":
        increment_counter(METRIC_TIMEZONE_SOURCE_USER_PROVIDED)
    else:
        increment_counter(METRIC_TIMEZONE_SOURCE_DERIVED)

    if payload.birth_time is not None:
        parsed_time = _parse_birth_time(payload.birth_time)
        local_datetime = datetime.combine(payload.birth_date, parsed_time, tzinfo=timezone)
    else:
        # Improved consistency (Story 22.1 review): use midnight LOCAL when time is missing
        # but timezone is known.
        local_datetime = datetime.combine(payload.birth_date, time(0, 0), tzinfo=timezone)

    utc_datetime = local_datetime.astimezone(ZoneInfo("UTC"))

    # Audit Grade precision: use float timestamp for Julian Day calculation
    ts_full = utc_datetime.timestamp()
    timestamp_utc = int(ts_full)
    julian_day = _julian_day_from_timestamp(ts_full)

    # SwissEph range validation: approx -5401 BC to 5399 AD
    # JD 0 is -4712-01-01. SwissEph usually supports JD -1000000 to 5000000.
    # We'll use a safe range for standard astrology: -3000 BC to 3000 AD
    # JD for -3000-01-01 is ~ 625674.5
    # JD for 3000-01-01 is ~ 2817152.5
    if julian_day < 625674.5 or julian_day > 2817152.5:
        raise BirthPreparationError(
            code="date_out_of_range",
            message="birth_date is out of supported calculation range (-3000 to 3000)",
            details={"julian_day": str(julian_day)},
        )

    # Terrestrial Time (TT) optional trace fields (story 22.2)
    delta_t_sec: float | None = None
    jd_tt: float | None = None
    time_scale = "UT"

    if tt_enabled:
        # decimal_year from full timestamp for continuity (Story 22.2 audit fix)
        # Uses standard astronomical 365.25 day year for polynomial scaling
        decimal_year = 2000.0 + (julian_day - 2451545.0) / 365.25
        delta_t_sec = _delta_t_seconds(decimal_year)
        jd_tt = julian_day + delta_t_sec / 86400.0
        time_scale = "TT"
        increment_counter(METRIC_TT_ENABLED)

    logger.debug(
        (
            "natal_preparation_time_conversion timezone=%s source=%s "
            "jd_ut=%.9f ts_full=%.6f time_scale=%s"
        ),
        effective_timezone_iana,
        timezone_source,
        julian_day,
        ts_full,
        time_scale,
    )

    return BirthPreparedData(
        birth_datetime_local=local_datetime.isoformat(),
        birth_datetime_utc=utc_datetime.isoformat(),
        timestamp_utc=timestamp_utc,
        julian_day=julian_day,
        birth_timezone=effective_timezone_iana,
        jd_ut=julian_day,
        timezone_used=effective_timezone_iana,
        timezone_iana=effective_timezone_iana,
        timezone_source=timezone_source,
        delta_t_sec=delta_t_sec,
        jd_tt=jd_tt,
        time_scale=time_scale,
    )
