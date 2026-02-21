import pytest

from app.domain.astrology.natal_preparation import (
    BirthInput,
    BirthPreparationError,
    prepare_birth_data,
)


def test_prepare_birth_data_converts_to_utc_and_jd() -> None:
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    assert result.birth_datetime_local.startswith("1990-06-15T10:30:00")
    assert result.birth_datetime_utc == "1990-06-15T08:30:00+00:00"
    assert result.timestamp_utc == 645438600
    assert abs(result.julian_day - 2448057.8541666665) < 1e-9


def test_prepare_birth_data_is_deterministic() -> None:
    payload = BirthInput(
        birth_date="2001-01-01",
        birth_time="01:02:03",
        birth_place="Lyon",
        birth_timezone="Europe/Paris",
    )

    first = prepare_birth_data(payload)
    second = prepare_birth_data(payload)

    assert first == second


def test_prepare_birth_data_rejects_invalid_timezone() -> None:
    with pytest.raises(BirthPreparationError) as error:
        prepare_birth_data(
            BirthInput(
                birth_date="1990-06-15",
                birth_time="10:30",
                birth_place="Paris",
                birth_timezone="Mars/Olympus",
            )
        )

    assert error.value.code == "invalid_timezone"
