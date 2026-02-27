import pytest

from app.domain.astrology.natal_preparation import (
    METRIC_TIMEZONE_ERRORS,
    BirthInput,
    BirthPreparationError,
    BirthPreparedData,
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


# ---------------------------------------------------------------------------
# Story 22.1 — Champs temporels standardisés: jd_ut + timezone_used
# ---------------------------------------------------------------------------


def test_prepare_birth_data_returns_all_required_temporal_fields() -> None:
    """AC1: prepared_input contient les 5 champs temporels obligatoires."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    # Tous les champs obligatoires doivent être présents
    assert result.birth_datetime_local is not None
    assert result.birth_datetime_utc is not None
    assert result.timestamp_utc is not None
    assert result.jd_ut is not None
    assert result.timezone_used is not None


def test_prepare_birth_data_jd_ut_equals_julian_day() -> None:
    """jd_ut est le nom canonique de julian_day (Julian Day Universal Time)."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    assert result.jd_ut == result.julian_day


def test_prepare_birth_data_timezone_used_equals_birth_timezone() -> None:
    """timezone_used reflète exactement le fuseau IANA utilisé pour la conversion."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="America/New_York",
        )
    )

    assert result.timezone_used == "America/New_York"
    assert result.timezone_used == result.birth_timezone


def test_prepare_birth_data_jd_ut_consistent_with_timestamp_utc() -> None:
    """jd_ut est cohérent avec timestamp_utc via la formule standard."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="2000-01-01",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    expected_jd_ut = (result.timestamp_utc / 86400.0) + 2440587.5
    assert abs(result.jd_ut - expected_jd_ut) < 1e-9


# ---------------------------------------------------------------------------
# Story 22.1 — Golden test: cas historique Europe/Paris 1973
# AC2: birth_datetime_utc correspond à la conversion IANA attendue, jd_ut cohérent
# ---------------------------------------------------------------------------


def test_golden_paris_1973_utc_conversion_coherent() -> None:
    """AC2: Europe/Paris 1973 — France UTC+1 toute l'année (DST réintroduit en 1976).

    En 1973, la France n'appliquait pas l'heure d'été: UTC+1 toute l'année.
    12:00 local Europe/Paris → 11:00 UTC.
    """
    result = prepare_birth_data(
        BirthInput(
            birth_date="1973-06-15",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    # France 1973: pas de DST, UTC+1 toute l'année
    assert result.birth_datetime_utc == "1973-06-15T11:00:00+00:00"
    assert result.timezone_used == "Europe/Paris"

    # jd_ut doit être cohérent avec timestamp_utc
    expected_jd_ut = (result.timestamp_utc / 86400.0) + 2440587.5
    assert abs(result.jd_ut - expected_jd_ut) < 1e-9

    # Vérification de la précision décimale
    assert isinstance(result.jd_ut, float)
    assert result.jd_ut == result.julian_day


def test_golden_paris_1973_timestamp_value() -> None:
    """Vérification du timestamp UTC exact pour Europe/Paris 1973-06-15 12:00."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1973-06-15",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    # 1973-06-15 11:00:00 UTC
    # Calcul: 3 ans complets (1970+1971+1972=1096j) + 165j (01/01→14/06) = 1261 jours
    # + 11h = 1261*86400 + 39600 = 108990000
    assert result.timestamp_utc == 108990000

    expected_jd = 108990000 / 86400.0 + 2440587.5
    assert abs(result.jd_ut - expected_jd) < 1e-9


# ---------------------------------------------------------------------------
# Story 22.1 — Observabilité: compteur timezone invalide
# ---------------------------------------------------------------------------


def test_invalid_timezone_increments_metric_counter() -> None:
    """Un fuseau invalide incrémente natal_preparation_timezone_errors_total."""
    from datetime import timedelta

    from app.infra.observability.metrics import get_counter_sum_in_window, reset_metrics

    reset_metrics()

    with pytest.raises(BirthPreparationError):
        prepare_birth_data(
            BirthInput(
                birth_date="1990-06-15",
                birth_time="10:30",
                birth_place="Paris",
                birth_timezone="Invalid/Timezone",
            )
        )

    count = get_counter_sum_in_window(METRIC_TIMEZONE_ERRORS, timedelta(minutes=1))
    assert count == 1.0


# ---------------------------------------------------------------------------
# Story 22.1 — Rétrocompatibilité: legacy BirthPreparedData sans jd_ut/timezone_used
# ---------------------------------------------------------------------------


def test_birth_prepared_data_legacy_compat_fills_canonical_fields() -> None:
    """Un payload legacy sans jd_ut/timezone_used est complété par le model_validator."""
    legacy = BirthPreparedData(
        birth_datetime_local="1990-06-15T12:00:00+02:00",
        birth_datetime_utc="1990-06-15T10:00:00+00:00",
        timestamp_utc=645350400,
        julian_day=2448057.0,
        birth_timezone="Europe/Paris",
        # jd_ut et timezone_used absents → remplis par le validator
    )

    assert legacy.jd_ut == 2448057.0
    assert legacy.timezone_used == "Europe/Paris"


def test_prepare_birth_data_missing_time_uses_local_midnight() -> None:
    """Review Fix: Si l'heure est absente, on utilise minuit LOCAL (pas UTC)."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time=None,
            birth_place="New York",
            birth_timezone="America/New_York",
        )
    )

    # 1990-06-15 00:00:00 America/New_York (EDT, UTC-4)
    # 00:00:00 local -> 04:00:00 UTC
    assert result.birth_datetime_local.startswith("1990-06-15T00:00:00")
    assert "-04:00" in result.birth_datetime_local
    assert result.birth_datetime_utc == "1990-06-15T04:00:00+00:00"


def test_prepare_birth_data_supports_fractional_seconds() -> None:
    """Review Fix: Support des secondes fractionnaires (ex: ISO string)."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30:15.500",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    assert "10:30:15.500" in result.birth_datetime_local
    # 10:30:15.5 Paris (UTC+2) -> 08:30:15.5 UTC
    assert result.birth_datetime_utc == "1990-06-15T08:30:15.500000+00:00"

    # jd_ut should have sub-second precision
    expected_ts = 645438615.5
    assert abs(result.timestamp_utc - int(expected_ts)) == 0
    expected_jd = (expected_ts / 86400.0) + 2440587.5
    assert abs(result.jd_ut - expected_jd) < 1e-9
