"""Tests du contrat de resultat natal type."""

import pytest
from pydantic import ValidationError

from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.natal_preparation import BirthPreparedData


def test_natal_result_rejects_untyped_planet_payloads() -> None:
    """Le resultat natal refuse les payloads planetaires non conformes."""
    prepared = BirthPreparedData(
        birth_datetime_local="1990-06-15T10:30:00+02:00",
        birth_datetime_utc="1990-06-15T08:30:00Z",
        timestamp_utc=645438600,
        julian_day=2448057.8541666665,
        birth_timezone="Europe/Paris",
    )

    with pytest.raises(ValidationError):
        NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            prepared_input=prepared,
            planet_positions=[{"planet_code": "sun", "longitude": "invalid"}],
            houses=[],
            aspects=[],
        )


def test_natal_result_exposes_condition_collections() -> None:
    """Le contrat natal expose condition et dominance sans casser les dignites."""
    prepared = BirthPreparedData(
        birth_datetime_local="1990-06-15T10:30:00+02:00",
        birth_datetime_utc="1990-06-15T08:30:00Z",
        timestamp_utc=645438600,
        julian_day=2448057.8541666665,
        birth_timezone="Europe/Paris",
    )

    result = NatalResult(
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        house_system="placidus",
        prepared_input=prepared,
        planet_positions=[],
        houses=[],
        aspects=[],
    )

    assert result.dignities == []
    assert result.condition_profiles == []
    assert result.condition_signals == []
    assert result.planet_dominance is None
