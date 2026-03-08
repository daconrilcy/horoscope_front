import pytest

from app.core.config import Settings, settings
from app.jobs.calibration import natal_profiles, validate_dataset


def test_active_ruleset_version_tracks_ruleset_version() -> None:
    local_settings = Settings()
    local_settings.ruleset_version = "rules-v2"

    assert local_settings.active_ruleset_version == "rules-v2"

    local_settings.active_ruleset_version = "rules-v3"

    assert local_settings.ruleset_version == "rules-v3"


def test_calibration_versions_are_resolved_dynamically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "active_reference_version", "ref-v2")
    monkeypatch.setattr(settings, "ruleset_version", "rules-v2")

    assert dict(natal_profiles.CALIBRATION_VERSIONS) == {
        "reference_version": "ref-v2",
        "ruleset_version": "rules-v2",
    }


def test_validate_returns_false_when_profile_keys_are_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        validate_dataset,
        "CALIBRATION_PROFILES",
        [
            {
                "label": "profile_1",
                "natal_chart": {},
                "timezone": "Europe/Paris",
                "latitude": 48.85,
                "longitude": 2.35,
            },
            {
                "label": "profile_2",
                "timezone": "Europe/London",
                "latitude": 51.51,
                "longitude": -0.13,
            },
        ],
    )
    monkeypatch.setattr(
        validate_dataset,
        "CALIBRATION_DATE_RANGE",
        {"start": "2024-01-01", "end": "2024-12-31"},
    )
    monkeypatch.setattr(
        validate_dataset,
        "CALIBRATION_VERSIONS",
        natal_profiles.CalibrationVersions(),
    )

    assert validate_dataset.validate() is False
    output = capsys.readouterr().out
    assert "clés manquantes" in output
    assert "Moins de 5 profils" in output


def test_validate_returns_false_on_invalid_date_range(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        validate_dataset,
        "CALIBRATION_PROFILES",
        natal_profiles.CALIBRATION_PROFILES,
    )
    monkeypatch.setattr(
        validate_dataset,
        "CALIBRATION_DATE_RANGE",
        {"start": "invalid-date", "end": "2024-12-31"},
    )
    monkeypatch.setattr(
        validate_dataset,
        "CALIBRATION_VERSIONS",
        natal_profiles.CalibrationVersions(),
    )

    assert validate_dataset.validate() is False
    output = capsys.readouterr().out
    assert "Plage temporelle invalide" in output
