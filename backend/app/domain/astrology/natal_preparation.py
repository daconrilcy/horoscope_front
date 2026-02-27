from __future__ import annotations

import logging
from datetime import date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

METRIC_TIMEZONE_ERRORS = "natal_preparation_timezone_errors_total"


class BirthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: date
    birth_time: str | None = Field(default=None, min_length=5, max_length=15)
    birth_place: str = Field(min_length=1, max_length=255)
    birth_timezone: str = Field(min_length=1, max_length=64)
    place_resolved_id: int | None = Field(default=None, gt=0)
    # Optional geo/context fields accepted from frontend payloads.
    # They are currently not required by the natal engine pipeline.
    birth_city: str | None = Field(default=None, max_length=255)
    birth_country: str | None = Field(default=None, max_length=100)
    birth_lat: float | None = None
    birth_lon: float | None = None

    @field_validator("birth_place", "birth_timezone")
    @classmethod
    def validate_non_blank(cls, value: str, info: ValidationInfo) -> str:
        if not value.strip():
            raise ValueError(f"{info.field_name} must not be blank")
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

    @model_validator(mode="after")
    def _fill_canonical_temporal_fields(self) -> BirthPreparedData:
        if self.jd_ut is None:
            self.jd_ut = self.julian_day
        if self.timezone_used is None:
            self.timezone_used = self.birth_timezone
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


def prepare_birth_data(payload: BirthInput) -> BirthPreparedData:
    try:
        timezone = ZoneInfo(payload.birth_timezone)
    except ZoneInfoNotFoundError as error:
        increment_counter(METRIC_TIMEZONE_ERRORS)
        logger.warning(
            "natal_preparation_invalid_timezone timezone=%s",
            payload.birth_timezone,
        )
        raise BirthPreparationError(
            code="invalid_timezone",
            message="birth_timezone is invalid",
            details={"field": "birth_timezone", "value": payload.birth_timezone},
        ) from error

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

    logger.debug(
        "natal_preparation_time_conversion timezone=%s jd_ut=%.9f ts_full=%.6f",
        payload.birth_timezone,
        julian_day,
        ts_full,
    )

    return BirthPreparedData(
        birth_datetime_local=local_datetime.isoformat(),
        birth_datetime_utc=utc_datetime.isoformat(),
        timestamp_utc=timestamp_utc,
        julian_day=julian_day,
        birth_timezone=payload.birth_timezone,
        jd_ut=julian_day,
        timezone_used=payload.birth_timezone,
    )
