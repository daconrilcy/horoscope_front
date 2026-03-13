from unittest.mock import MagicMock

from app.api.v1.schemas.consultation import (
    ConsultationPrecheckRequest,
    ConsultationStatus,
    SafeguardIssue,
    UserProfileQuality,
)
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.services.user_birth_profile_service import (
    UserBirthProfileData,
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


def _mock_birth_profile(monkeypatch, *, birth_time: str | None) -> None:
    monkeypatch.setattr(
        UserBirthProfileService,
        "get_for_user",
        MagicMock(
            return_value=UserBirthProfileData(
                birth_date="1990-01-01",
                birth_time=birth_time,
                birth_place="Paris",
                birth_timezone="Europe/Paris",
                geolocation_consent=False,
            )
        ),
    )


def test_precheck_no_profile(monkeypatch):
    db = MagicMock()
    request = ConsultationPrecheckRequest(consultation_type="period")

    monkeypatch.setattr(
        UserBirthProfileService,
        "get_for_user",
        MagicMock(
            side_effect=UserBirthProfileServiceError(
                code="birth_profile_not_found",
                message="birth profile not found",
            )
        ),
    )

    result = ConsultationPrecheckService.precheck(db, 1, request)

    assert result.user_profile_quality == UserProfileQuality.missing
    assert result.status == ConsultationStatus.blocked
    assert "user_birth_profile" in result.missing_fields


def test_precheck_incomplete_profile(monkeypatch):
    db = MagicMock()
    request = ConsultationPrecheckRequest(consultation_type="period")

    _mock_birth_profile(monkeypatch, birth_time=None)

    result = ConsultationPrecheckService.precheck(db, 1, request)

    assert result.user_profile_quality == UserProfileQuality.incomplete
    assert result.status == ConsultationStatus.degraded
    assert result.fallback_mode == "user_no_birth_time"


def test_precheck_safeguard_refusal_health(monkeypatch):
    db = MagicMock()
    request = ConsultationPrecheckRequest(
        consultation_type="period",
        question="Vais-je guérir de mon cancer ?",
    )

    _mock_birth_profile(monkeypatch, birth_time="12:00")

    result = ConsultationPrecheckService.precheck(db, 1, request)

    assert result.status == ConsultationStatus.blocked
    assert result.safeguard_issue == SafeguardIssue.health
    assert "safeguard_refusal_health" in result.blocking_reasons


def test_precheck_safeguard_reframing_legal(monkeypatch):
    db = MagicMock()
    request = ConsultationPrecheckRequest(
        consultation_type="work",
        question="Vais-je gagner mon procès ?",
    )

    _mock_birth_profile(monkeypatch, birth_time="12:00")

    result = ConsultationPrecheckService.precheck(db, 1, request)

    assert result.status == ConsultationStatus.degraded
    assert result.safeguard_issue == SafeguardIssue.legal_finance
    assert result.fallback_mode == "safeguard_reframed"
