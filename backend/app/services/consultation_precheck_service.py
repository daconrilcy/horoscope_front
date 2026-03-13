from typing import List, Optional
from sqlalchemy.orm import Session
from app.api.v1.schemas.consultation import (
    ConsultationPrecheckData,
    ConsultationPrecheckRequest,
    PrecisionLevel,
    ConsultationStatus,
    UserProfileQuality,
    FallbackMode,
    SafeguardIssue,
)
from app.services.user_birth_profile_service import UserBirthProfileService, UserBirthProfileServiceError

class ConsultationPrecheckService:
    @staticmethod
    def precheck(db: Session, user_id: int, request: ConsultationPrecheckRequest) -> ConsultationPrecheckData:
        missing_fields = []
        blocking_reasons = []
        available_modes = []
        fallback_mode = None
        safeguard_issue = None
        
        # 1. Check User Birth Profile
        try:
            user_profile = UserBirthProfileService.get_for_user(db, user_id)
            user_quality = UserProfileQuality.complete if user_profile.birth_time else UserProfileQuality.incomplete
        except UserBirthProfileServiceError:
            user_quality = UserProfileQuality.missing
            missing_fields.append("user_birth_profile")
            blocking_reasons.append("birth_profile_not_found")

        # 2. Basic precision & status
        if user_quality == UserProfileQuality.missing:
            precision = PrecisionLevel.blocked
            status = ConsultationStatus.blocked
        elif user_quality == UserProfileQuality.incomplete:
            precision = PrecisionLevel.medium
            status = ConsultationStatus.degraded
            fallback_mode = FallbackMode.user_no_birth_time
            available_modes.append("user_no_birth_time")
        else:
            precision = PrecisionLevel.high
            status = ConsultationStatus.nominal
            available_modes.append("nominal")

        # 3. Handle specific consultation types
        if request.consultation_type == "relation":
            if not request.other_person:
                # If it's a relation consultation but we don't have other person data yet, 
                # we might be at the beginning of the wizard. 
                # We report what's missing but we don't necessarily block if we just want to know "what's possible"
                missing_fields.append("other_person")
                if status != ConsultationStatus.blocked:
                   # If user profile is OK, we can still do "something" or we wait for other person
                   available_modes.append("relation_user_only")
            else:
                if not request.other_person.birth_time_known or not request.other_person.birth_time:
                    if status != ConsultationStatus.blocked:
                        status = ConsultationStatus.degraded
                        precision = PrecisionLevel.medium
                        fallback_mode = FallbackMode.other_no_birth_time
                        available_modes.append("other_no_birth_time")
                else:
                    if status == ConsultationStatus.nominal:
                        available_modes.append("relation_full")
                    else:
                        available_modes.append("relation_degraded")

        # 4. Handle timing
        if request.consultation_type == "timing":
            if user_quality == UserProfileQuality.incomplete:
                # Timing strictly needs birth time for accurate houses
                status = ConsultationStatus.degraded
                precision = PrecisionLevel.limited
                fallback_mode = FallbackMode.timing_degraded

        # 5. Placeholder for safeguard (Story 47.4 will implement it deeper)
        
        return ConsultationPrecheckData(
            consultation_type=request.consultation_type,
            user_profile_quality=user_quality,
            precision_level=precision,
            status=status,
            missing_fields=missing_fields,
            available_modes=available_modes,
            fallback_mode=fallback_mode,
            safeguard_issue=safeguard_issue,
            blocking_reasons=blocking_reasons
        )
