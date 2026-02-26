from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class BirthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: date
    birth_time: str | None = Field(default=None, min_length=5, max_length=8)
    birth_place: str = Field(min_length=1, max_length=255)
    birth_timezone: str = Field(min_length=1, max_length=64)
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


class BirthPreparationError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def _parse_birth_time(raw_value: str) -> time:
    formats = ["%H:%M", "%H:%M:%S"]
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


def _julian_day_from_timestamp(timestamp_utc: int) -> float:
    return (timestamp_utc / 86400.0) + 2440587.5


def prepare_birth_data(payload: BirthInput) -> BirthPreparedData:
    try:
        timezone = ZoneInfo(payload.birth_timezone)
    except ZoneInfoNotFoundError as error:
        raise BirthPreparationError(
            code="invalid_timezone",
            message="birth_timezone is invalid",
            details={"field": "birth_timezone", "value": payload.birth_timezone},
        ) from error

    if payload.birth_time is not None:
        parsed_time = _parse_birth_time(payload.birth_time)
        local_datetime = datetime.combine(payload.birth_date, parsed_time, tzinfo=timezone)
    else:
        # birth_time absent: use midnight UTC as fallback for julian_day computation
        local_datetime = datetime.combine(payload.birth_date, time(0, 0), tzinfo=ZoneInfo("UTC"))

    utc_datetime = local_datetime.astimezone(ZoneInfo("UTC"))

    timestamp_utc = int(utc_datetime.timestamp())
    julian_day = _julian_day_from_timestamp(timestamp_utc)

    return BirthPreparedData(
        birth_datetime_local=local_datetime.isoformat(),
        birth_datetime_utc=utc_datetime.isoformat(),
        timestamp_utc=timestamp_utc,
        julian_day=julian_day,
        birth_timezone=payload.birth_timezone,
    )
