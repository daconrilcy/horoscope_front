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


def test_prepare_birth_data_supports_4_char_time() -> None:
    """Review Fix: Support du format 'H:MM' (ex: '9:00')."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="9:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    assert "09:00:00" in result.birth_datetime_local


# ---------------------------------------------------------------------------
# Story 26.2 — DST ambiguity and non-existent local times
# ---------------------------------------------------------------------------


def test_prepare_birth_data_rejects_ambiguous_local_time() -> None:
    """AC1: Heure locale ambiguë -> erreur métier explicite."""
    with pytest.raises(BirthPreparationError) as exc_info:
        prepare_birth_data(
            BirthInput(
                birth_date="2024-11-03",
                birth_time="01:30",
                birth_place="New York",
                birth_timezone="America/New_York",
            )
        )

    error = exc_info.value
    assert error.code == "ambiguous_local_time"
    assert error.details["timezone"] == "America/New_York"
    assert error.details["local_datetime"] == "2024-11-03T01:30:00"
    assert error.details["candidate_offsets"] == ["-04:00", "-05:00"]


def test_prepare_birth_data_rejects_nonexistent_local_time() -> None:
    """AC2: Heure locale non-existante -> erreur métier explicite."""
    with pytest.raises(BirthPreparationError) as exc_info:
        prepare_birth_data(
            BirthInput(
                birth_date="2024-03-10",
                birth_time="02:30",
                birth_place="New York",
                birth_timezone="America/New_York",
            )
        )

    error = exc_info.value
    assert error.code == "nonexistent_local_time"
    assert error.details["timezone"] == "America/New_York"
    assert error.details["local_datetime"] == "2024-03-10T02:30:00"


def test_prepare_birth_data_midnight_dst_transition() -> None:
    """Edge case: DST transition with non-hour offset (Australia/Lord_Howe)."""
    # Lord Howe Island has a 30-minute DST transition.
    # On 2024-04-07, 02:00:00 local time jumped back to 01:30:00.
    # So 01:45:00 local time is ambiguous (fold).
    with pytest.raises(BirthPreparationError) as exc_info:
        prepare_birth_data(
            BirthInput(
                birth_date="2024-04-07",
                birth_time="01:45",
                birth_place="Lord Howe",
                birth_timezone="Australia/Lord_Howe",
            )
        )
    assert exc_info.value.code == "ambiguous_local_time"
    assert exc_info.value.details["candidate_offsets"] == ["+11:00", "+10:30"]


def test_prepare_birth_data_ambiguity_metrics_incremented() -> None:
    """Observabilité: time_ambiguity_total|type=... incrémenté selon le cas."""
    from datetime import timedelta

    from app.infra.observability.metrics import get_counter_sum_in_window, reset_metrics

    reset_metrics()

    with pytest.raises(BirthPreparationError):
        prepare_birth_data(
            BirthInput(
                birth_date="2024-11-03",
                birth_time="01:30",
                birth_place="New York",
                birth_timezone="America/New_York",
            )
        )

    with pytest.raises(BirthPreparationError):
        prepare_birth_data(
            BirthInput(
                birth_date="2024-03-10",
                birth_time="02:30",
                birth_place="New York",
                birth_timezone="America/New_York",
            )
        )

    ambiguous_count = get_counter_sum_in_window(
        "time_ambiguity_total|type=ambiguous", timedelta(minutes=1)
    )
    nonexistent_count = get_counter_sum_in_window(
        "time_ambiguity_total|type=nonexistent", timedelta(minutes=1)
    )
    assert ambiguous_count == 1.0
    assert nonexistent_count == 1.0


# ---------------------------------------------------------------------------
# Story 26.1 — timezone_iana + timezone_source tracabilite
# ---------------------------------------------------------------------------


def test_prepare_birth_data_timezone_source_user_provided() -> None:
    """AC1: Quand birth_timezone est fourni, timezone_source='user_provided'."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    assert result.timezone_source == "user_provided"
    assert result.timezone_iana == "Europe/Paris"


def test_prepare_birth_data_timezone_iana_equals_birth_timezone() -> None:
    """AC1: timezone_iana reflète le fuseau utilisateur, pas écrasé."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="2000-01-01",
            birth_time="12:00",
            birth_place="New York",
            birth_timezone="America/New_York",
        )
    )

    assert result.timezone_iana == "America/New_York"
    assert result.timezone_used == "America/New_York"
    assert result.timezone_source == "user_provided"


def test_prepare_birth_data_timezone_source_user_provided_not_overwritten() -> None:
    """AC1: La valeur user_provided ne doit pas être écrasée par dérivation."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
            # lat/lon présents mais timezone explicite → source reste user_provided
            birth_lat=48.8566,
            birth_lon=2.3522,
        ),
        derive_enabled=True,
    )

    assert result.timezone_source == "user_provided"
    assert result.timezone_iana == "Europe/Paris"


def test_prepare_birth_data_derive_timezone_from_latlon(monkeypatch: object) -> None:
    """AC2: Sans birth_timezone et derive_enabled=True, timezone est dérivée depuis lat/lon."""
    from app.domain.astrology import natal_preparation

    # Mock derivation to avoid brittleness and dependency on timezonefinder
    # data files in unit tests.
    monkeypatch.setattr(
        natal_preparation, "_derive_timezone_from_coords", lambda lat, lon: "Europe/Paris"
    )

    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone=None,
            birth_lat=48.8566,
            birth_lon=2.3522,
        ),
        derive_enabled=True,
    )

    assert result.timezone_source == "derived"
    assert result.timezone_iana == "Europe/Paris"


def test_prepare_birth_data_no_timezone_no_derive_raises() -> None:
    """AC1: Sans birth_timezone et derive_enabled=False, erreur missing_timezone."""
    with pytest.raises(BirthPreparationError) as exc_info:
        prepare_birth_data(
            BirthInput(
                birth_date="1990-06-15",
                birth_time="10:30",
                birth_place="Paris",
                birth_timezone=None,
            ),
            derive_enabled=False,
        )

    assert exc_info.value.code == "missing_timezone"


def test_prepare_birth_data_derive_enabled_no_latlon_raises() -> None:
    """AC2: derive_enabled=True mais sans lat/lon → erreur missing_coordinates."""
    with pytest.raises(BirthPreparationError) as exc_info:
        prepare_birth_data(
            BirthInput(
                birth_date="1990-06-15",
                birth_time="10:30",
                birth_place="Paris",
                birth_timezone=None,
                birth_lat=None,
                birth_lon=None,
            ),
            derive_enabled=True,
        )

    assert exc_info.value.code == "missing_coordinates"


def test_prepare_birth_data_timezone_iana_consistent_with_timezone_used() -> None:
    """AC3: timezone_iana et timezone_used reflètent la même source effective."""
    result = prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    assert result.timezone_iana == result.timezone_used


def test_prepare_birth_data_timezone_source_metric_incremented() -> None:
    """Observabilité: le compteur timezone_source est incrémenté selon la source."""
    from datetime import timedelta

    from app.infra.observability.metrics import get_counter_sum_in_window, reset_metrics

    reset_metrics()

    prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    count = get_counter_sum_in_window("timezone_source_user_provided_total", timedelta(minutes=1))
    assert count == 1.0


def test_prepare_birth_data_derive_timezone_metric_incremented(monkeypatch: object) -> None:
    """Observabilité: le compteur timezone_source_derived est incrémenté lors d'une dérivation."""
    from datetime import timedelta

    from app.domain.astrology import natal_preparation
    from app.infra.observability.metrics import get_counter_sum_in_window, reset_metrics

    # Mock derivation to avoid dependency on timezonefinder data files.
    monkeypatch.setattr(
        natal_preparation, "_derive_timezone_from_coords", lambda lat, lon: "Europe/Paris"
    )

    reset_metrics()

    prepare_birth_data(
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone=None,
            birth_lat=48.8566,
            birth_lon=2.3522,
        ),
        derive_enabled=True,
    )

    count = get_counter_sum_in_window("timezone_source_derived_total", timedelta(minutes=1))
    assert count == 1.0


def test_birth_prepared_data_legacy_compat_fills_timezone_iana() -> None:
    """Rétrocompatibilité: un payload legacy sans timezone_iana est complété par le validator."""
    legacy = BirthPreparedData(
        birth_datetime_local="1990-06-15T12:00:00+02:00",
        birth_datetime_utc="1990-06-15T10:00:00+00:00",
        timestamp_utc=645350400,
        julian_day=2448057.0,
        birth_timezone="Europe/Paris",
        # timezone_iana et timezone_source absents → timezone_iana rempli par le validator
    )

    assert legacy.timezone_iana == "Europe/Paris"  # dérivé de timezone_used
