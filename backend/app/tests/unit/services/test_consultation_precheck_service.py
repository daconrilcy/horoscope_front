import pytest
from unittest.mock import MagicMock
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.api.v1.schemas.consultation import ConsultationPrecheckRequest, PrecisionLevel, ConsultationStatus, UserProfileQuality, SafeguardIssue
from app.services.user_birth_profile_service import UserBirthProfileServiceError

def test_precheck_no_profile():
    db = MagicMock()
    user_id = 1
    request = ConsultationPrecheckRequest(consultation_type="period")
    
    with MagicMock() as mock_service:
        from app.services.user_birth_profile_service import UserBirthProfileService
        UserBirthProfileService.get_for_user = MagicMock(side_effect=Exception("not found"))
        
        result = ConsultationPrecheckService.precheck(db, user_id, request)
        
        assert result.user_profile_quality == UserProfileQuality.missing
        assert result.status == ConsultationStatus.blocked
        assert "user_birth_profile" in result.missing_fields

def test_precheck_incomplete_profile():
    db = MagicMock()
    user_id = 1
    request = ConsultationPrecheckRequest(consultation_type="period")
    
    from app.services.user_birth_profile_service import UserBirthProfileService, UserBirthProfileData
    UserBirthProfileService.get_for_user = MagicMock(return_value=UserBirthProfileData(
        birth_date="1990-01-01", birth_time=None, birth_place="Paris", birth_timezone="Europe/Paris", geolocation_consent=False
    ))
    
    result = ConsultationPrecheckService.precheck(db, user_id, request)
    assert result.user_profile_quality == UserProfileQuality.incomplete
    assert result.status == ConsultationStatus.degraded
    assert result.fallback_mode == "user_no_birth_time"

def test_precheck_safeguard_refusal_health():
    db = MagicMock()
    user_id = 1
    from app.services.user_birth_profile_service import UserBirthProfileService, UserBirthProfileData
    UserBirthProfileService.get_for_user = MagicMock(return_value=UserBirthProfileData(
        birth_date="1990-01-01", birth_time="12:00", birth_place="Paris", birth_timezone="Europe/Paris", geolocation_consent=False
    ))
    
    request = ConsultationPrecheckRequest(
        consultation_type="period",
        question="Vais-je guérir de mon cancer ?"
    )
    
    result = ConsultationPrecheckService.precheck(db, user_id, request)
    assert result.status == ConsultationStatus.blocked
    assert result.safeguard_issue == SafeguardIssue.health
    assert "safeguard_refusal_health" in result.blocking_reasons

def test_precheck_safeguard_reframing_legal():
    db = MagicMock()
    user_id = 1
    from app.services.user_birth_profile_service import UserBirthProfileService, UserBirthProfileData
    UserBirthProfileService.get_for_user = MagicMock(return_value=UserBirthProfileData(
        birth_date="1990-01-01", birth_time="12:00", birth_place="Paris", birth_timezone="Europe/Paris", geolocation_consent=False
    ))
    
    request = ConsultationPrecheckRequest(
        consultation_type="work",
        question="Vais-je gagner mon procès ?"
    )
    
    result = ConsultationPrecheckService.precheck(db, user_id, request)
    assert result.status == ConsultationStatus.degraded
    assert result.safeguard_issue == SafeguardIssue.legal_finance
    assert result.fallback_mode == "safeguard_reframed"
