from typing import Final

from sqlalchemy.orm import Session

from app.api.v1.schemas.consultation import (
    ConsultationPrecheckData,
    ConsultationPrecheckRequest,
    ConsultationStatus,
    FallbackMode,
    PrecisionLevel,
    SafeguardIssue,
    UserProfileQuality,
)
from app.services.consultation_fallback_service import ConsultationFallbackService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)

HEALTH_KEYWORDS: Final[tuple[str, ...]] = (
    "santé",
    "maladie",
    "cancer",
    "guérison",
    "opération",
    "docteur",
    "medecin",
    "health",
    "disease",
    "cure",
    "doctor",
)
DISTRESS_KEYWORDS: Final[tuple[str, ...]] = (
    "suicide",
    "finir ma vie",
    "déprime",
    "détresse",
    "distress",
    "depressed",
)
OBSESSIVE_RELATION_KEYWORDS: Final[tuple[str, ...]] = (
    "obsédée",
    "espionner",
    "harceler",
    "obsession",
    "stalking",
)
PREGNANCY_KEYWORDS: Final[tuple[str, ...]] = (
    "enceinte",
    "grossesse",
    "bébé",
    "enfant",
    "pregnant",
    "pregnancy",
    "baby",
)
DEATH_KEYWORDS: Final[tuple[str, ...]] = ("mort", "décès", "mourir", "death", "die")
LEGAL_FINANCE_KEYWORDS: Final[tuple[str, ...]] = (
    "argent",
    "procès",
    "loi",
    "juge",
    "héritage",
    "money",
    "legal",
    "law",
    "judge",
    "inheritance",
)
MANIPULATION_KEYWORDS: Final[tuple[str, ...]] = (
    "manipulation",
    "secte",
    "emprise",
    "gourou",
    "cult",
)


class ConsultationPrecheckService:
    @staticmethod
    def _detect_safeguard_issue(question: str | None) -> SafeguardIssue | None:
        if not question:
            return None

        q = question.lower()
        if any(keyword in q for keyword in HEALTH_KEYWORDS):
            return SafeguardIssue.health
        if any(keyword in q for keyword in DISTRESS_KEYWORDS):
            return SafeguardIssue.emotional_distress
        if any(keyword in q for keyword in OBSESSIVE_RELATION_KEYWORDS):
            return SafeguardIssue.obsessive_relation
        if any(keyword in q for keyword in PREGNANCY_KEYWORDS):
            return SafeguardIssue.pregnancy
        if any(keyword in q for keyword in DEATH_KEYWORDS):
            return SafeguardIssue.death
        if any(keyword in q for keyword in LEGAL_FINANCE_KEYWORDS):
            return SafeguardIssue.legal_finance
        if any(keyword in q for keyword in MANIPULATION_KEYWORDS):
            return SafeguardIssue.third_party_manipulation

        return None

    @staticmethod
    def precheck(
        db: Session,
        user_id: int,
        request: ConsultationPrecheckRequest,
    ) -> ConsultationPrecheckData:
        missing_fields: list[str] = []
        blocking_reasons: list[str] = []
        available_modes: list[str] = []
        fallback_mode: FallbackMode | None = None

        try:
            user_profile = UserBirthProfileService.get_for_user(db, user_id)
            user_quality = (
                UserProfileQuality.complete
                if user_profile.birth_time
                else UserProfileQuality.incomplete
            )
        except UserBirthProfileServiceError:
            user_quality = UserProfileQuality.missing
            missing_fields.append("user_birth_profile")
            blocking_reasons.append("birth_profile_not_found")

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

        if request.consultation_type == "relation":
            if not request.other_person:
                missing_fields.append("other_person")
                if status != ConsultationStatus.blocked:
                    fallback_mode = FallbackMode.relation_user_only
                    status = ConsultationStatus.degraded
                    precision = PrecisionLevel.medium
                    available_modes.append("relation_user_only")
            else:
                if not request.other_person.birth_time_known:
                    if status != ConsultationStatus.blocked:
                        status = ConsultationStatus.degraded
                        precision = PrecisionLevel.medium
                        fallback_mode = FallbackMode.other_no_birth_time
                        available_modes.append("other_no_birth_time")
                elif status == ConsultationStatus.nominal:
                    available_modes.append("relation_full")

        if request.consultation_type == "timing" and user_quality == UserProfileQuality.incomplete:
            status = ConsultationStatus.degraded
            precision = PrecisionLevel.limited
            fallback_mode = FallbackMode.timing_degraded

        safeguard_issue = ConsultationPrecheckService._detect_safeguard_issue(request.question)
        if safeguard_issue:
            resolution = ConsultationFallbackService.resolve_safeguard(safeguard_issue)
            if resolution == "refusal":
                status = ConsultationStatus.blocked
                precision = PrecisionLevel.blocked
                blocking_reasons.append(f"safeguard_refusal_{safeguard_issue.value}")
                fallback_mode = FallbackMode.safeguard_refused
            elif resolution == "reframing" and status != ConsultationStatus.blocked:
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
            blocking_reasons=blocking_reasons,
        )
