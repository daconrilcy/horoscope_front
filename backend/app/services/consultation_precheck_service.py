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
from app.services.user_birth_profile_service import UserBirthProfileService
from app.services.consultation_fallback_service import ConsultationFallbackService

class ConsultationPrecheckService:
    @staticmethod
    def _detect_safeguard_issue(question: Optional[str]) -> Optional[SafeguardIssue]:
        if not question:
            return None
        
        q = question.lower()
        if any(w in q for w in ["santé", "maladie", "cancer", "guérison", "opération", "docteur", "medecin", "health", "disease", "cure", "doctor"]):
            return SafeguardIssue.health
        if any(w in q for w in ["suicide", "finir ma vie", "déprime", "détresse", "distress", "depressed"]):
            return SafeguardIssue.emotional_distress
        if any(w in q for w in ["obsédée", "espionner", "harceler", "obsession", "stalking"]):
            return SafeguardIssue.obsessive_relation
        if any(w in q for w in ["enceinte", "grossesse", "bébé", "enfant", "pregnant", "pregnancy", "baby"]):
            return SafeguardIssue.pregnancy
        if any(w in q for w in ["mort", "décès", "mourir", "death", "die"]):
            return SafeguardIssue.death
        if any(w in q for w in ["argent", "procès", "loi", "juge", "héritage", "money", "legal", "law", "judge", "inheritance"]):
            return SafeguardIssue.legal_finance
        if any(w in q for w in ["manipulation", "secte", "emprise", "gourou", "cult"]):
            return SafeguardIssue.third_party_manipulation
            
        return None

    @staticmethod
    def precheck(db: Session, user_id: int, request: ConsultationPrecheckRequest) -> ConsultationPrecheckData:
        missing_fields = []
        blocking_reasons = []
        available_modes = []
        fallback_mode = None
        safeguard_issue = ConsultationPrecheckService._detect_safeguard_issue(request.question) if hasattr(request, 'question') else None
        
        # 1. Check User Birth Profile
        try:
            user_profile = UserBirthProfileService.get_for_user(db, user_id)
            user_quality = UserProfileQuality.complete if user_profile.birth_time else UserProfileQuality.incomplete
        except Exception: # Simplified for now, should be UserBirthProfileServiceError
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
                missing_fields.append("other_person")
                if status != ConsultationStatus.blocked:
                   available_modes.append("relation_user_only")
            else:
                if not request.other_person.birth_time_known:
                    if status != ConsultationStatus.blocked:
                        status = ConsultationStatus.degraded
                        precision = PrecisionLevel.medium
                        fallback_mode = FallbackMode.other_no_birth_time
                        available_modes.append("other_no_birth_time")
                else:
                    if status == ConsultationStatus.nominal:
                        available_modes.append("relation_full")

        # 4. Handle timing
        if request.consultation_type == "timing":
            if user_quality == UserProfileQuality.incomplete:
                status = ConsultationStatus.degraded
                precision = PrecisionLevel.limited
                fallback_mode = FallbackMode.timing_degraded

        # 5. Safeguard Logic
        safeguard_issue = ConsultationPrecheckService._detect_safeguard_issue(request.question)
        if safeguard_issue:
            resolution = ConsultationFallbackService.resolve_safeguard(safeguard_issue)
            if resolution == "refusal":
                status = ConsultationStatus.blocked
                precision = PrecisionLevel.blocked
                blocking_reasons.append(f"safeguard_refusal_{safeguard_issue.value}")
                fallback_mode = FallbackMode.safeguard_refused
            elif resolution == "reframing":
                if status != ConsultationStatus.blocked:
                    status = ConsultationStatus.degraded
                    fallback_mode = FallbackMode.safeguard_reframed
                    available_modes.append("safeguard_reframed")

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
