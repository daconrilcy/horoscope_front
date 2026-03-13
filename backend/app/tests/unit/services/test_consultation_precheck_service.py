import pytest
from unittest.mock import MagicMock
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.api.v1.schemas.consultation import ConsultationPrecheckRequest, PrecisionLevel, ConsultationStatus, UserProfileQuality
from app.services.user_birth_profile_service import UserBirthProfileServiceError

def test_precheck_no_profile():
    db = MagicMock()
    user_id = 1
    request = ConsultationPrecheckRequest(consultation_type="period")
    
    # Mock UserBirthProfileService.get_for_user to raise error
    with MagicMock() as mock_service:
        from app.services.user_birth_profile_service import UserBirthProfileService
        UserBirthProfileService.get_for_user = MagicMock(side_effect=UserBirthProfileServiceError(code="birth_profile_not_found", message="not found"))
        
        result = ConsultationPrecheckService.precheck(db, user_id, request)
        
        assert result.user_profile_quality == UserProfileQuality.missing
        assert result.status == ConsultationStatus.blocked
        assert result.precision_level == PrecisionLevel.blocked
        assert "user_birth_profile" in result.missing_fields
        assert "birth_profile_not_found" in result.blocking_reasons

def test_precheck_incomplete_profile():
    db = MagicMock()
    user_id = 1
    request = ConsultationPrecheckRequest(consultation_type="period")
    
    with MagicMock() as mock_service:
        from app.services.user_birth_profile_service import UserBirthProfileService, UserBirthProfileData
        UserBirthProfileService.get_for_user = MagicMock(return_value=UserBirthProfileData(
            birth_date="1990-01-01",
            birth_time=None,
            birth_place="Paris",
            birth_timezone="Europe/Paris",
            geolocation_consent=False
        ))
        
        result = ConsultationPrecheckService.precheck(db, user_id, request)
        
        assert result.user_profile_quality == UserProfileQuality.incomplete
        assert result.status == ConsultationStatus.degraded
        assert result.precision_level == PrecisionLevel.medium
        assert result.fallback_mode == "user_no_birth_time"

def test_precheck_relation_missing_other():
    db = MagicMock()
    user_id = 1
    request = ConsultationPrecheckRequest(consultation_type="relation")
    
    with MagicMock() as mock_service:
        from app.services.user_birth_profile_service import UserBirthProfileService, UserBirthProfileData
        UserBirthProfileService.get_for_user = MagicMock(return_value=UserBirthProfileData(
            birth_date="1990-01-01",
            birth_time="12:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
            geolocation_consent=False
        ))
        
        result = ConsultationPrecheckService.precheck(db, user_id, request)
        
        assert result.consultation_type == "relation"
        assert "other_person" in result.missing_fields
        assert "relation_user_only" in result.available_modes
